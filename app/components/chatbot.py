# app/components/chatbot.py - ChatBot ARREGLADO con Gráficas Detalladas
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import random
import logging

from ..core.database import obtener_todos_inquilinos

logger = logging.getLogger(__name__)

def mostrar_chatbot_avanzado(motor_ia):
    """🤖 ChatBot ARREGLADO con visualizaciones avanzadas"""
    
    # Inicializar estado del chat
    if 'mensajes_chat' not in st.session_state:
        st.session_state.mensajes_chat = []
    
    if 'inquilinos_df' not in st.session_state:
        st.session_state.inquilinos_df = cargar_inquilinos_data()
    
    # Header mejorado
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; color: white; text-align: center;'>
        <h2 style='margin: 0; font-size: 1.8rem;'>🤖 RoomBot IA</h2>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Asistente Inteligente de Compatibilidad</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar historial de mensajes
    mostrar_historial_chat()
    
    # Input del usuario
    mostrar_input_chat(motor_ia)
    
    # Sugerencias de preguntas
    mostrar_sugerencias_preguntas(motor_ia)

def cargar_inquilinos_data():
    """Carga datos de inquilinos"""
    try:
        data = obtener_todos_inquilinos()
        if data:
            df = pd.DataFrame(data)
            if 'id_inquilino' in df.columns:
                df['id_inquilino'] = pd.to_numeric(df['id_inquilino'], errors='coerce')
                df = df.dropna(subset=['id_inquilino']).astype({'id_inquilino': int})
            return df
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

def mostrar_historial_chat():
    """Muestra el historial de mensajes del chat - ARREGLADO"""
    
    with st.container():
        if not st.session_state.mensajes_chat:
            # Mensaje de bienvenida ARREGLADO
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%); 
                        padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                        border-left: 4px solid #667eea; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                    <div style='font-size: 2rem; margin-right: 0.5rem;'>🤖</div>
                    <div style='font-weight: bold; color: #667eea; font-size: 1.2rem;'>RoomBot IA</div>
                </div>
                <div style='color: #333; line-height: 1.6;'>
                    ¡Hola! Soy tu asistente inteligente de compatibilidad de inquilinos. Puedo ayudarte con:
                </div>
                <ul style='margin: 1rem 0; color: #555; line-height: 1.8;'>
                    <li>🤝 Analizar compatibilidad entre inquilinos</li>
                    <li>🏆 Encontrar las mejores recomendaciones</li>
                    <li>📊 Mostrar estadísticas detalladas con gráficas</li>
                    <li>🔍 Buscar inquilinos por características</li>
                </ul>
                <div style='color: #667eea; font-style: italic; margin-top: 1rem;'>
                    ¿En qué puedo ayudarte hoy?
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # Mostrar mensajes existentes - ARREGLADO
            mensajes_recientes = st.session_state.mensajes_chat[-8:]  # Últimos 8
            for mensaje in mensajes_recientes:
                if mensaje['tipo'] == 'usuario':
                    mostrar_mensaje_usuario(mensaje['contenido'], mensaje['timestamp'])
                else:
                    mostrar_mensaje_bot(mensaje['contenido'], mensaje['timestamp'], mensaje.get('datos'))

def mostrar_mensaje_usuario(contenido, timestamp):
    """Mensaje del usuario - ARREGLADO"""
    hora = timestamp.strftime("%H:%M")
    st.markdown(f"""
    <div style='display: flex; justify-content: flex-end; margin: 1rem 0;'>
        <div style='background: linear-gradient(135deg, #0084ff 0%, #0066cc 100%); 
                    color: white; padding: 1rem 1.2rem; border-radius: 20px 20px 5px 20px; 
                    max-width: 70%; box-shadow: 0 2px 8px rgba(0,132,255,0.3);
                    font-weight: 500;'>
            {contenido}
            <div style='text-align: right; font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem;'>
                {hora}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_mensaje_bot(contenido, timestamp, datos=None):
    """Mensaje del bot - ARREGLADO SIN HTML RESIDUAL"""
    hora = timestamp.strftime("%H:%M")
    
    # Limpiar contenido de asteriscos de markdown
    contenido_limpio = contenido.replace('**', '').replace('*', '')
    
    # Convertir a HTML limpio
    contenido_html = contenido_limpio.replace('\n', '<br>')
    
    # Mensaje principal del bot
    st.markdown(f"""
    <div style='display: flex; justify-content: flex-start; margin: 1rem 0;'>
        <div style='background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%); 
                    color: #333333; padding: 1rem 1.2rem; border-radius: 20px 20px 20px 5px; 
                    max-width: 85%; box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                    border-left: 4px solid #667eea;'>
            <div style='display: flex; align-items: center; margin-bottom: 0.8rem;'>
                <span style='font-size: 1.2rem; margin-right: 0.5rem;'>🤖</span>
                <span style='font-weight: bold; color: #667eea;'>RoomBot IA</span>
            </div>
            <div style='color: #333333; line-height: 1.6;'>
                {contenido_html}
            </div>
            <div style='font-size: 0.75rem; color: #888; margin-top: 0.8rem;'>
                {hora}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Si hay datos adicionales (gráficas), mostrarlas
    if datos and datos.get('tipo') == 'estadisticas_detalladas':
        mostrar_graficas_estadisticas(datos['df'])

def mostrar_input_chat(motor_ia):
    """Input del chat - ARREGLADO"""
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            mensaje = st.text_input(
                "Escribe tu mensaje:",
                placeholder="Ej: ¿Cuál es la compatibilidad entre 123 y 456?",
                label_visibility="collapsed"
            )
        
        with col2:
            enviar = st.form_submit_button("Enviar", type="primary", use_container_width=True)
        
        if enviar and mensaje.strip():
            procesar_mensaje(mensaje.strip(), motor_ia)
            st.rerun()

def mostrar_sugerencias_preguntas(motor_ia):
    """Sugerencias mejoradas"""
    
    df = st.session_state.inquilinos_df
    
    if not df.empty:
        st.markdown("---")
        st.markdown("**💡 Preguntas sugeridas:**")
        
        ids_ejemplo = df['id_inquilino'].head(4).tolist()
        
        # Primera fila
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Estadísticas detalladas", key="btn_stats_det"):
                procesar_mensaje("Muéstrame estadísticas detalladas con gráficas", motor_ia)
                st.rerun()
        
        with col2:
            if len(ids_ejemplo) >= 2 and st.button("🤝 Ejemplo compatibilidad", key="btn_compat"):
                procesar_mensaje(f"¿Cuál es la compatibilidad entre {ids_ejemplo[0]} y {ids_ejemplo[1]}?", motor_ia)
                st.rerun()
        
        with col3:
            if len(ids_ejemplo) >= 1 and st.button("🏆 Mejores matches", key="btn_matches"):
                procesar_mensaje(f"Encuentra los mejores matches para {ids_ejemplo[0]}", motor_ia)
                st.rerun()
        
        with col4:
            if st.button("🔍 Buscar fumadores", key="btn_search"):
                procesar_mensaje("Busca inquilinos fumadores", motor_ia)
                st.rerun()
        
        # Segunda fila
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            if st.button("🏃 Buscar deportistas", key="btn_deport"):
                procesar_mensaje("Busca inquilinos deportistas", motor_ia)
                st.rerun()
        
        with col6:
            if st.button("📈 Análisis completo", key="btn_analisis"):
                procesar_mensaje("Hazme un análisis completo del sistema", motor_ia)
                st.rerun()
        
        with col7:
            if st.button("❓ Ayuda", key="btn_help"):
                procesar_mensaje("ayuda", motor_ia)
                st.rerun()
        
        with col8:
            if len(ids_ejemplo) >= 2 and st.button("🎯 Análisis random", key="btn_random"):
                id1, id2 = random.sample(ids_ejemplo, 2)
                procesar_mensaje(f"Analiza la compatibilidad entre {id1} y {id2}", motor_ia)
                st.rerun()

def procesar_mensaje(mensaje, motor_ia):
    """Procesa mensaje - MEJORADO"""
    
    agregar_mensaje('usuario', mensaje)
    respuesta, datos_extra = generar_respuesta_avanzada(mensaje, motor_ia)
    agregar_mensaje('bot', respuesta, datos_extra)

def agregar_mensaje(tipo, contenido, datos=None):
    """Agrega mensaje al historial"""
    mensaje = {
        'tipo': tipo,
        'contenido': contenido,
        'timestamp': datetime.now(),
        'datos': datos
    }
    st.session_state.mensajes_chat.append(mensaje)
    
    if len(st.session_state.mensajes_chat) > 50:
        st.session_state.mensajes_chat = st.session_state.mensajes_chat[-50:]

def generar_respuesta_avanzada(mensaje, motor_ia):
    """Genera respuesta AVANZADA con datos para gráficas"""
    
    mensaje_lower = mensaje.lower()
    df = st.session_state.inquilinos_df
    
    try:
        # Estadísticas DETALLADAS
        if any(palabra in mensaje_lower for palabra in ['estadística', 'estadísticas', 'resumen', 'datos', 'análisis completo', 'detallad']):
            respuesta = generar_estadisticas_detalladas(df)
            datos_extra = {'tipo': 'estadisticas_detalladas', 'df': df}
            return respuesta, datos_extra
        
        # Compatibilidad
        numeros = re.findall(r'\d+', mensaje)
        if len(numeros) >= 2 and any(palabra in mensaje_lower for palabra in ['compatibilidad', 'compatible', 'analiz']):
            respuesta = generar_compatibilidad_detallada(int(numeros[0]), int(numeros[1]), df, motor_ia)
            return respuesta, None
        
        # Recomendaciones
        elif len(numeros) >= 1 and any(palabra in mensaje_lower for palabra in ['recomenda', 'match', 'mejor']):
            respuesta = generar_recomendaciones_detalladas(int(numeros[0]), df, motor_ia)
            return respuesta, None
        
        # Búsquedas
        elif any(palabra in mensaje_lower for palabra in ['busca', 'encuentra', 'filtra']):
            respuesta = generar_busqueda_detallada(mensaje_lower, df)
            return respuesta, None
        
        # Ayuda
        elif any(palabra in mensaje_lower for palabra in ['ayuda', 'help']):
            respuesta = generar_ayuda_detallada()
            return respuesta, None
        
        # Saludos
        elif any(palabra in mensaje_lower for palabra in ['hola', 'buenos', 'saludos']):
            respuesta = "¡Hola! 👋 Soy RoomBot IA, tu asistente especializado en compatibilidad de inquilinos. Estoy equipado con análisis avanzado, gráficas interactivas y recomendaciones inteligentes. ¿En qué puedo ayudarte hoy?"
            return respuesta, None
        
        # Respuesta genérica
        else:
            respuesta = generar_respuesta_generica_mejorada(mensaje, numeros)
            return respuesta, None
            
    except Exception as e:
        logger.error(f"Error generando respuesta: {e}")
        respuesta = f"❌ Lo siento, hubo un error procesando tu solicitud: {str(e)}"
        return respuesta, None

def generar_estadisticas_detalladas(df):
    """Genera estadísticas MUY DETALLADAS SIN ASTERISCOS"""
    
    if df.empty:
        return "❌ No hay inquilinos registrados en el sistema."
    
    total = len(df)
    edad_promedio = df['edad'].mean() if 'edad' in df else 0
    edad_mediana = df['edad'].median() if 'edad' in df else 0
    
    respuesta = f"""📊 ANÁLISIS ESTADÍSTICO COMPLETO DEL SISTEMA

🔢 MÉTRICAS GENERALES:
• Total de inquilinos registrados: {total}
• Edad promedio: {edad_promedio:.1f} años
• Edad mediana: {edad_mediana:.1f} años
• Rango de edades: {df['edad'].min():.0f} - {df['edad'].max():.0f} años

📈 DISTRIBUCIÓN POR CARACTERÍSTICAS:
"""
    
    # Analizar cada categoría en detalle
    categorias = {
        'fumador': '🚬 Hábito de Fumar',
        'mascotas': '🐕 Mascotas', 
        'orden': '🧹 Nivel de Orden',
        'deporte': '⚽ Actividad Deportiva',
        'bioritmo': '⏰ Ritmo de Vida',
        'nivel_educativo': '🎓 Nivel Educativo',
        'personalidad': '😊 Personalidad'
    }
    
    for categoria, titulo in categorias.items():
        if categoria in df.columns:
            conteos = df[categoria].value_counts()
            respuesta += f"\n{titulo}:\n"
            
            for valor, count in conteos.items():
                porcentaje = (count / total) * 100
                barra = "█" * int(porcentaje / 5)  # Barra visual
                respuesta += f"   • {valor}: {count} inquilinos ({porcentaje:.1f}%) {barra}\n"
    
    # Análisis de compatibilidad general
    if 'compatible' in df.columns:
        compatibles = (df['compatible'] == 1).sum()
        porcentaje_compat = (compatibles / total) * 100
        respuesta += f"""
🎯 ÍNDICE DE COMPATIBILIDAD GENERAL:
• Inquilinos altamente compatibles: {compatibles} de {total} ({porcentaje_compat:.1f}%)
• Potencial de matches exitosos: {'Alto' if porcentaje_compat > 50 else 'Medio' if porcentaje_compat > 30 else 'Bajo'}
"""
    
    # Insights adicionales
    respuesta += f"""
💡 INSIGHTS CLAVE:
• Perfil predominante: {obtener_perfil_predominante(df)}
• Oportunidades de matching: {obtener_oportunidades_matching(df)}
• Recomendación del sistema: {obtener_recomendacion_sistema(df)}

📊 Consulta las gráficas circulares detalladas abajo para visualizar mejor los datos
"""
    
    return respuesta

def mostrar_graficas_estadisticas(df):
    """Muestra gráficas circulares DETALLADAS tipo reloj"""
    
    if df.empty:
        return
    
    st.markdown("### 📊 Visualizaciones Detalladas")
    
    # Configurar gráficas en 2 columnas
    col1, col2 = st.columns(2)
    
    categorias_principales = ['fumador', 'mascotas', 'orden', 'deporte']
    
    for i, categoria in enumerate(categorias_principales):
        if categoria in df.columns:
            with col1 if i % 2 == 0 else col2:
                crear_grafica_circular(df, categoria)
    
    # Gráfica de edad
    if 'edad' in df.columns:
        st.markdown("#### 📈 Distribución de Edades")
        crear_histograma_edad(df)
    
    # Gráfica de compatibilidad general
    if 'compatible' in df.columns:
        st.markdown("#### 🎯 Índice de Compatibilidad General")
        crear_grafica_compatibilidad(df)

def crear_grafica_circular(df, categoria):
    """Crea gráfica circular tipo reloj para una categoría"""
    
    conteos = df[categoria].value_counts()
    
    # Colores personalizados según categoría
    colores = {
        'fumador': ['#ff6b6b', '#51cf66'],
        'mascotas': ['#ffd43b', '#74c0fc'],  
        'orden': ['#ff8cc8', '#69db7c'],
        'deporte': ['#ff922b', '#15aabf']
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=conteos.index,
        values=conteos.values,
        hole=0.4,  # Hace el gráfico tipo donut
        textinfo='label+percent+value',
        textfont_size=12,
        marker=dict(
            colors=colores.get(categoria, px.colors.qualitative.Set3),
            line=dict(color='#FFFFFF', width=2)
        )
    )])
    
    fig.update_layout(
        title={
            'text': f'📊 {categoria.title().replace("_", " ")}',
            'x': 0.5,
            'font': {'size': 16, 'color': '#333'}
        },
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        font=dict(family="Arial", size=12, color="#333")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def crear_histograma_edad(df):
    """Crea histograma de edades"""
    
    fig = px.histogram(
        df, 
        x='edad', 
        nbins=15,
        title='Distribución de Edades',
        color_discrete_sequence=['#667eea']
    )
    
    fig.update_layout(
        title={'x': 0.5, 'font': {'size': 16}},
        xaxis_title="Edad (años)",
        yaxis_title="Número de Inquilinos",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def crear_grafica_compatibilidad(df):
    """Crea gráfica de compatibilidad general"""
    
    compatibles = (df['compatible'] == 1).sum()
    no_compatibles = (df['compatible'] == 0).sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=['Alta Compatibilidad', 'Baja Compatibilidad'],
        values=[compatibles, no_compatibles],
        hole=0.5,
        textinfo='label+percent+value',
        marker=dict(
            colors=['#51cf66', '#ff6b6b'],
            line=dict(color='#FFFFFF', width=3)
        )
    )])
    
    fig.update_layout(
        title={'text': '🎯 Índice de Compatibilidad General', 'x': 0.5},
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def generar_compatibilidad_detallada(id1, id2, df, motor_ia):
    """Análisis de compatibilidad SÚPER DETALLADO SIN ASTERISCOS"""
    
    if df.empty:
        return "❌ No hay inquilinos registrados para analizar."
    
    if id1 not in df['id_inquilino'].values:
        return f"❌ No encontré inquilino con ID {id1}"
    
    if id2 not in df['id_inquilino'].values:
        return f"❌ No encontré inquilino con ID {id2}"
    
    if id1 == id2:
        return "❌ No puedo analizar la compatibilidad de un inquilino consigo mismo."
    
    try:
        # Obtener datos completos
        row1 = df[df['id_inquilino'] == id1].iloc[0]
        row2 = df[df['id_inquilino'] == id2].iloc[0]
        
        nombre1 = row1['nombre']
        nombre2 = row2['nombre']
        
        # Calcular compatibilidad
        if motor_ia and motor_ia.is_trained:
            try:
                resultado = motor_ia.calcular_compatibilidad_avanzada(id1, id2, df)
                if 'error' not in resultado:
                    compatibilidad = resultado['compatibilidad_porcentaje']
                else:
                    compatibilidad = calcular_compatibilidad_simple(id1, id2, df)
            except:
                compatibilidad = calcular_compatibilidad_simple(id1, id2, df)
        else:
            compatibilidad = calcular_compatibilidad_simple(id1, id2, df)
        
        # Análisis detallado por factor
        factores = ['fumador', 'mascotas', 'orden', 'deporte', 'bioritmo', 'visitas']
        analisis_factores = []
        coincidencias = 0
        
        for factor in factores:
            if factor in row1.index and factor in row2.index:
                val1 = str(row1[factor])
                val2 = str(row2[factor])
                coincide = val1 == val2
                
                if coincide:
                    coincidencias += 1
                
                analisis_factores.append({
                    'factor': factor,
                    'inquilino1': val1,
                    'inquilino2': val2,
                    'coincide': coincide,
                    'impacto': obtener_impacto_factor(factor)
                })
        
        # Generar respuesta limpia SIN ASTERISCOS
        respuesta = f"""🤝 ANÁLISIS COMPLETO DE COMPATIBILIDAD

👤 INQUILINOS ANALIZADOS:
• {nombre1} (ID: {id1}) - Edad: {row1.get('edad', 'N/A')} años
• {nombre2} (ID: {id2}) - Edad: {row2.get('edad', 'N/A')} años

📊 RESULTADO DE COMPATIBILIDAD:
• Puntuación General: {compatibilidad:.1f}%
• Coincidencias: {coincidencias} de {len(analisis_factores)} factores
• Nivel de Confianza: {'Alto' if compatibilidad >= 70 else 'Medio' if compatibilidad >= 50 else 'Bajo'}

🔍 ANÁLISIS DETALLADO POR FACTOR:
"""
        
        for analisis in analisis_factores:
            icono = "✅" if analisis['coincide'] else "❌"
            respuesta += f"\n{analisis['factor'].title()} ({analisis['impacto']}):\n"
            respuesta += f"   {icono} {nombre1}: {analisis['inquilino1']} | {nombre2}: {analisis['inquilino2']}\n"
        
        # Recomendación específica
        if compatibilidad >= 85:
            respuesta += f"\n🏆 RECOMENDACIÓN: ¡Excelente match! Esta combinación tiene muy alta probabilidad de éxito."
        elif compatibilidad >= 70:
            respuesta += f"\n👍 RECOMENDACIÓN: Buena compatibilidad. Recomendable como roommates."
        elif compatibilidad >= 50:
            respuesta += f"\n⚠️ RECOMENDACIÓN: Compatibilidad moderada. Evaluar factores específicos importantes para cada uno."
        else:
            respuesta += f"\n❌ RECOMENDACIÓN: Baja compatibilidad. Considerar otros candidatos."
        
        # Consejos específicos
        respuesta += f"\n\n💡 CONSEJOS PARA LA CONVIVENCIA:"
        respuesta += obtener_consejos_convivencia(analisis_factores, compatibilidad)
        
        return respuesta
        
    except Exception as e:
        return f"❌ Error calculando compatibilidad detallada: {str(e)}"

def generar_recomendaciones_detalladas(id_inquilino, df, motor_ia):
    """Recomendaciones MUY DETALLADAS SIN ASTERISCOS"""
    
    if df.empty:
        return "❌ No hay inquilinos registrados para analizar."
    
    if id_inquilino not in df['id_inquilino'].values:
        return f"❌ No encontré inquilino con ID {id_inquilino}"
    
    try:
        inquilino_base = df[df['id_inquilino'] == id_inquilino].iloc[0]
        nombre_base = inquilino_base['nombre']
        otros_inquilinos = df[df['id_inquilino'] != id_inquilino]
        
        if len(otros_inquilinos) == 0:
            return "❌ No hay otros inquilinos para generar recomendaciones."
        
        # Calcular compatibilidades detalladas
        recomendaciones = []
        
        for _, otro in otros_inquilinos.head(20).iterrows():
            try:
                if motor_ia and motor_ia.is_trained:
                    try:
                        resultado = motor_ia.calcular_compatibilidad_avanzada(id_inquilino, otro['id_inquilino'], df)
                        if 'error' not in resultado:
                            compatibilidad = resultado['compatibilidad_porcentaje']
                        else:
                            compatibilidad = calcular_compatibilidad_simple(id_inquilino, otro['id_inquilino'], df)
                    except:
                        compatibilidad = calcular_compatibilidad_simple(id_inquilino, otro['id_inquilino'], df)
                else:
                    compatibilidad = calcular_compatibilidad_simple(id_inquilino, otro['id_inquilino'], df)
                
                # Analizar factores en común
                factores_comunes = obtener_factores_comunes(inquilino_base, otro)
                diferencias_clave = obtener_diferencias_clave(inquilino_base, otro)
                
                recomendaciones.append({
                    'id': otro['id_inquilino'],
                    'nombre': otro['nombre'],
                    'edad': otro.get('edad', 'N/A'),
                    'compatibilidad': compatibilidad,
                    'factores_comunes': factores_comunes,
                    'diferencias': diferencias_clave,
                    'perfil': obtener_perfil_resumen(otro)
                })
            except:
                continue
        
        # Ordenar por compatibilidad
        recomendaciones.sort(key=lambda x: x['compatibilidad'], reverse=True)
        
        # Generar respuesta limpia SIN ASTERISCOS
        respuesta = f"""🏆 RECOMENDACIONES DETALLADAS PARA {nombre_base} (ID: {id_inquilino})

👤 PERFIL BASE:
• Edad: {inquilino_base.get('edad', 'N/A')} años
• Características: {obtener_perfil_resumen(inquilino_base)}

🎯 TOP 5 MATCHES RECOMENDADOS:
"""
        
        for i, rec in enumerate(recomendaciones[:5], 1):
            factores_texto = ', '.join(rec['factores_comunes'][:3]) if rec['factores_comunes'] else 'Ninguno'
            diferencias_texto = ', '.join(rec['diferencias'][:2]) if rec['diferencias'] else 'Ninguna'
            
            respuesta += f"""
{i}. {rec['nombre']} (ID: {rec['id']}) - {rec['compatibilidad']:.1f}% compatibilidad
   📊 Edad: {rec['edad']} años
   ✅ En común: {factores_texto}
   ⚠️ Diferencias: {diferencias_texto}
   🔖 Perfil: {rec['perfil']}
"""
        
        # Análisis estadístico
        avg_compatibility = sum(r['compatibilidad'] for r in recomendaciones[:10]) / min(len(recomendaciones), 10)
        mejores_opciones = len([r for r in recomendaciones if r['compatibilidad'] >= 70])
        
        respuesta += f"""
📈 ANÁLISIS ESTADÍSTICO:
• Compatibilidad promedio: {avg_compatibility:.1f}%
• Mejores opciones disponibles: {mejores_opciones}
• Recomendación del sistema: {'Excelentes opciones disponibles' if avg_compatibility >= 60 else 'Opciones moderadas, evaluar cuidadosamente'}

💡 Analiza en detalle cualquier pareja específica para obtener más información
"""
        
        return respuesta
        
    except Exception as e:
        return f"❌ Error generando recomendaciones detalladas: {str(e)}"

def generar_busqueda_detallada(mensaje, df):
    """Búsqueda DETALLADA con análisis"""
    
    if df.empty:
        return "❌ No hay inquilinos registrados para buscar."
    
    # Mapear términos de búsqueda expandido
    busquedas = {
        'fumador': ('fumador', 'si'),
        'no fumador': ('fumador', 'no'),
        'deportista': ('deporte', 'si'),
        'sedentario': ('deporte', 'no'),
        'mascota': ('mascotas', 'con mascotas'),
        'sin mascota': ('mascotas', 'sin mascotas'),
        'ordenad': ('orden', 'ordenada'),
        'desordenad': ('orden', 'desordenada'),
        'madrugador': ('bioritmo', 'madrugador'),
        'nocturno': ('bioritmo', 'nocturno'),
        'universitario': ('nivel_educativo', 'universitaria'),
        'extrovertido': ('personalidad', 'extrovertido'),
        'introvertido': ('personalidad', 'introvertido')
    }
    
    # Encontrar término
    campo = None
    valor = None
    termino_usado = None
    
    for termino, (c, v) in busquedas.items():
        if termino in mensaje:
            campo = c
            valor = v
            termino_usado = termino
            break
    
    if not campo:
        return "❓ No entendí qué característica buscas. Intenta con: fumadores, deportistas, ordenados, nocturnos, universitarios, etc."
    
    try:
        if campo not in df.columns:
            return f"❌ No tengo información sobre '{campo}' en la base de datos."
        
        resultados = df[df[campo] == valor]
        total_inquilinos = len(df)
        
        if len(resultados) == 0:
            return f"❌ No encontré inquilinos con la característica '{termino_usado}'"
        
        # Análisis estadístico
        porcentaje = (len(resultados) / total_inquilinos) * 100
        edad_promedio = resultados['edad'].mean() if 'edad' in resultados else 0
        
        respuesta = f"""🔍 **BÚSQUEDA DETALLADA: {termino_usado.upper()}S**

📊 **ESTADÍSTICAS:**
• **Total encontrados**: {len(resultados)} de {total_inquilinos} inquilinos ({porcentaje:.1f}%)
• **Edad promedio**: {edad_promedio:.1f} años
• **Representatividad**: {'Alta' if porcentaje > 40 else 'Media' if porcentaje > 20 else 'Baja'}

👥 **INQUILINOS ENCONTRADOS:**
"""
        
        for _, inquilino in resultados.head(15).iterrows():
            edad = inquilino.get('edad', 'N/A')
            perfil = obtener_perfil_resumen(inquilino)
            respuesta += f"• **{inquilino['nombre']}** (ID: {inquilino['id_inquilino']}) - {edad} años - {perfil}\n"
        
        if len(resultados) > 15:
            respuesta += f"\n... y {len(resultados) - 15} más."
        
        # Características adicionales del grupo
        if len(resultados) > 1:
            respuesta += f"\n\n🔍 **CARACTERÍSTICAS DEL GRUPO:**"
            respuesta += obtener_analisis_grupo(resultados)
        
        return respuesta
        
    except Exception as e:
        return f"❌ Error en la búsqueda detallada: {str(e)}"

def generar_ayuda_detallada():
    """Ayuda COMPLETA del sistema"""
    
    return """🤖 **GUÍA COMPLETA DE ROOMBOT IA**

🎯 **ANÁLISIS DE COMPATIBILIDAD:**
• "¿Cuál es la compatibilidad entre 123 y 456?"
• "Analiza detalladamente 789 y 101"
• "Compara los inquilinos 234 y 567"

🏆 **RECOMENDACIONES INTELIGENTES:**
• "Encuentra los mejores matches para 123"
• "¿Quién es más compatible con 456?"
• "Recomiéndame 5 opciones para 789"

📊 **ESTADÍSTICAS Y ANÁLISIS:**
• "Muéstrame estadísticas detalladas"
• "Análisis completo del sistema"
• "Datos con gráficas circulares"

🔍 **BÚSQUEDAS ESPECIALIZADAS:**
• "Busca inquilinos fumadores"
• "Encuentra deportistas universitarios"
• "Muestra personas ordenadas y madrugadoras"
• "Busca nocturnos con mascotas"

💡 **CARACTERÍSTICAS AVANZADAS:**
✅ Análisis con IA y machine learning
✅ Gráficas circulares interactivas tipo reloj
✅ Explicaciones detalladas de compatibilidad
✅ Recomendaciones personalizadas
✅ Estadísticas visuales avanzadas
✅ Búsquedas inteligentes por múltiples criterios

🎨 **VISUALIZACIONES DISPONIBLES:**
• Gráficas circulares (tipo donut/reloj)
• Histogramas de distribución
• Análisis de compatibilidad visual
• Métricas en tiempo real

¡Explora todas las funcionalidades usando lenguaje natural! 🚀"""

def generar_respuesta_generica_mejorada(mensaje, numeros):
    """Respuesta genérica MEJORADA"""
    
    if len(numeros) >= 2:
        return f"🤔 Veo que mencionas los números {numeros[0]} y {numeros[1]}. ¿Quieres que analice la compatibilidad entre estos inquilinos? Solo pregúntame: '¿Cuál es la compatibilidad entre {numeros[0]} y {numeros[1]}?'"
    
    elif len(numeros) == 1:
        return f"🤔 Mencionas el número {numeros[0]}. ¿Buscas recomendaciones para este inquilino? Pregúntame: 'Encuentra los mejores matches para {numeros[0]}'"
    
    else:
        respuestas = [
            "🤔 No estoy seguro de entender tu consulta. ¿Podrías ser más específico sobre qué necesitas?",
            "❓ Puedo ayudarte con análisis de compatibilidad, recomendaciones, estadísticas detalladas o búsquedas especializadas.",
            "💡 Usa los botones de sugerencias o escribe 'ayuda' para ver todas mis capacidades avanzadas.",
            "🎯 Puedes preguntarme sobre cualquier aspecto del sistema de compatibilidad de inquilinos."
        ]
        return random.choice(respuestas)

# ============================================================================
# FUNCIONES AUXILIARES DETALLADAS
# ============================================================================

def calcular_compatibilidad_simple(id1, id2, df):
    """Cálculo de compatibilidad MEJORADO"""
    try:
        row1 = df[df['id_inquilino'] == id1].iloc[0]
        row2 = df[df['id_inquilino'] == id2].iloc[0]
        
        # Factores con pesos diferentes
        factores_pesos = {
            'fumador': 0.25,
            'orden': 0.20,
            'bioritmo': 0.20,
            'mascotas': 0.15,
            'deporte': 0.10,
            'visitas': 0.05,
            'personalidad': 0.05
        }
        
        compatibilidad_total = 0
        peso_total = 0
        
        for factor, peso in factores_pesos.items():
            if factor in row1.index and factor in row2.index:
                peso_total += peso
                if row1[factor] == row2[factor]:
                    compatibilidad_total += peso
        
        if peso_total == 0:
            return 50.0
        
        # Bonus por edad similar
        if 'edad' in row1.index and 'edad' in row2.index:
            diff_edad = abs(row1['edad'] - row2['edad'])
            bonus_edad = max(0, (10 - diff_edad) / 10) * 0.1
            compatibilidad_total += bonus_edad
            peso_total += 0.1
        
        return min(95.0, (compatibilidad_total / peso_total) * 100)
        
    except:
        return 50.0

def obtener_perfil_predominante(df):
    """Determina el perfil predominante"""
    if df.empty:
        return "No determinado"
    
    perfiles = []
    if 'fumador' in df.columns:
        no_fumadores = (df['fumador'] == 'no').mean()
        if no_fumadores > 0.6:
            perfiles.append("No fumadores")
    
    if 'deporte' in df.columns:
        deportistas = (df['deporte'] == 'si').mean()
        if deportistas > 0.5:
            perfiles.append("Deportistas")
    
    if 'orden' in df.columns:
        ordenados = (df['orden'] == 'ordenada').mean()
        if ordenados > 0.5:
            perfiles.append("Ordenados")
    
    return ", ".join(perfiles) if perfiles else "Diverso"

def obtener_oportunidades_matching(df):
    """Determina oportunidades de matching"""
    if df.empty:
        return "No determinado"
    
    total = len(df)
    if total < 10:
        return "Base pequeña, expandir registro"
    elif total < 50:
        return "Base creciente, buenas oportunidades"
    else:
        return "Base amplia, excelentes oportunidades"

def obtener_recomendacion_sistema(df):
    """Recomendación general del sistema"""
    if df.empty:
        return "Registrar más inquilinos"
    
    total = len(df)
    if 'compatible' in df.columns:
        tasa_compat = (df['compatible'] == 1).mean()
        if tasa_compat > 0.6:
            return "Sistema optimizado para matches exitosos"
        elif tasa_compat > 0.4:
            return "Buen balance para matching efectivo"
        else:
            return "Ampliar criterios de compatibilidad"
    
    return "Continuar registro y análisis"

def obtener_impacto_factor(factor):
    """Determina el impacto de cada factor"""
    impactos = {
        'fumador': 'Alto Impacto',
        'orden': 'Alto Impacto', 
        'bioritmo': 'Alto Impacto',
        'mascotas': 'Impacto Medio',
        'deporte': 'Impacto Medio',
        'visitas': 'Impacto Bajo',
        'personalidad': 'Impacto Bajo'
    }
    return impactos.get(factor, 'Impacto Medio')

def obtener_consejos_convivencia(analisis_factores, compatibilidad):
    """Genera consejos específicos de convivencia"""
    consejos = []
    
    for factor in analisis_factores:
        if not factor['coincide']:
            if factor['factor'] == 'fumador':
                consejos.append("• Establecer reglas claras sobre fumar en espacios comunes")
            elif factor['factor'] == 'orden':
                consejos.append("• Definir estándares de limpieza y organización")
            elif factor['factor'] == 'bioritmo':
                consejos.append("• Acordar horarios de silencio y actividades")
            elif factor['factor'] == 'mascotas':
                consejos.append("• Discutir políticas sobre mascotas y responsabilidades")
    
    if compatibilidad >= 70:
        consejos.append("• Mantener comunicación abierta para optimizar la convivencia")
    else:
        consejos.append("• Establecer reuniones periódicas para resolver diferencias")
    
    return "\n" + "\n".join(consejos) if consejos else "\n• Excelente base para una convivencia armoniosa"

def obtener_factores_comunes(inquilino1, inquilino2):
    """Identifica factores en común entre dos inquilinos"""
    factores = ['fumador', 'mascotas', 'orden', 'deporte', 'bioritmo', 'nivel_educativo']
    comunes = []
    
    for factor in factores:
        if factor in inquilino1.index and factor in inquilino2.index:
            if inquilino1[factor] == inquilino2[factor]:
                comunes.append(f"{factor}: {inquilino1[factor]}")
    
    return comunes

def obtener_diferencias_clave(inquilino1, inquilino2):
    """Identifica diferencias clave entre dos inquilinos"""
    factores = ['fumador', 'mascotas', 'orden', 'deporte', 'bioritmo']
    diferencias = []
    
    for factor in factores:
        if factor in inquilino1.index and factor in inquilino2.index:
            if inquilino1[factor] != inquilino2[factor]:
                diferencias.append(f"{factor}")
    
    return diferencias

def obtener_perfil_resumen(inquilino):
    """Genera un resumen del perfil del inquilino"""
    caracteristicas = []
    
    if 'fumador' in inquilino.index:
        caracteristicas.append("No fumador" if inquilino['fumador'] == 'no' else "Fumador")
    
    if 'deporte' in inquilino.index:
        caracteristicas.append("Deportista" if inquilino['deporte'] == 'si' else "Sedentario")
        
    if 'orden' in inquilino.index:
        caracteristicas.append("Ordenado" if inquilino['orden'] == 'ordenada' else "Relajado")
    
    if 'bioritmo' in inquilino.index:
        caracteristicas.append("Madrugador" if inquilino['bioritmo'] == 'madrugador' else "Nocturno")
    
    return ", ".join(caracteristicas[:3])

def obtener_analisis_grupo(grupo_df):
    """Analiza características de un grupo de inquilinos"""
    if grupo_df.empty:
        return ""
    
    analisis = []
    
    # Edad
    if 'edad' in grupo_df.columns:
        edad_prom = grupo_df['edad'].mean()
        analisis.append(f"Edad promedio: {edad_prom:.1f} años")
    
    # Características predominantes
    factores = ['fumador', 'deporte', 'orden', 'bioritmo']
    for factor in factores:
        if factor in grupo_df.columns:
            moda = grupo_df[factor].mode()
            if not moda.empty:
                freq = (grupo_df[factor] == moda.iloc[0]).mean() * 100
                if freq > 60:
                    analisis.append(f"Predominantemente {moda.iloc[0]} en {factor}")
    
    return "\n• " + "\n• ".join(analisis) if analisis else "\nGrupo diverso sin características predominantes"