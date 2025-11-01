#!/bin/bash

# Render Startup Script - MONITORING APP ONLY
echo "🚀 Starting MONITORING APP (minimal, no CSP issues)..."

# Set environment variables
export FLASK_APP=web/monitoring_app.py
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:/app"

# Create necessary directories
mkdir -p logs cache models/enterprise data

# Start the application with Gunicorn (Procfile should handle this, but explicit is better)
echo "📊 Starting monitoring_app via Gunicorn..."
cd web && gunicorn monitoring_app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 --preload