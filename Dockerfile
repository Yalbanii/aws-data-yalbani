# Imagen base con Python
FROM python:3.11
 
# Instalar dependencias necesarias
RUN pip install --no-cache-dir  streamlit mysql-connector-python pandas  matplotlib seaborn dotenv
 
# Crear directorio de trabajo/app
WORKDIR /appProyect
 
# Copiar el código de la app COPY app.py /app/
COPY app_proyecto.py /Proyecto Final/Archivos analisis/app_proyecto
 
# Exponer el puerto de Streamlit
EXPOSE 8501
 
# Comando para correr Streamlit
CMD ["streamlit", "run", "app_proyecto.py", "--server.port=8501", "--server.address=0.0.0.0"]
