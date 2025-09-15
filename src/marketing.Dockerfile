FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY src/marketing-requirements.txt .
RUN pip install --no-cache-dir -r marketing-requirements.txt

# Crear estructura de directorios
RUN mkdir -p /app/src

# Copiar código fuente completo
COPY src/ ./src/

# Configurar PYTHONPATH
ENV PYTHONPATH=/app/src

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación
CMD ["python", "-m", "uvicorn", "marketing.main_simple:app", "--host", "0.0.0.0", "--port", "8000"]