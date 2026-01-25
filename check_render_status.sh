#!/bin/bash
# Script per verificare stato Render vs Locale

echo "🔍 VERIFICA STATO SISTEMA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Locale
echo ""
echo "📂 LOCALE (Mac):"
LOCAL_PARTITE=$(wc -l < data/dataset_pulito.csv)
LOCAL_PARTITE=$((LOCAL_PARTITE - 1))  # Rimuovi header
LOCAL_DATA=$(tail -1 data/dataset_pulito.csv | cut -d',' -f1)
echo "   Partite: $LOCAL_PARTITE"
echo "   Ultima data: $LOCAL_DATA"

# Modelli
MODELLI_DATA=$(ls -lt models/enterprise/*.pkl | head -1 | awk '{print $6, $7, $8}')
echo "   Modelli aggiornati: $MODELLI_DATA"

# Render
echo ""
echo "☁️  RENDER (Cloud):"
RENDER_HEALTH=$(curl -s https://pronostici-calcio-professional.onrender.com/api/health)
RENDER_PARTITE=$(echo "$RENDER_HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin)['database_records'])" 2>/dev/null || echo "ERROR")
RENDER_STATUS=$(echo "$RENDER_HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "ERROR")

echo "   Partite: $RENDER_PARTITE"
echo "   Status: $RENDER_STATUS"

# Automazione
RENDER_AUTO=$(curl -s https://pronostici-calcio-professional.onrender.com/api/automation/status)
LAST_UPDATE=$(echo "$RENDER_AUTO" | python3 -c "import sys, json; print(json.load(sys.stdin)['last_update'])" 2>/dev/null || echo "null")

echo "   Last update: $LAST_UPDATE"

# Confronto
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$LOCAL_PARTITE" == "$RENDER_PARTITE" ]; then
    echo "✅ SINCRONIZZATO: Locale e Render hanno stesso dataset"
else
    echo "⚠️  DESINCRONIZZATO:"
    echo "   Locale: $LOCAL_PARTITE partite"
    echo "   Render: $RENDER_PARTITE partite"
    echo ""
    echo "   Azione: Deploy manuale richiesto su Render"
    echo "   URL: https://dashboard.render.com/web/srv-cu5lvj08fa8c73fnpug0"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
