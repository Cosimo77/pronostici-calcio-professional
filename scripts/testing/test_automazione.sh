#!/bin/bash
# TEST AUTOMAZIONE - Verifica sistema tracking completo

echo "🧪 TEST SISTEMA TRACKING FASE 2"
echo "=================================="

cd /Users/cosimomassaro/Desktop/pronostici_calcio

# Test 1: File necessari
echo ""
echo "1️⃣ Verifica file..."
files=("genera_tracking_fase2.py" "aggiorna_tracking_fase2.py" "aggiorna_risultati_auto.py" "monitora_tracking.sh")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MANCANTE"
    fi
done

# Test 2: CSV tracking
echo ""
echo "2️⃣ Verifica CSV tracking..."
if [ -f "tracking_fase2_febbraio2026.csv" ]; then
    num_trades=$(wc -l < tracking_fase2_febbraio2026.csv)
    echo "  ✅ File trovato: $((num_trades - 1)) trade"
else
    echo "  ❌ tracking_fase2_febbraio2026.csv non trovato"
fi

# Test 3: API endpoint
echo ""
echo "3️⃣ Test API tracking..."
response=$(curl -s -w "%{http_code}" http://localhost:5008/api/tracking/fase2 -o /tmp/api_test.json)
if [ "$response" = "200" ]; then
    echo "  ✅ API risponde correttamente (HTTP 200)"
    total=$(python3 -c "import json; print(json.load(open('/tmp/api_test.json'))['summary']['total_trades'])" 2>/dev/null)
    echo "  📊 Trade totali: $total"
else
    echo "  ⚠️  API non disponibile (HTTP $response)"
fi

# Test 4: Crontab
echo ""
echo "4️⃣ Verifica crontab..."
cron_count=$(crontab -l 2>/dev/null | grep -c "tracking_fase2\|tracking_cron")
if [ "$cron_count" -gt 0 ]; then
    echo "  ✅ Crontab configurato ($cron_count job trovati)"
else
    echo "  ⚠️  Nessun job cron trovato"
fi

# Test 5: Esecuzione manuale
echo ""
echo "5️⃣ Test esecuzione script..."
python3 genera_tracking_fase2.py --local > /tmp/test_genera.log 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Script genera_tracking_fase2.py funziona"
else
    echo "  ❌ Errore esecuzione genera_tracking_fase2.py"
    echo "     Vedi: /tmp/test_genera.log"
fi

echo ""
echo "=================================="
echo "✅ Test completato!"
echo ""
echo "📋 Prossimi step:"
echo "  1. Dashboard: http://localhost:5008/tracking"
echo "  2. Log cron: tail -f logs/tracking_cron.log"
echo "  3. Test manuale: ./monitora_tracking.sh"
echo "=================================="
