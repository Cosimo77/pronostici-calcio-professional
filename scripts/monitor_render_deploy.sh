#!/bin/bash
# Monitor deploy Render dopo merge PR

RENDER_URL="https://pronostici-calcio-professional.onrender.com"
CHECK_INTERVAL=30  # secondi
MAX_CHECKS=20      # 10 minuti max

echo "🔍 Monitoring Render Deploy..."
echo "📡 URL: $RENDER_URL"
echo "⏱️  Check ogni $CHECK_INTERVAL secondi (max $MAX_CHECKS checks)"
echo ""

for i in $(seq 1 $MAX_CHECKS); do
    echo "[$i/$MAX_CHECKS] Checking..."
    
    # Check health endpoint
    HEALTH=$(curl -s --max-time 10 "$RENDER_URL/api/health" 2>&1)
    
    if [[ $? -eq 0 ]]; then
        # Parse JSON
        STATUS=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', 'N/A'))" 2>/dev/null)
        DB_RECORDS=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('database_records', 0))" 2>/dev/null)
        LAST_CHECK=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('last_check', 'N/A'))" 2>/dev/null)
        
        echo "   Status: $STATUS"
        echo "   DB Records: $DB_RECORDS"
        echo "   Last Check: $LAST_CHECK"
        
        # Check se deploy completato (2753 records attesi)
        if [[ "$DB_RECORDS" -ge 2753 ]]; then
            echo ""
            echo "✅ DEPLOY COMPLETATO!"
            echo "📊 Dataset aggiornato: $DB_RECORDS records"
            
            # Verifica dataset info
            echo ""
            echo "🔍 Verifica dataset details..."
            curl -s "$RENDER_URL/api/dataset_info" | python3 -m json.tool | head -15
            
            exit 0
        fi
    else
        echo "   ⚠️  Server unreachable (rebuilding...)"
    fi
    
    echo ""
    
    if [[ $i -lt $MAX_CHECKS ]]; then
        sleep $CHECK_INTERVAL
    fi
done

echo "⚠️  Timeout raggiunto dopo $(($MAX_CHECKS * $CHECK_INTERVAL / 60)) minuti"
echo "💡 Il deploy potrebbe richiedere più tempo. Controlla manualmente:"
echo "   curl $RENDER_URL/api/health"
