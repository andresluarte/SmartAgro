# Usar una imagen base de Python

FROM python:3.11-slim
# Instalar las dependencias de PostgreSQL y herramientas de compilación
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos
COPY requirements.txt .

# Instalar los requisitos
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Comando para ejecutar la aplicación
CMD ["gunicorn", "agrosmartiot.wsgi"]
