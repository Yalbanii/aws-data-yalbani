import pandas as pd 
import streamlit as st
import boto3
import io
import plotly.express as px

st.set_page_config(layout="wide")

# --- Carga de Datos desde S3 ---
@st.cache_data
def cargar_datos_procesados():
    s3 = boto3.client("s3")
    bucket = "xideralaws-curso-yalbani"
    OUTPUT_PREFIX = "db_export/" 
    
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=OUTPUT_PREFIX)
        
        if "Contents" not in response:
            st.warning("La función Lambda aun no ha subido datos. No se encontraron archivos. CHECALO!")
            return pd.DataFrame()
            
        all_files = [
            f for f in response["Contents"] 
            if f['Key'].endswith('.csv') and f['Size'] > 0
        ]
        
        if not all_files:
            st.warning("Archivos CSV no encontrados. Ejecuta la Lambda.")
            return pd.DataFrame()

        all_files = sorted(all_files, key=lambda x: x['LastModified'], reverse=True)
        latest_key = all_files[0]['Key'] 
        
        st.info(f"Cargando el ultimo archivo: {latest_key.split('/')[-1]}")
        obj = s3.get_object(Bucket=bucket, Key=latest_key)
        body = obj["Body"].read()
        
        df_final = pd.read_csv(io.BytesIO(body))
        return df_final
        
    except Exception as e:
        st.error(f" Error al cargar el CSV desde S3. Verifica el bucket. {e}")
        return pd.DataFrame() 

df_analisis = cargar_datos_procesados()

# --- Funciones de Detalle ---
def get_head_and_tail(dataframe):
    # --- Devuelve las primeras filas y las ultimas filas. ---
    if dataframe.shape[0] <= 10:
        return dataframe
    else:
        df_head = dataframe.head(5)
        df_tail = dataframe.tail(5)
        separator = pd.DataFrame([['...'] * dataframe.shape[1]], columns=dataframe.columns)
        return pd.concat([df_head, separator, df_tail], ignore_index=True)


# --- KPIs ---
st.header("📊 Analisis de Personas por Ciudad (Datos MySQL a S3)")

if not df_analisis.empty:
    
    # Conteo por Ciudad
    df_conteo = df_analisis.groupby('ciudad').size().reset_index(name='Total Personas')
    df_conteo = df_conteo.sort_values('Total Personas', ascending=False)

    # --- Sidebar ---
    st.sidebar.header("Filtros")
    
    max_conteo = df_conteo['Total Personas'].max()
    min_personas_filter = st.sidebar.slider(
        "Minimo de Personas por Ciudad", 
        min_value=1, 
        max_value=int(max_conteo) if max_conteo > 1 else 10,
        value=1
    )
    
    df_filtrado = df_conteo[df_conteo['Total Personas'] >= min_personas_filter]

    col1, col2 = st.columns(2)
    col1.metric("Total de Registros en la DB", len(df_analisis))
    col2.metric("Ciudades que Cumplen el Filtro", len(df_filtrado))

    st.markdown("---")
    
    st.subheader(f"Ciudades con al menos {min_personas_filter} Personas")
    
    fig = px.bar(
        df_filtrado.head(15), 
        x='ciudad',
        y='Total Personas',
        title="Conteo de Personas por Ciudad",
        color='Total Personas',
        template='plotly_white'
    )
    fig.update_layout(
        xaxis_title="Ciudad",
        yaxis_title="Total de Personas",
        xaxis={'categoryorder':'total descending'}
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Detalle de Datos
    st.markdown("---")
    st.subheader("👀 Muestra de Registros Extraidos (Head & Tail)")
    
    df_muestra = get_head_and_tail(df_analisis)
    st.dataframe(df_muestra, use_container_width=True)