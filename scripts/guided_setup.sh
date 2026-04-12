#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "🎯 GUIDA PASSO-PASSO - Sistema Validation"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 1: Verifica server
echo "STEP 1: Verifica Server Flask"
echo "────────────────────────────────────────"

if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
    echo "✅ Server ONLINE"
    SERVER_STATUS="online"
else
    echo "⚠️  Server offline - Avviando..."
    python3 web/app_professional.py > logs/flask_app.log 2>&1 &
    SERVER_PID=$!
    echo "   PID: $SERVER_PID"
    echo "   Log: logs/flask_app.log"
    echo ""
    echo "⏳ Attendo 10 secondi per startup..."
    sleep 10
    
    if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
        echo "✅ Server AVVIATO con successo"
        SERVER_STATUS="online"
    else
        echo "❌ Errore avvio server - Check logs:"
        echo "   $ tail -50 logs/flask_app.log"
        SERVER_STATUS="error"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ "$SERVER_STATUS" != "online" ]; then
    echo "⚠️  Server non disponibile - Fix required"
    echo ""
    echo "Run manualmente:"
    echo "  Terminal 1: python3 web/app_professional.py"
    echo "  Terminal 2: python scripts/test_today_matches.py"
    exit 1
fi

# Step 2: Test match oggi
echo ""
echo "STEP 2: Test Predizioni Match Oggi"
echo "────────────────────────────────────────"
echo ""
echo "Match disponibili oggi (6 Aprile 2026):"
echo "  • Juventus vs Genoa (16:00)"
echo "  • Napoli vs AC Milan (18:45)"
echo ""
echo "Avvio test con validazione bookmaker..."
echo ""

python3 scripts/test_today_matches.py

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "STEP 3: Prossime Azioni"
echo "────────────────────────────────────────"
echo ""
echo "✅ Predizioni testate e loggiate"
echo ""
echo "📋 TODO:"
echo "  1. Rivedi warnings (se presenti)"
echo "  2. Aspetta risultati match"
echo "  3. Update risultati:"
echo "     $ nano scripts/update_match_results.py"
echo "     $ python scripts/update_match_results.py"
echo "  4. Dopo 5+ match, genera report:"
echo "     $ python3 -c \"from scripts.setup_validation_tracking import generate_performance_report; generate_performance_report()\""
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ GUIDA COMPLETATA"
echo ""
