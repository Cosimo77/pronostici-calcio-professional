#!/bin/bash
# Script professionale di monitoraggio deploy Render

echo "🔍 Monitoraggio Deploy Render - Dataset Update"
echo "================================================"
echo ""

RENDER_URL="https://pronostici-calcio-professional.onrender.com"
MAX_WAIT=600  # 10 minuti max
INTERVAL=15    # Check ogni 15 secondi
elapsed=0

echo "⏳ Attendendo deploy Render (max 10 min)..."
echo ""

while [ $elapsed -lt $MAX_WAIT ]; do
    # Check health endpoint
    response=$(curl -s --max-time 10 "$RENDER_URL/api/health" 2>&1)

    if echo "$response" | grep -q '"status": "healthy"'; then
        echo "✅ Server Render ONLINE"

        # Estrai database_records
        db_records=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('database_records', 'N/A'))" 2>/dev/null)

        echo "   📊 Database records: $db_records"

        if [ "$db_records" = "2753" ]; then
            echo ""
            echo "🎉 DEPLOY COMPLETATO CON SUCCESSO!"
            echo "   ✅ Dataset aggiornato: 2743 → 2753 records"
            echo ""

            # Check dataset info
            echo "📋 Verifica dataset completo:"
            curl -s "$RENDER_URL/api/dataset_info" | python3 -m json.tool | head -15
            exit 0
        elif [ "$db_records" = "2743" ]; then
            echo "   ⏳ Deploy in corso... (ancora vecchio dataset)"
        else
            echo "   ℹ️  Records: $db_records (atteso: 2753)"
        fi
    else
        echo "⚠️  Server in sleep/rebuild - riprovo..."
    fi

    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
    echo "   ⏱️  Elapsed: ${elapsed}s / ${MAX_WAIT}s"
done

echo ""
echo "⚠️  Timeout raggiunto (10 min) - verifica manuale:"
echo "   curl $RENDER_URL/api/health"
echo "   Dashboard: https://dashboard.render.com"
exit 1
