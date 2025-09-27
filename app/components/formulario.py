# app/components/formulario.py
import streamlit as st
from datetime import datetime
from app.core.inquilino_schema import Inquilino
from app.core.database import db_manager


def _generar_id_automatico() -> int:
    """
    Busca el mayor id_inquilino actual y devuelve el siguiente.
    Si no hay registros, vuelve 1. Tiene un fallback seguro.
    """
    try:
        datos = db_manager.obtener_todos_inquilinos()  # ✅ corregido
        if not datos:
            return 1
        max_id = max(int(doc.get("id_inquilino", 0)) for doc in datos)
        return max_id + 1
    except Exception:
        # Fallback simple si hubiera algún problema leyendo la DB
        from time import time
        return int(time()) % 1_000_000 or 1


def _calcular_compatible_regla_simple(d: dict) -> int:
    """
    Misma regla del generador demo:
    +1 si no fuma, +1 ordenada, +1 sin mascotas, +1 deporte, +1 madrugador.
    Compatible = 1 si puntaje >= 3; si no, 0
    """
    puntaje = 0
    puntaje += 1 if d.get("fumador") == "no" else 0
    puntaje += 1 if d.get("orden") == "ordenada" else 0
    puntaje += 1 if d.get("mascotas") == "sin mascotas" else 0
    puntaje += 1 if d.get("deporte") == "si" else 0
    puntaje += 1 if d.get("bioritmo") == "madrugador" else 0
    return 1 if puntaje >= 3 else 0


def mostrar_formulario_registro():
    """
    📝 Formulario de registro de inquilinos con:
    - ID automático obligatorio
    - Edad 0–100
    - compatible calculado automáticamente
    """
    st.markdown("## 📝 Registro Inteligente de Inquilinos")
    st.write("Completa la información del inquilino. El ID se genera automáticamente.")

    with st.form("form_inquilino", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("👤 Nombre completo")
            cedula = st.text_input("🆔 Número de cédula")
            edad = st.slider("🎂 Edad", min_value=0, max_value=100, value=25)
            genero = st.selectbox("⚧ Género", ["masculino", "femenino", "otro"])
            fumador = st.radio("🚬 ¿Fumador?", ["si", "no"], horizontal=True)

        with col2:
            mascotas = st.radio("🐕 Mascotas", ["con mascotas", "sin mascotas"], horizontal=True)
            orden = st.radio("🧹 Nivel de orden", ["ordenada", "desordenada"], horizontal=True)
            deporte = st.radio("⚽ ¿Practica deporte?", ["si", "no"], horizontal=True)
            bioritmo = st.radio("⏰ Biorritmo", ["madrugador", "nocturno"], horizontal=True)

        st.markdown("---")

        nivel_educativo = st.selectbox("🎓 Nivel educativo", ["", "secundaria", "universitaria", "posgrado"])
        musica_tipo = st.text_input("🎵 Tipo de música favorita")
        plan_perfecto = st.text_input("🎯 Plan perfecto de fin de semana")
        visitas = st.radio("👥 ¿Recibe visitas frecuentes?", ["si", "no"], horizontal=True)
        personalidad = st.text_input("😃 Tipo de personalidad")
        instrumento = st.radio("🎸 ¿Toca algún instrumento?", ["si", "no"], horizontal=True)

        submitted = st.form_submit_button("✅ Registrar Inquilino")

        if submitted:
            try:
                # Generar ID obligatorio
                nuevo_id = _generar_id_automatico()

                # Datos base (sin compatibles aún)
                payload = {
                    "id_inquilino": nuevo_id,
                    "nombre": nombre,
                    "cedula": int(cedula) if cedula else None,
                    "edad": edad,
                    "genero": genero,
                    "fumador": fumador,
                    "mascotas": mascotas,
                    "orden": orden,
                    "deporte": deporte,
                    "bioritmo": bioritmo,
                    "nivel_educativo": nivel_educativo or None,
                    "musica_tipo": musica_tipo or None,
                    "plan_perfecto": plan_perfecto or None,
                    "visitas": visitas,
                    "personalidad": personalidad or None,
                    "instrumento": instrumento,
                    "created_at": datetime.utcnow(),
                }

                # Calcular etiqueta compatible
                payload["compatible"] = _calcular_compatible_regla_simple(payload)

                # Validar con Pydantic
                nuevo_inquilino = Inquilino(**payload)

                # Insertar en MongoDB
                db_manager.insertar_inquilino(nuevo_inquilino.dict())  # ✅ corregido
                st.success(
                    f"🎉 Inquilino **{nuevo_inquilino.nombre}** registrado con ID **{nuevo_inquilino.id_inquilino}**. "
                    f"(compatible={nuevo_inquilino.compatible})"
                )

            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")
