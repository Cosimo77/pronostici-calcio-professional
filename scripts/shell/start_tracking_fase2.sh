#!/bin/bash
# QUICK START - Sistema Tracking FASE 2
# Esegui questo script per setup completo

echo "=================================================="
echo "🚀 SETUP SISTEMA TRACKING FASE 2"
echo "=================================================="

cd /Users/cosimomassaro/Desktop/pronostici_calcio

# 1. Genera CSV tracking iniziale
echo ""
echo "📊 Step 1: Generazione file tracking..."
python3 genera_tracking_fase2.py

if [ ! -f "tracking_fase2_febbraio2026.csv" ]; then
    echo "❌ Errore: File tracking non creato"
    exit 1
fi

echo ""
echo "✅ File tracking creato con successo!"

# 2. Avvia web server
echo ""
echo "=================================================="
echo "🌐 Step 2: Avvio web server..."
echo "=================================================="
echo ""
echo "📍 Dashboard disponibile su:"
echo "   • Homepage: http://localhost:5000"
echo "   • Tracking FASE 2: http://localhost:5000/tracking"
echo "   • API Tracking: http://localhost:5000/api/tracking/fase2"
echo ""
echo "⏳ Avvio server..."
echo ""

# Attiva venv se esiste
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Avvia Flask
python3 -m web.app_professional
