# Imagen base con Python
FROM python:3.11
 
# Instalar dependencias necesarias
RUN pip install --no-cache-dir streamlit boto3 pandas plotly python-dotenv
 
# Crear directorio de trabajo
WORKDIR /app

# Copiar el código de la app (ajusta la ruta según tu estructura)
COPY app_proyecto.py /app/

# Exponer el puerto de Streamlit
EXPOSE 8501
 
# Comando para correr Streamlit
CMD ["streamlit", "run", "app_proyecto.py", "--server.port=8501", "--server.address=0.0.0.0"]
