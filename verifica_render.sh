#!/bin/bash
# Script da eseguire il 1 Febbraio dopo deploy Render

echo "=== VERIFICA POST-DEPLOY 1 FEBBRAIO ==="
echo ""

# 1. Verifica stato
echo "1. Controllo stato sistema..."
./check_render_status.sh

echo ""
echo "2. Test predizione Render..."
curl -s "https://pronostici-calcio-professional.onrender.com/api/predict_enterprise" \
  -H "Content-Type: application/json" \
  -d '{"squadra_casa": "Inter", "squadra_ospite": "Milan"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Predizione: {d[\"predizione\"]}'); print(f'Confidenza: {d[\"confidenza\"]:.1f}%')"

echo ""
echo "3. Workflow status..."
curl -s "https://pronostici-calcio-professional.onrender.com/api/automation/status" \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Running: {d[\"running\"]}'); print(f'Last update: {d[\"last_update\"]}')"

echo ""
echo "=== CHECKLIST FINALE ==="
echo "[ ] Render mostra 2673 partite"
echo "[ ] Predizioni funzionano"
echo "[ ] Auto-deploy DISABILITATO (Settings -> Build & Deploy)"
echo ""
echo "Se tutto OK, sistema è PRONTO!"
echo "Prossimo auto-update: 2 Febbraio ore 06:00"
