# ==========================================
# DESCARGAR APP.PY PARA SUBIR A STREAMLIT CLOUD
# ==========================================

from google.colab import files

# Guardar la versión final
with open('app.py', 'w') as f:
    f.write('''
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import random
import time

st.set_page_config(
    page_title="ANAYANSI - Canal Predictor",
    page_icon="🌊",
    layout="wide"
)

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 900; color: #00b4d8; }
    .sub-header { font-size: 1rem; color: #94a3b8; margin-top: -8px; }
    .metric-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; }
    .metric-value { font-size: 2rem; font-weight: 700; color: white; }
    .metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; }
    .chat-ai { background: rgba(0,150,255,0.1); border-left: 3px solid #00b4d8; padding: 12px; border-radius: 8px; margin: 8px 0; color: #e2e8f0; }
    .chat-user { background: rgba(15,23,42,0.8); border-left: 3px solid #64748b; padding: 12px; border-radius: 8px; margin: 8px 0; color: #94a3b8; }
    .footer { text-align: center; color: #475569; padding: 20px 0; border-top: 1px solid #1e293b; margin-top: 20px; }
    div.stButton > button { background: #00b4d8; color: white; border-radius: 10px; border: none; padding: 0.5rem 1.5rem; }
</style>
""", unsafe_allow_html=True)

class AnayansiIA:
    def __init__(self):
        self.aprendizaje = []
    
    def aprender(self, texto):
        self.aprendizaje.append({"fecha": datetime.now().isoformat(), "texto": texto})
        return "Anayansi ha aprendido: " + texto[:50] + "..."
    
    def preguntar(self, pregunta, df, stats):
        p = pregunta.lower()
        if "cwt" in p:
            return "El CWT actual es de " + str(round(stats["cwt"], 1)) + " horas."
        if "barco" in p:
            return "Hay " + str(stats["total"]) + " barcos. " + str(stats["norte"]) + " al Norte y " + str(stats["sur"]) + " al Sur."
        if "espera" in p:
            return "Hay " + str(stats["espera"]) + " barcos en espera."
        if "velocidad" in p:
            return "Velocidad promedio: " + str(round(stats["velocidad_prom"], 1)) + " nudos."
        if "esclusa" in p:
            resultado = ""
            for nombre, datos in stats["esclusas"].items():
                resultado = resultado + nombre + ": " + str(datos["total"]) + " barcos. "
            return resultado
        if "clima" in p:
            return "Condiciones climaticas favorables para la navegacion."
        return "El Canal tiene " + str(stats["total"]) + " barcos con CWT de " + str(round(stats["cwt"], 1)) + " horas."
    
    def generar_reporte(self, df, stats):
        lineas = []
        lineas.append("=" * 50)
        lineas.append("ANAYANSI - REPORTE DEL CANAL")
        lineas.append("=" * 50)
        lineas.append("Fecha: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
        lineas.append("")
        lineas.append("RESUMEN:")
        lineas.append("  Barcos: " + str(stats["total"]))
        lineas.append("  CWT: " + str(round(stats["cwt"], 1)) + " horas")
        lineas.append("  Velocidad: " + str(round(stats["velocidad_prom"], 1)) + " nudos")
        lineas.append("  Espera: " + str(stats["espera"]))
        lineas.append("  Norte: " + str(stats["norte"]) + " | Sur: " + str(stats["sur"]))
        lineas.append("")
        lineas.append("ESCLUSAS:")
        for nombre, datos in stats["esclusas"].items():
            lineas.append("  " + nombre + ": " + str(datos["total"]) + " barcos")
        lineas.append("")
        lineas.append("TIPOS:")
        for tipo, cantidad in stats["tipos"].items():
            lineas.append("  " + tipo + ": " + str(cantidad))
        lineas.append("")
        lineas.append("=" * 50)
        return "\n".join(lineas)

@st.cache_data(ttl=10)
def generar_datos():
    np.random.seed(int(time.time() / 10) % 1000)
    n = np.random.randint(60, 90)
    
    puntos = [(9.36, -79.92), (9.27, -79.92), (9.20, -79.88), (9.015, -79.62), (8.995, -79.585), (8.90, -79.52)]
    tipos = ["Portacontenedores", "Granelero", "Petrolero", "Gasero", "Carguero", "Crucero"]
    estados = ["Navegando", "Navegando", "Navegando", "En espera", "Entrando"]
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
        velocidad = np.random.uniform(0, 1) if estado == "En espera" else np.random.uniform(4, 16)
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
            "prioridad": random.choice(prioridades)
        }
        barcos.append(barco)
    return pd.DataFrame(barcos)

def analizar(df):
    stats = {
        "total": len(df),
        "norte": len(df[df["direccion"] == "Norte"]),
        "sur": len(df[df["direccion"] == "Sur"]),
        "espera": len(df[df["estado"] == "En espera"]),
        "prioridad_alta": len(df[df["prioridad"] == "Alta"]),
        "velocidad_prom": df["velocidad"].mean(),
        "esclusas": {},
        "tipos": df["tipo"].value_counts().to_dict()
    }
    for e in ["Gatun", "Pedro Miguel", "Miraflores"]:
        df_e = df[df["esclusa"] == e]
        stats["esclusas"][e] = {"total": len(df_e), "espera": len(df_e[df_e["estado"] == "En espera"])}
    stats["cwt"] = 12 + max(0, (stats["total"] - 30) * 0.1) + stats["espera"] * 0.12
    stats["cwt"] = min(40, max(8, stats["cwt"]))
    if stats["cwt"] < 14:
        stats["nivel"] = "Bajo"; stats["color"] = "#10b981"
    elif stats["cwt"] < 18:
        stats["nivel"] = "Moderado"; stats["color"] = "#f59e0b"
    elif stats["cwt"] < 23:
        stats["nivel"] = "Alto"; stats["color"] = "#f97316"
    else:
        stats["nivel"] = "Critico"; stats["color"] = "#ef4444"
    return stats

if "anayansi" not in st.session_state:
    st.session_state.anayansi = AnayansiIA()
    st.session_state.chat = [{"rol": "anayansi", "msg": "Hola! Soy Anayansi, IA del Canal de Panama. Preguntame sobre barcos, CWT, esclusas o clima."}]

anayansi = st.session_state.anayansi

with st.sidebar:
    st.markdown("### 🌊 ANAYANSI")
    st.markdown("Sabiduria del mar")
    st.markdown("---")
    df = generar_datos()
    stats = analizar(df)
    st.session_state["df"] = df
    st.session_state["stats"] = stats
    col1, col2 = st.columns(2)
    col1.metric("Barcos", stats["total"])
    col2.metric("CWT", f"{stats['cwt']:.1f}h")
    st.markdown("---")
    st.caption("Aprendizaje: " + str(len(anayansi.aprendizaje)) + " registros")
    if st.button("Actualizar"):
        st.cache_data.clear()
        st.rerun()

st.markdown('<h1 class="main-header">🌊 ANAYANSI - Canal Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Sistema IA para el Canal de Panama</p>', unsafe_allow_html=True)

df = st.session_state.get("df", generar_datos())
stats = st.session_state.get("stats", analizar(df))

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Mapa", "Analisis", "Chat", "Aprendizaje", "Datos"])

with tab1:
    st.markdown("### Dashboard")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Barcos", stats["total"])
    col2.metric("CWT", f"{stats['cwt']:.1f}h")
    col3.metric("Velocidad", f"{stats['velocidad_prom']:.1f}")
    col4.metric("Espera", stats["espera"])
    col5.metric("Prioridad Alta", stats["prioridad_alta"])
    st.markdown("---")
    st.markdown("#### Congestion")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<h2 style='color:{stats['color']};'>{stats['nivel']}</h2>", unsafe_allow_html=True)
    with col2:
        st.progress(min(stats["cwt"] / 30, 1.0))
    st.markdown("---")
    st.markdown("#### Esclusas")
    c1, c2, c3 = st.columns(3)
    for col, (nombre, datos) in zip([c1, c2, c3], stats["esclusas"].items()):
        with col:
            st.markdown(f"**{nombre}**")
            st.write("Total: " + str(datos["total"]))
            st.write("Espera: " + str(datos["espera"]))

with tab2:
    st.markdown("### Mapa")
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="nombre", color="prioridad", color_discrete_map={"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"}, size="velocidad", size_max=14, zoom=9, height=500)
    fig.update_layout(mapbox_style="carto-positron", mapbox_center={"lat": 9.15, "lon": -79.75})
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Analisis")
    col1, col2 = st.columns(2)
    with col1:
        tipos_df = pd.DataFrame({"Tipo": list(stats["tipos"].keys()), "Cantidad": list(stats["tipos"].values())})
        fig = px.bar(tipos_df, x="Tipo", y="Cantidad", color="Cantidad", color_continuous_scale="Viridis")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("CWT", f"{stats['cwt']:.1f}h")
        st.metric("Velocidad", f"{stats['velocidad_prom']:.1f} nudos")
        st.metric("En Espera", stats["espera"])

with tab4:
    st.markdown("### Chat con Anayansi")
    for msg in st.session_state.chat:
        if msg["rol"] == "anayansi":
            st.markdown(f'<div class="chat-ai">🌊 Anayansi: {msg["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">Tu: {msg["msg"]}</div>', unsafe_allow_html=True)
    pregunta = st.text_input("Pregunta a Anayansi:", placeholder="Ej: Cual es el CWT actual?")
    if pregunta:
        st.session_state.chat.append({"rol": "usuario", "msg": pregunta})
        respuesta = anayansi.preguntar(pregunta, df, stats)
        st.session_state.chat.append({"rol": "anayansi", "msg": respuesta})
        st.rerun()
    if st.button("Limpiar chat"):
        st.session_state.chat = [{"rol": "anayansi", "msg": "Hola! Soy Anayansi, IA del Canal de Panama. Preguntame sobre barcos, CWT, esclusas o clima."}]
        st.rerun()

with tab5:
    st.markdown("### Aprendizaje de Anayansi")
    st.metric("Registros de aprendizaje", len(anayansi.aprendizaje))
    if anayansi.aprendizaje:
        st.markdown("#### Ultimos aprendizajes")
        for item in anayansi.aprendizaje[-5:]:
            st.caption(item["fecha"][:16] + " - " + item["texto"][:50] + "...")
    st.markdown("---")
    st.markdown("#### Ensenar a Anayansi")
    nuevo = st.text_area("Que quieres que Anayansi aprenda?")
    if st.button("Ensenar") and nuevo:
        resultado = anayansi.aprender(nuevo)
        st.success(resultado)
        st.rerun()

with tab6:
    st.markdown("### Datos y Reportes")
    display_df = df[["nombre", "direccion", "tipo", "estado", "esclusa", "velocidad", "eta_horas", "prioridad"]].copy()
    display_df["velocidad"] = display_df["velocidad"].round(1)
    display_df["eta_horas"] = display_df["eta_horas"].round(1)
    display_df["direccion"] = display_df["direccion"].apply(lambda x: "Norte" if x == "Norte" else "Sur")
    display_df.columns = ["Nombre", "Direccion", "Tipo", "Estado", "Esclusa", "Velocidad", "ETA (h)", "Prioridad"]
    st.dataframe(display_df, use_container_width=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(label="Descargar datos (CSV)", data=csv, file_name="canal_datos.csv", mime="text/csv")
    with col2:
        reporte = anayansi.generar_reporte(df, stats)
        st.download_button(label="Descargar Reporte (TXT)", data=reporte, file_name="reporte_canal.txt", mime="text/plain")

st.markdown('<div class="footer">🌊 ANAYANSI - Canal Predictor | Sabiduria del mar | Panama</div>', unsafe_allow_html=True)
''')

# Descargar app.py
files.download('app.py')
print("✅ app.py descargado")