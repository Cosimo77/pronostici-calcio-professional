#!/bin/bash

# ⚡ Check Rapido Partite Serie A Disponibili
# Uso: bash check_partite_disponibili.sh
# Exit code: 0 = partite OK, 1 = nessuna partita

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║           🔍 CHECK PARTITE SERIE A DISPONIBILI                  ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Verifica server Flask attivo
if ! curl -s http://localhost:5008 > /dev/null 2>&1; then
    echo "❌ Server Flask NON online su :5008"
    echo "   Avvia: python3 -m web.app_professional"
    exit 1
fi

echo "✅ Server Flask online"
echo ""

# Fetch partite da API
echo "📡 Fetching partite da The Odds API..."
RESPONSE=$(curl -s http://localhost:5008/api/upcoming_matches)

# Parse JSON
TOTAL_MATCHES=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_matches', 0))" 2>/dev/null || echo "0")
QUOTA_REMAINING=$(echo "$RESPONSE" | python3 -c "import sys, json; api_quota=json.load(sys.stdin).get('api_quota', {}); print(api_quota.get('remaining', 'N/A'))" 2>/dev/null || echo "N/A")
QUOTA_USED=$(echo "$RESPONSE" | python3 -c "import sys, json; api_quota=json.load(sys.stdin).get('api_quota', {}); print(api_quota.get('used', 'N/A'))" 2>/dev/null || echo "N/A")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 RISULTATI"
echo ""

if [ "$TOTAL_MATCHES" -eq 0 ]; then
    echo "❌ NESSUNA partita Serie A disponibile"
    echo ""
    echo "   API Quota: ${QUOTA_USED}/500 usate, ${QUOTA_REMAINING} rimanenti"
    echo ""
    echo "🔴 TEST END-TO-END NON ESEGUIBILE"
    echo "   → Attendi partite disponibili"
    echo "   → Ricontrolla domani"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
else
    echo "✅ ${TOTAL_MATCHES} partite Serie A disponibili"
    echo ""
    echo "   API Quota: ${QUOTA_USED}/500 usate, ${QUOTA_REMAINING} rimanenti"
    echo ""
    echo "🟢 PRONTO PER TEST END-TO-END"
    echo ""
    echo "   Esegui ora:"
    echo "   $ python3 test_completo_betting_reale.py"
    echo ""
    echo "   DEVE risultare: 5/5 test PASS (exit code 0)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
fi
