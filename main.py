# main.py - RoomMatchAI v2.0
# Arreglar rutas de importación
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import logging

from app.core.config import config
from app.core.database import DatabaseManager   # ✅ usar la clase
from app.core.ia_engine import MotorIA
from app.components import dashboard, formulario, chatbot

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("RoomMatchAI")

st.set_page_config(
    page_title="RoomMatchAI",
    page_icon="🏠",
    layout="wide",
)

# ✅ Instancia global de la base de datos
db_manager = DatabaseManager()

# ==============================
# INICIALIZAR SISTEMA
# ==============================
def inicializar_sistema():
    logger.info("🔧 Inicializando Motor IA...")
    if "motor_ia" not in st.session_state:
        st.session_state.motor_ia = MotorIA()
        st.session_state.motor_ia.cargar_modelos()

# ==============================
# SIDEBAR
# ==============================
def mostrar_sidebar():
    st.sidebar.title("📌 Navegación")
    return st.sidebar.radio(
        "Selecciona una opción:",
        [
            "📊 Dashboard",
            "📝 Registrar Inquilino",
            "🤖 ChatBot",
            "⚙️ Configuración",
            "ℹ️ Acerca de"
        ]
    )

# ==============================
# PANTALLAS PRINCIPALES
# ==============================
def pantalla_dashboard():
    st.markdown("## 📊 Dashboard de Análisis")
    dashboard.mostrar_dashboard_completo(st.session_state.motor_ia)

def pantalla_formulario():
    st.markdown("## 📝 Registro de Inquilinos")
    if hasattr(formulario, "mostrar_formulario"):
        formulario.mostrar_formulario()
    elif hasattr(formulario, "mostrar_formulario_registro"):
        formulario.mostrar_formulario_registro()
    else:
        st.error("❌ No hay función de formulario disponible en formulario.py")

def pantalla_chatbot():
    st.markdown("## 🤖 ChatBot de Compatibilidad")
    chatbot.mostrar_chatbot_avanzado(st.session_state.motor_ia)

def pantalla_configuracion():
    st.markdown("## ⚙️ Configuración del Sistema")
    st.json({
        "Base de Datos": config.MONGO_URI,
        "Colección": config.MONGO_COLLECTION,
        "Debug": config.DEBUG,
        "Nivel Log": config.LOG_LEVEL
    })

def pantalla_acerca():
    st.markdown("## ℹ️ Acerca de RoomMatchAI")
    st.info("""
    🏠 **RoomMatchAI v2.0**  
    Proyecto desarrollado para **SENASoft 2025**.  
    Combina **IA + Análisis de datos** para encontrar la mejor compatibilidad entre inquilinos.  

    👨‍💻 Equipo: Desarrolladores Junior  
    📚 Tecnologías: Python, Streamlit, MongoDB, Scikit-learn, Plotly  
    """)

# ==============================
# MAIN
# ==============================
def main():
    st.title("🏠 RoomMatchAI")
    st.caption("Sistema Inteligente de Compatibilidad de Inquilinos")

    inicializar_sistema()
    opcion = mostrar_sidebar()

    if opcion == "📊 Dashboard":
        pantalla_dashboard()
    elif opcion == "📝 Registrar Inquilino":
        pantalla_formulario()
    elif opcion == "🤖 ChatBot":
        pantalla_chatbot()
    elif opcion == "⚙️ Configuración":
        pantalla_configuracion()
    elif opcion == "ℹ️ Acerca de":
        pantalla_acerca()

# ==============================
# EJECUTAR APP
# ==============================
if __name__ == "__main__":
    main()
