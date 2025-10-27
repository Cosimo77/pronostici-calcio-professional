#!/bin/bash

# 🔍 ACCESSO RAPIDO AL MONITORAGGIO
# Script per aprire direttamente la dashboard

echo "🔍 Aprendo Dashboard Monitoraggio..."
echo "=================================="

# Sostituisci con il tuo URL Render
APP_URL="https://tua-app.onrender.com"

echo "🌐 App principale: $APP_URL/enterprise"
echo "📊 Monitoraggio: $APP_URL/monitoring"
echo "🔗 API Health: $APP_URL/api/health"
echo "📈 API Metrics: $APP_URL/api/metrics_summary"

echo ""
echo "⏰ Se /monitoring da 'Not Found':"
echo "1. Aspetta 2-3 minuti per il deploy"
echo "2. Controlla che Render abbia finito di aggiornare"
echo "3. Prova prima /api/health per verificare che l'app sia attiva"

# Su macOS apri automaticamente
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🚀 Apertura automatica dashboard..."
    # Decommentare quando hai il tuo URL
    # open "$APP_URL/monitoring"
fi