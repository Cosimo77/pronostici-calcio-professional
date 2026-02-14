#!/bin/bash

# Render Startup Script - AUTOMAZIONE COMPLETA
echo "🚀 AUTO-SETUP Sistema Completo..."

# Auto-setup: scarica dati freschi e riaddestra modelli OGNI deploy
python3 scripts/auto_setup_render.py || echo "⚠️ Auto-setup fallito, uso dati esistenti"

# Set environment variables
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:/app"

# Create necessary directories
mkdir -p logs cache models/enterprise data

# Start professional app with Gunicorn
echo "📊 Starting app_professional via Gunicorn..."
exec gunicorn web.app_professional:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 --worker-class gevent --preload