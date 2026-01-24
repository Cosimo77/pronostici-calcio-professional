#!/bin/bash
# Script per verificare stato GitHub Actions

echo "🔍 Verifica GitHub Actions..."
echo ""

# 1. Controlla se workflow esiste
echo "📋 Workflow disponibili:"
curl -s "https://api.github.com/repos/Cosimo77/pronostici-calcio-professional/actions/workflows" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
workflows = data.get('workflows', [])
if workflows:
    for w in workflows:
        print(f\"  ✅ {w['name']} - State: {w['state']} - Path: {w['path']}\")
else:
    print('  ❌ Nessun workflow trovato')
    print('     → Vai su https://github.com/Cosimo77/pronostici-calcio-professional/actions')
    print('     → Clicca \"Enable workflows\" se presente')
"

echo ""

# 2. Controlla ultime esecuzioni
echo "📊 Ultime esecuzioni:"
curl -s "https://api.github.com/repos/Cosimo77/pronostici-calcio-professional/actions/runs?per_page=5" | \
  python3 -c "
import sys, json
from datetime import datetime
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])
if runs:
    for r in runs[:5]:
        created = r['created_at'][:16].replace('T', ' ')
        status = '✅' if r['conclusion'] == 'success' else '❌' if r['conclusion'] == 'failure' else '⏳'
        print(f\"  {status} {created} - {r['name']} - {r['event']}\")
else:
    print('  ℹ️  Nessuna esecuzione ancora')
    print('     → Esegui manualmente il workflow per attivare lo schedule')
"

echo ""
echo "🎯 Prossimi step:"
echo "   1. Se workflow non trovato: abilita Actions su GitHub"
echo "   2. Esegui workflow manualmente per attivare schedule"
echo "   3. Schedule partirà automaticamente domani alle 06:00"
