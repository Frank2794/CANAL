import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
import json
from collections import defaultdict

st.set_page_config(
    page_title="ANAYANSI - IA Avanzada",
    page_icon="🧠",
    layout="wide"
)

# ==========================================
# ESTILOS
# ==========================================

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 900; color: #00b4d8; }
    .sub-header { font-size: 0.9rem; color: #94a3b8; margin-top: -5px; }
    .metric-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 12px; }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: white; }
    .metric-label { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; }
    .chat-ai { background: rgba(0,150,255,0.1); border-left: 3px solid #00b4d8; padding: 10px; border-radius: 8px; margin: 6px 0; color: #e2e8f0; font-size: 0.9rem; }
    .chat-user { background: rgba(15,23,42,0.8); border-left: 3px solid #64748b; padding: 10px; border-radius: 8px; margin: 6px 0; color: #94a3b8; font-size: 0.9rem; }
    .insight-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; margin: 5px 0; }
    .footer { text-align: center; color: #475569; padding: 10px 0; border-top: 1px solid #1e293b; margin-top: 15px; font-size: 0.65rem; }
    div.stButton > button { background: #00b4d8; color: white; border-radius: 8px; border: none; padding: 0.3rem 1rem; font-size: 0.8rem; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 6px 12px; }
    .stTabs [aria-selected="true"] { background: #00b4d8; color: white; border-radius: 6px; }
    .esclusa-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; }
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
        self.memoria_conversaciones = []
        self.patrones = defaultdict(list)
        self.predicciones = []
        self.razonamiento = []
        self.confianza = 0.85
    
    def recordar(self, mensaje):
        self.memoria_conversaciones.append({
            "timestamp": datetime.now().isoformat(),
            "mensaje": mensaje
        })
        if len(self.memoria_conversaciones) > 100:
            self.memoria_conversaciones = self.memoria_conversaciones[-100:]
    
    def aprender(self, texto):
        self.aprendizaje.append({"fecha": datetime.now().isoformat(), "texto": texto})
        self.logs.append({"timestamp": datetime.now().isoformat(), "accion": "aprendizaje", "datos": texto})
        return "✅ Anayansi ha aprendido: " + texto[:50] + "..."
    
    def aprender_automaticamente(self, df, stats):
        nuevos = []
        if stats["total"] > 60:
            msg = "Alto tráfico detectado: " + str(stats["total"]) + " barcos activos."
            self.aprender(msg); nuevos.append(msg)
        if stats["cwt"] > 20:
            msg = "CWT crítico: " + str(round(stats["cwt"], 1)) + " horas."
            self.aprender(msg); nuevos.append(msg)
        elif stats["cwt"] > 15:
            msg = "CWT elevado: " + str(round(stats["cwt"], 1)) + " horas."
            self.aprender(msg); nuevos.append(msg)
        for nombre, datos in stats["esclusas"].items():
            if datos["espera"] > 6:
                msg = "Congestión en " + nombre + ": " + str(datos["espera"]) + " barcos en espera."
                self.aprender(msg); nuevos.append(msg)
        if stats.get("viento", 0) > 25:
            msg = "Vientos fuertes: " + str(round(stats["viento"], 1)) + " nudos."
            self.aprender(msg); nuevos.append(msg)
        if stats.get("oleaje", 0) > 2.5:
            msg = "Oleaje elevado: " + str(round(stats["oleaje"], 1)) + " metros."
            self.aprender(msg); nuevos.append(msg)
        return nuevos
    
    def predecir_congestion(self, df, stats):
        riesgo = 0
        if stats["total"] > 50: riesgo += 30
        if stats["espera"] > 8: riesgo += 25
        if stats["cwt"] > 18: riesgo += 20
        if stats.get("viento", 0) > 20: riesgo += 15
        if stats.get("oleaje", 0) > 2: riesgo += 10
        
        if riesgo > 70:
            nivel = "🔴 Alto"
            mensaje = "Se espera congestión significativa en las próximas horas."
        elif riesgo > 40:
            nivel = "🟡 Moderado"
            mensaje = "Posible congestión en las próximas horas."
        else:
            nivel = "🟢 Bajo"
            mensaje = "Tráfico fluido esperado."
        
        return [{
            "nivel": nivel,
            "mensaje": mensaje,
            "riesgo": riesgo,
            "factores": {
                "barcos": stats["total"],
                "espera": stats["espera"],
                "cwt": stats["cwt"],
                "viento": stats.get("viento", 0),
                "oleaje": stats.get("oleaje", 0)
            }
        }]
    
    def razonar(self, pregunta, df, stats):
        p = pregunta.lower()
        ideas = []
        if "clima" in p or "viento" in p:
            if stats.get("viento", 0) > 20:
                ideas.append("🌪️ Vientos fuertes pueden afectar la navegación.")
                if stats["total"] > 40:
                    ideas.append("⚠️ Combinación de vientos fuertes y tráfico denso requiere precaución.")
        if "esclusa" in p or "espera" in p:
            espera_total = sum([d["espera"] for d in stats["esclusas"].values()])
            if espera_total > 15:
                ideas.append("⏳ Alta congestión en esclusas. Tiempos de espera prolongados.")
            elif espera_total > 8:
                ideas.append("⏳ Congestión moderada en esclusas.")
        if "cwt" in p:
            if stats["cwt"] > 20:
                ideas.append("⏱️ CWT crítico. El Canal está operando al límite.")
                ideas.append("📊 " + str(stats["total"]) + " barcos activos contribuyen a la congestión.")
        if not ideas:
            ideas.append("🧠 He analizado tu consulta. No encuentro conexiones adicionales relevantes.")
        return "\n".join(ideas)
    
    def barcos_ultimas_24h(self, df):
        ahora = datetime.now()
        historial = []
        for _, b in df.iterrows():
            horas = np.random.uniform(0, 24)
            ts = ahora - timedelta(hours=horas)
            historial.append({
                "timestamp": ts.isoformat(),
                "nombre": b["nombre"],
                "tipo": b["tipo"],
                "direccion": b["direccion"],
                "esclusa": b["esclusa"],
                "velocidad": b["velocidad"]
            })
        historial.sort(key=lambda x: x["timestamp"], reverse=True)
        return historial
    
    def preguntar(self, pregunta, df, stats):
        p = pregunta.lower()
        self.logs.append({"timestamp": datetime.now().isoformat(), "accion": "pregunta", "datos": pregunta})
        self.recordar(pregunta)
        
        for _, barco in df.iterrows():
            self.historial_barcos.append({
                "timestamp": datetime.now().isoformat(),
                "nombre": barco["nombre"],
                "velocidad": barco["velocidad"],
                "direccion": barco["direccion"],
                "esclusa": barco["esclusa"]
            })
            if len(self.historial_barcos) > 100:
                self.historial_barcos = self.historial_barcos[-100:]
        
        for esclusa in ["gatun", "pedro miguel", "miraflores"]:
            if esclusa in p and ("barco" in p or "pasando" in p):
                df_e = df[df["esclusa"].str.lower() == esclusa]
                if not df_e.empty:
                    respuesta = "🚢 **Barcos en " + esclusa.title() + ":**\n\n"
                    for _, b in df_e.iterrows():
                        dir = "⬆️ Norte" if b["direccion"] == "Norte" else "⬇️ Sur"
                        respuesta += "• **" + b["nombre"] + "** - " + b["tipo"] + " - " + dir + " (" + str(round(b["velocidad"], 1)) + " nudos)\n"
                    datos_esclusa = stats["esclusas"].get(esclusa.title(), {})
                    if datos_esclusa.get("espera", 0) > 5:
                        respuesta += "\n💡 **Insight:** Esta esclusa tiene " + str(datos_esclusa["espera"]) + " barcos en espera. Posible demora."
                    return respuesta
                return "No hay barcos en " + esclusa.title() + " en este momento."
        
        if "predecir" in p or "futuro" in p or "congestion" in p:
            predicciones = self.predecir_congestion(df, stats)
            if predicciones:
                pred = predicciones[0]
                respuesta = "🔮 **Predicción de congestión:**\n\n"
                respuesta += "• Nivel: " + pred["nivel"] + "\n"
                respuesta += "• " + pred["mensaje"] + "\n"
                respuesta += "• Riesgo: " + str(pred["riesgo"]) + "%\n\n"
                respuesta += "📊 **Factores:**\n"
                respuesta += "• Barcos: " + str(pred["factores"]["barcos"]) + "\n"
                respuesta += "• En espera: " + str(pred["factores"]["espera"]) + "\n"
                respuesta += "• CWT: " + str(round(pred["factores"]["cwt"], 1)) + "h"
                return respuesta
        
        if "por que" in p or "explica" in p or "razon" in p:
            return "🧠 **Razonamiento:**\n\n" + self.razonar(pregunta, df, stats)
        
        if "clima" in p or "viento" in p:
            return "🌤️ **Clima:**\n• Temp: " + str(round(stats.get("temp", 25), 1)) + "°C\n• Viento: " + str(round(stats.get("viento", 15), 1)) + " nudos\n• Humedad: " + str(round(stats.get("humedad", 70), 0)) + "%"
        
        if "marea" in p:
            return "🌊 **Marea:** " + str(round(stats.get("marea", 2.5), 1)) + "m"
        
        if "profundidad" in p:
            return "📏 **Profundidad:** " + str(round(stats.get("profundidad", 13.5), 1)) + "m"
        
        if "oleaje" in p:
            return "🌊 **Oleaje:** " + str(round(stats.get("oleaje", 1.0), 1)) + "m"
        
        if "pas" in p and "barco" in p:
            historial = self.barcos_ultimas_24h(df)
            if historial:
                respuesta = "📋 **Últimos 24h:**\n\n"
                for i, b in enumerate(historial[:6]):
                    hora = b["timestamp"][11:16]
                    dir = "⬆️" if b["direccion"] == "Norte" else "⬇️"
                    respuesta += str(i+1) + ". " + b["nombre"] + " " + dir + " (" + hora + ")\n"
                return respuesta
            return "No hay registros."
        
        if "cwt" in p:
            return "⏱️ **CWT:** " + str(round(stats["cwt"], 1)) + "h - " + stats["nivel"]
        
        if "barco" in p:
            return "🚢 **" + str(stats["total"]) + " barcos**\n⬆️ " + str(stats["norte"]) + " Norte\n⬇️ " + str(stats["sur"]) + " Sur"
        
        if "esclusa" in p:
            return "⚙️ " + " | ".join([n + ": " + str(d["total"]) + " barcos" for n, d in stats["esclusas"].items()])
        
        if "aprender" in p or "enseñar" in p:
            return "🧠 Puedes enseñarme en la pestaña **Aprendizaje**."
        
        return "🌊 " + str(stats["total"]) + " barcos | CWT: " + str(round(stats["cwt"], 1)) + "h | " + stats["nivel"]
    
    def generar_reporte(self, df, stats):
        lineas = []
        lineas.append("=" * 50)
        lineas.append("ANAYANSI - REPORTE INTELIGENTE")
        lineas.append("=" * 50)
        lineas.append(datetime.now().strftime("%Y-%m-%d %H:%M"))
        lineas.append("")
        lineas.append("📊 OPERATIVO:")
        lineas.append("  Barcos: " + str(stats["total"]))
        lineas.append("  CWT: " + str(round(stats["cwt"], 1)) + "h - " + stats["nivel"])
        lineas.append("  Velocidad: " + str(round(stats["velocidad_prom"], 1)) + " nudos")
        lineas.append("  Espera: " + str(stats["espera"]))
        lineas.append("  Norte: " + str(stats["norte"]) + " | Sur: " + str(stats["sur"]))
        lineas.append("")
        lineas.append("⚙️ ESLUSCAS:")
        for n, d in stats["esclusas"].items():
            estado = "✅" if d["espera"] < 4 else "🟡" if d["espera"] < 8 else "🔴"
            lineas.append("  " + n + ": " + str(d["total"]) + " barcos " + estado)
        lineas.append("")
        lineas.append("🌤️ CLIMA:")
        lineas.append("  Temp: " + str(round(stats.get("temp", 25), 1)) + "°C")
        lineas.append("  Viento: " + str(round(stats.get("viento", 15), 1)) + " nudos")
        lineas.append("  Marea: " + str(round(stats.get("marea", 2.5), 1)) + "m")
        lineas.append("  Oleaje: " + str(round(stats.get("oleaje", 1.0), 1)) + "m")
        lineas.append("")
        lineas.append("🧠 APRENDIZAJE:")
        lineas.append("  Registros: " + str(len(self.aprendizaje)))
        lineas.append("  Memoria: " + str(len(self.memoria_conversaciones)) + " conversaciones")
        lineas.append("  Confianza: " + str(int(self.confianza * 100)) + "%")
        lineas.append("")
        lineas.append("=" * 50)
        return "\n".join(lineas)

# ==========================================
# GENERAR DATOS - CON COLUMNAS COMPLETAS
# ==========================================

@st.cache_data(ttl=60)
def generar_datos():
    np.random.seed(int(time.time() / 60) % 1000)
    n = np.random.randint(35, 55)
    
    puntos = [
        (9.36, -79.92), (9.27, -79.92), (9.20, -79.88),
        (9.015, -79.62), (8.995, -79.585), (8.90, -79.52)
    ]
    
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
# ANALISIS
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
    """Crea un mapa interactivo con más información"""
    
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
    
    # Agregar esclusas como marcadores especiales
    esclusas_coords = {
        "Gatún": {"lat": 9.27, "lon": -79.92},
        "Pedro Miguel": {"lat": 9.015, "lon": -79.62},
        "Miraflores": {"lat": 8.995, "lon": -79.585}
    }
    
    for nombre, coords in esclusas_coords.items():
        fig.add_scatter_mapbox(
            lat=[coords["lat"]],
            lon=[coords["lon"]],
            mode="markers",
            marker=dict(size=20, color="red", symbol="triangle-up"),
            name="⚙️ " + nombre,
            hoverinfo="text",
            hovertext=["⚙️ Esclusa de " + nombre]
        )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 9.15, "lon": -79.75},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# ==========================================
# INICIALIZAR
# ==========================================

if "anayansi" not in st.session_state:
    st.session_state.anayansi = AnayansiIA()
    st.session_state.chat = [{"rol": "anayansi", "msg": "🧠 ¡Hola! Soy **Anayansi**, la sabiduría del mar.\n\n**¿Qué puedo hacer?**\n• 🔮 **Predecir** congestión futura\n• 🧠 **Razonar** conectando información\n• 📊 **Analizar** patrones y tendencias\n• 💬 **Recordar** conversaciones anteriores\n• 🌊 **Responder** sobre barcos, esclusas, clima"}]
    st.session_state.df = None
    st.session_state.stats = None

anayansi = st.session_state.anayansi

if st.session_state.df is None:
    st.session_state.df = generar_datos()
    st.session_state.stats = analizar(st.session_state.df)
    st.session_state.nuevos_aprendizajes = anayansi.aprender_automaticamente(st.session_state.df, st.session_state.stats)

df = st.session_state.df
stats = st.session_state.stats

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("### 🧠 ANAYANSI")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    col1.metric("🚢", stats["total"])
    col2.metric("⏱️", f"{stats['cwt']:.1f}h")
    
    st.markdown("---")
    st.caption("🧠 Confianza: " + str(int(anayansi.confianza * 100)) + "%")
    st.caption("📚 Aprendizaje: " + str(len(anayansi.aprendizaje)) + " registros")
    st.caption("💬 Memoria: " + str(len(anayansi.memoria_conversaciones)) + " mensajes")
    
    st.markdown("---")
    
    if st.button("🔄 Actualizar"):
        st.cache_data.clear()
        st.session_state.df = None
        st.session_state.stats = None
        st.rerun()

# ==========================================
# CONTENIDO PRINCIPAL
# ==========================================

st.markdown('<div class="main-header">🧠 ANAYANSI - IA Avanzada</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sabiduría del mar - Aprendizaje, Razonamiento y Predicción</div>', unsafe_allow_html=True)

# ==========================================
# KPIS
# ==========================================

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("🚢 Barcos", stats["total"])
col2.metric("⏱️ CWT", f"{stats['cwt']:.1f}h")
col3.metric("📈 Vel.", f"{stats['velocidad_prom']:.1f}")
col4.metric("⏳ Espera", stats["espera"])
col5.metric("⭐ Alta", stats["prioridad_alta"])
col6.metric("🌊 Oleaje", f"{stats['oleaje']:.1f}m")

st.markdown("---")

# ==========================================
# PREDICCIONES Y RAZONAMIENTO
# ==========================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔮 Predicción de Congestión")
    predicciones = anayansi.predecir_congestion(df, stats)
    if predicciones:
        pred = predicciones[0]
        st.markdown(f"""
        <div class="insight-card">
            <div style="font-size:1.2rem; font-weight:700;">{pred['nivel']}</div>
            <div>{pred['mensaje']}</div>
            <div style="margin-top:5px; color:#94a3b8; font-size:0.8rem;">
                Riesgo: {pred['riesgo']}% | Basado en {pred['factores']['barcos']} barcos, CWT {round(pred['factores']['cwt'], 1)}h
            </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 🌤️ Clima y Mar")
    st.markdown(f"""
    <div class="insight-card">
        <div>🌡️ Temperatura: <strong>{stats['temp']:.1f}°C</strong></div>
        <div>💨 Viento: <strong>{stats['viento']:.1f}</strong> nudos</div>
        <div>🌊 Marea: <strong>{stats['marea']:.1f}m</strong></div>
        <div>📏 Profundidad: <strong>{stats['profundidad']:.1f}m</strong></div>
        <div>🌊 Oleaje: <strong>{stats['oleaje']:.1f}m</strong></div>
    </div>
    """, unsafe_allow_html=True)

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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🗺️ Mapa", "📊 Análisis", "💬 Chat IA", "🧠 Aprendizaje", "📋 Datos", "📈 Insights"])

# TAB 1: MAPA MEJORADO
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
        tipos_df = pd.DataFrame({"Tipo": list(stats["tipos"].keys()), "Cantidad": list(stats["tipos"].values())})
        fig = px.bar(tipos_df, x="Tipo", y="Cantidad", color="Cantidad", color_continuous_scale="Viridis")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("CWT", f"{stats['cwt']:.1f}h")
        st.metric("Velocidad", f"{stats['velocidad_prom']:.1f} nudos")
        st.metric("Espera", stats["espera"])
        st.metric("Prioridad Alta", stats["prioridad_alta"])

# TAB 3: CHAT IA
with tab3:
    st.markdown("### 💬 Chat con Anayansi")
    st.caption("💡 Pregunta: barcos en Gatun, predice congestion, explica el CWT, clima")
    
    for msg in st.session_state.chat:
        if msg["rol"] == "anayansi":
            st.markdown(f'<div class="chat-ai">🧠 Anayansi: {msg["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">👤 Tú: {msg["msg"]}</div>', unsafe_allow_html=True)
    
    pregunta = st.text_input("Pregunta a Anayansi:", placeholder="¿Qué barcos están en Miraflores?")
    if pregunta:
        st.session_state.chat.append({"rol": "usuario", "msg": pregunta})
        respuesta = anayansi.preguntar(pregunta, df, stats)
        st.session_state.chat.append({"rol": "anayansi", "msg": respuesta})
        st.rerun()
    
    if st.button("🗑️ Limpiar"):
        st.session_state.chat = [{"rol": "anayansi", "msg": "🧠 Hola! Soy Anayansi. Puedo predecir congestión, razonar sobre datos y aprender. ¿Qué necesitas saber?"}]
        st.rerun()

# TAB 4: APRENDIZAJE
with tab4:
    st.markdown("### 🧠 Aprendizaje")
    st.caption("Anayansi aprende automáticamente y guarda todo en memoria")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📚 Registros", len(anayansi.aprendizaje))
        st.metric("💬 Memoria", str(len(anayansi.memoria_conversaciones)) + " mensajes")
        st.metric("🧠 Confianza", str(int(anayansi.confianza * 100)) + "%")
    with col2:
        st.markdown("#### 📝 Últimos aprendizajes")
        if anayansi.aprendizaje:
            for item in anayansi.aprendizaje[-4:]:
                st.caption(f"📅 {item['fecha'][:16]}")
                st.caption(f"📝 {item['texto'][:60]}...")
                st.markdown("---")
        else:
            st.info("Aún no hay registros")
    
    st.markdown("---")
    st.markdown("#### 🧠 Enseñar a Anayansi")
    nuevo = st.text_area("¿Qué quieres que aprenda?")
    if st.button("📚 Enseñar") and nuevo:
        st.success(anayansi.aprender(nuevo))
        st.rerun()

# TAB 5: DATOS
with tab5:
    st.markdown("### 📋 Datos")
    
    display_df = df[["nombre", "direccion", "tipo", "estado", "esclusa", "velocidad", "eta_horas", "prioridad", "eslora", "calado", "carga"]].copy()
    display_df["velocidad"] = display_df["velocidad"].round(1)
    display_df["eta_horas"] = display_df["eta_horas"].round(1)
    display_df["eslora"] = display_df["eslora"].round(0)
    display_df["calado"] = display_df["calado"].round(1)
    display_df["carga"] = display_df["carga"].round(0)
    display_df["direccion"] = display_df["direccion"].apply(lambda x: "⬆️ Norte" if x == "Norte" else "⬇️ Sur")
    display_df.columns = ["Nombre", "Dir", "Tipo", "Estado", "Esclusa", "Vel", "ETA (h)", "Prioridad", "Eslora (m)", "Calado (m)", "Carga (t)"]
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 CSV", data=csv, file_name="canal_datos.csv", mime="text/csv")
    with col2:
        reporte = anayansi.generar_reporte(df, stats)
        st.download_button("📄 Reporte IA", data=reporte, file_name="reporte_ia.txt", mime="text/plain")

# TAB 6: INSIGHTS
with tab6:
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
    
    st.markdown("#### 📊 Estadísticas de IA")
    col1, col2, col3 = st.columns(3)
    col1.metric("🧠 Confianza", str(int(anayansi.confianza * 100)) + "%")
    col2.metric("📚 Aprendizajes", len(anayansi.aprendizaje))
    col3.metric("💬 Interacciones", len(anayansi.memoria_conversaciones))
    
    st.markdown("---")
    st.caption("💡 Anayansi mejora con cada interacción. Mientras más converses, más inteligente se vuelve.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    🧠 ANAYANSI - IA Avanzada | Aprendizaje, Razonamiento y Predicción
</div>
""", unsafe_allow_html=True)
