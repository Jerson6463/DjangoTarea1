# Dockerfile

#Imagen base oficial de Python
FROM python:3.11-slim

# Evitar archivos .pyc y buffering de stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar cliente PostgreSQL para dbshell
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias primero (aprovecha caché de capas)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código fuente
COPY . .

# Puerto que expondrá el contenedor
EXPOSE 8000

# Comando por defecto al iniciar el contenedor
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]