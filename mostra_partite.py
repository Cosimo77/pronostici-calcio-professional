#!/usr/bin/env python3
"""Mostra partite Serie A prossime giorni"""
import requests
from datetime import datetime, timedelta

API_KEY = '7109a3c71a972ef639c56bcf0b13bb4b'

# Fetch partite
r = requests.get(
    'https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds',
    params={'apiKey': API_KEY, 'regions': 'eu', 'markets': 'h2h', 'oddsFormat': 'decimal'}
)

partite = r.json()

# Raggruppa per data
from collections import defaultdict
by_date = defaultdict(list)

for p in partite:
    data = p['commence_time'].split('T')[0]
    by_date[data].append(p)

# Mostra prossimi 3 giorni
print("\n⚽ SERIE A - PROSSIME PARTITE")
print("=" * 70)

for data in sorted(by_date.keys())[:3]:
    partite_giorno = by_date[data]
    data_ita = datetime.fromisoformat(data).strftime('%d/%m/%Y')
    
    print(f"\n📅 {data_ita} ({len(partite_giorno)} partite)")
    print("-" * 70)
    
    for p in partite_giorno:
        ora = p['commence_time'].split('T')[1][:5]
        casa = p['home_team']
        ospite = p['away_team']
        
        # Quote medie
        books = [b for b in p.get('bookmakers', []) if len(b.get('markets', [{}])[0].get('outcomes', [])) >= 3]
        if books:
            outcomes = books[0]['markets'][0]['outcomes']
            h_avg = next((o['price'] for o in outcomes if o['name'] == casa), 0)
            x_avg = next((o['price'] for o in outcomes if o['name'] == 'Draw'), 0)
            a_avg = next((o['price'] for o in outcomes if o['name'] == ospite), 0)
            
            print(f"{ora}  {casa:20} vs {ospite:20}")
            print(f"       1={h_avg:.2f}  X={x_avg:.2f}  2={a_avg:.2f}")

print(f"\n\n📊 Quota API rimasta: {r.headers.get('x-requests-remaining', 'N/A')}/500")
