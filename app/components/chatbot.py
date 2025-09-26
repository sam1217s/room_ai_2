# app/components/chatbot.py - RoomBot IA Avanzado con Flujos Inteligentes
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple, Any
import logging
import time

from ..core.database import obtener_todos_inquilinos
from ..core.config import config

logger = logging.getLogger(__name__)

# ============================================================================
# SISTEMA DE ESTADOS Y CONTEXTO
# ============================================================================

class RoomBotContext:
    """🧠 Contexto y memoria del chatbot"""
    
    def __init__(self):
        self.estado_actual = 'INICIO'
        self.historial_conversacion = []
        self.datos_sesion = {}
        self.ultima_consulta = None
        self.inquilinos_df = None
    
    def agregar_mensaje(self, tipo: str, mensaje: str, datos_extra: Dict = None):
        """Agrega mensaje al historial"""
        entrada = {
            'timestamp': datetime.now(),
            'tipo': tipo,  # 'usuario' o 'bot'
            'mensaje': mensaje,
            'estado': self.estado_actual,
            'datos_extra': datos_extra or {}
        }
        self.historial_conversacion.append(entrada)
        
        # Mantener solo últimos 50 mensajes
        if len(self.historial_conversacion) > 50:
            self.historial_conversacion = self.historial_conversacion[-50:]
    
    def obtener_contexto_reciente(self, n: int = 5) -> List[Dict]:
        """Obtiene los últimos n mensajes para contexto"""
        return self.historial_conversacion[-n:]
    
    def limpiar_contexto(self):
        """Limpia el contexto y reinicia"""
        self.estado_actual = 'INICIO'
        self.historial_conversacion = []
        self.datos_sesion = {}
        self.ultima_consulta = None

class RoomBotIA:
    """🤖 RoomBot con Inteligencia Artificial Avanzada"""
    
    def __init__(self, motor_ia):
        self.motor_ia = motor_ia
        self.context = RoomBotContext()
        
        # Comandos y patrones de reconocimiento
        self.comandos_disponibles = {
            'compatibilidad': {
                'patrones': [
                    r'compatibilidad\s+(\d+)\s+(\d+)',
                    r'compatibilidad\s+entre\s+(\d+)\s+y\s+(\d+)',
                    r'analizar\s+(\d+)\s+(\d+)',
                    r'comparar\s+(\d+)\s+(\d+)'
                ],
                'descripcion': 'Analiza compatibilidad entre dos inquilinos',
                'ejemplos': ['compatibilidad 123 456', 'analizar 123 456']
            },
            'recomendaciones': {
                'patrones': [
                    r'recomendaciones\s+(\d+)',
                    r'matches\s+(\d+)',
                    r'compatible\s+con\s+(\d+)',
                    r'quien\s+es\s+compatible\s+con\s+(\d+)'
                ],
                'descripcion': 'Encuentra inquilinos compatibles',
                'ejemplos': ['recomendaciones 123', 'matches 123']
            },
            'grupos': {
                'patrones': [
                    r'grupo\s+(\d+)\s+de\s+(\d+)',
                    r'crear\s+grupo\s+(\d+)',
                    r'agrupar\s+(\d+)',
                    r'clusters?\s+(\d+)'
                ],
                'descripcion': 'Crea grupos inteligentes',
                'ejemplos': ['grupo 5 de 8', 'crear grupo 5']
            },
            'buscar': {
                'patrones': [
                    r'buscar\s+(\w+)',
                    r'encontrar\s+(\w+)',
                    r'filtrar\s+(\w+)'
                ],
                'descripcion': 'Busca inquilinos por características',
                'ejemplos': ['buscar fumadores', 'encontrar deportistas']
            },
            'estadisticas': {
                'patrones': [
                    r'estad[ií]sticas?',
                    r'resumen',
                    r'datos',
                    r'total'
                ],
                'descripcion': 'Muestra estadísticas del sistema',
                'ejemplos': ['estadísticas', 'resumen']
            },
            'ayuda': {
                'patrones': [
                    r'ayuda',
                    r'help',
                    r'comandos',
                    r'que\s+puedes\s+hacer'
                ],
                'descripcion': 'Muestra comandos disponibles',
                'ejemplos': ['ayuda', 'comandos']
            }
        }
        
        # Respuestas contextuales
        self.respuestas_contextuales = {
            'saludo': [
                "¡Hola! 👋 Soy RoomBot, tu asistente inteligente de compatibilidad.",
                "¡Hola! 🤖 ¿En qué puedo ayudarte con la compatibilidad de inquilinos?",
                "¡Saludos! 🏡 Estoy aquí para ayudarte con análisis de compatibilidad."
            ],
            'despedida': [
                "¡Hasta luego! 👋 Fue un placer ayudarte.",
                "¡Nos vemos! 🤖 Vuelve cuando necesites analizar compatibilidades.",
                "¡Adiós! 🏡 Espero haber sido útil."
            ],
            'confuso': [
                "🤔 No estoy seguro de entender. ¿Podrías ser más específico?",
                "❓ No reconozco ese comando. Escribe 'ayuda' para ver lo que puedo hacer.",
                "🧐 Hmm, no entendí eso. ¿Puedes reformular tu pregunta?"
            ],
            'error': [
                "😅 Ups, algo salió mal. ¿Puedes intentar de nuevo?",
                "⚠️ Hubo un error procesando tu solicitud.",
                "🔧 Parece que hay un problema técnico. Inténtalo más tarde."
            ]
        }

def mostrar_chatbot_avanzado(motor_ia):
    """
    🤖 Interfaz principal del chatbot avanzado
    
    Args:
        motor_ia: Instancia del motor de IA
    """
    
    # Inicializar chatbot en session_state
    if 'roombot' not in st.session_state:
        st.session_state.roombot = RoomBotIA(motor_ia)
    
    roombot = st.session_state.roombot
    
    # Header del chatbot
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;'>
        <h2 style='text-align: center; margin-bottom: 1rem;'>🤖 RoomBot IA</h2>
        <p style='text-align: center; opacity: 0.9;'>
            Asistente Inteligente de Compatibilidad de Inquilinos
        </p>
        <p style='text-align: center; font-size: 0.9rem; opacity: 0.8;'>
            💬 Pregúntame sobre compatibilidades, recomendaciones y análisis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos de inquilinos
    cargar_datos_inquilinos(roombot)
    
    # Pestañas del chatbot
    tab1, tab2, tab3 = st.tabs(["💬 Chat Inteligente", "📖 Comandos Rápidos", "🎯 Análisis Guiado"])
    
    with tab1:
        _mostrar_chat_principal(roombot)
    
    with tab2:
        _mostrar_comandos_rapidos(roombot)
    
    with tab3:
        _mostrar_analisis_guiado(roombot)
# ============================================================================
# FUNCIONES PRINCIPALES DEL CHAT
# ============================================================================

def _mostrar_chat_principal(roombot: RoomBotIA):
    """Muestra la interfaz principal del chat"""
    
    # Área de conversación
    _mostrar_historial_conversacion(roombot)
    
    # Input del usuario
    _mostrar_input_usuario(roombot)
    
    # Panel de estado del sistema
    _mostrar_panel_estado(roombot)

def _mostrar_historial_conversacion(roombot: RoomBotIA):
    """Muestra el historial de la conversación"""
    
    st.markdown("### 💬 Conversación")
    
    # Contenedor con scroll para el historial
    chat_container = st.container()
    
    with chat_container:
        if not roombot.context.historial_conversacion:
            # Mensaje de bienvenida
            st.markdown(_generar_mensaje_bienvenida())
        else:
            # Mostrar historial
            for entrada in roombot.context.historial_conversacion[-10:]:  # Últimos 10 mensajes
                _renderizar_mensaje(entrada)
        
        # Separador antes del input
        st.markdown("---")

def _mostrar_input_usuario(roombot: RoomBotIA):
    """Muestra el input para el usuario"""
    
    # Área de input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        mensaje_usuario = st.text_input(
            "Tu mensaje:",
            placeholder="Escribe tu consulta aquí... (ej: 'compatibilidad 123 456')",
            key="chat_input"
        )
    
    with col2:
        enviar = st.button("📩 Enviar", type="primary", use_container_width=True)
    
    # Procesar mensaje
    if enviar and mensaje_usuario:
        _procesar_mensaje_usuario(roombot, mensaje_usuario)
        st.rerun()
    
    # Sugerencias rápidas
    _mostrar_sugerencias_rapidas(roombot)

def _mostrar_sugerencias_rapidas(roombot: RoomBotIA):
    """Muestra sugerencias rápidas de comandos"""
    
    if not roombot.context.inquilinos_df.empty:
        st.markdown("**💡 Sugerencias rápidas:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Obtener algunos IDs para sugerencias
        ids_disponibles = roombot.context.inquilinos_df['id_inquilino'].head(4).tolist()
        
        with col1:
            if st.button(f"📊 Estadísticas", key="sug_stats"):
                _procesar_mensaje_usuario(roombot, "estadísticas")
                st.rerun()
        
        with col2:
            if len(ids_disponibles) >= 2 and st.button(f"🤝 Compatibilidad", key="sug_comp"):
                mensaje = f"compatibilidad {ids_disponibles[0]} {ids_disponibles[1]}"
                _procesar_mensaje_usuario(roombot, mensaje)
                st.rerun()
        
        with col3:
            if len(ids_disponibles) >= 1 and st.button(f"🏆 Matches", key="sug_match"):
                mensaje = f"recomendaciones {ids_disponibles[0]}"
                _procesar_mensaje_usuario(roombot, mensaje)
                st.rerun()
        
        with col4:
            if st.button("👥 Grupos", key="sug_groups"):
                _procesar_mensaje_usuario(roombot, "crear grupo 5")
                st.rerun()

def _mostrar_comandos_rapidos(roombot: RoomBotIA):
    """Muestra panel de comandos rápidos"""
    
    st.subheader("⚡ Comandos Rápidos")
    
    if roombot.context.inquilinos_df.empty:
        st.warning("⚠️ No hay inquilinos registrados para analizar.")
        return
    
    # Sección de compatibilidad rápida
    st.markdown("### 🤝 Análisis de Compatibilidad")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    opciones_inquilinos = [
        f"{row['id_inquilino']} - {row['nombre']}" 
        for _, row in roombot.context.inquilinos_df.iterrows()
    ]
    
    with col1:
        inquilino1 = st.selectbox("Primer inquilino:", opciones_inquilinos, key="quick_comp1")
    
    with col2:
        inquilino2 = st.selectbox("Segundo inquilino:", opciones_inquilinos, key="quick_comp2")
    
    with col3:
        if st.button("🔍 Analizar", type="primary"):
            id1 = int(inquilino1.split(" - ")[0])
            id2 = int(inquilino2.split(" - ")[0])
            
            if id1 != id2:
                _procesar_mensaje_usuario(roombot, f"compatibilidad {id1} {id2}")
                st.rerun()
            else:
                st.error("⚠️ Selecciona inquilinos diferentes")
    
    st.markdown("---")
    
    # Sección de recomendaciones rápidas
    st.markdown("### 🏆 Recomendaciones Rápidas")
    
    col_a, col_b, col_c = st.columns([2, 1, 1])
    
    with col_a:
        inquilino_base = st.selectbox("Inquilino base:", opciones_inquilinos, key="quick_rec")
    
    with col_b:
        num_recomendaciones = st.selectbox("Cantidad:", [3, 5, 8, 10], index=1)
    
    with col_c:
        if st.button("🏆 Recomendar", type="primary"):
            id_base = int(inquilino_base.split(" - ")[0])
            mensaje = f"recomendaciones {id_base} top {num_recomendaciones}"
            _procesar_mensaje_usuario(roombot, mensaje)
            st.rerun()
    
    st.markdown("---")
    
    # Sección de grupos rápidos
    st.markdown("### 👥 Creación de Grupos")
    
    col_i, col_ii, col_iii = st.columns(3)
    
    with col_i:
        num_grupos = st.selectbox("Número de grupos:", [3, 4, 5, 6, 8], index=2)
    
    with col_ii:
        max_por_grupo = st.selectbox("Máximo por grupo:", [4, 6, 8, 10], index=2)
    
    with col_iii:
        if st.button("👥 Crear Grupos", type="primary"):
            mensaje = f"grupos {num_grupos} de {max_por_grupo}"
            _procesar_mensaje_usuario(roombot, mensaje)
            st.rerun()

def _mostrar_analisis_guiado(roombot: RoomBotIA):
    """Muestra análisis guiado paso a paso"""
    
    st.subheader("🎯 Análisis Guiado")
    
    if roombot.context.inquilinos_df.empty:
        st.warning("⚠️ No hay inquilinos registrados para analizar.")
        return
    
    # Flujo guiado
    opciones_analisis = [
        "Seleccionar tipo de análisis...",
        "🔍 Análisis completo de compatibilidad",
        "🏆 Búsqueda de mejores matches",
        "📊 Análisis estadístico detallado",
        "👥 Organización en grupos óptimos",
        "🎯 Análisis por características específicas"
    ]
    
    tipo_analisis = st.selectbox("¿Qué tipo de análisis necesitas?", opciones_analisis)
    
    if tipo_analisis != "Seleccionar tipo de análisis...":
        if tipo_analisis == "🔍 Análisis completo de compatibilidad":
            _flujo_analisis_compatibilidad_completo(roombot)
        
        elif tipo_analisis == "🏆 Búsqueda de mejores matches":
            _flujo_mejores_matches(roombot)
        
        elif tipo_analisis == "📊 Análisis estadístico detallado":
            _flujo_analisis_estadistico(roombot)
        
        elif tipo_analisis == "👥 Organización en grupos óptimos":
            _flujo_organizacion_grupos(roombot)
        
        elif tipo_analisis == "🎯 Análisis por características específicas":
            _flujo_analisis_caracteristicas(roombot)
# ============================================================================
# PROCESAMIENTO DE MENSAJES
# ============================================================================

def _procesar_mensaje_usuario(roombot: RoomBotIA, mensaje: str):
    """Procesa un mensaje del usuario y genera respuesta"""
    
    # Agregar mensaje del usuario al historial
    roombot.context.agregar_mensaje('usuario', mensaje)
    
    # Limpiar y normalizar mensaje
    mensaje_limpio = mensaje.lower().strip()
    
    # Detectar tipo de comando
    comando_detectado = _detectar_comando(mensaje_limpio, roombot)
    
    # Generar respuesta
    if comando_detectado:
        respuesta = _ejecutar_comando(comando_detectado, mensaje_limpio, roombot)
    else:
        respuesta = _generar_respuesta_generica(mensaje_limpio, roombot)
    
    # Agregar respuesta del bot al historial
    roombot.context.agregar_mensaje('bot', respuesta['mensaje'], respuesta.get('datos'))

def _detectar_comando(mensaje: str, roombot: RoomBotIA) -> Optional[Dict]:
    """Detecta qué comando está intentando usar el usuario"""
    
    for comando, config in roombot.comandos_disponibles.items():
        for patron in config['patrones']:
            match = re.search(patron, mensaje, re.IGNORECASE)
            if match:
                return {
                    'comando': comando,
                    'parametros': match.groups(),
                    'texto_original': mensaje,
                    'match_object': match
                }
    
    # Detección de comandos más flexibles
    if any(palabra in mensaje for palabra in ['hola', 'saludos', 'buenos']):
        return {'comando': 'saludo', 'parametros': [], 'texto_original': mensaje}
    
    if any(palabra in mensaje for palabra in ['adiós', 'chao', 'hasta luego']):
        return {'comando': 'despedida', 'parametros': [], 'texto_original': mensaje}
    
    return None

def _ejecutar_comando(comando_info: Dict, mensaje: str, roombot: RoomBotIA) -> Dict:
    """Ejecuta el comando detectado"""
    
    comando = comando_info['comando']
    parametros = comando_info['parametros']
    
    try:
        if comando == 'compatibilidad':
            return _comando_compatibilidad(parametros, roombot)
        
        elif comando == 'recomendaciones':
            return _comando_recomendaciones(parametros, mensaje, roombot)
        
        elif comando == 'grupos':
            return _comando_grupos(parametros, mensaje, roombot)
        
        elif comando == 'buscar':
            return _comando_buscar(parametros, roombot)
        
        elif comando == 'estadisticas':
            return _comando_estadisticas(roombot)
        
        elif comando == 'ayuda':
            return _comando_ayuda(roombot)
        
        elif comando == 'saludo':
            return _comando_saludo(roombot)
        
        elif comando == 'despedida':
            return _comando_despedida(roombot)
        
        else:
            return {'mensaje': f"🤔 Comando '{comando}' no implementado aún."}
    
    except Exception as e:
        logger.error(f"Error ejecutando comando {comando}: {e}")
        return {
            'mensaje': f"❌ Error ejecutando comando: {str(e)}",
            'error': True
        }

def _generar_respuesta_generica(mensaje: str, roombot: RoomBotIA) -> Dict:
    """Genera respuesta genérica cuando no se detecta comando específico"""
    
    # Intentar extraer números (posibles IDs)
    numeros = re.findall(r'\d+', mensaje)
    
    if len(numeros) >= 2:
        # Posible consulta de compatibilidad
        return {
            'mensaje': f"🤔 ¿Quieres analizar la compatibilidad entre {numeros[0]} y {numeros[1]}? "
                      f"Usa: 'compatibilidad {numeros[0]} {numeros[1]}'"
        }
    
    elif len(numeros) == 1:
        # Posible consulta de recomendaciones
        return {
            'mensaje': f"🤔 ¿Buscas recomendaciones para el inquilino {numeros[0]}? "
                      f"Usa: 'recomendaciones {numeros[0]}'"
        }
    
    else:
        # Respuesta genérica confusa
        import random
        respuesta = random.choice(roombot.respuestas_contextuales['confuso'])
        return {'mensaje': respuesta}
# ============================================================================
# COMANDOS ESPECÍFICOS
# ============================================================================

def _comando_compatibilidad(parametros: Tuple, roombot: RoomBotIA) -> Dict:
    """Ejecuta comando de análisis de compatibilidad"""
    
    if len(parametros) < 2:
        return {'mensaje': "❌ Necesito dos IDs de inquilinos. Ejemplo: 'compatibilidad 123 456'"}
    
    try:
        id1, id2 = int(parametros[0]), int(parametros[1])
        
        # Verificar que los IDs existen
        df = roombot.context.inquilinos_df
        if id1 not in df['id_inquilino'].values:
            return {'mensaje': f"❌ No encontré inquilino con ID {id1}"}
        
        if id2 not in df['id_inquilino'].values:
            return {'mensaje': f"❌ No encontré inquilino con ID {id2}"}
        
        if id1 == id2:
            return {'mensaje': "❌ No puedo analizar compatibilidad de un inquilino consigo mismo"}
        
        # Calcular compatibilidad
        resultado = roombot.motor_ia.calcular_compatibilidad_avanzada(id1, id2, df)
        
        if 'error' in resultado:
            return {'mensaje': f"❌ Error calculando compatibilidad: {resultado['error']}"}
        
        # Formatear respuesta
        nombre1 = df[df['id_inquilino'] == id1].iloc[0]['nombre']
        nombre2 = df[df['id_inquilino'] == id2].iloc[0]['nombre']
        
        compatibilidad = resultado['compatibilidad_porcentaje']
        explicacion = resultado['explicacion']
        recomendacion = resultado['recomendacion']
        
        respuesta = f"""
**🤝 Análisis de Compatibilidad**

**👤 Inquilinos:** {nombre1} (ID: {id1}) ↔ {nombre2} (ID: {id2})

**📊 Resultado:** {compatibilidad:.1f}% de compatibilidad

**🔍 Análisis:** {explicacion}

**💡 Recomendación:** {recomendacion}

**📑 Detalles técnicos:**
- Similitud coseno: {resultado['similitud_coseno']:.1f}%
- Predicción ML: {resultado['prediccion_satisfaccion']:.1f}%
- Confianza: {resultado['confianza']:.0%}
"""
        
        return {
            'mensaje': respuesta,
            'datos': {
                'tipo': 'compatibilidad',
                'id1': id1, 'id2': id2,
                'compatibilidad': compatibilidad,
                'resultado_completo': resultado
            }
        }
    
    except ValueError:
        return {'mensaje': "❌ Los IDs deben ser números válidos"}
    except Exception as e:
        return {'mensaje': f"❌ Error inesperado: {str(e)}"}

def _comando_recomendaciones(parametros: Tuple, mensaje: str, roombot: RoomBotIA) -> Dict:
    """Ejecuta comando de recomendaciones"""
    
    if len(parametros) < 1:
        return {'mensaje': "❌ Necesito el ID del inquilino. Ejemplo: 'recomendaciones 123'"}
    
    try:
        id_inquilino = int(parametros[0])
        
        # Extraer número de recomendaciones del mensaje
        numeros_adicionales = re.findall(r'top\s+(\d+)|(\d+)\s+recomendaciones', mensaje)
        n_recomendaciones = 5  # Por defecto
        
        if numeros_adicionales:
            for match in numeros_adicionales:
                for grupo in match:
                    if grupo:
                        n_recomendaciones = min(int(grupo), 15)  # Máximo 15
                        break
        
        # Verificar que el ID existe
        df = roombot.context.inquilinos_df
        if id_inquilino not in df['id_inquilino'].values:
            return {'mensaje': f"❌ No encontré inquilino con ID {id_inquilino}"}
        
        # Generar recomendaciones
        recomendaciones = roombot.motor_ia.generar_recomendaciones_top(
            id_inquilino, df, n_recomendaciones
        )
        
        if not recomendaciones:
            return {'mensaje': f"⚠️ No se pudieron generar recomendaciones para el ID {id_inquilino}"}
        
        # Formatear respuesta
        nombre_base = df[df['id_inquilino'] == id_inquilino].iloc[0]['nombre']
        
        respuesta = f"**🏆 Top {len(recomendaciones)} Recomendaciones para {nombre_base} (ID: {id_inquilino})**\n\n"
        
        for i, rec in enumerate(recomendaciones, 1):
            respuesta += f"**{i}. {rec['nombre']}** (ID: {rec['id_inquilino']})\n"
            respuesta += f"   • Compatibilidad: {rec['compatibilidad']:.1f}%\n"
            respuesta += f"   • Confianza: {rec['confianza']:.0%}\n"
            respuesta += f"   • Coincidencias clave: {rec['coincidencias_clave']}\n\n"
        
        respuesta += f"💡 *Usa 'compatibilidad {id_inquilino} [ID]' para análisis detallado*"
        
        return {
            'mensaje': respuesta,
            'datos': {
                'tipo': 'recomendaciones',
                'id_base': id_inquilino,
                'recomendaciones': recomendaciones
            }
        }
    
    except ValueError:
        return {'mensaje': "❌ El ID debe ser un número válido"}
    except Exception as e:
        return {'mensaje': f"❌ Error inesperado: {str(e)}"}
def _comando_grupos(parametros: Tuple, mensaje: str, roombot: RoomBotIA) -> Dict:
    """Ejecuta comando de creación de grupos"""
    
    # Extraer parámetros del mensaje
    numeros = re.findall(r'\d+', mensaje)
    
    if len(numeros) >= 2:
        n_grupos = int(numeros[0])
        max_por_grupo = int(numeros[1])
    elif len(numeros) == 1:
        n_grupos = int(numeros[0])
        max_por_grupo = 8  # Por defecto
    else:
        n_grupos = 5  # Por defecto
        max_por_grupo = 8
    
    # Validaciones
    n_grupos = max(2, min(n_grupos, 10))  # Entre 2 y 10
    max_por_grupo = max(3, min(max_por_grupo, 20))  # Entre 3 y 20
    
    try:
        # Crear grupos
        df = roombot.context.inquilinos_df
        resultado = roombot.motor_ia.crear_grupos_inteligentes(df, n_grupos, max_por_grupo)
        
        if 'error' in resultado:
            return {'mensaje': f"❌ Error creando grupos: {resultado['error']}"}
        
        # Formatear respuesta
        grupos = resultado['grupos']
        pendientes = resultado['pendientes']
        
        respuesta = f"**👥 Grupos Inteligentes Creados ({n_grupos} grupos, máx. {max_por_grupo} por grupo)**\n\n"
        
        for nombre_grupo, info in grupos.items():
            miembros = info['miembros']
            compatibilidad = info['compatibilidad_promedio']
            
            respuesta += f"**🏘️ {nombre_grupo}** ({len(miembros)} integrantes - {compatibilidad:.1f}% compatibilidad)\n"
            
            for miembro in miembros:
                respuesta += f"   • {miembro['nombre']} (ID: {miembro['id_inquilino']})\n"
            
            # Características comunes
            if info['caracteristicas_comunes']:
                respuesta += f"   📋 Características: {', '.join(info['caracteristicas_comunes'][:2])}\n"
            
            respuesta += "\n"
        
        if pendientes:
            respuesta += f"**⏳ Pendientes por agrupar ({len(pendientes)}):**\n"
            for pendiente in pendientes:
                respuesta += f"   • {pendiente['nombre']} (ID: {pendiente['id_inquilino']})\n"
        
        # Métricas
        metricas = resultado.get('metricas_clustering', {})
        if metricas:
            respuesta += f"\n📊 **Calidad del clustering:** {metricas.get('silhouette_score', 0):.2f}"
        
        return {
            'mensaje': respuesta,
            'datos': {
                'tipo': 'grupos',
                'resultado_completo': resultado
            }
        }
    
    except Exception as e:
        return {'mensaje': f"❌ Error creando grupos: {str(e)}"}

def _comando_buscar(parametros: Tuple, roombot: RoomBotIA) -> Dict:
    """Ejecuta comando de búsqueda"""
    
    if len(parametros) < 1:
        return {'mensaje': "❌ ¿Qué quieres buscar? Ejemplo: 'buscar fumadores'"}
    
    termino = parametros[0].lower()
    df = roombot.context.inquilinos_df
    
    # Mapear términos a características
    mapeo_busqueda = {
        'fumadores': ('fumador', 'si'),
        'no-fumadores': ('fumador', 'no'),
        'deportistas': ('deporte', 'si'),
        'mascotas': ('mascotas', 'con mascotas'),
        'ordenados': ('orden', 'ordenada'),
        'relajados': ('orden', 'relajada'),
        'madrugadores': ('bioritmo', 'madrugador'),
        'nocturnos': ('bioritmo', 'nocturno'),
        'universitarios': ('nivel_educativo', 'universitaria')
    }
    
    if termino in mapeo_busqueda:
        campo, valor = mapeo_busqueda[termino]
        
        if campo in df.columns:
            resultados = df[df[campo] == valor]
            
            if len(resultados) == 0:
                return {'mensaje': f"❌ No encontré inquilinos {termino}"}
            
            respuesta = f"**🔍 Encontré {len(resultados)} inquilinos {termino}:**\n\n"
            
            for _, inquilino in resultados.head(10).iterrows():  # Máximo 10
                respuesta += f"• **{inquilino['nombre']}** (ID: {inquilino['id_inquilino']})\n"
            
            if len(resultados) > 10:
                respuesta += f"\n... y {len(resultados) - 10} más."
            
            return {
                'mensaje': respuesta,
                'datos': {
                    'tipo': 'busqueda',
                    'termino': termino,
                    'resultados': len(resultados)
                }
            }
        else:
            return {'mensaje': f"❌ No tengo información sobre '{campo}' para buscar"}
    
    else:
        return {'mensaje': f"❌ No sé cómo buscar '{termino}'. Intenta: fumadores, deportistas, ordenados, etc."}
# ============================================================================
# UTILIDADES DE DATOS
# ============================================================================

def cargar_datos_inquilinos(roombot):
    """Carga los inquilinos desde la base de datos y los guarda en el contexto del chatbot."""
    try:
        # Llamar a la función de la BD
        inquilinos_data = obtener_todos_inquilinos()

        if not inquilinos_data:
            st.warning("⚠️ No hay inquilinos registrados en la base de datos.")
            roombot.context.inquilinos_df = pd.DataFrame()
            return

        # Pasar a DataFrame
        df = pd.DataFrame(inquilinos_data)

        # Normalizar columna de IDs
        if "id_inquilino" in df.columns:
            df["id_inquilino"] = pd.to_numeric(df["id_inquilino"], errors="coerce")
            df = df.dropna(subset=["id_inquilino"]).astype({"id_inquilino": int})

        # Guardar en el contexto
        roombot.context.inquilinos_df = df

        logger.info(f"✅ {len(df)} inquilinos cargados en el chatbot")

    except Exception as e:
        logger.error(f"❌ Error cargando inquilinos: {e}")
        st.error("❌ No se pudieron cargar los inquilinos.")
        roombot.context.inquilinos_df = pd.DataFrame()
        
# ============================================================================
# MENSAJES DE INTERFAZ
# ============================================================================

def _generar_mensaje_bienvenida():
    """Muestra el mensaje de bienvenida inicial del chatbot en Streamlit."""
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #f0f4ff; border-radius: 10px; margin-bottom: 1rem;'>
            <h4>👋 ¡Bienvenido a RoomBot IA!</h4>
            <p>Estoy aquí para ayudarte a analizar la <b>compatibilidad de inquilinos</b>, 
            generar recomendaciones y mostrar estadísticas.</p>
            <p><b>Prueba con:</b></p>
            <ul>
                <li>🤝 <code>compatibilidad 101 202</code></li>
                <li>🏆 <code>recomendaciones 101</code></li>
                <li>👥 <code>crear grupo 5</code></li>
                <li>📊 <code>estadísticas</code></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================================
# PANEL DE ESTADO
# ============================================================================

def _mostrar_panel_estado(roombot):
    """Muestra un panel con el estado actual del chatbot"""
    
    st.markdown("### ⚙️ Estado del Sistema")
    
    estado = roombot.context.estado_actual
    total_mensajes = len(roombot.context.historial_conversacion)
    ultimo = roombot.context.historial_conversacion[-1]['mensaje'] if total_mensajes > 0 else "N/A"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📌 Estado", estado)
    with col2:
        st.metric("💬 Mensajes", total_mensajes)
    with col3:
        st.metric("📝 Último", ultimo[:20] + ("..." if len(ultimo) > 20 else ""))
    
    if roombot.context.inquilinos_df is not None:
        st.success(f"📊 Inquilinos cargados: {len(roombot.context.inquilinos_df)}")
    else:
        st.warning("⚠️ No hay datos de inquilinos cargados todavía.")
  
# ============================================================================
# RENDER DE MENSAJES
# ============================================================================

def _renderizar_mensaje(entrada: Dict):
    """Pinta un mensaje del chat en estilo burbuja (usuario) o Markdown (bot)."""
    timestamp = entrada.get("timestamp")
    if isinstance(timestamp, datetime):
        hora = timestamp.strftime("%H:%M")
    else:
        hora = datetime.now().strftime("%H:%M")

    tipo = entrada.get("tipo", "bot")
    mensaje = entrada.get("mensaje", "")

    if tipo == "usuario":
        # Bubble a la derecha (el mensaje del usuario suele ser texto plano)
        st.markdown(
            f"""
            <div style='text-align: right; margin: 0.75rem 0;'>
                <div style='background: #667eea; color: #fff; padding: 0.75rem 1rem;
                            border-radius: 15px 15px 5px 15px; display: inline-block;
                            max-width: 75%; white-space: pre-wrap; word-wrap: break-word;'>
                    {mensaje}
                    <div style='font-size: 0.7rem; opacity: 0.85; margin-top: 0.25rem;'>{hora}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Para el bot priorizamos Markdown para que se vea el formato (** **, listas, etc.)
        st.markdown(mensaje)
        st.caption(f"🤖 {hora}")

# ============================================================================
# PANEL LATERAL DE ESTADO
# ============================================================================

def _mostrar_panel_estado(roombot: RoomBotIA):
    """Panel lateral con estado del bot, métricas y acciones rápidas."""
    with st.sidebar:
        st.markdown("### 🤖 Estado del Bot")

        # Datos cargados
        df = roombot.context.inquilinos_df
        total_inquilinos = 0
        if df is not None and not df.empty:
            total_inquilinos = len(df)

        st.metric("📚 Inquilinos cargados", total_inquilinos)

        # Métricas del modelo
        try:
            metricas = roombot.motor_ia.obtener_metricas_modelo() or {}
        except Exception:
            metricas = {}

        acc = metricas.get("accuracy", 0) or 0
        st.metric("🧠 Precisión IA", f"{acc*100:.1f}%")

        # Mensajes en sesión
        total_mensajes = len(roombot.context.historial_conversacion or [])
        st.metric("💬 Mensajes en sesión", total_mensajes)

        st.markdown("---")

        recargar = st.button("🔄 Recargar datos")
        limpiar = st.button("🧹 Limpiar chat")

        if recargar:
            try:
                cargar_datos_inquilinos(roombot)
                st.success("Datos recargados.")
                st.rerun()
            except Exception as e:
                st.error(f"Error recargando datos: {e}")

        if limpiar:
            roombot.context.limpiar_contexto()
            st.success("Chat limpiado.")
            st.rerun()
        
        

