import requests
import json

# Test storage backend
response = requests.get('https://pronostici-calcio-pro.onrender.com/api/health')
health = response.json()

print('🔍 DIAGNOSI STORAGE NEON/POSTGRESQL\n')
print('='*60)

# Dataset storico (sempre su DB)
print('\n📊 DATASET STORICO (partite Serie A):')
print(f'   Database connesso: {"✅" if health.get("database_connesso") else "❌"}')
print(f'   Records: {health.get("database_records", "N/A")}')
print(f'   → Questo è sempre su PostgreSQL')

# Diario betting
print('\n💰 DIARIO BETTING (puntate):')
print(f'   DATABASE_URL configurato: {"✅" if health.get("database_url_set") else "❌"}')
print(f'   DATABASE_URL length: {health.get("database_url_length", "N/A")}')

# Check bet count
diario = requests.get('https://pronostici-calcio-pro.onrender.com/api/diario/all')
bet_count = len(diario.json())
print(f'   Bet correnti: {bet_count}')

# Conclusione
print('\n🎯 VERDETTO:')
if not health.get('database_url_set'):
    print('   ⚠️  DATABASE_URL NON CONFIGURATO su Render!')
    print('   ❌ Diario usa CSV (EFFIMERO - si perde al restart)')
    print('')
    print('   📋 AZIONE NECESSARIA:')
    print('   1. Crea database su Neon.tech')
    print('   2. Configura DATABASE_URL su Render')
    print('   3. Redeploy')
else:
    print('   ✅ DATABASE_URL configurato')
    print('   ✅ Diario su PostgreSQL/Neon (PERSISTENTE)')
    
print('\n' + '='*60)
