# --- Imports ---
import pandas as pd 
import streamlit as st
import plotly.express as px 
import matplotlib.pyplot as plt

# --- Config ---
st.set_page_config(page_title="Lifestyle and Sleep Pattern Dashboard", layout="wide")
 
@st.cache_data
def load_data():
    return pd.read_csv("Sleep_health_and_lifestyle_dataset.csv")
 
df = load_data()
 
# --- Sidebar ---
st.sidebar.header("Filtros")
gender_filter = st.sidebar.multiselect("Genero", options=df['Gender'].unique(), default=df['Gender'].unique())
stress_filter = st.sidebar.multiselect("Nivel de estres!", options=df['Stress Level'].unique(), default=df['Stress Level'].unique())
 
filtered_df = df[(df['Gender'].isin(gender_filter)) & (df['Stress Level'].isin(stress_filter))]
 
# --- KPIs ---
total_muestra = len(filtered_df)
avg_sleep_duration = filtered_df['Sleep Duration'].mean()
stress_level = filtered_df['Stress Level'].nunique()
 
st.title("🧠 Lifestyle and Sleep Pattern Dashboard")
 
col1, col2, col3 = st.columns(3)
col1.metric("Personas Totales", total_muestra)
col2.metric("Promedio de Duracion de Sueño", f"{avg_sleep_duration:.1f}")
col3.metric("Nivel de estrés promedio", stress_level)
 
st.markdown("---")
 
# --- Gráficos ---
col1, col2 = st.columns(2)
 
with col1:
    fig1 = px.bar(filtered_df['Occupation'].value_counts(), title="Ocupación de los Participantes", labels={'index':'Ocupacion', 'value':'Cantidad'})
    st.plotly_chart(fig1, use_container_width=True)
 
with col2:
    fig2 = px.pie(filtered_df, names='Stress Level', title="Distribución por nivel de estrés")
    st.plotly_chart(fig2, use_container_width=True)
 
 
# --- Top Ritmo Cardiaco ---
st.markdown("### ⭐ Top 10 ocupaciones con más alto ritmo cardiaco ")
# Lógica de Pandas para obtener el Top 10
heart_occupation = df.groupby('Occupation')['Heart Rate'].mean().sort_values(ascending=False)
top10_heart = heart_occupation.head(10)
# Ordenar de menor a mayor para que el top 1 quede arriba en el gráfico horizontal
top10_sorted = top10_heart.sort_values(ascending=True)
top10_df = top10_sorted.reset_index()
top10_df.columns = ['Occupation', 'Ritmo Cardiaco Promedio']
fig3 = px.bar(top10_df, x='Ritmo Cardiaco Promedio', y='Occupation', orientation='h', title="Ritmo Cardíaco Promedio por Ocupación (Descendente)")
st.plotly_chart(fig3, use_container_width=True)

# --- Top Ritmo Cardiaco ---
st.markdown("### 📉 Relación: Estrés vs. Calidad de Sueño Promedio")
stress_quality_data = df.groupby('Stress Level')['Quality of Sleep'].mean().sort_index(ascending=True)
stress_quality_df = stress_quality_data.reset_index()
stress_quality_df.columns = ['Nivel de Estrés', 'Calidad de Sueño Promedio']
fig4 = px.line(stress_quality_df, x='Nivel de Estrés', y='Calidad de Sueño Promedio', title="Calidad de Sueño Promedio por Nivel de Estrés", markers=True) # Añade puntos a la línea
# Mejorar eje X como números enteros (niveles de estrés)
fig4.update_xaxes(dtick=1)
st.plotly_chart(fig4, use_container_width=True)

# --- Detalle Participantes ---
st.markdown("### 👀 Detalle de Participantes")
st.dataframe(filtered_df[['Age', 'Gender', 'Occupation', 'Sleep Duration', 'Quality of Sleep', 'Stress Level', 'Sleep Disorder']])
