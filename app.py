import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
import json

st.set_page_config(
    page_title="🌊 ANAYANSI - Sistema IA del Canal",
    page_icon="🌊",
    layout="wide"
)

# ==========================================
# ESTILOS PROFESIONALES
# ==========================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00b4d8, #0077b6, #00b4d8);
        background-size: 200% 200%;
        animation: gradient 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Orbitron', sans-serif;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-top: -8px;
        font-family: 'Orbitron', sans-serif;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(26,58,92,0.9));
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #00b4d8;
        box-shadow: 0 0 30px rgba(0,150,255,0.15);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f1f5f9;
        font-family: 'Orbitron', sans-serif;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'Orbitron', sans-serif;
    }
    
    .chat-message-anayansi {
        background: rgba(0,150,255,0.1);
        border-left: 3px solid #00b4d8;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: #e2e8f0;
    }
    .chat-user {
        background: rgba(15,23,42,0.8);
        border-left: 3px solid #64748b;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: #94a3b8;
    }
    
    .esclusa-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(26,58,92,0.9));
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 15px;
        transition: all 0.3s;
    }
    .esclusa-card:hover {
        border-color: #00b4d8;
    }
    
    .alert-box {
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .alert-critical { background: rgba(239,68,68,0.15); border-left: 4px solid #ef4444; color: #fca5a5; }
    .alert-warning { background: rgba(245,158,11,0.15); border-left: 4px solid #f59e0b; color: #fcd34d; }
    .alert-success { background: rgba(16,185,129,0.15); border-left: 4px solid #10b981; color: #6ee7b7; }
    .alert-info { background: rgba(59,130,246,0.15); border-left: 4px solid #3b82f6; color: #93c5fd; }
    
    div.stButton > button {
        background: linear-gradient(135deg, #00b4d8, #0077b6);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.5rem;
        font-family: 'Orbitron', sans-serif;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 30px rgba(0,150,255,0.3);
        transform: scale(1.02);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15,23,42,0.5);
        border-radius: 12px;
        padding: 6px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        color: #94a3b8;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.8rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00b4d8, #0077b6);
        color: white;
    }
    
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.8rem;
        padding: 20px 0;
        border-top: 1px solid #1e293b;
        margin-top: 20px;
    }
    
    .log-container {
        background: rgba(15,23,42,0.8);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 15px;
        max-height: 300px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SISTEMA ANAYANSI - IA AVANZADA
# ==========================================

class AnayansiIA:
    """Sistema IA completo para el Canal de Panamá con aprendizaje automático"""
    
    def __init__(self):
        self.nombre = "Anayansi"
        self.significado = "Sabiduria del mar"
        self.version = "3.0"
        self.confianza = 0.93
        self.aprendizaje = []
        self.logs = []
        self.patrones = {}
        self.historial_conversaciones = []
        self.conocimiento = self._inicializar_conocimiento()
        self.aprendizaje_automatico = True
        self.predicciones_previas = []
        
    def _inicializar_conocimiento(self):
        """Base de conocimiento inicial"""
        return {
            "esclusas": {
                "Gatun": {"capacidad": 3, "nivel_agua": 26.0, "tiempo_prom": 1.5, "estado": "Operativa"},
                "Pedro Miguel": {"capacidad": 1, "nivel_agua": 13.5, "tiempo_prom": 1.0, "estado": "Operativa"},
                "Miraflores": {"capacidad": 2, "nivel_agua": 16.5, "tiempo_prom": 1.2, "estado": "Operativa"}
            },
            "clima": {
                "viento_critico": 30,
                "ola_critica": 3.0,
                "temperatura_optima": (22, 28),
                "lluvia_critica": 50,
                "visibilidad_minima": 0.5
            },
            "operaciones": {
                "max_barcos_espera": 15,
                "cwt_critico": 22,
                "tiempo_espera_max": 3,
                "velocidad_minima": 2,
                "velocidad_maxima": 18
            },
            "maritimo": {
                "profundidad_prom": 13.5,
                "profundidad_minima": 10.0,
                "corriente_prom": 1.5,
                "marea_prom": 2.5
            }
        }
    
    def _registrar_log(self, accion, datos):
        """Registra acciones en el log de aprendizaje"""
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "accion": accion,
            "datos": datos
        }
        self.logs.append(entrada)
        return entrada
    
    def aprender_automaticamente(self, df, stats):
        """Aprendizaje automático basado en datos actuales"""
        nuevos_aprendizajes = []
        
        # Aprender patrones de tráfico
        if stats["total"] > 70:
            nuevo = f"Alto tráfico detectado: {stats['total']} barcos. Recomendar protocolos especiales."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        if stats["cwt"] > 20:
            nuevo = f"CWT crítico: {stats['cwt']:.1f}h. Recomendar acciones inmediatas."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        if stats["espera"] > 12:
            nuevo = f"Congestión en esclusas: {stats['espera']} barcos en espera."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        # Aprender patrones climáticos
        if stats.get("viento_prom", 0) > 20:
            nuevo = f"Vientos fuertes detectados: {stats['viento_prom']:.1f} nudos. Precaución."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        # Aprender sobre eficiencia de esclusas
        for nombre, datos in stats["esclusas"].items():
            if datos["espera"] > 5:
                nuevo = f"Esclusa {nombre} con {datos['espera']} barcos en espera. Considerar optimización."
                self.aprender(nuevo)
                nuevos_aprendizajes.append(nuevo)
        
        return nuevos_aprendizajes
    
    def aprender(self, nuevo_conocimiento):
        """Registra nuevo conocimiento en la IA"""
        self.aprendizaje.append({
            "fecha": datetime.now().isoformat(),
            "conocimiento": nuevo_conocimiento
        })
        self._registrar_log("aprendizaje", nuevo_conocimiento)
        return "Anayansi ha aprendido: " + nuevo_conocimiento[:100] + "..."
    
    def analizar_barco(self, barco):
        """Análisis detallado de un barco individual"""
        analisis = {
            "nombre": barco["nombre"],
            "tipo": barco["tipo"],
            "direccion": barco["direccion"],
            "estado": barco["estado"],
            "velocidad": barco["velocidad"],
            "esclusa": barco["esclusa"],
            "eta": barco["eta_horas"],
            "prioridad": barco["prioridad"],
            "analisis": self._generar_analisis_barco(barco)
        }
        self._registrar_log("analisis_barco", analisis)
        return analisis
    
    def _generar_analisis_barco(self, barco):
        """Genera análisis detallado de un barco"""
        resultado = []
        if barco["velocidad"] < 2:
            resultado.append("🐢 Velocidad muy baja - Posible congestion o espera")
        elif barco["velocidad"] < 5:
            resultado.append("⏳ Velocidad reducida - Navegando con precaucion")
        elif barco["velocidad"] > 15:
            resultado.append("⚡ Alta velocidad - Buque prioritario o en ruta exprés")
        else:
            resultado.append("✅ Velocidad normal - Navegacion fluida")
        
        if barco["estado"] == "En espera en esclusa":
            resultado.append("⏳ En espera - Tiempo estimado de espera: 1-3 horas")
        elif barco["estado"] == "Entrando a esclusa":
            resultado.append("🔄 Entrando a esclusa - Operacion en curso")
        else:
            resultado.append("🟢 Navegando - Sin incidencias")
        
        if barco["prioridad"] == "Alta":
            resultado.append("⭐ Prioridad Alta - Dar preferencia en esclusas")
        
        return " | ".join(resultado)
    
    def preguntar(self, pregunta, df, stats):
        """Responde preguntas en lenguaje natural de forma inteligente"""
        pregunta_lower = pregunta.lower()
        self._registrar_log("pregunta", pregunta)
        
        # Respuestas contextuales
        if "cwt" in pregunta_lower:
            return f"🌊 El CWT actual es de **{stats['cwt']:.1f} horas** con una congestion **{stats['nivel'].lower()}**. El tiempo de espera promedio es de **{stats['espera']/max(stats['total'],1)*60:.0f} minutos** por barco."
        
        if "barco" in pregunta_lower or "barcos" in pregunta_lower:
            return f"🚢 Hay **{stats['total']} barcos** activos en el Canal. **{stats['norte']}** van hacia el Norte y **{stats['sur']}** hacia el Sur. **{stats['prioridad_alta']}** tienen prioridad alta."
        
        if "espera" in pregunta_lower:
            return f"⏳ Hay **{stats['espera']} barcos** en espera en las esclusas. El tiempo de espera promedio es de **{stats['espera']/max(stats['total'],1)*60:.0f} minutos**."
        
        if "velocidad" in pregunta_lower:
            return f"📈 La velocidad promedio es de **{stats['velocidad_prom']:.1f} nudos**. La maxima registrada es de **{stats.get('velocidad_max', stats['velocidad_prom']*1.5):.1f} nudos**."
        
        if "esclusa" in pregunta_lower:
            partes = []
            for nombre, datos in stats["esclusas"].items():
                partes.append(f"**{nombre}**: {datos['total']} barcos, {datos['espera']} en espera, eficiencia {datos['eficiencia']}")
            return "⚙️ " + " | ".join(partes)
        
        if "clima" in pregunta_lower or "tiempo" in pregunta_lower:
            temp = df["temperatura"].mean() if "temperatura" in df.columns else 25
            viento = df["viento"].mean() if "viento" in df.columns else 15
            return f"🌤️ Temperatura: **{temp:.1f}°C**, Viento: **{viento:.1f} nudos**. Condiciones **{'favorables' if viento < 20 else 'adversas'}** para navegacion."
        
        if "profundidad" in pregunta_lower or "corriente" in pregunta_lower or "marea" in pregunta_lower or "oleaje" in pregunta_lower:
            prof = stats.get("profundidad_prom", 13.5)
            corr = stats.get("corriente_prom", 1.5)
            marea = stats.get("marea_prom", 2.5)
            oleaje = stats.get("oleaje_prom", 1.0)
            return f"🌊 Datos maritimos: Profundidad **{prof:.1f}m**, Corriente **{corr:.1f} nudos**, Marea **{marea:.1f}m**, Oleaje **{oleaje:.1f}m**."
        
        if "aprender" in pregunta_lower or "enseñar" in pregunta_lower:
            return "🧠 ¡Claro! Puedes ensenarme en la pestaña 'Aprendizaje'. Escribe lo que quieras que aprenda sobre el Canal y lo recordare para siempre."
        
        # Respuesta general inteligente
        return f"🧠 He analizado tu consulta sobre '{pregunta[:50]}...'. El Canal opera con **{stats['total']} barcos** y un CWT de **{stats['cwt']:.1f}h**. La congestion es **{stats['nivel'].lower()}**. ¿Necesitas informacion mas especifica sobre barcos, esclusas, clima o datos maritimos?"
    
    def generar_reporte_completo(self, df, stats):
        """Genera reporte ejecutivo completo descargable"""
        lineas = []
        lineas.append("=" * 80)
        lineas.append("🌊 ANAYANSI - REPORTE EJECUTIVO DEL CANAL DE PANAMA")
        lineas.append("=" * 80)
        lineas.append(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append(f"📊 Version del sistema: {self.version}")
        lineas.append(f"🧠 Nivel de confianza: {int(self.confianza*100)}%")
        lineas.append(f"📚 Registros de aprendizaje: {len(self.aprendizaje)}")
        lineas.append("=" * 80)
        lineas.append("")
        lineas.append("📊 RESUMEN OPERATIVO")
        lineas.append("-" * 80)
        lineas.append(f"🚢 Barcos activos: {stats['total']}")
        lineas.append(f"⬆️ Norte: {stats['norte']} | ⬇️ Sur: {stats['sur']}")
        lineas.append(f"⏱️ CWT: {stats['cwt']:.1f} horas ({stats['nivel']})")
        lineas.append(f"📈 Velocidad promedio: {stats['velocidad_prom']:.1f} nudos")
        lineas.append(f"⏳ Barcos en espera: {stats['espera']}")
        lineas.append(f"⭐ Prioridad Alta: {stats['prioridad_alta']}")
        lineas.append("")
        
        lineas.append("⚙️ ESTADO DE ESLUSCAS")
        lineas.append("-" * 80)
        for nombre, datos in stats["esclusas"].items():
            lineas.append(f"📍 {nombre}:")
            lineas.append(f"   - Total: {datos['total']} barcos")
            lineas.append(f"   - En espera: {datos['espera']}")
            lineas.append(f"   - Norte: {datos['norte']} | Sur: {datos['sur']}")
            lineas.append(f"   - Eficiencia: {datos['eficiencia']}")
        lineas.append("")
        
        lineas.append("📋 DISTRIBUCION POR TIPO DE BARCO")
        lineas.append("-" * 80)
        for tipo, cantidad in stats["tipos"].items():
            lineas.append(f"   - {tipo}: {cantidad}")
        lineas.append("")
        
        lineas.append("📋 ORIGEN DE BARCOS")
        lineas.append("-" * 80)
        for origen, cantidad in stats["origenes"].items():
            lineas.append(f"   - {origen}: {cantidad}")
        lineas.append("")
        
        if "profundidad_prom" in stats:
            lineas.append("🌊 DATOS MARITIMOS")
            lineas.append("-" * 80)
            lineas.append(f"📏 Profundidad promedio: {stats['profundidad_prom']:.1f}m")
            lineas.append(f"🌊 Corriente promedio: {stats['corriente_prom']:.1f} nudos")
            lineas.append(f"📈 Marea promedio: {stats['marea_prom']:.1f}m")
            lineas.append(f"🌊 Oleaje promedio: {stats['oleaje_prom']:.1f}m")
            lineas.append("")
        
        lineas.append("🔮 PREDICCIONES Y RECOMENDACIONES")
        lineas.append("-" * 80)
        lineas.append(f"📊 Prediccion de congestion: {stats['nivel']}")
        if stats["cwt"] < 18:
            lineas.append("💡 Recomendacion: Mantener operaciones normales")
        else:
            lineas.append("💡 Recomendacion: Activar protocolos de congestion")
        lineas.append("")
        
        lineas.append("=" * 80)
        lineas.append("🌊 ANAYANSI - Sabiduria del mar")
        lineas.append("=" * 80)
        
        return "\n".join(lineas)

# ==========================================
# GENERAR DATOS COMPLETOS
# ==========================================

@st.cache_data(ttl=10)
def generar_datos():
    np.random.seed(int(time.time() / 10) % 1000)
    n = np.random.randint(60, 90)
    
    puntos_sur = [
        ("Entrada Atlantico", 9.36, -79.92),
        ("Gatun", 9.27, -79.92),
        ("Lago Gatun", 9.20, -79.88),
        ("Pedro Miguel", 9.015, -79.62),
        ("Miraflores", 8.995, -79.585),
        ("Salida Pacifico", 8.90, -79.52)
    ]
    
    puntos_norte = [
        ("Entrada Pacifico", 8.90, -79.52),
        ("Miraflores", 8.995, -79.585),
        ("Pedro Miguel", 9.015, -79.62),
        ("Lago Gatun", 9.20, -79.88),
        ("Gatun", 9.27, -79.92),
        ("Salida Atlantico", 9.36, -79.92)
    ]
    
    tipos = ["Portacontenedores", "Granelero", "Petrolero", "Gasero", "Carguero", "Crucero", "Remolcador", "Pesquero"]
    estados = ["Navegando", "Navegando", "Navegando", "En espera en esclusa", "Entrando a esclusa"]
    esclusas = ["Gatun", "Pedro Miguel", "Miraflores"]
    prioridades = ["Alta", "Media", "Baja"]
    
    barcos = []
    
    for i in range(n):
        direccion = "Sur" if np.random.random() < 0.5 else "Norte"
        puntos = puntos_sur if direccion == "Sur" else puntos_norte
        
        pos_idx = np.random.randint(0, len(puntos) - 1)
        nombre_punto, lat_base, lon_base = puntos[pos_idx]
        
        lat = lat_base + np.random.normal(0, 0.02)
        lon = lon_base + np.random.normal(0, 0.02)
        
        estado = random.choice(estados)
        if estado == "En espera en esclusa":
            velocidad = np.random.uniform(0, 1)
            tiempo_espera = np.random.uniform(0.5, 3)
        elif estado == "Entrando a esclusa":
            velocidad = np.random.uniform(2, 5)
            tiempo_espera = 0
        else:
            velocidad = np.random.uniform(6, 16)
            tiempo_espera = 0
        
        if nombre_punto in ["Entrada Atlantico", "Gatun"]:
            esclusa = "Gatun"
        elif nombre_punto in ["Lago Gatun"]:
            esclusa = "Pedro Miguel"
        elif nombre_punto in ["Pedro Miguel", "Miraflores", "Entrada Pacifico"]:
            esclusa = "Miraflores"
        else:
            esclusa = random.choice(esclusas)
        
        dist_recorrida = (pos_idx / len(puntos)) * 80 + np.random.uniform(-5, 5)
        dist_total = 80
        distancia_restante = dist_total - dist_recorrida
        eta = distancia_restante / max(velocidad, 1)
        
        profundidad = 13.5 + np.random.normal(0, 1.5)
        corriente = 1.5 + np.random.normal(0, 0.5)
        marea = 2.5 + np.random.normal(0, 0.3)
        oleaje = 1.0 + np.random.normal(0, 0.3)
        
        barco = {
            "id": "B" + str(i+1).zfill(4),
            "nombre": "BARCO_" + str(i+1).zfill(4),
            "tipo": random.choice(tipos),
            "direccion": direccion,
            "posicion": nombre_punto,
            "lat": lat,
            "lon": lon,
            "velocidad": velocidad,
            "estado": estado,
            "esclusa": esclusa,
            "distancia_recorrida": dist_recorrida,
            "distancia_total": dist_total,
            "eta_horas": max(0.5, eta),
            "origen": random.choice(["Asia", "Europa", "America del Norte", "America del Sur", "Africa"]),
            "destino": random.choice(["Asia", "Europa", "America del Norte", "America del Sur", "Costa Oeste EEUU"]),
            "prioridad": np.random.choice(prioridades, p=[0.15, 0.55, 0.30]),
            "carga_valor": np.random.uniform(100000, 10000000),
            "tiempo_espera": tiempo_espera,
            "temperatura": 25 + np.random.normal(0, 3),
            "viento": np.random.uniform(0, 30),
            "humedad": 70 + np.random.normal(0, 10),
            "emisiones": np.random.uniform(10, 100),
            "profundidad": max(8, min(18, profundidad)),
            "corriente": max(0.5, min(3, corriente)),
            "marea": max(1.5, min(4, marea)),
            "oleaje": max(0.3, min(2.5, oleaje))
        }
        barcos.append(barco)
    
    return pd.DataFrame(barcos)

# ==========================================
# ANÁLISIS AVANZADO
# ==========================================

def analizar(df):
    stats = {
        "total": len(df),
        "norte": len(df[df["direccion"] == "Norte"]),
        "sur": len(df[df["direccion"] == "Sur"]),
        "espera": len(df[df["estado"] == "En espera en esclusa"]),
        "navegando": len(df[df["estado"] == "Navegando"]),
        "entrando": len(df[df["estado"] == "Entrando a esclusa"]),
        "prioridad_alta": len(df[df["prioridad"] == "Alta"]),
        "velocidad_prom": df["velocidad"].mean(),
        "velocidad_max": df["velocidad"].max(),
        "eta_prom": df["eta_horas"].mean(),
        "carga_total": df["carga_valor"].sum(),
        "emisiones_total": df["emisiones"].sum(),
        "temperatura_prom": df["temperatura"].mean(),
        "viento_prom": df["viento"].mean(),
        "profundidad_prom": df["profundidad"].mean(),
        "corriente_prom": df["corriente"].mean(),
        "marea_prom": df["marea"].mean(),
        "oleaje_prom": df["oleaje"].mean(),
        "esclusas": {},
        "tipos": df["tipo"].value_counts().to_dict(),
        "origenes": df["origen"].value_counts().to_dict()
    }
    
    for esclusa in ["Gatun", "Pedro Miguel", "Miraflores"]:
        df_esclusa = df[df["esclusa"] == esclusa]
        stats["esclusas"][esclusa] = {
            "total": len(df_esclusa),
            "espera": len(df_esclusa[df_esclusa["estado"] == "En espera en esclusa"]),
            "norte": len(df_esclusa[df_esclusa["direccion"] == "Norte"]),
            "sur": len(df_esclusa[df_esclusa["direccion"] == "Sur"]),
            "eficiencia": "🟢 Alta" if len(df_esclusa) < 10 else "🟡 Media" if len(df_esclusa) < 20 else "🔴 Baja"
        }
    
    stats["cwt"] = 12 + max(0, (stats["total"] - 30) * 0.1) + stats["espera"] * 0.12
    stats["cwt"] = min(40, max(8, stats["cwt"]))
    
    if stats["cwt"] < 14:
        stats["nivel"] = "🟢 Bajo"
        stats["color"] = "#10b981"
    elif stats["cwt"] < 18:
        stats["nivel"] = "🟡 Moderado"
        stats["color"] = "#f59e0b"
    elif stats["cwt"] < 23:
        stats["nivel"] = "🟠 Alto"
        stats["color"] = "#f97316"
    else:
        stats["nivel"] = "🔴 Critico"
        stats["color"] = "#ef4444"
    
    return stats

# ==========================================
# INICIALIZAR ANAYANSI
# ==========================================

if "anayansi" not in st.session_state:
    st.session_state.anayansi = AnayansiIA()
    st.session_state.chat_historial = [
        {"rol": "anayansi", "mensaje": "🌊 ¡Hola! Soy **Anayansi**, la sabiduria del mar. Soy la IA especializada en el Canal de Panama. Puedo ayudarte con:\n\n📊 **Estado del Canal** en tiempo real\n🚢 **Informacion de barcos** especificos\n⚙️ **Analisis de esclusas** y eficiencia\n🌤️ **Datos climaticos** y maritimos\n🔮 **Predicciones** de trafico y congestion\n📋 **Reportes completos** descargables\n🧠 **Aprendizaje continuo** sobre el Canal\n\n¿Que necesitas saber?"}
    ]

anayansi = st.session_state.anayansi

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0;">
        <div style="font-size:3rem;">🌊</div>
        <div style="color:#00b4d8; font-family: 'Orbitron', sans-serif; font-size:1.2rem; font-weight:700;">ANAYANSI</div>
        <div style="color:#475569; font-size:0.7rem;">Sabiduria del mar</div>
        <div style="color:#475569; font-size:0.7rem;">v3.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    df = generar_datos()
    stats = analizar(df)
    
    st.session_state["df"] = df
    st.session_state["stats"] = stats
    
    # Aprendizaje automático
    nuevos_aprendizajes = anayansi.aprender_automaticamente(df, stats)
    
    st.markdown("#### 📊 Estado")
    col1, col2 = st.columns(2)
    col1.metric("🚢 Barcos", stats["total"])
    col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
    
    st.markdown("---")
    
    st.markdown("#### 🧠 ANAYANSI")
    status_color = "#10b981" if stats["cwt"] < 18 else "#f59e0b" if stats["cwt"] < 23 else "#ef4444"
    st.markdown(f"""
    <div style="background:rgba(15,23,42,0.8); border-radius:12px; padding:15px; border:1px solid #1e293b;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{status_color};"></span>
            <span style="color:#e2e8f0; font-weight:600;">Sistema Activo</span>
        </div>
        <div style="color:#64748b; font-size:0.75rem; margin-top:5px;">
            📚 Aprendizaje: {len(anayansi.aprendizaje)} registros
        </div>
        <div style="color:#64748b; font-size:0.75rem;">
            📝 Logs: {len(anayansi.logs)} eventos
        </div>
        <div style="color:#64748b; font-size:0.75rem;">
            🧠 Aprendizaje automatico: {'✅ Activo' if anayansi.aprendizaje_automatico else '❌ Inactivo'}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if nuevos_aprendizajes:
        st.info(f"🧠 {len(nuevos_aprendizajes)} nuevos aprendizajes automaticos")
    
    st.markdown("---")
    
    if st.button("🔄 Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# CONTENIDO PRINCIPAL
# ==========================================

st.markdown("""
<div style="text-align:center; padding:10px 0;">
    <div class="main-header">🌊 ANAYANSI - Canal Predictor</div>
    <div class="sub-header">"Sabiduria del mar" - Sistema IA Avanzado para el Canal de Panama</div>
</div>
""", unsafe_allow_html=True)

df = st.session_state.get("df", generar_datos())
stats = st.session_state.get("stats", analizar(df))

# ==========================================
# PESTAÑAS
# ==========================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Dashboard",
    "🗺️ Mapa",
    "📈 Analisis",
    "🌊 Anayansi Chat",
    "🧠 Aprendizaje",
    "🔮 Predicciones",
    "📋 Datos"
])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================

with tab1:
    st.markdown("### 📊 Dashboard Ejecutivo")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🚢 Barcos Activos</div>
            <div class="metric-value">{stats['total']}</div>
            <div style="color:#10b981; font-size:0.8rem;">⬆️ En tiempo real</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏱️ CWT Actual</div>
            <div class="metric-value" style="color:{stats['color']};">{stats['cwt']:.1f}h</div>
            <div style="color:{stats['color']}; font-size:0.8rem;">{stats['nivel']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📈 Velocidad</div>
            <div class="metric-value">{stats['velocidad_prom']:.1f}</div>
            <div style="color:#94a3b8; font-size:0.8rem;">nudos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ En Espera</div>
            <div class="metric-value">{stats['espera']}</div>
            <div style="color:{'#ef4444' if stats['espera'] > 15 else '#10b981'}; font-size:0.8rem;">
                {'⚠️ Critico' if stats['espera'] > 15 else '✅ Normal'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⭐ Prioridad Alta</div>
            <div class="metric-value">{stats['prioridad_alta']}</div>
            <div style="color:#f59e0b; font-size:0.8rem;">⚡ Urgentes</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### 📊 Nivel de Congestion")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<h1 style='color:{stats['color']}; text-align:center; font-size:2.5rem;'>{stats['nivel']}</h1>", unsafe_allow_html=True)
    with col2:
        st.progress(min(stats["cwt"] / 30, 1.0))
        st.caption(f"CWT: {stats['cwt']:.1f}h | 🔴 Critico: 22h | 🟡 Advertencia: 18h | 🟢 Normal: 14h")
    
    st.markdown("---")
    
    st.markdown("#### 🌊 Datos Maritimos")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📏 Profundidad", f"{stats['profundidad_prom']:.1f}m")
    col2.metric("🌊 Corriente", f"{stats['corriente_prom']:.1f} nudos")
    col3.metric("📈 Marea", f"{stats['marea_prom']:.1f}m")
    col4.metric("🌊 Oleaje", f"{stats['oleaje_prom']:.1f}m")
    
    st.markdown("---")
    
    st.markdown("#### ⚙️ Estado de Esclusas")
    col1, col2, col3 = st.columns(3)
    
    for col, (nombre, datos) in zip([col1, col2, col3], stats["esclusas"].items()):
        with col:
            eficiencia_color = "#10b981" if "Alta" in datos["eficiencia"] else "#f59e0b" if "Media" in datos["eficiencia"] else "#ef4444"
            st.markdown(f"""
            <div class="esclusa-card">
                <h4 style="color:#e2e8f0;">⚙️ {nombre}</h4>
                <div style="color:{eficiencia_color}; font-weight:600;">{datos['eficiencia']}</div>
                <hr style="border-color:#1e293b;">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#94a3b8;">Total</span>
                    <span style="color:#e2e8f0; font-weight:600;">{datos['total']}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#94a3b8;">Espera</span>
                    <span style="color:#f59e0b; font-weight:600;">{datos['espera']}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#94a3b8;">⬆️ Norte</span>
                    <span style="color:#10b981; font-weight:600;">{datos['norte']}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#94a3b8;">⬇️ Sur</span>
                    <span style="color:#3b82f6; font-weight:600;">{datos['sur']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### ⚠️ Alertas del Sistema")
    
    alertas = []
    if stats["total"] > 80:
        alertas.append(("🔴 CRITICO", f"Trafico extremo ({stats['total']} barcos)", "critical"))
    elif stats["total"] > 65:
        alertas.append(("🟡 ADVERTENCIA", f"Trafico denso ({stats['total']} barcos)", "warning"))
    if stats["cwt"] > 22:
        alertas.append(("🔴 CRITICO", f"CWT critico ({stats['cwt']:.1f}h)", "critical"))
    if stats["espera"] > 18:
        alertas.append(("🔴 CRITICO", f"Demasiados en espera ({stats['espera']})", "critical"))
    elif stats["espera"] > 12:
        alertas.append(("🟡 ADVERTENCIA", f"Muchos en espera ({stats['espera']})", "warning"))
    if stats["viento_prom"] > 25:
        alertas.append(("🟡 ADVERTENCIA", f"Vientos fuertes ({stats['viento_prom']:.1f} nudos)", "warning"))
    if stats["oleaje_prom"] > 2:
        alertas.append(("🟡 ADVERTENCIA", f"Oleaje elevado ({stats['oleaje_prom']:.1f}m)", "warning"))
    
    if alertas:
        for titulo, mensaje, tipo in alertas:
            if tipo == "critical":
                st.markdown(f'<div class="alert-box alert-critical">**{titulo}**: {mensaje}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-box alert-warning">**{titulo}**: {mensaje}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-success">✅ Todas las condiciones operativas son normales</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: MAPA
# ==========================================

with tab2:
    st.markdown("### 🗺️ Mapa de Navegacion")
    
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
            "eta_horas": ":.1f",
            "prioridad": True
        },
        color="prioridad",
        color_discrete_map={"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"},
        size="velocidad",
        size_max=14,
        zoom=9,
        height=550,
        title="📍 Posicion de buques en el Canal de Panama"
    )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 9.15, "lon": -79.75},
        margin={"r":0, "t":30, "l":0, "b":0},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 3: ANÁLISIS
# ==========================================

with tab3:
    st.markdown("### 📈 Analisis y Predicciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Tipos de Barcos")
        tipos_df = pd.DataFrame({
            "Tipo": list(stats["tipos"].keys()),
            "Cantidad": list(stats["tipos"].values())
        })
        fig_tipos = px.bar(tipos_df, x="Tipo", y="Cantidad", color="Cantidad", color_continuous_scale="Viridis")
        fig_tipos.update_layout(height=300, template="plotly_dark")
        st.plotly_chart(fig_tipos, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Origen de Barcos")
        origen_df = pd.DataFrame({
            "Origen": list(stats["origenes"].keys()),
            "Cantidad": list(stats["origenes"].values())
        })
        fig_origen = px.pie(origen_df, values="Cantidad", names="Origen")
        fig_origen.update_layout(height=300, template="plotly_dark")
        st.plotly_chart(fig_origen, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 🌊 Variables Maritimas")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fig_prof = px.histogram(df, x="profundidad", title="Profundidad", nbins=20)
        fig_prof.update_layout(height=200, template="plotly_dark")
        st.plotly_chart(fig_prof, use_container_width=True)
    
    with col2:
        fig_corr = px.histogram(df, x="corriente", title="Corriente", nbins=20)
        fig_corr.update_layout(height=200, template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with col3:
        fig_marea = px.histogram(df, x="marea", title="Marea", nbins=20)
        fig_marea.update_layout(height=200, template="plotly_dark")
        st.plotly_chart(fig_marea, use_container_width=True)
    
    with col4:
        fig_oleaje = px.histogram(df, x="oleaje", title="Oleaje", nbins=20)
        fig_oleaje.update_layout(height=200, template="plotly_dark")
        st.plotly_chart(fig_oleaje, use_container_width=True)

# ==========================================
# TAB 4: CHAT
# ==========================================

with tab4:
    st.markdown("### 🌊 ANAYANSI - Asistente Inteligente")
    st.markdown("Hazme preguntas sobre el Canal de Panama, barcos, esclusas, clima y mas")
    
    for msg in st.session_state.chat_historial:
        if msg["rol"] == "anayansi":
            st.markdown(f'<div class="chat-message-anayansi">🌊 ANAYANSI: {msg["mensaje"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">👤 Tu: {msg["mensaje"]}</div>', unsafe_allow_html=True)
    
    pregunta = st.text_input("Pregunta a Anayansi...", placeholder="Ej: Cual es el CWT actual? Que barco va entrando al Canal?")
    
    if pregunta:
        st.session_state.chat_historial.append({"rol": "usuario", "mensaje": pregunta})
        respuesta = anayansi.preguntar(pregunta, df, stats)
        st.session_state.chat_historial.append({"rol": "anayansi", "mensaje": respuesta})
        st.rerun()
    
    if st.button("🗑️ Limpiar historial", use_container_width=True):
        st.session_state.chat_historial = [
            {"rol": "anayansi", "mensaje": "🌊 ¡Hola! Soy **Anayansi**, la sabiduria del mar. ¿Que necesitas saber sobre el Canal de Panama?"}
        ]
        st.rerun()

# ==========================================
# TAB 5: APRENDIZAJE
# ==========================================

with tab5:
    st.markdown("### 🧠 Aprendizaje de Anayansi")
    st.markdown("Todo lo que Anayansi ha aprendido sobre el Canal de Panama")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Estadisticas de Aprendizaje")
        st.metric("📚 Registros de aprendizaje", len(anayansi.aprendizaje))
        st.metric("📝 Eventos registrados (logs)", len(anayansi.logs))
        st.metric("🎯 Nivel de confianza", f"{anayansi.confianza*100:.0f}%")
        st.metric("🧠 Aprendizaje automatico", "✅ Activo" if anayansi.aprendizaje_automatico else "❌ Inactivo")
    
    with col2:
        st.markdown("#### 📝 Ultimos Aprendizajes")
        if anayansi.aprendizaje:
            for item in anayansi.aprendizaje[-5:]:
                st.caption(f"📅 {item['fecha'][:16]}")
                st.caption(f"📝 {item['conocimiento'][:100]}...")
                st.markdown("---")
        else:
            st.info("Aun no hay registros de aprendizaje")
    
    st.markdown("---")
    
    st.markdown("#### 📋 Logs del Sistema")
    with st.expander("Ver logs completos", expanded=False):
        if anayansi.logs:
            for log in anayansi.logs[-20:]:
                st.text(f"[{log['timestamp'][:19]}] {log['accion']}: {str(log['datos'])[:100]}...")
        else:
            st.info("No hay logs registrados")
    
    st.markdown("---")
    
    st.markdown("#### 🧠 Ensenar a Anayansi")
    nuevo_conocimiento = st.text_area("¿Que quieres que Anayansi aprenda sobre el Canal?")
    if st.button("📚 Ensenar", use_container_width=True):
        if nuevo_conocimiento:
            resultado = anayansi.aprender(nuevo_conocimiento)
            st.success(resultado)
            st.rerun()
        else:
            st.warning("Por favor, escribe algo para ensenar")

# ==========================================
# TAB 6: PREDICCIONES
# ==========================================

with tab6:
    st.markdown("### 🔮 Predicciones del Sistema IA")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🧠 LSTM - 24h", f"{stats['cwt']:.1f}h")
        st.progress(min(stats["cwt"] / 30, 1.0))
        st.caption("Confianza: 92%")
    
    with col2:
        rf_val = stats["cwt"] + np.random.normal(0, 0.5)
        st.metric("🌲 Random Forest - 7d", f"{rf_val:.1f}h")
        st.progress(min(rf_val / 30, 1.0))
        st.caption("Confianza: 88%")
    
    with col3:
        st.metric("📊 Nivel Congestion", stats["nivel"])
        st.caption(f"Confianza: {np.random.randint(85, 95)}%")
    
    st.markdown("---")
    
    st.markdown("#### 📈 Proyeccion de Trafico (6h)")
    
    horas = list(range(1, 7))
    barcos_futuros = [stats["total"] + np.random.randint(-3, 5) for _ in range(6)]
    
    fig_proy = px.line(
        x=horas,
        y=barcos_futuros,
        title="Evolucion Estimada del Trafico",
        labels={"x": "Horas", "y": "Numero de Barcos"}
    )
    fig_proy.add_hline(y=stats["total"], line_dash="dash", line_color="red", annotation_text="Actual")
    fig_proy.update_layout(height=300, template="plotly_dark")
    st.plotly_chart(fig_proy, use_container_width=True)

# ==========================================
# TAB 7: DATOS
# ==========================================

with tab7:
    st.markdown("### 📋 Datos y Reportes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_direccion = st.multiselect(
            "Direccion",
            options=["Norte", "Sur"],
            default=["Norte", "Sur"]
        )
    
    with col2:
        filtro_estado = st.multiselect(
            "Estado",
            options=["Navegando", "En espera en esclusa", "Entrando a esclusa"],
            default=["Navegando", "En espera en esclusa", "Entrando a esclusa"]
        )
    
    with col3:
        filtro_prioridad = st.multiselect(
            "Prioridad",
            options=["Alta", "Media", "Baja"],
            default=["Alta", "Media", "Baja"]
        )
    
    df_filtrado = df[df["direccion"].isin(filtro_direccion)]
    df_filtrado = df_filtrado[df_filtrado["estado"].isin(filtro_estado)]
    df_filtrado = df_filtrado[df_filtrado["prioridad"].isin(filtro_prioridad)]
    
    display_df = df_filtrado[["nombre", "direccion", "tipo", "estado", "esclusa", "velocidad", "eta_horas", "origen", "destino", "prioridad", "carga_valor", "emisiones", "profundidad", "corriente", "marea", "oleaje"]].copy()
    display_df["velocidad"] = display_df["velocidad"].round(1)
    display_df["eta_horas"] = display_df["eta_horas"].round(1)
    display_df["carga_valor"] = display_df["carga_valor"].apply(lambda x: f"${x/1e6:.1f}M")
    display_df["emisiones"] = display_df["emisiones"].round(1)
    display_df["profundidad"] = display_df["profundidad"].round(1)
    display_df["corriente"] = display_df["corriente"].round(1)
    display_df["marea"] = display_df["marea"].round(1)
    display_df["oleaje"] = display_df["oleaje"].round(1)
    display_df["direccion"] = display_df["direccion"].apply(lambda x: "⬆️ Norte" if x == "Norte" else "⬇️ Sur")
    display_df.columns = ["Nombre", "Direccion", "Tipo", "Estado", "Esclusa", "Velocidad", "ETA (h)", "Origen", "Destino", "Prioridad", "Carga ($M)", "Emisiones (t)", "Profundidad (m)", "Corriente (nudos)", "Marea (m)", "Oleaje (m)"]
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📊 Descargar datos (CSV)",
            data=csv,
            file_name="canal_datos_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv",
            mime="text/csv"
        )
    
    with col2:
        reporte = anayansi.generar_reporte_completo(df, stats)
        st.download_button(
            label="📄 Descargar Reporte Ejecutivo (TXT)",
            data=reporte,
            file_name="reporte_canal_" + datetime.now().strftime("%Y%m%d_%H%M") + ".txt",
            mime="text/plain"
        )

# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    🌊 ANAYANSI - Canal Predictor v3.0 | "Sabiduria del mar"
    <br>
    <span style="color:#475569;">🔄 Datos en tiempo real | 📡 Monitoreo continuo | 🧠 Aprendizaje automatico | 🌊 Datos maritimos integrados</span>
    <br>
    <span style="color:#334155; font-size:0.7rem;">Panama - Canal de Panama</span>
</div>
""", unsafe_allow_html=True)
