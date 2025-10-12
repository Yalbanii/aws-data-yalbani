# --- Imports ---
import pandas as pd 
import streamlit as st
import plotly.express as px 
import matplotlib.pyplot as plt
import boto3
import json
from io import StringIO

# --- Config ---
st.set_page_config(page_title="Monitor de STATUS de Servidores", layout="wide")
@st.cache_data

# --- Carga de Datos desde S3 (Función Corregida) ---
@st.cache_data
def carga_datos():
    bucket_name = "xideralaws-curso-benjamin2"
    s3 = boto3.client("s3")
    prefix = "raw/"
    response = s3.list_objects_v2(Bucket=bucket_name , Prefix=prefix)
    data_frames = []
    
    if "Contents" in response:
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".json"):
                file_obj = s3.get_object(Bucket=bucket_name, Key=key)
                content = file_obj["Body"].read().decode("utf-8")
                json_data = json.loads(content)
                df_temp = pd.json_normalize(json_data)
                data_frames.append(df_temp)

    if data_frames:
        df = pd.concat(data_frames , ignore_index=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        expected_cols = [
            'timestamp', 
            'server_id', 
            'status', 
            'cpu_usage', 
            'memory_usage', 
            'disk_usage', 
            'region'
        ]
        df = pd.DataFrame(columns=expected_cols)

    return df

# --- Procesamiento de Datos ---
df = carga_datos()   

# --- Sidebar ---
st.sidebar.header("Filtros")
status = st.sidebar.multiselect("Status disponibles", options=df['status'].unique(), default=df['status'].unique())
server = st.sidebar.multiselect("Servidores analizados", options=df['server_id'].unique(), default=df['server_id'].unique())
 
filtered_df = df[(df['status'].isin(status)) & (df['server_id'].isin(server))]
 
# --- KPIs ---
total_estados = len(filtered_df)
total_servidores = filtered_df['server_id'].nunique()
 
st.title("🚦 Monitor de Status Dashboard")
 
col1, col2, col3 = st.columns(3)
col1.metric("Total de estados", total_estados)
col2.metric("Total de servidores", total_servidores)

st.markdown("---")

st.header("Contador de Estados")
error_count = filtered_df[filtered_df['status'] == 'ERROR'].shape[0]
warn_count = filtered_df[filtered_df['status'] == 'WARN'].shape[0]
ok_count = filtered_df[filtered_df['status'] == 'OK'].shape[0]

col4, col5, col6 = st.columns(3)

col4.metric(
    "Estados ERROR", 
    error_count, 
    delta="¡Revisar!", 
    delta_color="inverse" if error_count > 0 else "off"
)
col5.metric(
    "Estados WARN", 
    warn_count, 
    delta="Atención", 
    delta_color="off" if warn_count == 0 else "normal"
)
col6.metric("Estados OK", ok_count, delta="Normal", delta_color="off")

st.markdown("---")


# --- Gráficos ---
st.header("Distribucion total de los estados en todos los servidores disponibles")
estados_count = df['status'].value_counts()
fig1 = px.pie(
    estados_count,
    values = estados_count.values,
    names = estados_count.index,
    title = "Estados en servidores",
    color_discrete_map={'ERROR':'red', 'WARN':'yellow', 'OK':'green'}

)
st.plotly_chart(fig1)
 
st.header("Uso Promedio de Recursos")

if not filtered_df.empty:
    # Calcular el promedio de los datos a analizar
    usage_cols = ['cpu_usage', 'memory_usage', 'disk_usage']
    mean_usage = filtered_df[usage_cols].mean()

    usage_df = mean_usage.reset_index()
    usage_df.columns = ['Recurso', 'Uso Promedio']
    usage_df['Uso Promedio'] = usage_df['Uso Promedio'].round(2)

    fig2 = px.bar(
        usage_df,
        x='Recurso',
        y='Uso Promedio',
        title="Uso Promedio de CPU, Memoria y Disco (en %)",
        color='Recurso',
        text='Uso Promedio' # valor en la barra
    )
    fig2.update_yaxes(range=[0, 100])
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No hay datos para calcular el Uso Promedio de Recursos.")

# --- Detalle Servidores ---
st.markdown("### 👀 Detalle de Servidores")
st.dataframe(filtered_df[['timestamp', 'server_id', 'cpu_usage', 'memory_usage', 'disk_usage', 'region', 'status']])