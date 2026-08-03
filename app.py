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

# ==========================================
# CONFIGURACIÓN
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
    .boat-info { background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 8px; margin: 4px 0; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. MOTOR DE DECISIÓN AUTÓNOMA
# ==========================================

@dataclass
class DecisionContext:
    timestamp: datetime
    barcos_activos: int
    esclusas_disponibles: List[str]
    condiciones_climaticas: Dict[str, float]
    demanda_actual: float
    recursos_disponibles: Dict[str, int]
    historico_reciente: List[Dict]
    prioridades: Dict[str, float]

class MotorDecisionAutonoma:
    def __init__(self):
        self.nivel_autonomia = 0.85
        self.historial_decisiones = []
        self.reglas_aprendidas = []
        self.pesos_decision = {
            "seguridad": 0.35,
            "eficiencia": 0.30,
            "costo": 0.20,
            "sostenibilidad": 0.15
        }
        self.umbrales_criticos = {
            "congestion_maxima": 0.85,
            "tiempo_espera_max": 120.0,
            "velocidad_minima": 3.0,
            "distancia_seguridad": 0.3
        }
        self.decisiones_tomadas = 0
        self.aciertos = 0
        
    def decidir(self, contexto: Dict, opciones: List[Dict]) -> Dict:
        analisis = self._analizar_contexto(contexto)
        
        evaluaciones = []
        for opcion in opciones:
            puntaje = self._evaluar_opcion(opcion, analisis)
            evaluaciones.append({
                "opcion": opcion,
                "puntaje": puntaje,
                "razonamiento": self._generar_razonamiento(opcion, puntaje, analisis)
            })
        
        mejor = max(evaluaciones, key=lambda x: x["puntaje"])
        
        decision = {
            "timestamp": datetime.now().isoformat(),
            "contexto": analisis,
            "decision": mejor,
            "confianza": self._calcular_confianza(mejor),
            "razonamiento": mejor["razonamiento"],
            "alternativas": [e["opcion"] for e in evaluaciones if e != mejor][:3]
        }
        self.historial_decisiones.append(decision)
        self.decisiones_tomadas += 1
        
        if self.decisiones_tomadas > 10:
            self._auto_evaluar()
        
        return decision
    
    def _analizar_contexto(self, contexto: Dict) -> Dict:
        return {
            "operativo": self._analizar_operativo(contexto),
            "climatico": self._analizar_clima(contexto),
            "seguridad": self._analizar_seguridad(contexto),
            "historico": self._analizar_historico(contexto)
        }
    
    def _analizar_operativo(self, contexto: Dict) -> Dict:
        barcos = contexto.get("barcos", 0)
        esclusas = len(contexto.get("esclusas_disponibles", []))
        demanda = contexto.get("demanda_actual", 0)
        congestion = (barcos / (esclusas * 4)) if esclusas > 0 else 0.5
        return {
            "barcos": barcos,
            "esclusas": esclusas,
            "demanda": demanda,
            "congestion": min(congestion, 1.0),
            "capacidad_restante": max(0, 1 - congestion)
        }
    
    def _analizar_clima(self, contexto: Dict) -> Dict:
        viento = contexto.get("condiciones_climaticas", {}).get("viento", 0)
        oleaje = contexto.get("condiciones_climaticas", {}).get("oleaje", 0)
        return {
            "viento": viento,
            "oleaje": oleaje,
            "severidad": (viento / 30 + oleaje / 3) / 2,
            "recomienda_precaucion": viento > 20 or oleaje > 2
        }
    
    def _analizar_seguridad(self, contexto: Dict) -> Dict:
        return {
            "nivel_riesgo": contexto.get("riesgo", 0.2),
            "alertas_activas": contexto.get("alertas", []),
            "requiere_atencion": contexto.get("riesgo", 0) > 0.7
        }
    
    def _analizar_historico(self, contexto: Dict) -> Dict:
        historico = contexto.get("historico_reciente", [])
        if not historico:
            return {"tendencia": "estable", "confianza": 0.5}
        if len(historico) > 5:
            valores = [h.get("eficiencia", 0.5) for h in historico[-5:]]
            tendencia = (valores[-1] - valores[0]) / max(valores[0], 0.01)
            return {
                "tendencia": "mejora" if tendencia > 0.05 else "empeora" if tendencia < -0.05 else "estable",
                "confianza": min(abs(tendencia) * 2, 0.9)
            }
        return {"tendencia": "estable", "confianza": 0.5}
    
    def _evaluar_opcion(self, opcion: Dict, analisis: Dict) -> float:
        puntaje = 0
        puntaje += self._evaluar_seguridad(opcion, analisis) * self.pesos_decision["seguridad"]
        puntaje += self._evaluar_eficiencia(opcion, analisis) * self.pesos_decision["eficiencia"]
        puntaje += self._evaluar_costo(opcion, analisis) * self.pesos_decision["costo"]
        puntaje += self._evaluar_sostenibilidad(opcion, analisis) * self.pesos_decision["sostenibilidad"]
        return min(max(puntaje, 0), 1.0)
    
    def _evaluar_seguridad(self, opcion: Dict, analisis: Dict) -> float:
        riesgo = opcion.get("riesgo", 0.2)
        return 1.0 - riesgo
    
    def _evaluar_eficiencia(self, opcion: Dict, analisis: Dict) -> float:
        tiempo = opcion.get("tiempo", 60)
        eficiencia_base = 1.0 - (tiempo / 120)
        return min(max(eficiencia_base, 0), 1.0)
    
    def _evaluar_costo(self, opcion: Dict, analisis: Dict) -> float:
        costo = opcion.get("costo", 1000)
        costo_max = 5000
        return 1.0 - min(costo / costo_max, 1.0)
    
    def _evaluar_sostenibilidad(self, opcion: Dict, analisis: Dict) -> float:
        co2 = opcion.get("co2", 100)
        co2_max = 500
        return 1.0 - min(co2 / co2_max, 1.0)
    
    def _generar_razonamiento(self, opcion: Dict, puntaje: float, analisis: Dict) -> str:
        razones = []
        if puntaje > 0.8:
            razones.append("Excelente opción operativa")
        elif puntaje > 0.6:
            razones.append("Buena opción con margen de mejora")
        else:
            razones.append("Opción con riesgos considerables")
        if analisis["operativo"]["congestion"] > 0.7:
            razones.append(f"Alta congestión ({analisis['operativo']['congestion']*100:.0f}%)")
        if analisis["climatico"]["recomienda_precaucion"]:
            razones.append("Condiciones climáticas adversas")
        if opcion.get("prioridad") == "alta":
            razones.append("Prioridad alta justifica recursos adicionales")
        return " | ".join(razones)
    
    def _calcular_confianza(self, decision: Dict) -> float:
        base = 0.7
        puntaje = decision["puntaje"]
        historico = self._confianza_historica()
        return min(base + (puntaje - 0.5) * 0.5 + historico * 0.1, 0.98)
    
    def _confianza_historica(self) -> float:
        if not self.historial_decisiones:
            return 0.5
        exitos = sum(1 for d in self.historial_decisiones[-20:] if d.get("exito", False))
        return exitos / max(len(self.historial_decisiones[-20:]), 1)
    
    def _auto_evaluar(self):
        if self.decisiones_tomadas % 10 == 0:
            aciertos = sum(1 for d in self.historial_decisiones[-10:] if d.get("exito", False))
            tasa = aciertos / 10
            self.aciertos += aciertos
            logger.info(f"Auto-evaluación: Tasa de éxito {tasa*100:.1f}%")
            if tasa < 0.7:
                self.nivel_autonomia = max(0.5, self.nivel_autonomia - 0.05)
                logger.warning(f"Reduciendo autonomía a {self.nivel_autonomia*100:.0f}%")
            elif tasa > 0.85:
                self.nivel_autonomia = min(0.95, self.nivel_autonomia + 0.02)
                logger.info(f"Aumentando autonomía a {self.nivel_autonomia*100:.0f}%")

# ==========================================
# 2. SISTEMA DE OPTIMIZACIÓN CONTINUA
# ==========================================

class OptimizadorContinuo:
    def __init__(self):
        self.algoritmo = "aprendizaje_por_refuerzo"
        self.recompensas = []
        self.politicas_optimas = {}
        self.tasa_aprendizaje = 0.01
        self.factor_descuento = 0.95
        self.modelo_q = defaultdict(lambda: defaultdict(float))
        self.epsilon = 0.1
        
    def optimizar_asignacion_esclusas(self, barcos: List[Dict], esclusas_disponibles: List[str]) -> Dict:
        estado = self._codificar_estado(barcos, esclusas_disponibles)
        asignaciones = self._generar_asignaciones(barcos, esclusas_disponibles)
        
        mejor = None
        mejor_valor = -float('inf')
        for asignacion in asignaciones:
            valor = self._calcular_valor_asignacion(asignacion, estado)
            if valor > mejor_valor:
                mejor_valor = valor
                mejor = asignacion
        
        if estado not in self.modelo_q:
            self.modelo_q[estado] = defaultdict(float)
        self.modelo_q[estado][str(mejor)] = mejor_valor
        
        return {
            "asignacion": mejor,
            "valor": mejor_valor,
            "confianza": min(mejor_valor, 1.0),
            "estado": estado
        }
    
    def _codificar_estado(self, barcos: List[Dict], esclusas: List[str]) -> str:
        estado = {
            "barcos": len(barcos),
            "esclusas": len(esclusas),
            "tipos": [b.get("tipo", "desconocido") for b in barcos[:5]]
        }
        return hashlib.md5(str(estado).encode()).hexdigest()[:8]
    
    def _generar_asignaciones(self, barcos: List[Dict], esclusas: List[str]) -> List[Dict]:
        asignaciones = []
        for i, barco in enumerate(barcos):
            for esclusa in esclusas:
                asignaciones.append({
                    "barco": barco.get("nombre", f"B{i+1}"),
                    "esclusa": esclusa,
                    "prioridad": barco.get("prioridad", "media"),
                    "tiempo_estimado": random.randint(20, 60)
                })
        return asignaciones[:10]
    
    def _calcular_valor_asignacion(self, asignacion: Dict, estado: str) -> float:
        base = 0.5
        if asignacion["prioridad"] == "alta":
            base += 0.3
        elif asignacion["prioridad"] == "baja":
            base -= 0.2
        base += 0.1 * (1 - asignacion["tiempo_estimado"] / 60)
        if estado in self.modelo_q:
            valor_aprendido = self.modelo_q[estado].get(str(asignacion), 0)
            base = 0.7 * base + 0.3 * valor_aprendido
        return min(max(base, 0), 1.0)

# ==========================================
# 3. SISTEMA DE PREDICCIÓN Y PREVENCIÓN
# ==========================================

class SistemaPrediccionPrevencion:
    def __init__(self):
        self.modelos_prediccion = {}
        self.alertas_preventivas = []
        self.umbrales_prevencion = {
            "congestion_anticipada": 0.75,
            "clima_severo_anticipado": 0.7,
            "falla_anticipada": 0.6,
            "retraso_anticipado": 0.65
        }
        self.historial_predicciones = []
        
    def predecir_y_prevenir(self, datos_actuales: Dict) -> Dict:
        predicciones = self._generar_predicciones(datos_actuales)
        acciones_preventivas = []
        
        for prediccion in predicciones:
            if self._es_critico(prediccion):
                accion = self._generar_accion_preventiva(prediccion)
                acciones_preventivas.append(accion)
                if accion.get("urgencia", 0) > 0.8:
                    self._ejecutar_accion_preventiva(accion)
        
        return {
            "predicciones": predicciones,
            "acciones_preventivas": acciones_preventivas,
            "nivel_alerta": self._calcular_nivel_alerta(predicciones)
        }
    
    def _generar_predicciones(self, datos: Dict) -> List[Dict]:
        predicciones = []
        barcos = datos.get("barcos", 0)
        esclusas = len(datos.get("esclusas_disponibles", []))
        congestion_prob = min((barcos / (esclusas * 4)) * 1.2, 1.0)
        
        if congestion_prob > self.umbrales_prevencion["congestion_anticipada"]:
            predicciones.append({
                "tipo": "congestion",
                "probabilidad": congestion_prob,
                "tiempo_estimado": datetime.now() + timedelta(hours=2),
                "severidad": "alta" if congestion_prob > 0.85 else "media"
            })
        
        viento = datos.get("condiciones_climaticas", {}).get("viento", 0)
        if viento > 25:
            predicciones.append({
                "tipo": "clima_severo",
                "probabilidad": min((viento - 20) / 20, 1.0),
                "tiempo_estimado": datetime.now() + timedelta(hours=1),
                "severidad": "alta" if viento > 30 else "media"
            })
        
        return predicciones
    
    def _es_critico(self, prediccion: Dict) -> bool:
        umbral = self.umbrales_prevencion.get(prediccion["tipo"] + "_anticipado", 0.7)
        return prediccion["probabilidad"] > umbral
    
    def _generar_accion_preventiva(self, prediccion: Dict) -> Dict:
        acciones = {
            "congestion": {"accion": "Redistribuir tráfico a esclusas alternativas", "urgencia": 0.8},
            "clima_severo": {"accion": "Activar protocolo de seguridad climática", "urgencia": 0.9},
            "falla": {"accion": "Programar mantenimiento preventivo", "urgencia": 0.7},
            "retraso": {"accion": "Ajustar horarios y prioridades", "urgencia": 0.6}
        }
        base = acciones.get(prediccion["tipo"], {"accion": "Monitorear situación", "urgencia": 0.5})
        return {
            "tipo": prediccion["tipo"],
            "accion": base["accion"],
            "urgencia": base["urgencia"] * prediccion["probabilidad"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _ejecutar_accion_preventiva(self, accion: Dict):
        logger.info(f"🛡️ Ejecutando acción preventiva: {accion['accion']}")
        self.alertas_preventivas.append(accion)
    
    def _calcular_nivel_alerta(self, predicciones: List[Dict]) -> str:
        if not predicciones:
            return "🟢 Normal"
        max_prob = max(p["probabilidad"] for p in predicciones)
        if max_prob > 0.85:
            return "🔴 Crítico"
        elif max_prob > 0.7:
            return "🟡 Advertencia"
        return "🟢 Normal"

# ==========================================
# 4. SISTEMA DE MEMORIA Y RAZONAMIENTO
# ==========================================

class MemoriaRazonamiento:
    def __init__(self):
        self.memoria_episodica = []
        self.memoria_semantica = defaultdict(list)
        self.memoria_procedimental = []
        self.red_semantica = self._construir_red_semantica()
        self.capacidad_maxima = 1000
        
    def _construir_red_semantica(self) -> Dict:
        return {
            "canal": ["esclusas", "barcos", "tráfico", "clima"],
            "esclusas": ["gatun", "pedro_miguel", "miraflores", "capacidad", "tiempo_espera"],
            "barcos": ["tipo", "prioridad", "velocidad", "carga", "origen", "destino"],
            "clima": ["viento", "oleaje", "marea", "visibilidad"],
            "operaciones": ["eficiencia", "costo", "seguridad", "optimizacion"]
        }
    
    def razonar(self, problema: str, contexto: Dict) -> Dict:
        experiencias = self._buscar_experiencias(problema, contexto)
        conocimiento = self._buscar_conocimiento(problema)
        
        if experiencias:
            return self._razonar_por_casos(problema, experiencias, contexto)
        elif conocimiento:
            return self._razonar_por_reglas(problema, conocimiento, contexto)
        else:
            return self._razonar_creativamente(problema, contexto)
    
    def _buscar_experiencias(self, problema: str, contexto: Dict) -> List[Dict]:
        similares = []
        palabras_clave = set(problema.lower().split())
        for exp in self.memoria_episodica[-100:]:
            exp_palabras = set(exp.get("problema", "").lower().split())
            similitud = len(palabras_clave & exp_palabras) / max(len(palabras_clave), 1)
            if similitud > 0.3:
                similares.append(exp)
        return similares[:5]
    
    def _buscar_conocimiento(self, problema: str) -> List[str]:
        conocimiento = []
        palabras = problema.lower().split()
        for palabra in palabras:
            if palabra in self.red_semantica:
                conocimiento.extend(self.red_semantica[palabra])
            else:
                for clave, valor in self.red_semantica.items():
                    if palabra in valor:
                        conocimiento.append(clave)
        return list(set(conocimiento))
    
    def _razonar_por_casos(self, problema: str, experiencias: List[Dict], contexto: Dict) -> Dict:
        mejor_caso = max(experiencias, key=lambda x: x.get("efectividad", 0))
        return {
            "metodo": "razonamiento_por_casos",
            "solucion": mejor_caso.get("solucion", "Adaptar solución previa"),
            "confianza": mejor_caso.get("efectividad", 0.6),
            "caso_referencia": mejor_caso.get("problema", "Caso similar"),
            "adaptacion": self._adaptar_solucion(mejor_caso, contexto)
        }
    
    def _razonar_por_reglas(self, problema: str, conocimiento: List[str], contexto: Dict) -> Dict:
        reglas = []
        if "esclusas" in conocimiento and contexto.get("barcos", 0) > 30:
            reglas.append("Alto volumen de barcos requiere optimización de esclusas")
        if "clima" in conocimiento and contexto.get("viento", 0) > 20:
            reglas.append("Condiciones climáticas adversas requieren precaución")
        return {
            "metodo": "razonamiento_por_reglas",
            "solucion": reglas[0] if reglas else "Monitoreo continuo",
            "confianza": 0.7,
            "reglas_aplicadas": reglas
        }
    
    def _razonar_creativamente(self, problema: str, contexto: Dict) -> Dict:
        return {
            "metodo": "razonamiento_creativo",
            "solucion": "Nueva solución propuesta basada en principios generales",
            "confianza": 0.5,
            "innovacion": True
        }
    
    def _adaptar_solucion(self, caso: Dict, contexto: Dict) -> str:
        adaptaciones = []
        if contexto.get("barcos", 0) > caso.get("barcos", 0):
            adaptaciones.append("Ajustar por mayor volumen de tráfico")
        if contexto.get("viento", 0) > caso.get("viento", 0):
            adaptaciones.append("Incorporar factores climáticos")
        return " | ".join(adaptaciones) if adaptaciones else "Aplicar solución directamente"
    
    def aprender_experiencia(self, problema: str, solucion: str, resultado: Dict):
        experiencia = {
            "problema": problema,
            "solucion": solucion,
            "resultado": resultado,
            "timestamp": datetime.now().isoformat(),
            "efectividad": self._evaluar_efectividad(resultado)
        }
        self.memoria_episodica.append(experiencia)
        if len(self.memoria_episodica) > self.capacidad_maxima:
            self.memoria_episodica = self.memoria_episodica[-self.capacidad_maxima:]
    
    def _evaluar_efectividad(self, resultado: Dict) -> float:
        return 0.9 if resultado.get("exitoso", False) else 0.3

# ==========================================
# 5. SISTEMA DE OPTIMIZACIÓN DE RECURSOS
# ==========================================

class OptimizadorRecursos:
    def __init__(self):
        self.recursos = {
            "esclusas": {"capacidad": 4, "tiempo_ciclo": 45, "costo_operacion": 1000},
            "remolcadores": {"cantidad": 8, "costo_hora": 500, "velocidad": 8},
            "pilotos": {"cantidad": 24, "costo_hora": 300},
            "equipo_mantenimiento": {"equipos": 5, "costo_hora": 400}
        }
        self.asignacion_actual = {}
        self.eficiencia_historica = []
    
    def optimizar_recursos_dinamico(self, demanda: Dict, condiciones: Dict) -> Dict:
        demanda_actual = self._evaluar_demanda(demanda)
        recursos_necesarios = self._calcular_recursos_necesarios(demanda_actual, condiciones)
        asignacion = self._asignar_recursos_optimos(recursos_necesarios)
        eficiencia = self._calcular_eficiencia_asignacion(asignacion)
        
        if eficiencia < 0.8:
            asignacion = self._rebalancear_recursos(asignacion)
            eficiencia = self._calcular_eficiencia_asignacion(asignacion)
        
        self.asignacion_actual = asignacion
        
        return {
            "asignacion": asignacion,
            "eficiencia": eficiencia,
            "demanda": demanda_actual,
            "recomendaciones": self._generar_recomendaciones(asignacion)
        }
    
    def _evaluar_demanda(self, demanda: Dict) -> Dict:
        return {
            "barcos": demanda.get("barcos", 0),
            "urgencia": demanda.get("urgencia", 0.5),
            "complejidad": demanda.get("complejidad", 0.5)
        }
    
    def _calcular_recursos_necesarios(self, demanda: Dict, condiciones: Dict) -> Dict:
        barcos = demanda["barcos"]
        esclusas_necesarias = max(1, int(barcos / 4))
        remolcadores_necesarios = max(2, int(barcos / 6))
        pilotos_necesarios = max(3, int(barcos / 3))
        
        if condiciones.get("viento", 0) > 20:
            remolcadores_necesarios += 2
            pilotos_necesarios += 2
        
        return {
            "esclusas": esclusas_necesarias,
            "remolcadores": remolcadores_necesarios,
            "pilotos": pilotos_necesarios,
            "mantenimiento": max(1, int(barcos / 20))
        }
    
    def _asignar_recursos_optimos(self, recursos_necesarios: Dict) -> Dict:
        asignacion = {}
        for recurso, cantidad in recursos_necesarios.items():
            disponible = self.recursos.get(recurso, {}).get("cantidad", 0)
            asignacion[recurso] = {
                "asignado": min(cantidad, disponible),
                "disponible": disponible,
                "utilizacion": min(cantidad / max(disponible, 1), 1.0)
            }
        return asignacion
    
    def _calcular_eficiencia_asignacion(self, asignacion: Dict) -> float:
        if not asignacion:
            return 0.5
        eficiencias = []
        for datos in asignacion.values():
            eficiencia = 1.0 - (datos.get("disponible", 0) - datos.get("asignado", 0)) / max(datos.get("disponible", 1), 1)
            eficiencias.append(eficiencia)
        return sum(eficiencias) / len(eficiencias)
    
    def _rebalancear_recursos(self, asignacion: Dict) -> Dict:
        for recurso, datos in asignacion.items():
            if datos["utilizacion"] < 0.5:
                datos["asignado"] = int(datos["asignado"] * 0.8)
                datos["utilizacion"] = datos["asignado"] / max(datos["disponible"], 1)
        return asignacion
    
    def _generar_recomendaciones(self, asignacion: Dict) -> List[str]:
        recomendaciones = []
        for recurso, datos in asignacion.items():
            if datos["utilizacion"] > 0.9:
                recomendaciones.append(f"⚠️ Alta utilización de {recurso} - Considerar aumentar capacidad")
            elif datos["utilizacion"] < 0.3:
                recomendaciones.append(f"💡 Baja utilización de {recurso} - Posible exceso de capacidad")
        return recomendaciones

# ==========================================
# 6. SISTEMA DE EVALUACIÓN CONTINUA
# ==========================================

class SistemaEvaluacionContinua:
    def __init__(self):
        self.kpis = {
            "eficiencia_operativa": 0,
            "satisfaccion_usuario": 0,
            "tiempo_respuesta": 0,
            "precision_prediccion": 0,
            "costo_operativo": 0,
            "sostenibilidad": 0
        }
        self.benchmarks = {
            "eficiencia_operativa": 0.85,
            "satisfaccion_usuario": 0.9,
            "tiempo_respuesta": 2.0,
            "precision_prediccion": 0.9,
            "costo_operativo": 100000,
            "sostenibilidad": 0.75
        }
        self.plan_mejora = []
        self.historial_evaluaciones = []
    
    def evaluar_y_mejorar(self, datos_actuales: Dict) -> Dict:
        kpis_actuales = self._medir_kpis(datos_actuales)
        brechas = self._identificar_brechas(kpis_actuales)
        plan_mejora = self._generar_plan_mejora(brechas)
        plan_priorizado = self._priorizar_mejoras(plan_mejora)
        
        evaluacion = {
            "timestamp": datetime.now().isoformat(),
            "kpis": kpis_actuales,
            "brechas": brechas,
            "plan_mejora": plan_priorizado
        }
        self.historial_evaluaciones.append(evaluacion)
        return evaluacion
    
    def _medir_kpis(self, datos: Dict) -> Dict:
        return {
            "eficiencia_operativa": datos.get("eficiencia", 0.8),
            "satisfaccion_usuario": datos.get("satisfaccion", 0.85),
            "tiempo_respuesta": datos.get("tiempo_respuesta", 1.5),
            "precision_prediccion": datos.get("precision", 0.88),
            "costo_operativo": datos.get("costo", 95000),
            "sostenibilidad": datos.get("sostenibilidad", 0.7)
        }
    
    def _identificar_brechas(self, kpis: Dict) -> Dict:
        brechas = {}
        for kpi, valor in kpis.items():
            benchmark = self.benchmarks.get(kpi, 0)
            if isinstance(valor, (int, float)):
                if valor < benchmark:
                    brechas[kpi] = {
                        "actual": valor,
                        "objetivo": benchmark,
                        "brecha": benchmark - valor,
                        "prioridad": "alta" if (benchmark - valor) / benchmark > 0.15 else "media"
                    }
        return brechas
    
    def _generar_plan_mejora(self, brechas: Dict) -> List[Dict]:
        plan = []
        for kpi, datos in brechas.items():
            if datos["prioridad"] == "alta":
                plan.append({
                    "area": kpi,
                    "accion": self._sugerir_mejora(kpi),
                    "impacto_estimado": datos["brecha"] / datos["objetivo"],
                    "tiempo_estimado": "3-5 días"
                })
        return plan
    
    def _sugerir_mejora(self, kpi: str) -> str:
        sugerencias = {
            "eficiencia_operativa": "Optimizar procesos de asignación de esclusas",
            "satisfaccion_usuario": "Mejorar tiempos de respuesta y comunicación",
            "tiempo_respuesta": "Optimizar código y aumentar capacidad de procesamiento",
            "precision_prediccion": "Entrenar modelo con datos más recientes",
            "costo_operativo": "Identificar y eliminar ineficiencias operativas",
            "sostenibilidad": "Implementar prácticas de reducción de emisiones"
        }
        return sugerencias.get(kpi, "Monitorear y ajustar continuamente")
    
    def _priorizar_mejoras(self, plan: List[Dict]) -> List[Dict]:
        return sorted(plan, key=lambda x: x["impacto_estimado"], reverse=True)

# ==========================================
# 7. SISTEMA COMPLETO - INTEGRACIÓN
# ==========================================

class SistemaCompleto:
    def __init__(self):
        self.motor_decision = MotorDecisionAutonoma()
        self.optimizador = OptimizadorContinuo()
        self.prediccion = SistemaPrediccionPrevencion()
        self.memoria = MemoriaRazonamiento()
        self.recursos = OptimizadorRecursos()
        self.evaluacion = SistemaEvaluacionContinua()
        
        self.modo_operativo = "autonomo"
        self.nivel_autonomia = 0.85
        self.estado_sistema = "operativo"
        self.metricas_sistema = {
            "decisiones_tomadas": 0,
            "alertas_generadas": 0,
            "optimizaciones_realizadas": 0,
            "tiempo_promedio_respuesta": 0
        }
        
    def procesar_operacion(self, datos_operativos: Dict) -> Dict:
        analisis = self.motor_decision._analizar_contexto(datos_operativos)
        predicciones = self.prediccion.predecir_y_prevenir(datos_operativos)
        recursos = self.recursos.optimizar_recursos_dinamico(
            {"barcos": datos_operativos.get("barcos", 0)},
            datos_operativos.get("condiciones_climaticas", {})
        )
        opciones = self._generar_opciones(datos_operativos)
        decisiones = self.motor_decision.decidir(datos_operativos, opciones)
        
        self.memoria.aprender_experiencia(
            str(datos_operativos),
            str(decisiones),
            {"exitoso": True}
        )
        
        evaluacion = self.evaluacion.evaluar_y_mejorar({
            "eficiencia": recursos["eficiencia"],
            "tiempo_respuesta": 1.5,
            "precision": decisiones["confianza"],
            "sostenibilidad": 0.75
        })
        
        self.metricas_sistema["decisiones_tomadas"] += 1
        self.metricas_sistema["alertas_generadas"] += len(predicciones["acciones_preventivas"])
        self.metricas_sistema["optimizaciones_realizadas"] += 1
        
        return {
            "analisis": analisis,
            "predicciones": predicciones,
            "recursos": recursos,
            "decisiones": decisiones,
            "evaluacion": evaluacion,
            "metricas": self.metricas_sistema,
            "confianza_sistema": self.nivel_autonomia,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generar_opciones(self, datos: Dict) -> List[Dict]:
        opciones = []
        esclusas = datos.get("esclusas_disponibles", ["Gatun", "Pedro Miguel", "Miraflores"])
        prioridades = ["alta", "media", "baja"]
        
        for i, esclusa in enumerate(esclusas):
            for prioridad in prioridades:
                opciones.append({
                    "asignar": esclusa,
                    "prioridad": prioridad,
                    "tiempo": random.randint(20, 60),
                    "costo": random.randint(500, 2000),
                    "riesgo": random.uniform(0.1, 0.4),
                    "co2": random.randint(50, 200)
                })
        return opciones
    
    def configurar_modo_operativo(self, modo: str) -> Dict:
        self.modo_operativo = modo
        if modo == "autonomo":
            self.nivel_autonomia = 0.95
            self.motor_decision.nivel_autonomia = 0.95
            mensaje = "🤖 Modo autónomo activado - Sistema toma decisiones sin intervención"
        elif modo == "supervisado":
            self.nivel_autonomia = 0.5
            self.motor_decision.nivel_autonomia = 0.5
            mensaje = "👁️ Modo supervisado - Sistema sugiere, humano decide"
        else:
            self.nivel_autonomia = 0.1
            self.motor_decision.nivel_autonomia = 0.1
            mensaje = "🖐️ Modo manual - Control humano total"
        
        return {
            "modo": modo,
            "nivel_autonomia": self.nivel_autonomia,
            "mensaje": mensaje
        }

# ==========================================
# GENERAR DATOS - COMPLETO CON TODAS LAS COLUMNAS
# ==========================================

@st.cache_data(ttl=30)
def generar_datos():
    np.random.seed(int(time.time() / 30) % 1000)
    n = np.random.randint(35, 55)
    
    puntos = [(9.36, -79.92), (9.27, -79.92), (9.20, -79.88), (9.015, -79.62), (8.995, -79.585), (8.90, -79.52)]
    tipos = ["Portacontenedores", "Granelero", "Petrolero", "Gasero", "Carguero", "Crucero", "Remolcador", "Pesquero"]
    estados = ["Navegando", "Navegando", "Navegando", "En espera", "Entrando"]
    esclusas = ["Gatun", "Pedro Miguel", "Miraflores"]
    prioridades = ["Alta", "Media", "Baja"]
    
    barcos = []
    for i in range(n):
        idx = np.random.randint(0, len(puntos))
        lat, lon = puntos[idx]
        lat += np.random.normal(0, 0.02)
        lon += np.random.normal(0, 0.02)
        direccion = "Sur" if np.random.random() < 0.5 else "Norte"
        estado = random.choice(estados)
        velocidad = np.random.uniform(0, 1) if estado == "En espera" else np.random.uniform(4, 16)
        barco = {
            "nombre": "B" + str(i+1).zfill(4),
            "tipo": random.choice(tipos),
            "direccion": direccion,
            "lat": lat,
            "lon": lon,
            "velocidad": velocidad,
            "estado": estado,
            "esclusa": random.choice(esclusas),
            "eta_horas": np.random.uniform(0.5, 8),
            "prioridad": random.choice(prioridades),
            "eslora": round(np.random.uniform(80, 400), 0),
            "calado": round(np.random.uniform(8, 18), 1),
            "carga": round(np.random.uniform(100, 10000), 0)
        }
        barcos.append(barco)
    return pd.DataFrame(barcos)

# ==========================================
# ANÁLISIS - COMPLETO
# ==========================================

@st.cache_data(ttl=30)
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
# FUNCIÓN PARA MAPA MEJORADO
# ==========================================

def crear_mapa_mejorado(df):
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
            "prioridad": True,
            "eslora": True,
            "calado": True,
            "carga": True
        },
        color="prioridad",
        color_discrete_map={"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"},
        size="velocidad",
        size_max=16,
        zoom=9,
        height=500,
        title="📍 Navegación en el Canal de Panamá"
    )
    
    esclusas_coords = {
        "Gatún": {"lat": 9.27, "lon": -79.92},
        "Pedro Miguel": {"lat": 9.015, "lon": -79.62},
        "Miraflores": {"lat": 8.995, "lon": -79.585}
    }
    
    for nombre, coords in esclusas_coords.items():
        fig.add_trace(
            go.Scattermapbox(
                lat=[coords["lat"]],
                lon=[coords["lon"]],
                mode="markers",
                marker=dict(size=20, color="red", symbol="triangle-up"),
                name="⚙️ " + nombre,
                hoverinfo="text",
                hovertext=["⚙️ Esclusa de " + nombre]
            )
        )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 9.15, "lon": -79.75},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# ==========================================
# INICIALIZAR SISTEMA
# ==========================================

if "sistema_ia" not in st.session_state:
    st.session_state.sistema_ia = SistemaCompleto()
    st.session_state.sistema_ia.configurar_modo_operativo("autonomo")

sistema = st.session_state.sistema_ia

if "df" not in st.session_state:
    st.session_state.df = generar_datos()
    st.session_state.stats = analizar(st.session_state.df)

df = st.session_state.df
stats = st.session_state.stats

# ==========================================
# SIDEBAR - COMPLETO
# ==========================================

with st.sidebar:
    st.markdown("### 🧠 ANAYANSI")
    st.markdown("---")
    
    st.markdown(f"**🤖 Modo:** {sistema.modo_operativo.upper()}")
    st.markdown(f"**⚡ Autonomía:** {sistema.nivel_autonomia*100:.0f}%")
    st.markdown(f"**📊 Decisiones:** {sistema.metricas_sistema['decisiones_tomadas']}")
    st.markdown(f"**🔔 Alertas:** {sistema.metricas_sistema['alertas_generadas']}")
    
    st.markdown("---")
    
    st.markdown("#### 🎮 Control del Sistema")
    modos = ["autonomo", "supervisado", "manual"]
    modo_actual = st.selectbox("Modo Operativo", modos, index=modos.index(sistema.modo_operativo))
    
    if modo_actual != sistema.modo_operativo:
        resultado = sistema.configurar_modo_operativo(modo_actual)
        st.success(resultado["mensaje"])
        st.rerun()
    
    st.markdown("---")
    
    # KPIs del sidebar
    col1, col2 = st.columns(2)
    col1.metric("🚢 Barcos", stats["total"])
    col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
    
    st.markdown("---")
    st.markdown("#### ⬆️⬇️ Dirección")
    col1, col2 = st.columns(2)
    col1.metric("Norte", stats["norte"])
    col2.metric("Sur", stats["sur"])
    
    st.markdown("---")
    st.caption("🧠 Confianza: " + str(int(sistema.motor_decision.nivel_autonomia * 100)) + "%")
    
    if st.button("🔄 Procesar Operación"):
        with st.spinner("🧠 Procesando..."):
            datos = {
                "barcos": stats["total"],
                "esclusas_disponibles": list(stats["esclusas"].keys()),
                "condiciones_climaticas": {"viento": stats["viento"], "oleaje": stats["oleaje"]},
                "demanda_actual": stats["total"] / 50,
                "recursos_disponibles": {"remolcadores": 6, "pilotos": 18}
            }
            resultado = sistema.procesar_operacion(datos)
            st.session_state.ultima_operacion = resultado
            st.success("✅ Operación procesada")
            st.rerun()

# ==========================================
# CONTENIDO PRINCIPAL - COMPLETO
# ==========================================

st.markdown('<div class="main-header">🧠 ANAYANSI - IA Cognitiva</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Inteligencia Artificial para Optimización Operativa del Canal de Panamá</div>', unsafe_allow_html=True)

# Mostrar última decisión si existe
if "ultima_operacion" in st.session_state:
    resultado = st.session_state.ultima_operacion
    
    st.markdown("### 🎯 Última Decisión de la IA")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🧠 Confianza", f"{resultado['decisiones']['confianza']*100:.0f}%")
    with col2:
        st.metric("⚡ Eficiencia", f"{resultado['recursos']['eficiencia']*100:.0f}%")
    with col3:
        alerta = resultado['predicciones']['nivel_alerta']
        st.metric("🔔 Alerta", alerta)
    
    st.markdown(f"""
    <div class="decision-card">
        <b>📋 Decisión:</b> {resultado['decisiones']['decision']['opcion']['asignar']} - Prioridad {resultado['decisiones']['decision']['opcion']['prioridad']}
        <br><b>💡 Razonamiento:</b> {resultado['decisiones']['razonamiento']}
        <br><b>⏱️ Tiempo Estimado:</b> {resultado['decisiones']['decision']['opcion']['tiempo']} minutos
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# KPIS - COMPLETO
# ==========================================

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("🚢 Barcos", stats["total"])
col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
col3.metric("📈 Vel.", f"{stats['velocidad_prom']:.1f}")
col4.metric("⏳ Espera", stats["espera"])
col5.metric("⭐ Alta", stats["prioridad_alta"])
col6.metric("⬆️ Norte", stats["norte"])
col7.metric("⬇️ Sur", stats["sur"])

st.markdown("---")

# ==========================================
# CLIMA Y MAR
# ==========================================

st.markdown("#### 🌤️ Clima y Mar")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🌡️ Temp", f"{stats['temp']:.1f}°C")
col2.metric("💨 Viento", f"{stats['viento']:.1f} nudos")
col3.metric("🌊 Marea", f"{stats['marea']:.1f}m")
col4.metric("📏 Profundidad", f"{stats['profundidad']:.1f}m")
col5.metric("🌊 Oleaje", f"{stats['oleaje']:.1f}m")

st.markdown("---")

# ==========================================
# PREDICCIONES Y RECOMENDACIONES
# ==========================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔮 Predicción de Congestión")
    datos_pred = {
        "barcos": stats["total"],
        "esclusas_disponibles": list(stats["esclusas"].keys()),
        "condiciones_climaticas": {"viento": stats["viento"], "oleaje": stats["oleaje"]}
    }
    prediccion = sistema.prediccion.predecir_y_prevenir(datos_pred)
    
    nivel_color = {"🟢 Normal": "#10b981", "🟡 Advertencia": "#f59e0b", "🔴 Crítico": "#ef4444"}
    nivel = prediccion["nivel_alerta"]
    color = nivel_color.get(nivel, "#94a3b8")
    
    st.markdown(f"""
    <div class="insight-card">
        <div style="font-size:1.2rem; font-weight:700; color:{color};">{nivel}</div>
        <div style="margin-top:8px;">
            <b>Predicciones:</b> {len(prediccion['predicciones'])} eventos detectados
        </div>
        <div style="margin-top:4px; font-size:0.85rem; color:#94a3b8;">
            {len(prediccion['acciones_preventivas'])} acciones preventivas generadas
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
# ESLUSCAS - COMPLETO
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ Mapa", "📊 Análisis", "💬 Chat IA", "🧠 Decisiones IA", "📈 Insights", "⚙️ Configuración IA"
])

# TAB 1: MAPA
with tab1:
    st.markdown("### 🗺️ Mapa de Navegación")
    st.caption("🟢 Barcos con prioridad baja | 🟡 Media | 🔴 Alta | 🔺 Esclusas")
    
    fig = crear_mapa_mejorado(df)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 📊 Resumen del Mapa")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Barcos en el mapa", stats["total"])
    with col2:
        st.metric("⚙️ Esclusas activas", len(stats["esclusas"]))
    with col3:
        st.metric("🔴 Prioridad Alta", stats["prioridad_alta"])

# TAB 2: ANÁLISIS
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

# TAB 3: CHAT IA
with tab3:
    st.markdown("### 💬 Chat con Anayansi")
    st.caption("💡 Pregunta sobre decisiones, predicciones o estado del sistema")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"rol": "anayansi", "msg": "🧠 ¡Hola! Soy Anayansi, tu IA cognitiva. Puedo tomar decisiones operativas, predecir problemas y optimizar recursos. ¿Qué necesitas saber?"}
        ]
    
    for msg in st.session_state.chat_messages:
        if msg["rol"] == "anayansi":
            st.markdown(f'<div class="chat-ai">🧠 Anayansi: {msg["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">👤 Tú: {msg["msg"]}</div>', unsafe_allow_html=True)
    
    pregunta = st.text_input("Pregunta a Anayansi:", placeholder="¿Qué decisión recomiendas para optimizar el tráfico?")
    if pregunta:
        st.session_state.chat_messages.append({"rol": "usuario", "msg": pregunta})
        
        if "decisión" in pregunta.lower() or "optimizar" in pregunta.lower():
            datos = {
                "barcos": stats["total"],
                "esclusas_disponibles": list(stats["esclusas"].keys()),
                "condiciones_climaticas": {"viento": stats["viento"], "oleaje": stats["oleaje"]},
                "demanda_actual": stats["total"] / 50
            }
            opciones = [
                {"asignar": "Gatun", "prioridad": "alta", "tiempo": 35, "costo": 1200},
                {"asignar": "Pedro Miguel", "prioridad": "media", "tiempo": 45, "costo": 800},
                {"asignar": "Miraflores", "prioridad": "baja", "tiempo": 40, "costo": 950}
            ]
            decision = sistema.motor_decision.decidir(datos, opciones)
            respuesta = f"🎯 **Decisión recomendada:** {decision['decision']['opcion']['asignar']} con prioridad {decision['decision']['opcion']['prioridad']}\n\n💡 {decision['razonamiento']}\n\nConfianza: {decision['confianza']*100:.0f}%"
        elif "predicción" in pregunta.lower() or "clima" in pregunta.lower():
            datos_pred = {
                "barcos": stats["total"],
                "esclusas_disponibles": list(stats["esclusas"].keys()),
                "condiciones_climaticas": {"viento": stats["viento"], "oleaje": stats["oleaje"]}
            }
            prediccion = sistema.prediccion.predecir_y_prevenir(datos_pred)
            respuesta = f"🔮 **Predicción:** {prediccion['nivel_alerta']}\n\n📊 {len(prediccion['predicciones'])} eventos detectados\n🛡️ {len(prediccion['acciones_preventivas'])} acciones preventivas"
        else:
            respuesta = f"📊 Estado actual del sistema:\n• Barcos: {stats['total']}\n• CWT: {stats['cwt']:.1f}h\n• Modo: {sistema.modo_operativo.upper()}\n• Confianza: {sistema.nivel_autonomia*100:.0f}%"
        
        st.session_state.chat_messages.append({"rol": "anayansi", "msg": respuesta})
        st.rerun()
    
    if st.button("🗑️ Limpiar chat"):
        st.session_state.chat_messages = [
            {"rol": "anayansi", "msg": "🧠 ¡Hola! Soy Anayansi, tu IA cognitiva. ¿Qué necesitas saber?"}
        ]
        st.rerun()

# TAB 4: DECISIONES IA
with tab4:
    st.markdown("### 🧠 Decisiones de la IA")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Decisiones tomadas", sistema.metricas_sistema["decisiones_tomadas"])
        st.metric("🎯 Tasa de acierto", f"{sistema.motor_decision.aciertos / max(sistema.motor_decision.decisiones_tomadas, 1) * 100:.1f}%")
    with col2:
        st.metric("⚡ Autonomía", f"{sistema.nivel_autonomia*100:.0f}%")
        st.metric("🧠 Confianza", f"{sistema.motor_decision.nivel_autonomia*100:.0f}%")
    
    st.markdown("---")
    
    st.markdown("#### 📋 Historial de Decisiones")
    if sistema.motor_decision.historial_decisiones:
        for decision in sistema.motor_decision.historial_decisiones[-5:]:
            st.markdown(f"""
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:10px; margin:5px 0;">
                <b>🕐 {decision['timestamp'][:19]}</b>
                <br>📋 {decision['decision']['opcion']['asignar']} - Prioridad {decision['decision']['opcion']['prioridad']}
                <br>💡 {decision['razonamiento'][:100]}...
                <br>🎯 Confianza: {decision['confianza']*100:.0f}%
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aún no hay decisiones registradas. Procesa una operación para comenzar.")

# TAB 5: INSIGHTS
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
    
    if stats.get("viento", 0) > 20 and stats["total"] > 40:
        st.warning("🌪️ **Vientos fuertes + tráfico denso.** Se recomienda precaución.")
    
    st.markdown("---")
    
    st.markdown("#### 📊 Métricas de la IA")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧠 Confianza", str(int(sistema.nivel_autonomia * 100)) + "%")
    col2.metric("📚 Decisiones", sistema.metricas_sistema["decisiones_tomadas"])
    col3.metric("🔔 Alertas", sistema.metricas_sistema["alertas_generadas"])
    col4.metric("⚡ Eficiencia", f"{sistema.metricas_sistema['optimizaciones_realizadas']}")

# TAB 6: CONFIGURACIÓN IA - CORREGIDA
with tab6:
    st.markdown("### ⚙️ Configuración de la IA")
    
    st.markdown("#### 🎯 Pesos de Decisión")
    col1, col2 = st.columns(2)
    with col1:
        st.slider("Seguridad", 0.0, 1.0, sistema.motor_decision.pesos_decision["seguridad"], 0.05, key="peso_seguridad")
        st.slider("Eficiencia", 0.0, 1.0, sistema.motor_decision.pesos_decision["eficiencia"], 0.05, key="peso_eficiencia")
    with col2:
        st.slider("Costo", 0.0, 1.0, sistema.motor_decision.pesos_decision["costo"], 0.05, key="peso_costo")
        st.slider("Sostenibilidad", 0.0, 1.0, sistema.motor_decision.pesos_decision["sostenibilidad"], 0.05, key="peso_sostenibilidad")
    
    if st.button("💾 Actualizar Pesos"):
        sistema.motor_decision.pesos_decision = {
            "seguridad": st.session_state.peso_seguridad,
            "eficiencia": st.session_state.peso_eficiencia,
            "costo": st.session_state.peso_costo,
            "sostenibilidad": st.session_state.peso_sostenibilidad
        }
        st.success("✅ Pesos actualizados correctamente")
    
    st.markdown("---")
    
    st.markdown("#### 🎚️ Umbrales Críticos")
    col1, col2 = st.columns(2)
    with col1:
        congestion_actual = float(sistema.motor_decision.umbrales_criticos["congestion_maxima"])
        st.slider("Congestión Máxima", 0.5, 1.0, congestion_actual, 0.05, key="umbral_congestion")
        
        espera_actual = float(sistema.motor_decision.umbrales_criticos["tiempo_espera_max"])
        st.slider("Tiempo Espera Máx (min)", 30.0, 180.0, espera_actual, 5.0, key="umbral_espera")
    
    with col2:
        velocidad_actual = float(sistema.motor_decision.umbrales_criticos["velocidad_minima"])
        st.slider("Velocidad Mínima (nudos)", 1.0, 6.0, velocidad_actual, 0.5, key="umbral_velocidad")
        
        distancia_actual = float(sistema.motor_decision.umbrales_criticos["distancia_seguridad"])
        st.slider("Distancia Seguridad (millas)", 0.1, 0.5, distancia_actual, 0.05, key="umbral_distancia")
    
    if st.button("💾 Actualizar Umbrales"):
        sistema.motor_decision.umbrales_criticos = {
            "congestion_maxima": st.session_state.umbral_congestion,
            "tiempo_espera_max": st.session_state.umbral_espera,
            "velocidad_minima": st.session_state.umbral_velocidad,
            "distancia_seguridad": st.session_state.umbral_distancia
        }
        st.success("✅ Umbrales actualizados correctamente")

# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    🧠 ANAYANSI - IA Cognitiva v3.0 | Sistema de Optimización Operativa Autónoma
    <br>
    <span style="color:#475569;">🤖 Modo: </span><span style="color:#00b4d8;">{}</span>
</div>
""".format(sistema.modo_operativo.upper()), unsafe_allow_html=True)
