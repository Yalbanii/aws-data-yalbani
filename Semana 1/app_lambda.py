import pandas as pd 
import streamlit as st
import boto3
import io
import json
import plotly.express as px

# --- Carga de Datos Procesados desde S3 ---
@st.cache_data
def cargar_datos_procesados():
    s3 = boto3.client("s3")
    bucket = "xideralaws-curso-yalbani"
    OUTPUT_PREFIX = "processed/"
    
    try:
        # Listar todos los archivos en la carpeta procesada
        response = s3.list_objects_v2(Bucket=bucket, Prefix=OUTPUT_PREFIX)
        
        if "Contents" not in response:
            st.warning("Lambda no ha ejecutado el procesamiento. No se encontraron archivos procesados.")
            return pd.DataFrame()
            
        # Encontrar el archivo mas reciente (timestamp mas alto)
        all_files = response["Contents"]
        # Filtrar solo archivos CSV si fuera necesario, y ordenar por la ultima modificacion
        all_files = sorted(all_files, key=lambda x: x['LastModified'], reverse=True)
        
        # El archivo mas reciente es el primero
        latest_key = all_files[0]['Key'] 
        
        # Leer el archivo mas reciente
        st.info(f"Cargando el ultimo archivo procesado: {latest_key.split('/')[-1]}")
        obj = s3.get_object(Bucket=bucket, Key=latest_key)
        body = obj["Body"].read()
        
        df_final = pd.read_csv(io.BytesIO(body))
        return df_final
        
    except Exception as e:
        st.error(f"Error al cargar el CSV procesado desde S3: {e}")
        return pd.DataFrame() 

df_analisis = cargar_datos_procesados()

# --- Sidebar ---
st.sidebar.header("Filtros")
max_titulos = df_analisis['title'].max()
min_titulos_filter = st.sidebar.slider(
    "Mínimo de Títulos", 
    min_value=1, 
    max_value=int(max_titulos), 
    value=1
)

# --- Streamlit ---
total_df = df_analisis[df_analisis['title'] >= min_titulos_filter]
total_peliculas = len(total_df) # No son peliculas, es el número de directores que cumplen el filtro

st.markdown("---")
st.header("🎬 Top 5 Directores de Netflix (Procesado por Lambda)")

df_directores = cargar_datos_procesados()

if not df_directores.empty:  
    df_top_5 = df_directores.head(5) 

    st.dataframe(df_top_5) 
    
    fig = px.bar(
        df_top_5,
        x='director',
        y='title',
        title="Top 5 Directores por Numero de Titulos en Netflix",
        color='title',
        template='plotly_white' 
    )
    fig.update_layout(
        xaxis_title="Director",
        yaxis_title="Total de Titulos",
        xaxis={'categoryorder':'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Ejecuta la funcion Lambda en AWS para generar el archivo procesado!")

    
# --- Detalle Base ---
st.markdown(" 👀 Detalle de Peliculas")
st.dataframe(total_df)
    

