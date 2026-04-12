#!/bin/bash
# Workflow completo post-merge: attende merge PR e monitora deploy Render

REPO="Cosimo77/pronostici-calcio-professional"
BRANCH="main"
RENDER_URL="https://pronostici-calcio-professional.onrender.com"

echo "🤖 Workflow Automatico Post-Merge"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "⏳ Step 1: Attendo merge PR su GitHub..."
echo "   (Fai il merge quando vuoi - lo script aspetta)"
echo ""

# Attendi che main locale sia indietro rispetto a origin/main (segno che PR è stata mergiata)
INITIAL_COMMIT=$(git rev-parse main)

while true; do
    git fetch origin main --quiet 2>/dev/null
    REMOTE_COMMIT=$(git rev-parse origin/main)

    if [[ "$REMOTE_COMMIT" != "$INITIAL_COMMIT" ]]; then
        echo "✅ PR Mergiata! Nuovo commit su origin/main rilevato"
        echo "   Commit: $REMOTE_COMMIT"
        break
    fi

    echo -ne "   Checking... (ogni 15s)\r"
    sleep 15
done

echo ""
echo "🔄 Step 2: Aggiorno repository locale..."
git pull origin main --quiet
echo "✅ Repository locale aggiornato"

echo ""
echo "⏳ Step 3: Attendo avvio rebuild Render..."
echo "   (Render rileva push e inizia rebuild automaticamente)"
sleep 30

echo ""
echo "🔍 Step 4: Monitoring deploy Render (check ogni 30s)..."
echo "═══════════════════════════════════════════════════════════════"
echo ""

MAX_CHECKS=20
for i in $(seq 1 $MAX_CHECKS); do
    echo "[$i/$MAX_CHECKS] Checking Render..."

    HEALTH=$(curl -s --max-time 10 "$RENDER_URL/api/health" 2>&1)

    if [[ $? -eq 0 ]]; then
        STATUS=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', 'N/A'))" 2>/dev/null)
        DB_RECORDS=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('database_records', 0))" 2>/dev/null)

        echo "   Status: $STATUS | DB Records: $DB_RECORDS"

        if [[ "$DB_RECORDS" -ge 2753 ]]; then
            echo ""
            echo "═══════════════════════════════════════════════════════════════"
            echo "✅ DEPLOY COMPLETATO CON SUCCESSO!"
            echo "═══════════════════════════════════════════════════════════════"
            echo ""
            echo "📊 Dataset Info:"
            curl -s "$RENDER_URL/api/dataset_info" | python3 -m json.tool | head -20
            echo ""
            echo "🎯 Sistema pronto per predizioni con dati aggiornati al 06/04/2026"
            echo ""
            exit 0
        fi
    else
        echo "   ⚠️  Server unreachable (rebuilding...)"
    fi

    if [[ $i -lt $MAX_CHECKS ]]; then
        sleep 30
    fi
done

echo ""
echo "⚠️  Timeout - deploy in corso ma richiede più tempo"
echo "💡 Controlla manualmente: curl $RENDER_URL/api/health"
