#!/bin/bash
# DASHBOARD QUICK START - Apri tutto in un comando

echo "🚀 AVVIO SISTEMA TRACKING FASE 2"
echo "=================================="

cd /Users/cosimomassaro/Desktop/pronostici_calcio

# Verifica server già attivo
if lsof -ti:5008 > /dev/null 2>&1; then
    echo "✅ Server già attivo su porta 5008"
else
    echo "🔄 Avvio server Flask..."
    nohup python3 -m web.app_professional > logs/server.log 2>&1 &
    sleep 3
fi

echo ""
echo "📊 DASHBOARD DISPONIBILI:"
echo "  • Tracking FASE 2: http://localhost:5008/tracking"
echo "  • Homepage: http://localhost:5008"
echo "  • Upcoming Matches: http://localhost:5008/upcoming_matches"
echo ""
echo "🔧 API ENDPOINTS:"
echo "  • Tracking Data: http://localhost:5008/api/tracking/fase2"
echo "  • Cache Stats: http://localhost:5008/api/cache/stats"
echo ""
echo "📋 FILE TRACKING:"
echo "  • CSV: tracking_fase2_febbraio2026.csv ($(wc -l < tracking_fase2_febbraio2026.csv) righe)"
echo "  • Log: logs/tracking_cron.log"
echo ""
echo "⚡ COMANDI RAPIDI:"
echo "  • Rigenera tracking: python3 genera_tracking_fase2.py"
echo "  • Aggiorna P&L: python3 aggiorna_tracking_fase2.py"
echo "  • Test completo: bash test_automazione.sh"
echo ""
echo "=================================="

# Apri browser automaticamente
if command -v open > /dev/null 2>&1; then
    echo "🌐 Apertura dashboard..."
    open http://localhost:5008/tracking
fi
