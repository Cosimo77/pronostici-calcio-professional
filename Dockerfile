# Dockerfile per Pronostici Calcio Enterprise
FROM python:3.11-slim

# Metadata
LABEL maintainer="pronostici-calcio-team"
LABEL version="1.0.0-enterprise"
LABEL description="Sistema Pronostici Calcio Enterprise con ML deterministico"

# Argomenti build-time
ARG APP_ENV=production
ARG USER_ID=1000
ARG GROUP_ID=1000

# Variabili ambiente
ENV FLASK_ENV=${APP_ENV}
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Crea utente non-root per sicurezza
RUN groupadd -g ${GROUP_ID} appgroup && \
    useradd -u ${USER_ID} -g appgroup -m -s /bin/bash appuser

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Directory applicazione
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia codice applicazione
COPY --chown=appuser:appgroup . .

# Crea directory per logs e cache
RUN mkdir -p logs cache models/enterprise && \
    chown -R appuser:appgroup logs cache models

# Cambio all'utente non-root
USER appuser

# Esponi porta (Render usa variabile $PORT dinamica)
EXPOSE ${PORT:-5008}

# Script di avvio - Usa $PORT di Render
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --worker-class gevent --worker-connections 1000 web.app_professional:app