import pandas as pd
import streamlit as st
import boto3
import io
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
# ==========================================
# CONFIGURACIÓN DE AWS
# ==========================================
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-west-1'  # Hardcoded - tu región
)

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="⚽ Mundial 2026 Analisis",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS PERSONALIZADOS
# ==========================================
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 1rem 0;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
}
div[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# CARGA DESDE S3
# ==========================================
@st.cache_data(ttl=600)
def cargar_csv_desde_s3(bucket, key):
    """Carga un archivo CSV desde S3 con cache"""
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()
        return pd.read_csv(io.BytesIO(body))
    except Exception as e:
        st.error(f"❌ Error al cargar {key}: {e}")
        st.error(f"Bucket: {bucket}, Key: {key}")
        return pd.DataFrame()
        
# ==========================================
# CONFIGURACIÓN S3
# ==========================================
BUCKET = "xideralaws-curso-yalbani"
PREFIX = "datos_limpios/"
PREFIX_LAMBDA = "datos_limpios/lambda/"

# ==========================================
# CARGAR DATOS
# ==========================================
with st.spinner("🔄 Cargando datos desde S3..."):
    # Datos asistencia y estadios
    df_asistencia = cargar_csv_desde_s3(BUCKET, f"{PREFIX}tabla_final.csv")
    df_estadios = cargar_csv_desde_s3(BUCKET, f"{PREFIX}df_grafica_individual.csv")
    df_resumen_paises = cargar_csv_desde_s3(BUCKET, f"{PREFIX}tabla_ordenada_max.csv")
    df_victorias = cargar_csv_desde_s3(BUCKET, f"{PREFIX}df_analisis_victoria.csv")
    df_goles = cargar_csv_desde_s3(BUCKET, f"{PREFIX}df_conteo_goles.csv")
    df_proyeccion = cargar_csv_desde_s3(BUCKET, f"{PREFIX}df_proyeccion_financiera.csv")
    
    # Datos de jugadores
    df_top50_paises = cargar_csv_desde_s3(BUCKET, f"{PREFIX_LAMBDA}analisis_top_50_ga_paises.csv")
    df_goleadores_top3 = cargar_csv_desde_s3(BUCKET, f"{PREFIX_LAMBDA}analisis_goleadores_top_3.csv")
    df_top10_paises_goleadores = cargar_csv_desde_s3(BUCKET, f"{PREFIX_LAMBDA}analisis_top_10_paises_goleadores.csv")

# ==========================================
# HEADER PRINCIPAL
# ==========================================
st.markdown('<h1 class="main-header">⚽🏆 DASHBOARD PROYECTO FINAL: ANÁLISIS MUNDIAL 2026 🏆⚽</h1>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# SIDEBAR - NAVEGACIÓN Y FILTROS
# ==========================================
st.sidebar.image("https://i.pinimg.com/736x/44/24/8d/44248da179630acb5098361137c8e900.jpg", width=200)
st.sidebar.title("🎯 Panel de Control")
st.sidebar.markdown("---")

# Seccion de análisis
seccion = st.sidebar.radio(
    "📊 Selecciona un Análisis:",
    [
        "🏟️ Asistencia y Capacidad",
        "🌎 Estadios por País Local",
        "⚽ Análisis de Goles",
        "💰 Proyección Financiera",
        "👤 Análisis de Jugadores"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Datos actualizados desde S3**\n\n Acceso concedido en S3 para explorar los análisis del Mundial 2026.")

# ==========================================
# SECCIÓN 1: ASISTENCIA Y CAPACIDAD
# ==========================================
if seccion == "🏟️ Asistencia y Capacidad":
    st.header("🏟️ Análisis de Asistencia vs Capacidad de Estadios")
    
    if not df_asistencia.empty:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total de Eventos",
                value=f"{len(df_asistencia):,}",
                delta="Histórico completo de eventos"
            )
        
        with col2:
            promedio_llenado = df_asistencia['Porcentaje_Llenado'].mean()
            st.metric(
                label="📈 Promedio de sold-out de estadios",
                value=f"{promedio_llenado:.1f}%",
                delta=f"{promedio_llenado - 80:.1f}% vs 80%"
            )
        
        with col3:
            max_asistencia = df_asistencia['HIGHEST_ATTENDANCE'].max()
            st.metric(
                label="👥 Máxima Asistencia",
                value=f"{max_asistencia:,.0f}",
                delta="Récord histórico"
            )
        
        with col4:
            eventos_llenos = len(df_asistencia[df_asistencia['Porcentaje_Llenado'] >= 95])
            st.metric(
                label="🎉 Eventos >95% Llenos",
                value=eventos_llenos,
                delta=f"{(eventos_llenos/len(df_asistencia)*100):.1f}%"
            )
        
        st.markdown("---")
        
        # Filtros en Sidebar
        st.sidebar.markdown("### 🔍 Filtros de Asistencia")
        min_llenado = st.sidebar.slider(
            "Porcentaje mínimo de sold-out en estadios (%)",
            min_value=0,
            max_value=100,
            value=0,
            step=5
        )
        
        years_disponibles = sorted(df_asistencia['Year'].dropna().unique())
        years_seleccionados = st.sidebar.multiselect(
            "Años",
            options=years_disponibles,
            default=years_disponibles
        )
        
        # Aplicar filtros
        df_filtrado = df_asistencia[
            (df_asistencia['Porcentaje_Llenado'] >= min_llenado) &
            (df_asistencia['Year'].isin(years_seleccionados))
        ].copy()
        
        # Tabs para diferentes visualizaciones
        tab1, tab2, tab3 = st.tabs(["📊 Top 10", "📉 Menor sold-out", "📋 Datos Detallados"])
        
        with tab1:
            st.subheader("🏆 Top 10 Eventos con Mayor Porcentaje de SOLD-OUT")
            top_10 = df_filtrado.head(10).copy()
            top_10['Label'] = top_10['STADIUM'] + ' (' + top_10['Year'].astype(str) + ')'
            
            fig_top = px.bar(
                top_10.sort_values('Porcentaje_Llenado', ascending=True),
                x='Porcentaje_Llenado',
                y='Label',
                orientation='h',
                color='Porcentaje_Llenado',
                color_continuous_scale='Viridis',
                text='Porcentaje_Llenado',
                title='Top 10 Eventos con Mayor Porcentaje de Sold Out'
            )
            fig_top.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_top.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_top, use_container_width=True)
        
        with tab2:
            st.subheader("📉 Top 10 Eventos con Menor Porcentaje de sold-out")
            bottom_10 = df_filtrado.tail(10).copy()
            bottom_10['Label'] = bottom_10['STADIUM'] + ' (' + bottom_10['Year'].astype(str) + ')'
            
            fig_bottom = px.bar(
                bottom_10.sort_values('Porcentaje_Llenado', ascending=True),
                x='Porcentaje_Llenado',
                y='Label',
                orientation='h',
                color='Porcentaje_Llenado',
                color_continuous_scale='Reds_r',
                text='Porcentaje_Llenado',
                title='Top 10 Eventos con Menor Porcentaje de Sold Out'
            )
            fig_bottom.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bottom.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_bottom, use_container_width=True)
        
        with tab3:
            st.subheader("📋 Tabla de Datos Completa")
            st.dataframe(
                df_filtrado.style.background_gradient(subset=['Porcentaje_Llenado'], cmap='RdYlGn'),
                use_container_width=True,
                height=400
            )

# ==========================================
# SECCIÓN 2: ESTADIOS POR PAÍS
# ==========================================
elif seccion == "🌎 Estadios por País Local":
    st.header("🌎 Análisis de Estadios por País Anfitrión")
    
    if not df_estadios.empty and not df_resumen_paises.empty:
        # KPIs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_estadios = len(df_estadios)
            st.metric("🏟️ Total de Estadios", total_estadios)
        
        with col2:
            capacidad_total = df_estadios['Capacity'].sum()
            st.metric("👥 Capacidad Total", f"{capacidad_total:,.0f}")
        
        with col3:
            capacidad_promedio = df_estadios['Capacity'].mean()
            st.metric("📊 Capacidad Promedio", f"{capacidad_promedio:,.0f}")
        
        st.markdown("---")
        
        # Filtros
        st.sidebar.markdown("### 🔍 Filtros de Estadios")
        paises_disponibles = df_estadios['Country'].unique()
        paises_seleccionados = st.sidebar.multiselect(
            "Países",
            options=paises_disponibles,
            default=paises_disponibles
        )
        
        df_estadios_filtrado = df_estadios[df_estadios['Country'].isin(paises_seleccionados)]
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Por País", "🏟️ Todos los Estadios", "📈 Comparativa"])
        
        with tab1:
            st.subheader("📊 Resumen de Capacidad por País")
            col_a, col_b = st.columns(2)
            
            with col_a:
                fig_max = px.bar(
                    df_resumen_paises,
                    x='Country',
                    y='Capacidad_Maxima',
                    color='Country',
                    title='Capacidad Máxima por País',
                    text='Capacidad_Maxima'
                )
                fig_max.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig_max.update_layout(showlegend=False)
                st.plotly_chart(fig_max, use_container_width=True)
            
            with col_b:
                fig_prom = px.bar(
                    df_resumen_paises,
                    x='Country',
                    y='Capacidad_Promedio',
                    color='Country',
                    title='Capacidad Promedio por País',
                    text='Capacidad_Promedio'
                )
                fig_prom.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig_prom.update_layout(showlegend=False)
                st.plotly_chart(fig_prom, use_container_width=True)
        
        with tab2:
            st.subheader("🏟️ Capacidad Individual de Cada Estadio")
            fig_todos = px.bar(
                df_estadios_filtrado.sort_values('Capacity', ascending=True),
                x='Capacity',
                y='Stadium',
                color='Country',
                orientation='h',
                title='Capacidad de Estadios Individuales',
                text='Capacity',
                height=max(600, len(df_estadios_filtrado) * 25)
            )
            fig_todos.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig_todos, use_container_width=True)
        
        with tab3:
            st.subheader("📈 Comparativa General")
            st.dataframe(df_resumen_paises, use_container_width=True)

# ==========================================
# SECCIÓN 3: ANÁLISIS DE GOLES
# ==========================================
elif seccion == "⚽ Análisis de Goles":
    st.header("⚽ Análisis de Goles y Victorias Locales")
    
    if not df_victorias.empty and not df_goles.empty:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_partidos = df_victorias['Total_Partidos'].sum()
            st.metric("⚽ Partidos >4 Goles", f"{total_partidos:,}")
        
        with col2:
            prom_victoria_local = df_victorias['Porcentaje_Victoria_Local'].mean()
            st.metric("🏠 Victoria Local Promedio", f"{prom_victoria_local:.1f}%")
        
        with col3:
            total_encuentros = df_goles['Total_Encuentros'].sum()
            st.metric("📊 Total Encuentros", total_encuentros)
        
        with col4:
            max_goles = df_goles['total_goles'].max()
            st.metric("🔥 Máximo de Goles", f"{max_goles} goles")
        
        st.markdown("---")
        
        # Filtros
        st.sidebar.markdown("### 🔍 Filtros de Goles")
        min_partidos = st.sidebar.slider(
            "Mínimo de partidos por país",
            min_value=1,
            max_value=int(df_victorias['Total_Partidos'].max()),
            value=5
        )
        
        df_victorias_filtrado = df_victorias[df_victorias['Total_Partidos'] >= min_partidos]
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["🏠 Victorias Locales", "⚽ Distribución de Goles", "📋 Detalles"])
        
        with tab1:
            st.subheader("🏠 Porcentaje de Victoria Local por País")
            st.markdown("*En partidos con más de 4 goles*")
            
            fig_victoria = px.bar(
                df_victorias_filtrado.head(15),
                x='country',
                y='Porcentaje_Victoria_Local',
                color='Total_Partidos',
                color_continuous_scale='Teal',
                title='Porcentaje de Victoria del Equipo Local',
                text='Porcentaje_Victoria_Local'
            )
            fig_victoria.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_victoria.update_layout(
                xaxis_title="País Anfitrión",
                yaxis_title="% Victoria Local",
                yaxis_range=[0, 100],
                height=500
            )
            st.plotly_chart(fig_victoria, use_container_width=True)
            
            # Insight
            mejor_pais = df_victorias_filtrado.loc[df_victorias_filtrado['Porcentaje_Victoria_Local'].idxmax()]
            st.info(f"🏆 **País con mayor ventaja local:** {mejor_pais['country']} con {mejor_pais['Porcentaje_Victoria_Local']:.1f}% ({mejor_pais['Total_Partidos']} partidos)")
        
        with tab2:
            
            st.subheader("⚽ Distribución de Encuentros por Cantidad de Goles")
            
            # PREPARACIÓN DE DATOS PARA DETALLE DE LOS DATOS QUE NO SE VEN (filtrar el rango 12-31)
            try:
                
                df_goles['total_goles_num'] = df_goles['total_goles_str'].astype(int)
            except ValueError:
                df_goles['total_goles_num'] = df_goles['total_goles_str'].str.extract('(\d+)').astype(int)
            df_zoom = df_goles[
                (df_goles['total_goles_num'] >= 12) & 
                (df_goles['total_goles_num'] <= 31)
            ].sort_values(by='Total_Encuentros', ascending=False)
            
            col_main, col_zoom = st.columns([0.6, 0.4]) 
            
            # --- COLUMNA IZQUIERDA: GRÁFICO PRINCIPAL DONA ---
            with col_main:
                st.markdown("Vista General (Todos los Rangos)")
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=df_goles['total_goles_str'],
                    values=df_goles['Total_Encuentros'],
                    hole=0.3,
                    marker=dict(
                        colors=px.colors.sequential.RdBu,
                        line=dict(color='white', width=0.1)
                    ),
                    textposition='outside',
                    textinfo='percent+label',
                )])
                
                total_goles_altos = df_goles['Total_Encuentros'].sum()
                fig_pie.update_layout(
                    title='Distribución de Encuentros con Más de 4 Goles en total.',
                    annotations=[dict(
                        text=f'{total_goles_altos}<br>Encuentros',
                        x=0.5, y=0.5,
                        font_size=20,
                        showarrow=False
                    )],
                    height=700 
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            
            # --- COLUMNA DERECHA: GRÁFICO DE BARRAS (ZOOM) ---
            with col_zoom:
                st.markdown(f" 🔎 Detalle del Rango de {df_zoom['total_goles_num'].min()} a {df_zoom['total_goles_num'].max()} Goles")
            
                if not df_zoom.empty:
                    fig_bar = px.bar(
                        df_zoom,
                        x='total_goles_str',
                        y='Total_Encuentros',
                        color='Total_Encuentros',
                        title='Comparación de Encuentros en Rango Alto',
                        template='plotly_white'
                    )
                    fig_bar.update_layout(height=500, xaxis_title="Total de Goles por Encuentro", yaxis_title="Cantidad de Encuentros")
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.warning("No hay datos en el rango de 12 a 31 goles para mostrar el detalle.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                df_goles['total_goles_sumados'] = df_goles['total_goles_num'] * df_goles['Total_Encuentros']
                total_goles_sumados = df_goles['total_goles_sumados'].sum()
                st.metric("⚽ Total de Goles Anotados", total_goles_sumados)            
                
            with col_b:
                mas_comun = df_goles.loc[df_goles['Total_Encuentros'].idxmax()]
                st.metric("🎯 Más Común", mas_comun['total_goles_str'])   


        with tab3:
            st.subheader("📋 Detalles por País")
            st.dataframe(
                df_victorias_filtrado.style.background_gradient(subset=['Porcentaje_Victoria_Local'], cmap='RdYlGn'),
                use_container_width=True
            )

# ==========================================
# SECCIÓN 4: PROYECCIÓN FINANCIERA
# ==========================================
elif seccion == "💰 Proyección Financiera":
    st.header("💰 Evolución y Proyección del Fondo de Premios")
    
    if not df_proyeccion.empty:
        # Separar histórico y proyección
        df_historico = df_proyeccion[df_proyeccion['Tipo'] == 'Histórico']
        df_proyectado = df_proyeccion[df_proyeccion['Tipo'] == 'Proyección']
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ultimo_historico = df_historico['Total_Fund_Millions'].iloc[-1]
            st.metric(
                "💵 Último Fondo Real",
                f"${ultimo_historico:.1f}M",
                delta=f"Año {int(df_historico['Year'].iloc[-1])}"
            )
        
        with col2:
            proyeccion_2026 = df_proyectado['Total_Fund_Millions'].iloc[0]
            st.metric(
                "🔮 Proyección 2026",
                f"${proyeccion_2026:.1f}M",
                delta=f"+${proyeccion_2026 - ultimo_historico:.1f}M"
            )
        
        with col3:
            crecimiento = ((proyeccion_2026 - ultimo_historico) / ultimo_historico) * 100
            st.metric(
                "📈 Crecimiento Esperado",
                f"{crecimiento:.1f}%",
                delta="vs último mundial"
            )
        
        with col4:
            primer_historico = df_historico['Total_Fund_Millions'].iloc[0]
            crecimiento_total = ((ultimo_historico - primer_historico) / primer_historico) * 100
            st.metric(
                "📊 Crecimiento Histórico Total",
                f"{crecimiento_total:.1f}%",
                delta=f"{int(df_historico['Year'].iloc[0])}-{int(df_historico['Year'].iloc[-1])}"
            )
        
        st.markdown("---")
        
        # Gráfico principal
        st.subheader("📈 Evolución del Fondo Total de Premios")
        
        fig_proyeccion = go.Figure()
        
        # Línea histórica
        fig_proyeccion.add_trace(go.Scatter(
            x=df_historico['Year'].astype(str),
            y=df_historico['Total_Fund_Millions'],
            mode='lines+markers+text',
            name='Histórico',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=10, color='#4ECDC4'),
            text=df_historico['Total_Fund_Millions'].apply(lambda x: f'${x:.0f}M'),
            textposition='top center',
            textfont=dict(size=11, color='#4ECDC4')
        ))
        
        # Línea de proyección
        if not df_proyectado.empty:
            # Conectar último histórico con proyección
            ultimo_historico_row = df_historico.iloc[[-1]]
            df_conexion = pd.concat([ultimo_historico_row, df_proyectado])
            
            fig_proyeccion.add_trace(go.Scatter(
                x=df_conexion['Year'].astype(str),
                y=df_conexion['Total_Fund_Millions'],
                mode='lines+markers+text',
                name='Proyección',
                line=dict(color='#FF6B6B', width=3, dash='dash'),
                marker=dict(size=12, color='#FF6B6B', symbol='star'),
                text=df_conexion['Total_Fund_Millions'].apply(lambda x: f'${x:.0f}M'),
                textposition='top center',
                textfont=dict(size=12, color='#FF6B6B', family='Arial Black')
            ))
        
        fig_proyeccion.update_layout(
            title='Evolución del Fondo Total de Premios (Millones USD)',
            xaxis_title='Año del Mundial',
            yaxis_title='Fondo Total (Millones USD)',
            template='plotly_white',
            height=500,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_proyeccion, use_container_width=True)
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("📊 Tabla de Datos")
            st.dataframe(
                df_proyeccion[['Year', 'Total_Fund_Millions', 'Tipo']].rename(columns={
                    'Year': 'Año',
                    'Total_Fund_Millions': 'Fondo (Millones USD)',
                    'Tipo': 'Tipo de Dato'
                }),
                use_container_width=True
            )
        
        with col_b:
            st.subheader("💡 Insights Clave")
            st.markdown(f"""
            - **Fondo actual:** ${ultimo_historico:.1f} millones
            - **Proyección 2026:** ${proyeccion_2026:.1f} millones
            - **Incremento esperado:** ${proyeccion_2026 - ultimo_historico:.1f}M ({crecimiento:.1f}%)
            - **Años analizados:** {len(df_historico)}
            - **Tendencia:** {'📈 Crecimiento sostenido' if crecimiento > 0 else '📉 Decrecimiento'}
            """)
            
            if crecimiento > 15:
                st.success("🚀 **Excelente perspectiva:** El crecimiento proyectado supera el 15%!!")
            elif crecimiento > 5:
                st.info("✅ **Crecimiento moderado:** Proyección estable y positiva")
            else:
                st.warning("⚠️ **Crecimiento bajo:** Revisar factores económicos")

# ==========================================
# SECCIÓN 5: ANÁLISIS DE JUGADORES (NUEVA)
# ==========================================
elif seccion == "👤 Análisis de Jugadores":
    st.header("👤 Análisis de Rendimiento de Jugadores")
    st.markdown("*Datos generados por análisis Lambda - Estadísticas de jugadores destacados*")
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not df_top50_paises.empty:
            total_jugadores_top = df_top50_paises['Jugadores_Top_50'].sum()
            st.metric("⭐ Jugadores Top 50 G+A", f"{total_jugadores_top}")
    
    with col2:
        if not df_goleadores_top3.empty:
            total_goleadores = len(df_goleadores_top3)
            st.metric("🎯 Goleadores Elite (+ de 3 goles internacionales)", f"{total_goleadores}")
    
    with col3:
        if not df_top10_paises_goleadores.empty:
            paises_destacados = len(df_top10_paises_goleadores)
            st.metric("🌍 Países con más Goleadores", f"{paises_destacados}")
    
    st.markdown("---")
    
    # Tabs para los 3 análisis
    tab1, tab2, tab3 = st.tabs(["🌍 Top 50 G+A por País", "🎯 Goleadores Elite", "🏆 Top Países Goleadores"])
    
    with tab1:
        st.subheader("🌍 Distribución Geográfica del Top 50 (Goles + Asistencias)")
        
        if not df_top50_paises.empty:
            fig_top50 = px.bar(
                df_top50_paises,
                x='COUNTRY',
                y='Jugadores_Top_50',
                title='Top 50 Jugadores por Goles + Asistencias - Distribución por País',
                color='Jugadores_Top_50',
                color_continuous_scale='Viridis',
                text='Jugadores_Top_50',
                template='plotly_white'
            )
            fig_top50.update_traces(texttemplate='%{text}', textposition='outside')
            fig_top50.update_layout(
                xaxis_title="País",
                yaxis_title="Cantidad de Jugadores",
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig_top50, use_container_width=True)
            
            # Insight
            pais_lider = df_top50_paises.loc[df_top50_paises['Jugadores_Top_50'].idxmax()]
            st.success(f"🏆 **País líder:** {pais_lider['COUNTRY']} con {pais_lider['Jugadores_Top_50']} jugadores en el Top 50")
            
            with st.expander("📋 Ver Datos Detallados"):
                st.dataframe(df_top50_paises, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos disponibles para este análisis")
    
    with tab2:
        st.subheader("🎯 Goleadores con mayor cantidad de goles.")
        st.markdown("*Análisis de jugadores con mayor efectividad goleadora*")
        
        if not df_goleadores_top3.empty:
            # Filtro en sidebar
            st.sidebar.markdown("### 🔍 Filtros de Goleadores")
            min_goles = st.sidebar.slider(
                "Mínimo de goles",
                min_value=int(df_goleadores_top3['Goles'].min()),
                max_value=int(df_goleadores_top3['Goles'].max()),
                value=int(df_goleadores_top3['Goles'].min())
            )
            
            df_goleadores_filtrado = df_goleadores_top3[df_goleadores_top3['Goles'] >= min_goles]
            
            # Gráfico de barras con color por equipo/país
            fig_goleadores = px.bar(
                df_goleadores_filtrado.sort_values(by='Goles', ascending=False).head(20),
                x='Goleador',
                y='Goles',
                color='Equipo_Pais',
                title='Top 20 Goleadores Elite (Más Goles)',
                template='plotly_white',
                text='Goles',
                labels={'Equipo_Pais': 'Equipo/País'}
            )
            fig_goleadores.update_traces(texttemplate='%{text}', textposition='outside')
            fig_goleadores.update_layout(
                xaxis_title="Goleador",
                yaxis_title="Cantidad de Goles",
                height=600,
                xaxis={'tickangle': -45}
            )
            st.plotly_chart(fig_goleadores, use_container_width=True)
            
            # Estadísticas adicionales
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                max_goleador = df_goleadores_filtrado.loc[df_goleadores_filtrado['Goles'].idxmax()]
                st.metric("👑 Máximo Goleador", max_goleador['Goleador'], f"{max_goleador['Goles']} goles")
            with col_b:
                promedio_goles = df_goleadores_filtrado['Goles'].mean()
                st.metric("📊 Promedio de Goles", f"{promedio_goles:.1f}")
            with col_c:
                total_goleadores_filtrados = len(df_goleadores_filtrado)
                st.metric("🎯 Total Goleadores", total_goleadores_filtrados)
            
            with st.expander("📋 Ver Tabla Completa de Goleadores"):
                st.dataframe(
                    df_goleadores_filtrado.sort_values('Goles', ascending=False).style.background_gradient(
                        subset=['Goles'], 
                        cmap='Reds'
                    ),
                    use_container_width=True,
                    height=400
                )
        else:
            st.warning("⚠️ No hay datos disponibles para este análisis")
    
    with tab3:
        st.subheader("🏆 Top 10 Países/Equipos con Mayor Número de Goleadores")
        st.markdown("*Países que más talento goleador aportan al Mundial*")
        
        if not df_top10_paises_goleadores.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Gráfico de pastel (donut)
                fig_pie_paises = px.pie(
                    df_top10_paises_goleadores,
                    values='Numero_de_Goleadores',
                    names='Pais_Equipo',
                    title='Distribución de Goleadores por País/Equipo',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie_paises.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                fig_pie_paises.update_layout(height=500)
                st.plotly_chart(fig_pie_paises, use_container_width=True)
            
            with col_chart2:
                # Gráfico de barras horizontal
                fig_bar_paises = px.bar(
                    df_top10_paises_goleadores.sort_values('Numero_de_Goleadores', ascending=True),
                    x='Numero_de_Goleadores',
                    y='Pais_Equipo',
                    orientation='h',
                    title='Ranking de Países por Cantidad de Goleadores',
                    color='Numero_de_Goleadores',
                    color_continuous_scale='Blues',
                    text='Numero_de_Goleadores'
                )
                fig_bar_paises.update_traces(texttemplate='%{text}', textposition='outside')
                fig_bar_paises.update_layout(
                    height=500,
                    showlegend=False,
                    yaxis_title="País/Equipo",
                    xaxis_title="Número de Goleadores"
                )
                st.plotly_chart(fig_bar_paises, use_container_width=True)
            
            # Insights
            st.markdown("---")
            col_insight1, col_insight2, col_insight3 = st.columns(3)
            
            with col_insight1:
                pais_top = df_top10_paises_goleadores.loc[df_top10_paises_goleadores['Numero_de_Goleadores'].idxmax()]
                st.info(f"🥇 **Líder:** {pais_top['Pais_Equipo']}\n\n{pais_top['Numero_de_Goleadores']} goleadores")
            
            with col_insight2:
                total_goleadores_top10 = df_top10_paises_goleadores['Numero_de_Goleadores'].sum()
                promedio_top10 = df_top10_paises_goleadores['Numero_de_Goleadores'].mean()
                st.info(f"📊 **Total Top 10:** {total_goleadores_top10}\n\n Promedio: {promedio_top10:.1f}")
            
            with col_insight3:
                pais_ultimo = df_top10_paises_goleadores.loc[df_top10_paises_goleadores['Numero_de_Goleadores'].idxmin()]
                st.info(f"🔟 **Décimo lugar:** {pais_ultimo['Pais_Equipo']}\n\n{pais_ultimo['Numero_de_Goleadores']} goleadores")
            
            with st.expander("📋 Ver Tabla Detallada"):
                st.dataframe(
                    df_top10_paises_goleadores.sort_values('Numero_de_Goleadores', ascending=False).style.background_gradient(
                        subset=['Numero_de_Goleadores'],
                        cmap='YlOrRd'
                    ),
                    use_container_width=True
                )
        else:
            st.warning("⚠️ No hay datos disponibles para este análisis")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>⚽ Mundial 2026 Analytics Dashboard</strong></p>
    <p>Datos procesados y almacenados en AWS S3 | Última actualización: Automática via LAMBDA de AWS! </p>
    <p>🇲🇽 México • 🇨🇦 Canadá • 🇺🇸 Estados Unidos</p>
</div>
""", unsafe_allow_html=True)
