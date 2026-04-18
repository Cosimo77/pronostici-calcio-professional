#!/usr/bin/env python3
"""Test sistema update risultati"""
from integrations.football_data_results import get_results_client
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("TEST SISTEMA UPDATE RISULTATI")
print("=" * 60)

# 1. Scarica risultati ultimi 7 giorni
print("\n1️⃣ SCARICO RISULTATI DA FOOTBALL-DATA.CO.UK...")
client = get_results_client()
results = client.get_results_for_tracking(days_back=7)

print(f"\n📊 Trovati {len(results)} risultati ultimi 7 giorni\n")

if results:
    print("Prime 5 partite:")
    for r in results[:5]:
        print(f"  {r['data']}: {r['casa']} {r['home_goals']}-{r['away_goals']} {r['ospite']}")
        print(f"    1X2: {r['1X2']} | OU2.5: {r['OU25']} | GGNG: {r['GGNG']}\n")
else:
    print("❌ Nessun risultato trovato (normale se non ci sono partite questa settimana)")

# 2. Check predizioni pending
print("\n2️⃣ VERIFICO PREDIZIONI PENDING NEL TRACKING...")
df = pd.read_csv('tracking_predictions_live.csv')
df['Data'] = pd.to_datetime(df['Data'])
pending = df[df['Risultato_Reale'].isna() | (df['Risultato_Reale'] == '')]

print(f"\n⏳ PREDIZIONI PENDING: {len(pending)}")
if len(pending) > 0:
    print(f"   Date range: {pending['Data'].min()} → {pending['Data'].max()}")

# 3. Match potenziali
cutoff = datetime.now() - timedelta(days=7)
pending_recent = pending[pending['Data'] >= cutoff]

print(f"\n🎯 Predizioni pending matchabili (ultimi 7gg): {len(pending_recent)}")
if len(pending_recent) > 0:
    print("\n   Top 5:")
    for _, row in pending_recent.head(5).iterrows():
        print(f"   {row['Data'].strftime('%Y-%m-%d')}: {row['Casa']} vs {row['Ospite']} ({row['Mercato']})")

# 4. Simula matching
if results and len(pending_recent) > 0:
    print("\n\n3️⃣ SIMULAZIONE MATCHING...")
    matches = 0
    for result in results:
        for _, pred in pending_recent.iterrows():
            if (pred['Casa'] == result['casa'] and 
                pred['Ospite'] == result['ospite'] and
                pred['Data'].strftime('%Y-%m-%d') == result['data']):
                matches += 1
                print(f"  ✅ MATCH: {result['casa']} vs {result['ospite']} ({result['data']})")
    
    print(f"\n📊 Potenziali update: {matches} predizioni")
else:
    print("\n📝 Nessun match possibile (nessun risultato o predizioni recenti)")

print("\n" + "=" * 60)
print("TEST COMPLETATO")
print("=" * 60)
