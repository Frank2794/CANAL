import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
import json
import logging
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import requests
import os
import threading
import asyncio
import websockets

# ==========================================
# CONFIGURACIÓN DE APIS
# ==========================================

# AISStream - WebSocket
AIS_API_KEY = "a81c935eddaee762e9523b53fc1201aafb308c87"
AIS_WS_URL = "wss://stream.aisstream.io/v0/stream"

# OpenWeather
OPENWEATHER_API_KEY = "66fcd26ed1d5e44ffc760302076c88e1"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Área del Canal de Panamá
CANAL_BBOX = [[-80.5, 8.5], [-79.0, 9.5]]
CANAL_COORDS = {"lat": 9.0, "lon": -79.6}

# Límites estrictos del Canal (para filtrar barcos)
LAT_MIN = 8.85
LAT_MAX = 9.40
LON_MIN = -80.0
LON_MAX = -79.5

# ==========================================
# CONFIGURACIÓN DE LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('anayansi.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="🧠 ANAYANSI - IA Cognitiva",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS CSS
# ==========================================

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 900; color: #00b4d8; }
    .sub-header { font-size: 0.9rem; color: #94a3b8; margin-top: -5px; }
    .metric-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 15px; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: white; }
    .metric-label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; }
    .chat-ai { background: rgba(0,150,255,0.1); border-left: 3px solid #00b4d8; padding: 12px; border-radius: 8px; margin: 8px 0; color: #e2e8f0; }
    .chat-user { background: rgba(15,23,42,0.8); border-left: 3px solid #64748b; padding: 12px; border-radius: 8px; margin: 8px 0; color: #94a3b8; }
    .insight-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 12px; margin: 8px 0; }
    .alert-card { background: rgba(239,68,68,0.1); border: 1px solid #ef4444; border-radius: 10px; padding: 12px; margin: 8px 0; }
    .warning-card { background: rgba(245,158,11,0.1); border: 1px solid #f59e0b; border-radius: 10px; padding: 12px; margin: 8px 0; }
    .info-card { background: rgba(0,150,255,0.1); border: 1px solid #00b4d8; border-radius: 10px; padding: 12px; margin: 8px 0; }
    .footer { text-align: center; color: #475569; padding: 15px 0; border-top: 1px solid #1e293b; margin-top: 20px; font-size: 0.7rem; }
    .decision-card { background: #0f172a; border: 1px solid #00b4d8; border-radius: 10px; padding: 15px; margin: 10px 0; }
    div.stButton > button { background: #00b4d8; color: white; border-radius: 8px; border: none; padding: 0.4rem 1.2rem; font-weight: 600; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 8px 16px; }
    .stTabs [aria-selected="true"] { background: #00b4d8; color: white; border-radius: 6px; }
    .esclusa-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 12px; }
    .real-time-indicator { color: #10b981; font-weight: 600; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CREAR CARPETAS PARA DATOS HISTÓRICOS
# ==========================================

os.makedirs("datos_historicos", exist_ok=True)

# ==========================================
# 1. CLIENTE AISSTREAM - WEBSOCKET CON FILTRO
# ==========================================

class ClienteAIS:
    """Cliente AISStream usando WebSocket - CON FILTRO DE COORDENADAS"""
    
    def __init__(self):
        self.api_key = AIS_API_KEY
        self.ws_url = AIS_WS_URL
        self.bbox = CANAL_BBOX
        self.vessels = {}
        self.barcos_activos = []
        self.ultima_actualizacion = None
        self.is_connected = False
        self._running = False
        self._lock = threading.Lock()
        self._thread = None
        self.lat_min = LAT_MIN
        self.lat_max = LAT_MAX
        self.lon_min = LON_MIN
        self.lon_max = LON_MAX
        
    def iniciar_conexion(self):
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_websocket, daemon=True)
        self._thread.start()
        logger.info("🔌 Conectando a AISStream WebSocket...")
        time.sleep(3)
        
    def _run_websocket(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._connect_websocket())
        except Exception as e:
            logger.error(f"❌ Error en WebSocket: {e}")
            self._running = False
    
    async def _connect_websocket(self):
        subscription_message = {
            "APIKey": self.api_key,
            "BoundingBoxes": [[
                [self.bbox[0][0], self.bbox[0][1]],
                [self.bbox[1][0], self.bbox[1][1]]
            ]],
            "FiltersShipMMSI": [],
            "MessageTypes": ["PositionReport", "ShipStaticData"]
        }
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                await websocket.send(json.dumps(subscription_message))
                self.is_connected = True
                self.ultima_actualizacion = datetime.now()
                logger.info("✅ Conectado a AISStream WebSocket")
                
                while self._running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        
                        if 'MessageType' in data and data['MessageType'] == 'PositionReport':
                            meta = data.get('MetaData', {})
                            pos = data.get('Message', {}).get('PositionReport', {})
                            
                            mmsi = str(meta.get('MMSI', ''))
                            if mmsi:
                                lat = pos.get('Latitude', 0)
                                lon = pos.get('Longitude', 0)
                                
                                if lat != 0 and lon != 0:
                                    if self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max:
                                        with self._lock:
                                            self.vessels[mmsi] = {
                                                'timestamp': meta.get('time_utc', datetime.utcnow().isoformat()),
                                                'mmsi': mmsi,
                                                'ship_name': meta.get('ShipName', 'Desconocido'),
                                                'ship_type': meta.get('ShipType', 'Desconocido'),
                                                'lat': lat,
                                                'lon': lon,
                                                'speed': pos.get('Sog', 0),
                                                'course': pos.get('Cog', 0)
                                            }
                                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error en WebSocket: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            logger.warning("⚠️ Conexión WebSocket cerrada. Reconectando...")
            await asyncio.sleep(5)
            if self._running:
                await self._connect_websocket()
        except Exception as e:
            logger.error(f"❌ Error en WebSocket: {e}")
            self.is_connected = False
            self._running = False
    
    def obtener_barcos_canal(self):
        if not self._running:
            self.iniciar_conexion()
        
        with self._lock:
            self.barcos_activos = list(self.vessels.values())
            return self.barcos_activos
    
    def procesar_barcos_formateados(self):
        barcos = self.obtener_barcos_canal()
        if not barcos:
            return []
        
        barcos_formateados = []
        for barco in barcos:
            lat = barco.get('lat', 0)
            lon = barco.get('lon', 0)
            speed = barco.get('speed', 0)
            
            if lat == 0 or lon == 0:
                continue
            if not (self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max):
                continue
            
            if lat > 9.15:
                direccion = "Sur"
            elif lat < 9.05:
                direccion = "Norte"
            else:
                direccion = "Navegando"
            
            posicion = self._determinar_posicion(lat, lon)
            esclusa = self._determinar_esclusa(lat, lon)
            
            barco_formateado = {
                "nombre": barco.get('ship_name', f"BARCO_{barco.get('mmsi', '')}"),
                "mmsi": barco.get('mmsi', ''),
                "tipo": barco.get('ship_type', 'Desconocido'),
                "direccion": direccion,
                "lat": lat,
                "lon": lon,
                "velocidad": speed,
                "estado": "Navegando" if speed > 1 else "En espera",
                "posicion": posicion,
                "esclusa": esclusa,
                "eta_horas": np.random.uniform(0.5, 6),
                "prioridad": "Media",
                "eslora": 200,
                "calado": 10,
                "carga": 5000,
                "distancia_recorrida": self._calcular_distancia(lat, lon),
                "progreso": self._calcular_progreso(lat, lon),
                "timestamp": datetime.now().isoformat()
            }
            barcos_formateados.append(barco_formateado)
        
        if barcos_formateados:
            self.ultima_actualizacion = datetime.now()
            logger.info(f"✅ {len(barcos_formateados)} barcos válidos en el Canal")
        else:
            logger.warning("⚠️ No hay barcos válidos en el área del Canal")
        
        return barcos_formateados
    
    def _determinar_posicion(self, lat, lon):
        if lat > 9.30:
            return "Entrada Atlántico"
        elif lat > 9.20 and lat <= 9.30:
            return "Gatún"
        elif lat > 9.10 and lat <= 9.20:
            return "Lago Gatún"
        elif lat > 9.03 and lat <= 9.10:
            return "Pedro Miguel"
        elif lat > 8.95 and lat <= 9.03:
            return "Miraflores"
        elif lat > 8.85 and lat <= 8.95:
            return "Salida Pacífico"
        else:
            return "En tránsito"
    
    def _determinar_esclusa(self, lat, lon):
        if 8.95 < lat < 9.05 and -79.6 < lon < -79.55:
            return "Miraflores"
        elif 9.05 < lat < 9.15 and -79.65 < lon < -79.58:
            return "Pedro Miguel"
        elif 9.20 < lat < 9.35 and -79.95 < lon < -79.85:
            return "Gatun"
        else:
            return "En tránsito"
    
    def _calcular_distancia(self, lat, lon):
        lat_ref = 9.36
        lon_ref = -79.92
        distancia = np.sqrt((lat - lat_ref)**2 + (lon - lon_ref)**2) * 111
        return max(0, min(80, distancia))
    
    def _calcular_progreso(self, lat, lon):
        distancia = self._calcular_distancia(lat, lon)
        return min(100, (distancia / 80) * 100)

# ==========================================
# 2. CLIENTE OPENWEATHER
# ==========================================

class ClienteOpenWeather:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = OPENWEATHER_BASE_URL
        self.coords = CANAL_COORDS
        
    def obtener_clima_actual(self):
        url = f"{self.base_url}/weather"
        params = {
            "lat": self.coords["lat"],
            "lon": self.coords["lon"],
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                datos = response.json()
                return {
                    "temperatura": datos["main"]["temp"],
                    "sensacion_termica": datos["main"]["feels_like"],
                    "humedad": datos["main"]["humidity"],
                    "presion": datos["main"]["pressure"],
                    "viento": datos["wind"]["speed"],
                    "descripcion": datos["weather"][0]["description"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Error OpenWeather: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Error conexión OpenWeather: {e}")
            return None
    
    def obtener_estado_maritimo(self):
        clima = self.obtener_clima_actual()
        if not clima:
            return None
        
        viento = clima["viento"]
        if viento < 5:
            estado_mar = "Calmo"
            nivel_oleaje = "Bajo (<0.5m)"
        elif viento < 15:
            estado_mar = "Moderado"
            nivel_oleaje = "Medio (0.5-1.5m)"
        elif viento < 25:
            estado_mar = "Fuerte"
            nivel_oleaje = "Alto (1.5-3m)"
        else:
            estado_mar = "Muy fuerte"
            nivel_oleaje = "Muy alto (>3m)"
        
        return {
            "estado_mar": estado_mar,
            "nivel_oleaje": nivel_oleaje,
            "visibilidad": "Buena" if clima["humedad"] < 80 else "Reducida",
            "recomendacion": self._recomendar_navegacion(viento)
        }
    
    def _recomendar_navegacion(self, viento):
        if viento < 10:
            return "✅ Navegación segura"
        elif viento < 20:
            return "⚠️ Precaución recomendada"
        else:
            return "🔴 Restricciones posibles"

# ==========================================
# 3. SISTEMA DE SEGUIMIENTO DE BARCOS
# ==========================================

class SistemaSeguimientoBarcos:
    def __init__(self):
        self.historial_pasos = []
        self.barcos_en_transito = {}
        self.barcos_completados = []
        self.registro_esclusas = defaultdict(list)
        self.historial_congestion = []
        self.recorridos_completos = []
        
    def registrar_paso_esclusa(self, barco: Dict, esclusa: str, tiempo_espera: float = 0):
        registro = {
            "timestamp": datetime.now().isoformat(),
            "barco": barco["nombre"],
            "tipo": barco["tipo"],
            "direccion": barco["direccion"],
            "esclusa": esclusa,
            "tiempo_espera": round(tiempo_espera, 1),
            "velocidad": barco["velocidad"],
            "posicion": barco.get("posicion", "Desconocida"),
            "distancia_recorrida": barco.get("distancia_recorrida", 0),
            "progreso": barco.get("progreso", 0),
            "distancia_total": 80,
            "hora": datetime.now().strftime("%H:%M")
        }
        self.historial_pasos.append(registro)
        self.registro_esclusas[esclusa].append(registro)
        self._registrar_congestion(esclusa, len(self.registro_esclusas[esclusa]))
        
        if barco["nombre"] not in self.barcos_en_transito:
            self.barcos_en_transito[barco["nombre"]] = {
                "barco": barco,
                "esclusas_pasadas": [],
                "inicio": datetime.now().isoformat(),
                "posiciones": [{
                    "timestamp": datetime.now().isoformat(),
                    "lat": barco["lat"],
                    "lon": barco["lon"],
                    "posicion": barco.get("posicion", "Desconocida"),
                    "progreso": barco.get("progreso", 0)
                }]
            }
        
        self.barcos_en_transito[barco["nombre"]]["esclusas_pasadas"].append({
            "esclusa": esclusa,
            "timestamp": datetime.now().isoformat(),
            "tiempo_espera": tiempo_espera
        })
        
        self.barcos_en_transito[barco["nombre"]]["posiciones"].append({
            "timestamp": datetime.now().isoformat(),
            "lat": barco["lat"],
            "lon": barco["lon"],
            "posicion": barco.get("posicion", "Desconocida"),
            "progreso": barco.get("progreso", 0)
        })
        
        return registro
    
    def _registrar_congestion(self, esclusa: str, barcos_esperando: int):
        self.historial_congestion.append({
            "timestamp": datetime.now().isoformat(),
            "esclusa": esclusa,
            "barcos_esperando": barcos_esperando,
            "nivel": "🟢 Bajo" if barcos_esperando < 5 else "🟡 Medio" if barcos_esperando < 10 else "🔴 Alto"
        })
    
    def registrar_salida_canal(self, barco: Dict, distancia_final: float):
        if barco["nombre"] in self.barcos_en_transito:
            recorrido = {
                "timestamp": datetime.now().isoformat(),
                "barco": barco["nombre"],
                "tipo": barco["tipo"],
                "direccion": barco["direccion"],
                "distancia_recorrida": distancia_final,
                "distancia_total": 80,
                "tiempo_total": self._calcular_tiempo_total(barco["nombre"]),
                "esclusas_pasadas": self.barcos_en_transito[barco["nombre"]]["esclusas_pasadas"],
                "posiciones": self.barcos_en_transito[barco["nombre"]]["posiciones"]
            }
            self.recorridos_completos.append(recorrido)
            
            registro = {
                "timestamp": datetime.now().isoformat(),
                "barco": barco["nombre"],
                "distancia_recorrida": distancia_final,
                "distancia_total": 80,
                "tiempo_total": self._calcular_tiempo_total(barco["nombre"])
            }
            self.barcos_completados.append(registro)
            self.barcos_en_transito.pop(barco["nombre"], None)
            return registro
        return None
    
    def _calcular_tiempo_total(self, nombre_barco):
        if nombre_barco in self.barcos_en_transito:
            inicio = datetime.fromisoformat(self.barcos_en_transito[nombre_barco]["inicio"])
            ahora = datetime.now()
            return round((ahora - inicio).total_seconds() / 60, 1)
        return 0
    
    def obtener_estado_barco(self, nombre_barco):
        if nombre_barco in self.barcos_en_transito:
            datos = self.barcos_en_transito[nombre_barco]
            esclusas_pasadas = len(datos["esclusas_pasadas"])
            ultima_esclusa = datos["esclusas_pasadas"][-1]["esclusa"] if esclusas_pasadas > 0 else "Ninguna"
            ultima_posicion = datos["posiciones"][-1] if datos["posiciones"] else {}
            progreso = ultima_posicion.get("progreso", 0)
            
            return {
                "estado": "En tránsito",
                "progreso": round(progreso, 1),
                "esclusas_pasadas": esclusas_pasadas,
                "ultima_esclusa": ultima_esclusa,
                "ultima_posicion": ultima_posicion.get("posicion", "Desconocida"),
                "tiempo_total": self._calcular_tiempo_total(nombre_barco),
                "distancia_recorrida": ultima_posicion.get("distancia_recorrida", 0)
            }
        else:
            for completado in self.barcos_completados:
                if completado["barco"] == nombre_barco:
                    return {
                        "estado": "✅ Completado",
                        "progreso": 100,
                        "distancia_recorrida": completado["distancia_recorrida"],
                        "tiempo_total": completado["tiempo_total"]
                    }
            return {"estado": "No encontrado"}
    
    def obtener_recorrido_barco(self, nombre_barco):
        if nombre_barco in self.barcos_en_transito:
            return self.barcos_en_transito[nombre_barco]["posiciones"]
        
        for recorrido in self.recorridos_completos:
            if recorrido["barco"] == nombre_barco:
                return recorrido["posiciones"]
        
        return []
    
    def obtener_estadisticas_esclusa(self, esclusa):
        if esclusa in self.registro_esclusas:
            registros = self.registro_esclusas[esclusa]
            if registros:
                tiempos_espera = [r["tiempo_espera"] for r in registros]
                return {
                    "total_barcos": len(registros),
                    "tiempo_espera_promedio": round(sum(tiempos_espera) / len(tiempos_espera), 1),
                    "tiempo_espera_max": round(max(tiempos_espera), 1),
                    "tiempo_espera_min": round(min(tiempos_espera), 1),
                    "ultimos_pasos": registros[-5:]
                }
        return None
    
    def obtener_datos_congestion(self):
        if not self.historial_congestion:
            return pd.DataFrame()
        df = pd.DataFrame(self.historial_congestion)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

# ==========================================
# 4. SISTEMA DE DATOS REALES
# ==========================================

class SistemaDatosReales:
    def __init__(self):
        self.cliente_ais = ClienteAIS()
        self.cliente_clima = ClienteOpenWeather()
        self.barcos = []
        self.clima = {}
        self.estado_maritimo = {}
        self.ultima_actualizacion = None
        
    def iniciar(self):
        self.cliente_ais.iniciar_conexion()
        self.actualizar_todo()
        
    def actualizar_todo(self):
        try:
            self.barcos = self.cliente_ais.procesar_barcos_formateados()
            self.clima = self.cliente_clima.obtener_clima_actual()
            self.estado_maritimo = self.cliente_clima.obtener_estado_maritimo()
            self.ultima_actualizacion = datetime.now()
            
            if self.barcos:
                logger.info(f"✅ {len(self.barcos)} barcos reales de AISStream")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando: {e}")
            return False
    
    def obtener_barcos_activos(self):
        return self.barcos
    
    def obtener_clima_actual(self):
        return self.clima
    
    def verificar_estado_conexiones(self):
        estado = {
            "ais": self.cliente_ais.is_connected,
            "clima": self.clima is not None,
            "ultima_actualizacion": self.ultima_actualizacion
        }
        return estado

# ==========================================
# 5. SISTEMA DE TIEMPO REAL
# ==========================================

class SistemaTiempoReal:
    def __init__(self):
        self.ultima_actualizacion = None
        self.proxima_actualizacion = None
        self.intervalo_segundos = 60
        self.actualizando = False
        self.historial_actualizaciones = []
        self.errores_actualizacion = []
        self.ejecutando = False
        self.thread_actualizacion = None
        
    def iniciar(self):
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.thread_actualizacion = threading.Thread(target=self._loop_actualizacion, daemon=True)
        self.thread_actualizacion.start()
        logger.info("🔄 Sistema de tiempo real iniciado (60s)")
        
    def _loop_actualizacion(self):
        while self.ejecutando:
            try:
                self.actualizar_todo()
                time.sleep(self.intervalo_segundos)
            except Exception as e:
                logger.error(f"❌ Error en loop de actualización: {e}")
                time.sleep(5)
    
    def actualizar_todo(self):
        if self.actualizando:
            return
        
        self.actualizando = True
        inicio = datetime.now()
        
        try:
            sistema_datos.actualizar_todo()
            
            df_actual = generar_datos()
            stats_actuales = analizar(df_actual)
            
            st.session_state.df = df_actual
            st.session_state.stats = stats_actuales
            st.session_state.ultima_actualizacion = datetime.now()
            
            if 'anayansi' in st.session_state:
                nuevos_aprendizajes = st.session_state.anayansi.aprender_automaticamente(df_actual, stats_actuales)
                st.session_state.nuevos_aprendizajes = nuevos_aprendizajes
            
            if len(df_actual) > 0 and 'sistema_seguimiento' in st.session_state:
                for _, barco in df_actual.iterrows():
                    if barco.get('esclusa', '') in ['Gatun', 'Pedro Miguel', 'Miraflores']:
                        st.session_state.sistema_seguimiento.registrar_paso_esclusa(
                            barco.to_dict(),
                            barco.get('esclusa', ''),
                            random.uniform(0.5, 2.0)
                        )
            
            self._guardar_historico(df_actual, stats_actuales)
            
            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()
            
            registro = {
                "timestamp": fin.isoformat(),
                "duracion": round(duracion, 2),
                "barcos": len(df_actual),
                "cwt": stats_actuales["cwt"],
                "exito": True
            }
            self.historial_actualizaciones.append(registro)
            
            if len(self.historial_actualizaciones) > 1000:
                self.historial_actualizaciones = self.historial_actualizaciones[-1000:]
            
            self.ultima_actualizacion = fin
            self.proxima_actualizacion = fin + timedelta(seconds=self.intervalo_segundos)
            
            self.actualizando = False
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en actualización: {e}")
            self.errores_actualizacion.append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            self.actualizando = False
            return False
    
    def _guardar_historico(self, df, stats):
        try:
            df.to_csv("datos_historicos/barcos_tiempo_real.csv", index=False)
            
            with open("datos_historicos/stats_tiempo_real.json", "w") as f:
                json.dump(stats, f, default=str)
            
            historico = []
            if os.path.exists("datos_historicos/historico_completo.json"):
                with open("datos_historicos/historico_completo.json", "r") as f:
                    historico = json.load(f)
            
            registro = {
                "timestamp": datetime.now().isoformat(),
                "barcos": len(df),
                "stats": stats
            }
            historico.append(registro)
            
            if len(historico) > 500:
                historico = historico[-500:]
            
            with open("datos_historicos/historico_completo.json", "w") as f:
                json.dump(historico, f, default=str)
                
        except Exception as e:
            logger.error(f"Error guardando histórico: {e}")
    
    def obtener_tendencia(self):
        try:
            if os.path.exists("datos_historicos/historico_completo.json"):
                with open("datos_historicos/historico_completo.json", "r") as f:
                    historico = json.load(f)
                    if historico:
                        return historico[-50:]
        except:
            pass
        return []

# ==========================================
# 6. FUNCIONES PARA GRÁFICOS
# ==========================================

def crear_grafico_tiempos_esclusas(sistema_seguimiento):
    esclusas = ["Gatun", "Pedro Miguel", "Miraflores"]
    datos = []
    
    for esclusa in esclusas:
        stats = sistema_seguimiento.obtener_estadisticas_esclusa(esclusa)
        if stats:
            datos.append({
                "Esclusa": esclusa,
                "Tiempo promedio (min)": stats["tiempo_espera_promedio"],
                "Tiempo máximo (min)": stats["tiempo_espera_max"],
                "Tiempo mínimo (min)": stats["tiempo_espera_min"]
            })
    
    if datos:
        df = pd.DataFrame(datos)
        fig = px.bar(
            df,
            x="Esclusa",
            y="Tiempo promedio (min)",
            title="⏱️ Tiempo Promedio de Espera por Esclusa",
            color="Esclusa",
            color_discrete_map={"Gatun": "#3b82f6", "Pedro Miguel": "#f59e0b", "Miraflores": "#10b981"},
            text="Tiempo promedio (min)"
        )
        fig.update_layout(height=350)
        return fig
    return None

def crear_grafico_congestion(sistema_seguimiento):
    df_congestion = sistema_seguimiento.obtener_datos_congestion()
    if not df_congestion.empty:
        fig = px.line(
            df_congestion,
            x="timestamp",
            y="barcos_esperando",
            color="esclusa",
            title="📊 Evolución de Congestión por Esclusa",
            labels={"timestamp": "Hora", "barcos_esperando": "Barcos en espera"}
        )
        fig.update_layout(height=300)
        return fig
    return None

def crear_mapa_calor_esclusas(sistema_seguimiento):
    df_congestion = sistema_seguimiento.obtener_datos_congestion()
    if not df_congestion.empty:
        df_congestion["hora"] = pd.to_datetime(df_congestion["timestamp"]).dt.hour
        pivot = df_congestion.pivot_table(
            values="barcos_esperando",
            index="hora",
            columns="esclusa",
            aggfunc="mean"
        ).fillna(0)
        
        if not pivot.empty:
            fig = px.imshow(
                pivot,
                title="🌡️ Mapa de Calor de Congestión por Esclusa",
                labels={"x": "Esclusa", "y": "Hora", "color": "Barcos esperando"},
                color_continuous_scale="RdYlGn_r"
            )
            fig.update_layout(height=300)
            return fig
    return None

def crear_grafico_progreso_barcos(sistema_seguimiento):
    if sistema_seguimiento.barcos_en_transito:
        data = []
        for nombre, datos in sistema_seguimiento.barcos_en_transito.items():
            estado = sistema_seguimiento.obtener_estado_barco(nombre)
            data.append({
                "Barco": nombre,
                "Progreso (%)": estado["progreso"],
                "Posición": estado.get("ultima_posicion", "Desconocida"),
                "Tiempo (min)": estado["tiempo_total"]
            })
        
        if data:
            df = pd.DataFrame(data)
            fig = px.bar(
                df,
                x="Barco",
                y="Progreso (%)",
                title="📈 Progreso de Barcos en Tránsito",
                color="Progreso (%)",
                color_continuous_scale="Viridis",
                text="Progreso (%)"
            )
            fig.update_layout(height=300)
            return fig
    return None

def crear_grafico_recorrido_barco(posiciones):
    if not posiciones:
        return None
    
    df = pd.DataFrame(posiciones)
    if len(df) < 2:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(df["timestamp"]),
        y=df["progreso"],
        mode='lines+markers',
        name='Progreso',
        line=dict(color='#00b4d8', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="📊 Recorrido del Barco en el Canal",
        xaxis_title="Tiempo",
        yaxis_title="Progreso (%)",
        height=300,
        template="plotly_dark",
        hovermode="x unified"
    )
    
    return fig

def crear_grafico_tiempo_real():
    historico = sistema_tiempo_real.obtener_tendencia()
    
    if historico and len(historico) > 2:
        fechas = []
        cwt_values = []
        barcos_values = []
        
        for registro in historico:
            if "timestamp" in registro and "stats" in registro:
                fechas.append(registro["timestamp"][11:19])
                cwt_values.append(registro["stats"].get("cwt", 0))
                barcos_values.append(registro["stats"].get("total", 0))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=fechas[-30:],
            y=cwt_values[-30:],
            mode='lines+markers',
            name='CWT',
            line=dict(color='#00b4d8', width=2),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=fechas[-30:],
            y=barcos_values[-30:],
            mode='lines+markers',
            name='Barcos',
            line=dict(color='#f59e0b', width=2),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="📊 Evolución en Tiempo Real (60s)",
            xaxis_title="Hora",
            yaxis_title="CWT (horas)",
            yaxis2=dict(
                title="Barcos",
                overlaying='y',
                side='right'
            ),
            height=300,
            template="plotly_dark",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    return None

# ==========================================
# 7. GENERAR DATOS
# ==========================================

@st.cache_data(ttl=60)
def generar_datos():
    sistema_datos.actualizar_todo()
    barcos_reales = sistema_datos.obtener_barcos_activos()
    
    if barcos_reales and len(barcos_reales) > 0:
        logger.info(f"✅ Usando {len(barcos_reales)} barcos reales de AISStream")
        df = pd.DataFrame(barcos_reales)
        return df
    
    logger.info("⚠️ Usando datos simulados (fallback)")
    barcos_simulados = generar_barcos_simulados(40)
    df = pd.DataFrame(barcos_simulados)
    return df

def generar_barcos_simulados(n):
    np.random.seed(int(time.time() / 30) % 1000)
    tipos = ["Portacontenedores", "Granelero", "Petrolero", "Gasero", "Carguero", "Crucero"]
    estados = ["Navegando", "Navegando", "Navegando", "En espera", "Entrando"]
    esclusas = ["Gatun", "Pedro Miguel", "Miraflores"]
    prioridades = ["Alta", "Media", "Baja"]
    posiciones = ["Entrada Atlántico", "Gatún", "Lago Gatún", "Pedro Miguel", "Miraflores", "Salida Pacífico"]
    
    barcos = []
    for i in range(n):
        progreso = np.random.uniform(0, 100)
        lat = 8.90 + (progreso / 100) * 0.40
        lon = -79.95 + (progreso / 100) * 0.40
        
        barco = {
            "nombre": f"BARCO_{i+1:04d}",
            "tipo": random.choice(tipos),
            "direccion": "Sur" if np.random.random() < 0.5 else "Norte",
            "lat": lat,
            "lon": lon,
            "velocidad": np.random.uniform(4, 16) if random.random() < 0.7 else np.random.uniform(0, 3),
            "estado": random.choice(estados),
            "esclusa": random.choice(esclusas),
            "posicion": random.choice(posiciones),
            "eta_horas": np.random.uniform(0.5, 8),
            "prioridad": random.choice(prioridades),
            "eslora": np.random.uniform(80, 400),
            "calado": np.random.uniform(8, 18),
            "carga": np.random.uniform(100, 10000),
            "distancia_recorrida": progreso * 0.8,
            "progreso": progreso,
            "timestamp": datetime.now().isoformat()
        }
        barcos.append(barco)
    return barcos

# ==========================================
# 8. ANÁLISIS
# ==========================================

@st.cache_data(ttl=60)
def analizar(df):
    stats = {
        "total": len(df),
        "norte": len(df[df["direccion"] == "Norte"]),
        "sur": len(df[df["direccion"] == "Sur"]),
        "espera": len(df[df["estado"] == "En espera"]),
        "prioridad_alta": len(df[df["prioridad"] == "Alta"]),
        "velocidad_prom": df["velocidad"].mean(),
        "esclusas": {},
        "tipos": df["tipo"].value_counts().to_dict(),
        "posiciones": df["posicion"].value_counts().to_dict() if "posicion" in df.columns else {},
        "progreso_prom": df["progreso"].mean() if "progreso" in df.columns else 0,
        "temp": 25 + np.random.normal(0, 2),
        "viento": np.random.uniform(5, 25),
        "humedad": 70 + np.random.normal(0, 8),
        "marea": 2.5 + np.random.normal(0, 0.2),
        "profundidad": 13.5 + np.random.normal(0, 0.3),
        "oleaje": 1.0 + np.random.normal(0, 0.2)
    }
    
    for e in ["Gatun", "Pedro Miguel", "Miraflores"]:
        df_e = df[df["esclusa"] == e]
        stats["esclusas"][e] = {"total": len(df_e), "espera": len(df_e[df_e["estado"] == "En espera"])}
    
    stats["cwt"] = 12 + max(0, (stats["total"] - 25) * 0.1) + stats["espera"] * 0.12
    stats["cwt"] = min(40, max(8, stats["cwt"]))
    
    if stats["cwt"] < 14:
        stats["nivel"] = "🟢 Bajo"; stats["color"] = "#10b981"
    elif stats["cwt"] < 18:
        stats["nivel"] = "🟡 Moderado"; stats["color"] = "#f59e0b"
    elif stats["cwt"] < 23:
        stats["nivel"] = "🟠 Alto"; stats["color"] = "#f97316"
    else:
        stats["nivel"] = "🔴 Critico"; stats["color"] = "#ef4444"
    
    return stats

# ==========================================
# 9. FUNCIONES PARA MAPA MEJORADO (2D Y 3D) - CORREGIDAS
# ==========================================

def crear_mapa_2d(df, estilo):
    """Crea mapa 2D con diferentes estilos - CORREGIDO"""
    estilos_map = {
        "🌍 Satélite": "satellite-streets",
        "🏙️ Calles": "carto-positron",
        "🌄 Relieve": "outdoors",
        "🌃 Nocturno": "dark"
    }
    
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos para mostrar en el mapa",
            height=550
        )
        return fig
    
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        hover_name="nombre",
        hover_data={
            "tipo": True,
            "direccion": True,
            "estado": True,
            "velocidad": ":.1f",
            "esclusa": True,
            "posicion": True,
            "progreso": ":.1f",
            "eta_horas": ":.1f",
            "prioridad": True
        },
        color="prioridad",
        color_discrete_map={"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"},
        size="velocidad",
        size_max=18,
        zoom=9.5,
        height=550,
        title="📍 Navegación en el Canal de Panamá"
    )
    
    # Agregar esclusas con add_scattermapbox
    esclusas_coords = {
        "Gatún": {"lat": 9.27, "lon": -79.92, "color": "#ef4444"},
        "Pedro Miguel": {"lat": 9.015, "lon": -79.62, "color": "#f59e0b"},
        "Miraflores": {"lat": 8.995, "lon": -79.585, "color": "#10b981"}
    }
    
    for nombre, coords in esclusas_coords.items():
        fig.add_scattermapbox(
            lat=[coords["lat"]],
            lon=[coords["lon"]],
            mode="markers",
            marker=dict(size=20, color=coords["color"], symbol="triangle-up"),
            name=f"⚙️ {nombre}",
            hoverinfo="text",
            hovertext=[f"<b>⚙️ Esclusa de {nombre}</b>"]
        )
    
    fig.update_layout(
        mapbox=dict(
            style=estilos_map.get(estilo, "satellite-streets"),
            center=dict(lat=9.15, lon=-79.75),
            zoom=9.5
        ),
        margin=dict(r=0, t=30, l=0, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    return fig

def crear_mapa_3d(df):
    """Crea mapa 3D con relieve - CORREGIDO"""
    
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No hay datos para mostrar en 3D", height=550)
        return fig
    
    color_map = {"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"}
    colores = df["prioridad"].map(color_map).fillna("#94a3b8")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter3d(
        x=df["lon"],
        y=df["lat"],
        z=df["velocidad"] * 0.3,
        mode="markers",
        marker=dict(
            size=df["velocidad"] * 1.2 + 4,
            color=colores,
            symbol="circle",
            opacity=0.8,
            line=dict(width=1, color="white")
        ),
        text=df["nombre"],
        hovertemplate=
            "<b>%{text}</b><br>" +
            "Velocidad: %{customdata[0]:.1f} nudos<br>" +
            "Progreso: %{customdata[1]:.0f}%<br>" +
            "Posición: %{customdata[2]}<br>" +
            "Prioridad: %{customdata[3]}<extra></extra>",
        customdata=np.column_stack([
            df["velocidad"],
            df["progreso"],
            df["posicion"],
            df["prioridad"]
        ]),
        name="Barcos"
    ))
    
    esclusas_coords = {
        "Gatún": {"lat": 9.27, "lon": -79.92},
        "Pedro Miguel": {"lat": 9.015, "lon": -79.62},
        "Miraflores": {"lat": 8.995, "lon": -79.585}
    }
    
    for nombre, coords in esclusas_coords.items():
        fig.add_trace(go.Scatter3d(
            x=[coords["lon"]],
            y=[coords["lat"]],
            z=[2],
            mode="markers+text",
            marker=dict(size=12, color="red", symbol="diamond"),
            text=[f"⚙️ {nombre}"],
            textposition="top center",
            name=f"⚙️ {nombre}",
            hovertemplate=f"<b>⚙️ Esclusa de {nombre}</b><extra></extra>"
        ))
    
    fig.update_layout(
        title="🌍 Mapa 3D del Canal de Panamá",
        scene=dict(
            xaxis=dict(title="Longitud", range=[-80.0, -79.5]),
            yaxis=dict(title="Latitud", range=[8.85, 9.40]),
            zaxis=dict(title="Velocidad (nudos)", range=[0, 8]),
            camera=dict(eye=dict(x=0.5, y=0.5, z=1.8)),
            bgcolor="rgba(0,0,0,0)"
        ),
        height=550,
        margin=dict(r=0, l=0, b=0, t=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    return fig

# ==========================================
# 10. FUNCIONES PARA EL DASHBOARD
# ==========================================

def mostrar_indicador_datos_reales():
    estado = sistema_datos.verificar_estado_conexiones()
    
    st.markdown("---")
    st.markdown("#### 📡 Datos en Tiempo Real")
    
    if estado["ais"]:
        st.success("🟢 AISStream WebSocket")
        st.caption(f"🚢 {len(sistema_datos.barcos)} barcos")
    else:
        st.warning("🟡 AISStream - Conectando...")
    
    if estado["clima"]:
        st.success("🟢 OpenWeather")
        if sistema_datos.clima:
            st.caption(f"🌡️ {sistema_datos.clima.get('temperatura', 'N/A')}°C")
    else:
        st.warning("🟡 OpenWeather - Conectando...")
    
    if sistema_datos.ultima_actualizacion:
        st.caption(f"🕐 {sistema_datos.ultima_actualizacion.strftime('%H:%M:%S')}")
    
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        with st.spinner("Actualizando datos reales..."):
            sistema_datos.actualizar_todo()
            st.rerun()

def mostrar_indicador_tiempo_real():
    sistema = st.session_state.sistema_tiempo_real
    
    st.markdown("---")
    st.markdown("#### ⚡ Tiempo Real")
    
    if sistema.ultima_actualizacion:
        ultima = sistema.ultima_actualizacion
        tiempo_transcurrido = (datetime.now() - ultima).seconds
        st.caption(f"🕐 Última actualización: {ultima.strftime('%H:%M:%S')}")
        st.caption(f"⏱️ Hace {tiempo_transcurrido}s")
        
        progreso = min(tiempo_transcurrido / sistema.intervalo_segundos, 1.0)
        st.progress(progreso)
        
        if sistema.proxima_actualizacion:
            st.caption(f"⏳ Próxima: {sistema.proxima_actualizacion.strftime('%H:%M:%S')}")
    else:
        st.warning("⏳ Iniciando...")
    
    if sistema.actualizando:
        st.info("🔄 Actualizando...")
    else:
        st.success("✅ Activo")
    
    if st.button("🔄 Actualizar Ahora", use_container_width=True):
        with st.spinner("Actualizando..."):
            sistema.actualizar_todo()
            st.rerun()

def mostrar_clima_dashboard():
    clima = sistema_datos.obtener_clima_actual()
    estado_mar = sistema_datos.cliente_clima.obtener_estado_maritimo()
    
    if clima:
        st.markdown("#### 🌤️ Clima y Mar - Datos Reales")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🌡️ Temperatura", f"{clima.get('temperatura', 'N/A')}°C")
        with col2:
            st.metric("💨 Viento", f"{clima.get('viento', 'N/A')} nudos")
        with col3:
            st.metric("💧 Humedad", f"{clima.get('humedad', 'N/A')}%")
        with col4:
            st.metric("📊 Presión", f"{clima.get('presion', 'N/A')} hPa")
        with col5:
            st.metric("🌊 Oleaje", estado_mar.get("nivel_oleaje", "N/A") if estado_mar else "N/A")
        
        if estado_mar and estado_mar.get("recomendacion"):
            rec = estado_mar["recomendacion"]
            if "✅" in rec:
                st.success(f"🚢 {rec}")
            elif "⚠️" in rec:
                st.warning(f"🚢 {rec}")
            else:
                st.error(f"🚢 {rec}")

def mostrar_grafico_tiempo_real():
    fig = crear_grafico_tiempo_real()
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⏳ Recopilando datos para gráfico en tiempo real...")

# ==========================================
# 11. SIMULAR PASO DE BARCOS
# ==========================================

def simular_paso_barcos(df, sistema_seguimiento):
    if isinstance(df, pd.DataFrame):
        barcos_aleatorios = df.sample(min(5, len(df)))
    else:
        barcos_aleatorios = df[:5]
    
    for _, barco in barcos_aleatorios.iterrows() if isinstance(df, pd.DataFrame) else enumerate(barcos_aleatorios):
        if isinstance(barco, pd.Series):
            barco_dict = barco.to_dict()
        else:
            barco_dict = barco
        
        esclusa = barco_dict.get("esclusa", random.choice(["Gatun", "Pedro Miguel", "Miraflores"]))
        tiempo_espera = random.uniform(0.5, 3.0)
        
        sistema_seguimiento.registrar_paso_esclusa(
            barco_dict,
            esclusa,
            tiempo_espera
        )
        
        distancia = random.uniform(10, 70)
        barco_dict["distancia_recorrida"] = distancia
        barco_dict["progreso"] = (distancia / 80) * 100
        
        if distancia > 70:
            sistema_seguimiento.registrar_salida_canal(barco_dict, distancia)
    
    return sistema_seguimiento

# ==========================================
# 12. INICIALIZAR SISTEMAS
# ==========================================

if "sistema_datos" not in st.session_state:
    st.session_state.sistema_datos = SistemaDatosReales()
    st.session_state.sistema_datos.iniciar()

sistema_datos = st.session_state.sistema_datos

if "sistema_seguimiento" not in st.session_state:
    st.session_state.sistema_seguimiento = SistemaSeguimientoBarcos()

sistema_seguimiento = st.session_state.sistema_seguimiento

if "sistema_tiempo_real" not in st.session_state:
    st.session_state.sistema_tiempo_real = SistemaTiempoReal()
    st.session_state.sistema_tiempo_real.iniciar()

sistema_tiempo_real = st.session_state.sistema_tiempo_real

if "df" not in st.session_state or "stats" not in st.session_state:
    df = generar_datos()
    stats = analizar(df)
    st.session_state.df = df
    st.session_state.stats = stats
    st.session_state.ultima_actualizacion = datetime.now()
else:
    df = st.session_state.df
    stats = st.session_state.stats

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("### 🧠 ANAYANSI")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    col1.metric("🚢 Barcos", stats["total"])
    col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
    
    st.markdown("---")
    st.markdown("#### ⬆️⬇️ Dirección")
    col1, col2 = st.columns(2)
    col1.metric("Norte", stats["norte"])
    col2.metric("Sur", stats["sur"])
    
    mostrar_indicador_tiempo_real()
    mostrar_indicador_datos_reales()
    
    st.markdown("---")
    
    if st.button("🔄 Procesar Operación", use_container_width=True):
        with st.spinner("🧠 Procesando..."):
            datos = {
                "barcos": stats["total"],
                "esclusas_disponibles": list(stats["esclusas"].keys()),
                "condiciones_climaticas": {"viento": stats["viento"], "oleaje": stats["oleaje"]}
            }
            st.success("✅ Operación procesada")
            st.rerun()

# ==========================================
# CONTENIDO PRINCIPAL
# ==========================================

st.markdown('<div class="main-header">🧠 ANAYANSI - IA Cognitiva</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Inteligencia Artificial para Optimización Operativa del Canal de Panamá</div>', unsafe_allow_html=True)

if 'ultima_actualizacion' in st.session_state:
    st.caption(f"🔄 Datos actualizados cada 60 segundos - Última: {st.session_state.ultima_actualizacion.strftime('%H:%M:%S')}")

st.markdown("---")

# ==========================================
# KPIS
# ==========================================

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
col1.metric("🚢 Barcos", stats["total"])
col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
col3.metric("📈 Vel.", f"{stats['velocidad_prom']:.1f}")
col4.metric("⏳ Espera", stats["espera"])
col5.metric("⭐ Alta", stats["prioridad_alta"])
col6.metric("⬆️ Norte", stats["norte"])
col7.metric("⬇️ Sur", stats["sur"])
col8.metric("📊 Progreso", f"{stats.get('progreso_prom', 0):.0f}%")

st.markdown("---")

# ==========================================
# CLIMA Y MAR
# ==========================================

mostrar_clima_dashboard()

st.markdown("---")

# ==========================================
# GRÁFICO EN TIEMPO REAL
# ==========================================

st.markdown("### 📊 Evolución en Tiempo Real (60s)")
mostrar_grafico_tiempo_real()

st.markdown("---")

# ==========================================
# PREDICCIONES Y CONGESTIÓN
# ==========================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔮 Predicción de Congestión")
    st.markdown(f"""
    <div class="insight-card">
        <div style="font-size:1.2rem; font-weight:700;">📊 Análisis en tiempo real</div>
        <div style="margin-top:8px;">
            <b>Barcos activos:</b> {stats['total']}
        </div>
        <div style="margin-top:4px; font-size:0.85rem; color:#94a3b8;">
            CWT: {stats['cwt']:.1f}h | Nivel: {stats['nivel']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 📊 Nivel de Congestión")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<h1 style='color:{stats['color']}; text-align:center;'>{stats['nivel']}</h1>", unsafe_allow_html=True)
    with col2:
        st.progress(min(stats["cwt"] / 30, 1.0))
        st.caption(f"CWT: {stats['cwt']:.1f}h | Crítico: 22h | Advertencia: 18h")

st.markdown("---")

# ==========================================
# ESLUSCAS
# ==========================================

c1, c2, c3 = st.columns(3)
for col, (nombre, datos) in zip([c1, c2, c3], stats["esclusas"].items()):
    with col:
        color = "#10b981" if datos["espera"] < 4 else "#f59e0b" if datos["espera"] < 8 else "#ef4444"
        status = "✅ Fluido" if datos["espera"] < 4 else "🟡 Moderado" if datos["espera"] < 8 else "🔴 Congestionado"
        st.markdown(f"""
        <div class="esclusa-card">
            <h4 style="color:#e2e8f0;">⚙️ {nombre}</h4>
            <hr style="border-color:#1e293b; margin:5px 0;">
            <div>🚢 Total: <strong>{datos['total']}</strong></div>
            <div>⏳ Espera: <strong>{datos['espera']}</strong></div>
            <div style="color:{color};">{status}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# PESTAÑAS
# ==========================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🗺️ Mapa",
    "📊 Análisis",
    "💬 Chat IA",
    "🧠 Decisiones IA",
    "📈 Insights",
    "⚙️ Configuración IA",
    "📋 Datos Completos",
    "🚢 Seguimiento",
    "📍 Recorridos"
])

# ==========================================
# TAB 1: MAPA MEJORADO (2D Y 3D)
# ==========================================

with tab1:
    st.markdown("### 🗺️ Mapa de Navegación Interactivo")
    
    # Opciones de visualización
    col1, col2 = st.columns(2)
    with col1:
        tipo_mapa = st.radio(
            "Tipo de Mapa",
            ["2D Interactivo", "3D con Relieve"],
            horizontal=True,
            key="tipo_mapa"
        )
    with col2:
        if tipo_mapa == "2D Interactivo":
            estilo_mapa = st.selectbox(
                "Estilo",
                ["🌍 Satélite", "🏙️ Calles", "🌄 Relieve", "🌃 Nocturno"],
                index=0,
                key="estilo_mapa_select"
            )
    
    st.caption("🟢 Barcos con prioridad baja | 🟡 Media | 🔴 Alta | 🔺 Esclusas")
    
    # Crear mapa según tipo seleccionado
    if tipo_mapa == "2D Interactivo":
        fig = crear_mapa_2d(df, estilo_mapa)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig_3d = crear_mapa_3d(df)
        st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown("---")
    
    # Resumen del mapa
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Barcos en el mapa", stats["total"])
    with col2:
        st.metric("⚙️ Esclusas activas", len(stats["esclusas"]))
    with col3:
        st.metric("🔴 Prioridad Alta", stats["prioridad_alta"])
    with col4:
        st.metric("📊 Progreso promedio", f"{stats.get('progreso_prom', 0):.0f}%")

# ==========================================
# TAB 2: ANÁLISIS
# ==========================================

with tab2:
    st.markdown("### 📊 Análisis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📊 Distribución por Tipo")
        tipos_df = pd.DataFrame({"Tipo": list(stats["tipos"].keys()), "Cantidad": list(stats["tipos"].values())})
        fig = px.bar(tipos_df, x="Tipo", y="Cantidad", color="Cantidad", color_continuous_scale="Viridis")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 📊 Distribución por Estado")
        estados_df = df["estado"].value_counts().reset_index()
        estados_df.columns = ["Estado", "Cantidad"]
        fig2 = px.pie(estados_df, values="Cantidad", names="Estado")
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Distribución por Dirección")
        dir_df = df["direccion"].value_counts().reset_index()
        dir_df.columns = ["Dirección", "Cantidad"]
        fig3 = px.bar(dir_df, x="Dirección", y="Cantidad", color="Dirección",
                      color_discrete_map={"Norte": "#10b981", "Sur": "#3b82f6"})
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("#### 📊 Distribución por Prioridad")
        pri_df = df["prioridad"].value_counts().reset_index()
        pri_df.columns = ["Prioridad", "Cantidad"]
        fig4 = px.bar(pri_df, x="Prioridad", y="Cantidad", color="Prioridad",
                      color_discrete_map={"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"})
        fig4.update_layout(height=300)
        st.plotly_chart(fig4, use_container_width=True)

# ==========================================
# TAB 3: CHAT IA
# ==========================================

with tab3:
    st.markdown("### 💬 Chat con Anayansi")
    st.caption("💡 Pregunta sobre el estado del Canal")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"rol": "anayansi", "msg": "🧠 ¡Hola! Soy Anayansi, tu IA cognitiva. Puedo responder preguntas sobre el Canal, barcos, esclusas, recorridos y clima. ¿Qué necesitas saber?"}
        ]
    
    for msg in st.session_state.chat_messages:
        if msg["rol"] == "anayansi":
            st.markdown(f'<div class="chat-ai">🧠 Anayansi: {msg["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">👤 Tú: {msg["msg"]}</div>', unsafe_allow_html=True)
    
    pregunta = st.text_input("Pregunta a Anayansi:", placeholder="¿Cuántos barcos hay en el Canal?")
    if pregunta:
        st.session_state.chat_messages.append({"rol": "usuario", "msg": pregunta})
        
        if "barco" in pregunta.lower() or "barcos" in pregunta.lower():
            respuesta = f"🚢 Actualmente hay **{stats['total']} barcos** en el Canal. **{stats['norte']}** van al Norte y **{stats['sur']}** al Sur."
        elif "cwt" in pregunta.lower():
            respuesta = f"⏱️ El CWT actual es de **{stats['cwt']:.1f} horas** - Nivel: {stats['nivel']}"
        elif "clima" in pregunta.lower():
            clima = sistema_datos.obtener_clima_actual()
            if clima:
                respuesta = f"🌤️ **Clima actual:** {clima.get('temperatura', 'N/A')}°C, Viento: {clima.get('viento', 'N/A')} nudos"
            else:
                respuesta = "🌤️ No se pudo obtener datos climáticos"
        elif "esclusa" in pregunta.lower():
            respuesta = "⚙️ **Estado de esclusas:**\n"
            for nombre, datos in stats["esclusas"].items():
                respuesta += f"• {nombre}: {datos['total']} barcos, {datos['espera']} en espera\n"
        elif "recorrido" in pregunta.lower() or "progreso" in pregunta.lower():
            respuesta = f"📊 **Progreso promedio de barcos:** {stats.get('progreso_prom', 0):.0f}%\n"
            if "posiciones" in stats:
                for pos, count in stats["posiciones"].items():
                    respuesta += f"• {pos}: {count} barcos\n"
        else:
            respuesta = f"📊 El Canal tiene **{stats['total']} barcos** con CWT de **{stats['cwt']:.1f}h**. ¿Necesitas más información?"
        
        st.session_state.chat_messages.append({"rol": "anayansi", "msg": respuesta})
        st.rerun()
    
    if st.button("🗑️ Limpiar chat"):
        st.session_state.chat_messages = [
            {"rol": "anayansi", "msg": "🧠 ¡Hola! Soy Anayansi, tu IA cognitiva. ¿Qué necesitas saber?"}
        ]
        st.rerun()

# ==========================================
# TAB 4: DECISIONES IA
# ==========================================

with tab4:
    st.markdown("### 🧠 Decisiones de la IA")
    
    st.markdown("#### 📊 Estado del Sistema")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚢 Barcos", stats["total"])
    with col2:
        st.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
    with col3:
        st.metric("📊 Congestión", stats["nivel"])
    
    st.markdown("---")
    
    st.markdown("#### 💡 Recomendación de la IA")
    if stats["cwt"] > 20:
        st.warning("🔴 **Recomendación:** CWT crítico. Se recomienda activar protocolos de gestión de tráfico.")
    elif stats["cwt"] > 15:
        st.info("🟡 **Recomendación:** CWT elevado. Monitorear evolución del tráfico.")
    else:
        st.success("🟢 **Recomendación:** Operaciones normales. Mantener monitoreo continuo.")
    
    if stats["espera"] > 10:
        st.warning("⏳ **Recomendación:** Alta congestión en esclusas. Considerar reasignación de barcos.")

# ==========================================
# TAB 5: INSIGHTS
# ==========================================

with tab5:
    st.markdown("### 📈 Insights y Patrones")
    
    st.markdown("#### 🔍 Patrones detectados")
    
    vel_prom = stats["velocidad_prom"]
    if vel_prom < 5:
        st.info("🐢 **Velocidad baja:** " + str(round(vel_prom, 1)) + " nudos. Posible congestión o condiciones adversas.")
    elif vel_prom > 12:
        st.success("🚀 **Velocidad alta:** " + str(round(vel_prom, 1)) + " nudos. Tráfico fluido.")
    
    espera_total = sum([d["espera"] for d in stats["esclusas"].values()])
    if espera_total > 15:
        st.warning("⏳ **Alta congestión en esclusas:** " + str(espera_total) + " barcos en espera total.")
    elif espera_total > 8:
        st.info("⏳ **Congestión moderada:** " + str(espera_total) + " barcos en espera total.")
    
    st.markdown("---")
    
    st.markdown("#### 📊 Métricas de Rendimiento")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🚢 Barcos", stats["total"])
    col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
    col3.metric("📈 Velocidad", f"{stats['velocidad_prom']:.1f}")
    col4.metric("📊 Progreso", f"{stats.get('progreso_prom', 0):.0f}%")

# ==========================================
# TAB 6: CONFIGURACIÓN IA
# ==========================================

with tab6:
    st.markdown("### ⚙️ Configuración de la IA")
    
    st.markdown("#### 🎯 Umbrales Críticos")
    col1, col2 = st.columns(2)
    with col1:
        st.slider("Congestión Máxima", 0.5, 1.0, 0.85, 0.05)
        st.slider("Tiempo Espera Máx (min)", 30, 180, 120, 10)
    with col2:
        st.slider("Velocidad Mínima (nudos)", 1.0, 6.0, 3.0, 0.5)
        st.slider("Distancia Seguridad (millas)", 0.1, 0.5, 0.3, 0.05)
    
    st.markdown("---")
    
    st.markdown("#### 📡 Conexiones")
    estado = sistema_datos.verificar_estado_conexiones()
    if estado["ais"]:
        st.success("✅ AISStream WebSocket: Conectado")
    else:
        st.warning("🟡 AISStream WebSocket: Conectando...")
    
    if estado["clima"]:
        st.success("✅ OpenWeather: Conectado")
    else:
        st.warning("🟡 OpenWeather: Conectando...")
    
    st.markdown("---")
    st.markdown("#### ⏱️ Intervalo de Actualización")
    intervalo = st.selectbox("Intervalo (segundos)", [15, 30, 60, 120, 300], index=2)
    if intervalo != sistema_tiempo_real.intervalo_segundos:
        sistema_tiempo_real.intervalo_segundos = intervalo
        st.success(f"✅ Intervalo actualizado a {intervalo}s")

# ==========================================
# TAB 7: DATOS COMPLETOS
# ==========================================

with tab7:
    st.markdown("### 📋 Datos Completos de Barcos")
    st.caption("Información detallada de todos los barcos activos en el Canal")
    
    display_df = df[["nombre", "direccion", "tipo", "estado", "esclusa", "posicion", "progreso", "velocidad", "eta_horas", "prioridad", "eslora", "calado", "carga"]].copy()
    display_df["velocidad"] = display_df["velocidad"].round(1)
    display_df["eta_horas"] = display_df["eta_horas"].round(1)
    display_df["eslora"] = display_df["eslora"].round(0)
    display_df["calado"] = display_df["calado"].round(1)
    display_df["carga"] = display_df["carga"].round(0)
    display_df["progreso"] = display_df["progreso"].round(1)
    display_df["direccion"] = display_df["direccion"].apply(lambda x: "⬆️ Norte" if x == "Norte" else "⬇️ Sur")
    display_df.columns = ["Nombre", "Dirección", "Tipo", "Estado", "Esclusa", "Posición", "Progreso (%)", "Velocidad", "ETA (h)", "Prioridad", "Eslora (m)", "Calado (m)", "Carga (t)"]
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar todos los datos (CSV)",
            data=csv,
            file_name=f"datos_canal_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

# ==========================================
# TAB 8: SEGUIMIENTO DE BARCOS
# ==========================================

with tab8:
    st.markdown("### 🚢 Seguimiento de Barcos en el Canal")
    st.caption("Monitoreo del paso de barcos por esclusas")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🔄 Simular Pasos de Barcos", use_container_width=True):
            with st.spinner("Simulando pasos..."):
                sistema_seguimiento = simular_paso_barcos(df, sistema_seguimiento)
                st.session_state.sistema_seguimiento = sistema_seguimiento
                st.success("✅ Simulación completada")
                st.rerun()
    with col2:
        if st.button("🗑️ Limpiar Historial", use_container_width=True):
            st.session_state.sistema_seguimiento = SistemaSeguimientoBarcos()
            st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🚢 En tránsito", len(sistema_seguimiento.barcos_en_transito))
    with col2:
        st.metric("✅ Completados", len(sistema_seguimiento.barcos_completados))
    with col3:
        st.metric("📊 Registros", len(sistema_seguimiento.historial_pasos))
    with col4:
        st.metric("⏱️ Tiempo promedio", "0 min")
    with col5:
        st.metric("⏳ En espera", 0)
    
    st.markdown("---")
    
    st.markdown("#### 📊 Análisis de Tiempos")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_tiempos = crear_grafico_tiempos_esclusas(sistema_seguimiento)
        if fig_tiempos:
            st.plotly_chart(fig_tiempos, use_container_width=True)
        else:
            st.info("⏳ Sin datos de tiempos aún. Simula pasos para ver gráficos.")
    
    with col2:
        fig_congestion = crear_grafico_congestion(sistema_seguimiento)
        if fig_congestion:
            st.plotly_chart(fig_congestion, use_container_width=True)
        else:
            st.info("📊 Sin datos de congestión aún. Simula pasos para ver gráficos.")
    
    st.markdown("---")
    
    st.markdown("#### 🚢 Barcos en Tránsito")
    if sistema_seguimiento.barcos_en_transito:
        data = []
        for nombre, datos in sistema_seguimiento.barcos_en_transito.items():
            estado = sistema_seguimiento.obtener_estado_barco(nombre)
            data.append({
                "Barco": nombre,
                "Progreso": f"{estado['progreso']:.0f}%",
                "Posición": estado.get("ultima_posicion", "Desconocida"),
                "Esclusas": estado["esclusas_pasadas"],
                "Última": estado["ultima_esclusa"],
                "Tiempo (min)": estado["tiempo_total"]
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("No hay barcos en tránsito actualmente")
    
    st.markdown("---")
    
    st.markdown("#### ⚙️ Estadísticas por Esclusa")
    col1, col2, col3 = st.columns(3)
    
    for col, esclusa in zip([col1, col2, col3], ["Gatun", "Pedro Miguel", "Miraflores"]):
        stats_esclusa = sistema_seguimiento.obtener_estadisticas_esclusa(esclusa)
        with col:
            if stats_esclusa:
                st.markdown(f"""
                <div class="esclusa-card">
                    <h4 style="color:#e2e8f0;">⚙️ {esclusa}</h4>
                    <hr style="border-color:#1e293b; margin:5px 0;">
                    <div>🚢 Barcos: <strong>{stats_esclusa['total_barcos']}</strong></div>
                    <div>⏳ Espera promedio: <strong>{stats_esclusa['tiempo_espera_promedio']} min</strong></div>
                    <div>⏱️ Máxima: <strong>{stats_esclusa['tiempo_espera_max']} min</strong></div>
                    <div>✅ Mínima: <strong>{stats_esclusa['tiempo_espera_min']} min</strong></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="esclusa-card">
                    <h4 style="color:#e2e8f0;">⚙️ {esclusa}</h4>
                    <hr style="border-color:#1e293b; margin:5px 0;">
                    <div style="color:#64748b;">Sin registros</div>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# TAB 9: RECORRIDOS DE BARCOS
# ==========================================

with tab9:
    st.markdown("### 📍 Recorridos de Barcos en el Canal")
    st.caption("Seguimiento completo del movimiento de barcos dentro del Canal")
    
    barcos_disponibles = list(sistema_seguimiento.barcos_en_transito.keys()) + [r["barco"] for r in sistema_seguimiento.recorridos_completos[-10:]]
    
    if barcos_disponibles:
        barco_seleccionado = st.selectbox("Seleccionar Barco", barcos_disponibles)
        
        if barco_seleccionado:
            posiciones = sistema_seguimiento.obtener_recorrido_barco(barco_seleccionado)
            estado = sistema_seguimiento.obtener_estado_barco(barco_seleccionado)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Progreso", f"{estado.get('progreso', 0):.0f}%")
            with col2:
                st.metric("📍 Posición", estado.get("ultima_posicion", "Desconocida"))
            with col3:
                st.metric("⏱️ Tiempo", f"{estado.get('tiempo_total', 0):.0f} min")
            
            st.markdown("---")
            
            fig_recorrido = crear_grafico_recorrido_barco(posiciones)
            if fig_recorrido:
                st.plotly_chart(fig_recorrido, use_container_width=True)
            else:
                st.info("⏳ No hay suficientes datos de recorrido para este barco")
            
            if posiciones:
                st.markdown("#### 📋 Historial de Posiciones")
                df_pos = pd.DataFrame(posiciones)
                df_pos["timestamp"] = pd.to_datetime(df_pos["timestamp"])
                df_pos["hora"] = df_pos["timestamp"].dt.strftime("%H:%M:%S")
                display_pos = df_pos[["hora", "posicion", "progreso", "lat", "lon"]].copy()
                display_pos.columns = ["Hora", "Posición", "Progreso (%)", "Latitud", "Longitud"]
                st.dataframe(display_pos, use_container_width=True)
    else:
        st.info("🚢 No hay barcos en tránsito aún. Simula pasos para ver recorridos.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    🧠 ANAYANSI - IA Cognitiva | Datos en tiempo real cada 60s
    <br>
    <span style="color:#475569;">🚢 Barcos: {} | 📡 AISStream WebSocket + OpenWeather</span>
    <br>
    <span style="color:#475569;">🔄 Última actualización: {}</span>
</div>
""".format(stats["total"], datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)
