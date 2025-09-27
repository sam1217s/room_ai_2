"""
Dashboard avanzado con analítica de inquilinos y motor IA.
Optimizado para SENASOFT 2025 - Nivel Intermedio.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

from app.core.database import db_manager   # ✅ importar instancia global

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def mostrar_dashboard_completo(motor_ia):
    """
    📊 Dashboard completo con analítica avanzada
    """
    # Cargar datos desde DB
    inquilinos_data = db_manager.obtener_todos_inquilinos()
    if not inquilinos_data:
        st.warning("⚠️ No hay datos registrados en la base.")
        return

    df = pd.DataFrame(inquilinos_data)

    st.markdown("""
    <div style='padding:1rem; background:#f9f9f9; border-radius:10px; margin-bottom:1rem;'>
        <h2 style='text-align:center;'>📊 Dashboard RoomMatchAI</h2>
        <p style='text-align:center; color:#555;'>Analítica avanzada de inquilinos con IA</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs principales
    tab1, tab2 = st.tabs([
        "📋 Resumen General",
        "🧠 IA y Patrones"
    ])

    with tab1:
        _mostrar_resumen_general(df, motor_ia)

    with tab2:
        _mostrar_patrones(df, motor_ia)


# ============================================================================
# SECCIÓN 1: MÉTRICAS Y DISTRIBUCIÓN
# ============================================================================
def _mostrar_resumen_general(df: pd.DataFrame, motor_ia):
    """Resumen general del sistema"""
    st.subheader("📋 Resumen Ejecutivo")

    col1, col2, col3, col4, col5 = st.columns(5)

    total = len(df)
    edad_prom = df["edad"].mean() if "edad" in df else 0
    fumadores = (df["fumador"] == "si").mean() * 100 if "fumador" in df else 0
    mascotas = (df["mascotas"] == "con mascotas").mean() * 100 if "mascotas" in df else 0

    # Métricas IA
    metricas = motor_ia.obtener_metricas_modelo() if motor_ia else {}
    accuracy = metricas.get("accuracy", 0) * 100

    col1.metric("👥 Inquilinos", f"{total:,}")
    col2.metric("📊 Edad Prom.", f"{edad_prom:.1f} años")
    col3.metric("🚬 Fumadores", f"{fumadores:.1f}%")
    col4.metric("🐶 Mascotas", f"{mascotas:.1f}%")
    col5.metric("🧠 Precisión IA", f"{accuracy:.1f}%")

    st.markdown("---")

    # Distribuciones
    col_a, col_b = st.columns(2)
    with col_a:
        _graficos_distribucion(df)
    with col_b:
        _mapa_correlaciones(df)


def _graficos_distribucion(df: pd.DataFrame):
    """Gráfico de distribución principal"""
    st.markdown("### 📊 Distribución de Características")
    features = ["fumador", "mascotas", "orden", "deporte"]

    rows, cols = 2, 2
    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=[f.title() for f in features],
        specs=[[{"type": "domain"}] * cols for _ in range(rows)]
    )

    for i, feature in enumerate(features):
        if feature in df:
            vals = df[feature].value_counts()
            row = (i // cols) + 1
            col = (i % cols) + 1
            fig.add_trace(
                go.Pie(labels=vals.index, values=vals.values, name=feature),
                row=row, col=col
            )

    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, config={"responsive": True})


def _mapa_correlaciones(df: pd.DataFrame):
    """Mapa de correlaciones numéricas básicas"""
    st.markdown("### 🔥 Correlaciones")
    corr_df = pd.DataFrame()

    if "fumador" in df:
        corr_df["fumador"] = (df["fumador"] == "si").astype(int)
    if "mascotas" in df:
        corr_df["mascotas"] = (df["mascotas"] == "con mascotas").astype(int)
    if "orden" in df:
        corr_df["orden"] = (df["orden"] == "ordenada").astype(int)
    if "deporte" in df:
        corr_df["deporte"] = (df["deporte"] == "si").astype(int)

    if corr_df.empty:
        st.info("⚠️ No hay suficientes datos categóricos.")
        return

    fig = px.imshow(
        corr_df.corr(),
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Mapa de Correlaciones"
    )
    st.plotly_chart(fig, config={"responsive": True})


# ============================================================================
# SECCIÓN 2: PATRONES DE IA
# ============================================================================
def _mostrar_patrones(df: pd.DataFrame, motor_ia):
    """Patrones descubiertos por IA"""
    st.subheader("🧠 Patrones Descubiertos")

    if not motor_ia or not motor_ia.is_trained:
        st.info("⚠️ Motor IA no entrenado.")
        return

    if hasattr(motor_ia, "feature_importance") and motor_ia.feature_importance:
        st.markdown("### 🔍 Importancia de Características")
        _plot_importancia(motor_ia.feature_importance)

    elif hasattr(motor_ia, "model") and hasattr(motor_ia.model, "feature_importances_"):
        importances = dict(zip(motor_ia.feature_names, motor_ia.model.feature_importances_))
        st.markdown("### 🔍 Importancia de Características (del modelo)")
        _plot_importancia(importances)

    else:
        st.info("⚠️ No hay datos de importancia de características disponibles.")


def _plot_importancia(importances: dict):
    """Gráfico de importancia de features"""
    items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
    feats, vals = zip(*items)

    fig = px.bar(
        x=vals, y=feats,
        orientation="h",
        title="Top 10 Características",
        color=vals, color_continuous_scale="viridis"
    )
    st.plotly_chart(fig, config={"responsive": True})
