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
    
    .weather-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(26,58,92,0.9));
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    .weather-icon {
        font-size: 2.5rem;
    }
    .weather-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    .weather-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SISTEMA ANAYANSI - IA AVANZADA
# ==========================================

class AnayansiIA:
    def __init__(self):
        self.aprendizaje = []
        self.logs = []
        self.historial_barcos = []
        self.confianza = 0.93
        self.aprendizaje_automatico = True
        self.conocimiento_clima = {
            "viento": {"normal": 15, "critico": 30},
            "oleaje": {"normal": 1.5, "critico": 3.0},
            "marea": {"normal": 2.5, "critico": 4.0}
        }
    
    def aprender(self, texto):
        self.aprendizaje.append({"fecha": datetime.now().isoformat(), "texto": texto})
        self.logs.append({"timestamp": datetime.now().isoformat(), "accion": "aprendizaje", "datos": texto})
        return "Anayansi ha aprendido: " + texto[:50] + "..."
    
    def aprender_automaticamente(self, df, stats):
        nuevos = []
        
        if stats["total"] > 70:
            msg = "Alto tráfico detectado: " + str(stats["total"]) + " barcos."
            self.aprender(msg); nuevos.append(msg)
        
        if stats["cwt"] > 20:
            msg = "CWT crítico: " + str(round(stats["cwt"], 1)) + "h."
            self.aprender(msg); nuevos.append(msg)
        
        if stats["espera"] > 12:
            msg = "Congestión en esclusas: " + str(stats["espera"]) + " barcos en espera."
            self.aprender(msg); nuevos.append(msg)
        
        if stats.get("viento_prom", 0) > 25:
            msg = "Vientos fuertes: " + str(round(stats["viento_prom"], 1)) + " nudos."
            self.aprender(msg); nuevos.append(msg)
        
        if stats.get("oleaje_prom", 0) > 2.5:
            msg = "Oleaje elevado: " + str(round(stats["oleaje_prom"], 1)) + "m."
            self.aprender(msg); nuevos.append(msg)
        
        for nombre, datos in stats["esclusas"].items():
            if datos["espera"] > 6:
                msg = "Esclusa " + nombre + " con " + str(datos["espera"]) + " barcos en espera."
                self.aprender(msg); nuevos.append(msg)
        
        return nuevos
    
    def barcos_ultimas_24h(self, df):
        ahora = datetime.now()
        historial = []
        for _, barco in df.iterrows():
            horas_atras = np.random.uniform(0, 24)
            timestamp = ahora - timedelta(hours=horas_atras)
            historial.append({
                "timestamp": timestamp.isoformat(),
                "nombre": barco["nombre"],
                "tipo": barco["tipo"],
                "direccion": barco["direccion"],
                "esclusa": barco["esclusa"],
                "velocidad": barco["velocidad"],
                "estado": barco["estado"]
            })
        historial.sort(key=lambda x: x["timestamp"], reverse=True)
        return historial
    
    def preguntar(self, pregunta, df, stats):
        p = pregunta.lower()
        self.logs.append({"timestamp": datetime.now().isoformat(), "accion": "pregunta", "datos": pregunta})
        
        # === PREGUNTAS ESPECÍFICAS POR ESLUSA ===
        esclusas_nombres = ["gatun", "pedro miguel", "miraflores"]
        for esclusa in esclusas_nombres:
            if esclusa in p and ("barco" in p or "pasando" in p or "que barco" in p):
                # Buscar barcos en esa esclusa específica
                df_esclusa = df[df["esclusa"].str.lower() == esclusa]
                if not df_esclusa.empty:
                    respuesta = "🚢 **Barcos en " + esclusa.title() + ":**\n\n"
                    for _, barco in df_esclusa.iterrows():
                        direc = "⬆️ Norte" if barco["direccion"] == "Norte" else "⬇️ Sur"
                        respuesta += "• **" + barco["nombre"] + "** - " + barco["tipo"] + " - " + direc + " - Vel: " + str(round(barco["velocidad"], 1)) + " nudos\n"
                    if len(df_esclusa) == 0:
                        respuesta = "No hay barcos en " + esclusa.title() + " en este momento."
                    return respuesta
                else:
                    return "No hay barcos en " + esclusa.title() + " en este momento."
        
        # === CLIMA, VIENTO, MAREA, PROFUNDIDAD ===
        if "clima" in p or "tiempo" in p:
            temp = stats.get("temperatura_prom", 25)
            viento = stats.get("viento_prom", 15)
            humedad = stats.get("humedad_prom", 70)
            return "🌤️ **Clima actual:**\n• Temperatura: " + str(round(temp, 1)) + "°C\n• Viento: " + str(round(viento, 1)) + " nudos\n• Humedad: " + str(round(humedad, 0)) + "%"
        
        if "viento" in p:
            viento = stats.get("viento_prom", 15)
            estado = "🌬️ Normal" if viento < 20 else "⚠️ Fuerte" if viento < 30 else "🔴 Muy fuerte"
            return "💨 **Viento:** " + str(round(viento, 1)) + " nudos - " + estado
        
        if "marea" in p:
            marea = stats.get("marea_prom", 2.5)
            return "🌊 **Marea:** " + str(round(marea, 1)) + " metros"
        
        if "profundidad" in p:
            prof = stats.get("profundidad_prom", 13.5)
            return "📏 **Profundidad promedio:** " + str(round(prof, 1)) + " metros"
        
        if "oleaje" in p:
            oleaje = stats.get("oleaje_prom", 1.0)
            estado = "🌊 Normal" if oleaje < 2 else "⚠️ Alto" if oleaje < 3 else "🔴 Muy alto"
            return "🌊 **Oleaje:** " + str(round(oleaje, 1)) + " metros - " + estado
        
        # === BARCOS QUE PASARON ===
        if "pas" in p and "barco" in p:
            historial = self.barcos_ultimas_24h(df)
            if historial:
                respuesta = "📋 **Barcos en las últimas 24h:**\n\n"
                for i, barco in enumerate(historial[:8]):
                    hora = barco["timestamp"][11:16]
                    direc = "⬆️ Norte" if barco["direccion"] == "Norte" else "⬇️ Sur"
                    respuesta += str(i+1) + ". **" + barco["nombre"] + "** - " + barco["tipo"] + " - " + direc + " - " + barco["esclusa"] + " (" + hora + ")\n"
                if len(historial) > 8:
                    respuesta += "\n... y " + str(len(historial) - 8) + " barcos más."
                return respuesta
            return "No hay registros de barcos en las últimas 24 horas."
        
        # === CWT ===
        if "cwt" in p:
            return "⏱️ **CWT actual:** " + str(round(stats["cwt"], 1)) + " horas - Nivel: " + stats["nivel"]
        
        # === BARCOS EN GENERAL ===
        if "barco" in p:
            return "🚢 **" + str(stats["total"]) + " barcos** activos. **" + str(stats["norte"]) + "** al Norte, **" + str(stats["sur"]) + "** al Sur."
        
        # === ESLUSCAS (TODAS) ===
        if "esclusa" in p and "todas" not in p:
            return self._respuesta_esclusas(stats)
        
        # === APRENDIZAJE ===
        if "aprender" in p or "enseñar" in p:
            return "🧠 Puedes enseñarme en la pestaña **Aprendizaje**. Yo aprendo automáticamente de los datos del Canal."
        
        return "🌊 He analizado tu consulta. El Canal tiene **" + str(stats["total"]) + " barcos** y CWT de **" + str(round(stats["cwt"], 1)) + "h**. ¿Necesitas información específica sobre barcos, esclusas, clima o mareas?"
    
    def _respuesta_esclusas(self, stats):
        partes = []
        for nombre, datos in stats["esclusas"].items():
            partes.append("**" + nombre + "**: " + str(datos["total"]) + " barcos, " + str(datos["espera"]) + " en espera")
        return "⚙️ " + " | ".join(partes)
    
    def generar_reporte(self, df, stats):
        lineas = []
        lineas.append("=" * 60)
        lineas.append("🌊 ANAYANSI - REPORTE COMPLETO DEL CANAL")
        lineas.append("=" * 60)
        lineas.append("Fecha: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
        lineas.append("")
        lineas.append("📊 RESUMEN OPERATIVO:")
        lineas.append("  Barcos activos: " + str(stats["total"]))
        lineas.append("  CWT: " + str(round(stats["cwt"], 1)) + " horas (" + stats["nivel"] + ")")
        lineas.append("  Velocidad promedio: " + str(round(stats["velocidad_prom"], 1)) + " nudos")
        lineas.append("  Barcos en espera: " + str(stats["espera"]))
        lineas.append("  Norte: " + str(stats["norte"]) + " | Sur: " + str(stats["sur"]))
        lineas.append("")
        lineas.append("🌤️ CLIMA Y MAR:")
        lineas.append("  Temperatura: " + str(round(stats.get("temperatura_prom", 25), 1)) + "°C")
        lineas.append("  Viento: " + str(round(stats.get("viento_prom", 15), 1)) + " nudos")
        lineas.append("  Marea: " + str(round(stats.get("marea_prom", 2.5), 1)) + "m")
        lineas.append("  Profundidad: " + str(round(stats.get("profundidad_prom", 13.5), 1)) + "m")
        lineas.append("  Oleaje: " + str(round(stats.get("oleaje_prom", 1.0), 1)) + "m")
        lineas.append("")
        lineas.append("⚙️ ESLUSCAS:")
        for nombre, datos in stats["esclusas"].items():
            lineas.append("  " + nombre + ": " + str(datos["total"]) + " barcos, " + str(datos["espera"]) + " en espera")
        lineas.append("")
        lineas.append("📋 TIPOS DE BARCOS:")
        for tipo, cantidad in stats["tipos"].items():
            lineas.append("  " + tipo + ": " + str(cantidad))
        lineas.append("")
        lineas.append("🧠 APRENDIZAJE:")
        lineas.append("  Registros: " + str(len(self.aprendizaje)))
        lineas.append("  Logs: " + str(len(self.logs)))
        lineas.append("")
        lineas.append("=" * 60)
        return "\n".join(lineas)

# ==========================================
# GENERAR DATOS COMPLETOS
# ==========================================

@st.cache_data(ttl=30)
def generar_datos():
    np.random.seed(int(time.time() / 30) % 1000)
    n = np.random.randint(50, 85)
    
    puntos = [
        (9.36, -79.92), (9.27, -79.92), (9.20, -79.88),
        (9.015, -79.62), (8.995, -79.585), (8.90, -79.52)
    ]
    
    tipos = ["Portacontenedores", "Granelero", "Petrolero", "Gasero", "Carguero", "Crucero", "Remolcador", "Pesquero"]
    estados = ["Navegando", "Navegando", "Navegando", "En espera en esclusa", "Entrando a esclusa"]
    esclusas = ["Gatun", "Pedro Miguel", "Miraflores"]
    prioridades = ["Alta", "Media", "Baja"]
    
    barcos = []
    for i in range(n):
        idx = np.random.randint(0, len(puntos))
        lat, lon = puntos[idx]
        lat = lat + np.random.normal(0, 0.02)
        lon = lon + np.random.normal(0, 0.02)
        direccion = "Sur" if np.random.random() < 0.5 else "Norte"
        estado = random.choice(estados)
        velocidad = np.random.uniform(0, 1) if estado == "En espera en esclusa" else np.random.uniform(4, 16)
        barco = {
            "nombre": "BARCO_" + str(i+1).zfill(4),
            "tipo": random.choice(tipos),
            "direccion": direccion,
            "lat": lat,
            "lon": lon,
            "velocidad": velocidad,
            "estado": estado,
            "esclusa": random.choice(esclusas),
            "eta_horas": np.random.uniform(0.5, 8),
            "origen": random.choice(["Asia", "Europa", "America", "Africa"]),
            "destino": random.choice(["Asia", "Europa", "America", "Africa"]),
            "prioridad": random.choice(prioridades),
            "carga": round(np.random.uniform(100, 10000), 0),
            "eslora": round(np.random.uniform(80, 400), 0),
            "calado": round(np.random.uniform(8, 18), 1)
        }
        barcos.append(barco)
    return pd.DataFrame(barcos)

# ==========================================
# ANÁLISIS
# ==========================================

def analizar(df):
    stats = {
        "total": len(df),
        "norte": len(df[df["direccion"] == "Norte"]),
        "sur": len(df[df["direccion"] == "Sur"]),
        "espera": len(df[df["estado"] == "En espera en esclusa"]),
        "prioridad_alta": len(df[df["prioridad"] == "Alta"]),
        "velocidad_prom": df["velocidad"].mean(),
        "esclusas": {},
        "tipos": df["tipo"].value_counts().to_dict(),
        # Datos climáticos y marítimos
        "temperatura_prom": 25 + np.random.normal(0, 3),
        "viento_prom": np.random.uniform(5, 30),
        "humedad_prom": 70 + np.random.normal(0, 10),
        "profundidad_prom": 13.5 + np.random.normal(0, 0.5),
        "marea_prom": 2.5 + np.random.normal(0, 0.3),
        "oleaje_prom": 1.0 + np.random.normal(0, 0.3)
    }
    
    for e in ["Gatun", "Pedro Miguel", "Miraflores"]:
        df_e = df[df["esclusa"] == e]
        stats["esclusas"][e] = {
            "total": len(df_e),
            "espera": len(df_e[df_e["estado"] == "En espera en esclusa"])
        }
    
    stats["cwt"] = 12 + max(0, (stats["total"] - 30) * 0.1) + stats["espera"] * 0.12
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
# INICIALIZAR
# ==========================================

if "anayansi" not in st.session_state:
    st.session_state.anayansi = AnayansiIA()
    st.session_state.chat = [{"rol": "anayansi", "msg": "🌊 ¡Hola! Soy **Anayansi**, la sabiduría del mar.\n\nPuedo responder preguntas como:\n• ¿Qué barcos están en Miraflores?\n• ¿Cómo está el clima y el viento?\n• ¿Cuál es la marea y profundidad?\n• ¿Qué barcos pasaron en las últimas 24h?\n• ¿Cómo está el CWT y la congestión?\n\nTambién aprendo automáticamente de los datos del Canal. ¿Qué necesitas saber?"}]
    st.session_state.datos_inicializados = True

anayansi = st.session_state.anayansi

df = generar_datos()
stats = analizar(df)

# Aprendizaje automático
nuevos_aprendizajes = anayansi.aprender_automaticamente(df, stats)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0;">
        <div style="font-size:3rem;">🌊</div>
        <div style="color:#00b4d8; font-family: 'Orbitron', sans-serif; font-size:1.2rem; font-weight:700;">ANAYANSI</div>
        <div style="color:#475569; font-size:0.7rem;">Sabiduría del mar</div>
        <div style="color:#475569; font-size:0.7rem;">v4.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    col1.metric("🚢 Barcos", stats["total"])
    col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
    
    st.markdown("---")
    
    st.markdown(f"""
    <div style="background:rgba(15,23,42,0.8); border-radius:12px; padding:15px; border:1px solid #1e293b;">
        <div style="color:#10b981;">● Sistema Activo</div>
        <div style="color:#64748b; font-size:0.75rem;">🧠 Aprendizaje automático: Activo</div>
        <div style="color:#64748b; font-size:0.75rem;">📚 Registros: {len(anayansi.aprendizaje)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if nuevos_aprendizajes:
        st.info(f"🧠 {len(nuevos_aprendizajes)} nuevos aprendizajes")
    
    st.markdown("---")
    
    if st.button("🔄 Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# CONTENIDO PRINCIPAL
# ==========================================

st.markdown('<div class="main-header">🌊 ANAYANSI - Canal Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">"Sabiduría del mar" - IA con Aprendizaje Automático</div>', unsafe_allow_html=True)

# ==========================================
# KPIS
# ==========================================

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("🚢 Barcos", stats["total"])
col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
col3.metric("📈 Velocidad", f"{stats['velocidad_prom']:.1f}")
col4.metric("⏳ Espera", stats["espera"])
col5.metric("⭐ Alta", stats["prioridad_alta"])
col6.metric("🌊 Oleaje", f"{stats['oleaje_prom']:.1f}m")

st.markdown("---")

# ==========================================
# CLIMA Y MAR - TARJETAS
# ==========================================

st.markdown("#### 🌤️ Condiciones Climáticas y Marítimas")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="weather-card">
        <div class="weather-icon">🌡️</div>
        <div class="weather-value">{stats['temperatura_prom']:.1f}°C</div>
        <div class="weather-label">Temperatura</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    viento_icon = "💨" if stats['viento_prom'] < 20 else "🌪️"
    st.markdown(f"""
    <div class="weather-card">
        <div class="weather-icon">{viento_icon}</div>
        <div class="weather-value">{stats['viento_prom']:.1f}</div>
        <div class="weather-label">Viento (nudos)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="weather-card">
        <div class="weather-icon">🌊</div>
        <div class="weather-value">{stats['marea_prom']:.1f}m</div>
        <div class="weather-label">Marea</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="weather-card">
        <div class="weather-icon">📏</div>
        <div class="weather-value">{stats['profundidad_prom']:.1f}m</div>
        <div class="weather-label">Profundidad</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    oleaje_icon = "🌊" if stats['oleaje_prom'] < 2 else "🌊⚠️"
    st.markdown(f"""
    <div class="weather-card">
        <div class="weather-icon">{oleaje_icon}</div>
        <div class="weather-value">{stats['oleaje_prom']:.1f}m</div>
        <div class="weather-label">Oleaje</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# CONGESTIÓN Y ESLUSCAS
# ==========================================

st.markdown("#### 📊 Nivel de Congestión")
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown(f"<h1 style='color:{stats['color']}; text-align:center;'>{stats['nivel']}</h1>", unsafe_allow_html=True)
with col2:
    st.progress(min(stats["cwt"] / 30, 1.0))

st.markdown("---")

st.markdown("#### ⚙️ Esclusas")
c1, c2, c3 = st.columns(3)
for col, (nombre, datos) in zip([c1, c2, c3], stats["esclusas"].items()):
    with col:
        st.markdown(f"""
        <div class="esclusa-card">
            <h4 style="color:#e2e8f0;">⚙️ {nombre}</h4>
            <hr style="border-color:#1e293b;">
            <div>🚢 Total: <strong>{datos['total']}</strong></div>
            <div>⏳ Espera: <strong>{datos['espera']}</strong></div>
            <div style="color:{'#10b981' if datos['espera'] < 4 else '#f59e0b' if datos['espera'] < 8 else '#ef4444'};">
                {'✅ Fluido' if datos['espera'] < 4 else '🟡 Moderado' if datos['espera'] < 8 else '🔴 Congestionado'}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# PESTAÑAS
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Mapa", "📈 Análisis", "💬 Chat", "🧠 Aprendizaje", "📋 Datos"
])

# TAB 1: MAPA
with tab1:
    st.markdown("### 🗺️ Mapa de Navegación")
    st.caption("🟢 Barcos con prioridad baja | 🟡 Media | 🔴 Alta")
    
    fig = px.scatter_mapbox(
        df, lat="lat", lon="lon",
        hover_name="nombre",
        hover_data={
            "tipo": True, "direccion": True, "estado": True,
            "velocidad": ":.1f", "esclusa": True, "eta_horas": ":.1f",
            "eslora": True, "calado": True
        },
        color="prioridad",
        color_discrete_map={"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"},
        size="velocidad", size_max=16, zoom=9, height=550
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 9.15, "lon": -79.75},
        margin={"r":0, "t":0, "l":0, "b":0},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: ANÁLISIS
with tab2:
    st.markdown("### 📈 Análisis")
    col1, col2 = st.columns(2)
    with col1:
        tipos_df = pd.DataFrame({"Tipo": list(stats["tipos"].keys()), "Cantidad": list(stats["tipos"].values())})
        fig = px.bar(tipos_df, x="Tipo", y="Cantidad", color="Cantidad", color_continuous_scale="Viridis")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("CWT Promedio", f"{stats['cwt']:.1f}h")
        st.metric("Velocidad Promedio", f"{stats['velocidad_prom']:.1f} nudos")
        st.metric("Barcos en Espera", stats["espera"])
        st.metric("Prioridad Alta", stats["prioridad_alta"])

# TAB 3: CHAT
with tab3:
    st.markdown("### 💬 Chat con Anayansi")
    st.caption("💡 Pregunta sobre barcos, esclusas, clima, viento, marea o profundidad")
    
    for msg in st.session_state.chat:
        if msg["rol"] == "anayansi":
            st.markdown(f'<div class="chat-message-anayansi">🌊 Anayansi: {msg["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">👤 Tú: {msg["msg"]}</div>', unsafe_allow_html=True)
    
    pregunta = st.text_input("Pregunta a Anayansi:", placeholder="Ej: ¿Qué barcos están en Miraflores?")
    if pregunta:
        st.session_state.chat.append({"rol": "usuario", "msg": pregunta})
        respuesta = anayansi.preguntar(pregunta, df, stats)
        st.session_state.chat.append({"rol": "anayansi", "msg": respuesta})
        st.rerun()
    
    if st.button("🗑️ Limpiar chat"):
        st.session_state.chat = [{"rol": "anayansi", "msg": "🌊 ¡Hola! Soy Anayansi. ¿Qué necesitas saber sobre el Canal?"}]
        st.rerun()

# TAB 4: APRENDIZAJE
with tab4:
    st.markdown("### 🧠 Aprendizaje de Anayansi")
    st.markdown("Anayansi aprende automáticamente de los datos del Canal")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📚 Registros", len(anayansi.aprendizaje))
        st.metric("📝 Logs", len(anayansi.logs))
        st.metric("🧠 Aprendizaje automático", "✅ Activo")
    with col2:
        st.markdown("#### 📝 Últimos aprendizajes")
        if anayansi.aprendizaje:
            for item in anayansi.aprendizaje[-5:]:
                st.caption(f"📅 {item['fecha'][:16]}")
                st.caption(f"📝 {item['texto'][:80]}...")
                st.markdown("---")
        else:
            st.info("Aún no hay registros")
    
    st.markdown("---")
    st.markdown("#### 🧠 Enseñar a Anayansi (opcional)")
    nuevo = st.text_area("¿Qué quieres que Anayansi aprenda?")
    if st.button("📚 Enseñar") and nuevo:
        resultado = anayansi.aprender(nuevo)
        st.success(resultado)
        st.rerun()

# TAB 5: DATOS
with tab5:
    st.markdown("### 📋 Datos de Barcos")
    
    display_df = df[["nombre", "direccion", "tipo", "estado", "esclusa", "velocidad", "eta_horas", "prioridad", "eslora", "calado", "carga"]].copy()
    display_df["velocidad"] = display_df["velocidad"].round(1)
    display_df["eta_horas"] = display_df["eta_horas"].round(1)
    display_df["eslora"] = display_df["eslora"].round(0)
    display_df["calado"] = display_df["calado"].round(1)
    display_df["direccion"] = display_df["direccion"].apply(lambda x: "⬆️ Norte" if x == "Norte" else "⬇️ Sur")
    display_df.columns = ["Nombre", "Dirección", "Tipo", "Estado", "Esclusa", "Velocidad", "ETA (h)", "Prioridad", "Eslora (m)", "Calado (m)", "Carga (t)"]
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar Datos (CSV)", data=csv, file_name="canal_datos.csv", mime="text/csv")
    with col2:
        reporte = anayansi.generar_reporte(df, stats)
        st.download_button("📄 Descargar Reporte (TXT)", data=reporte, file_name="reporte_canal.txt", mime="text/plain")

# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    🌊 ANAYANSI - Canal Predictor v4.0 | Sabiduría del mar | Aprendizaje Automático
</div>
""", unsafe_allow_html=True)
