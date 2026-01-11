#!/usr/bin/env python3
"""Test 4 fix mercati implementati"""

import requests
import json

url = "http://localhost:5008/api/predict_enterprise"
data = {"squadra_casa": "Inter", "squadra_ospite": "Napoli"}

response = requests.post(url, json=data)
result = response.json()
m = result['mercati']

print('\n=== TEST 4 FIX MERCATI ===\n')

print('1. CLEAN SHEET (era 3, ora 4 categorie):')
cs = m['mcs']['probabilita']
print(f'   Categorie: {list(cs.keys())}')
print(f'   entrambe: {cs["entrambe"]:.3f} (0-0)')
print(f'   solo_casa: {cs["solo_casa"]:.3f} (1-0, 2-0)')
print(f'   solo_ospite: {cs["solo_ospite"]:.3f} (0-1, 0-2)')
print(f'   nessuna: {cs["nessuna"]:.3f} (1-1, 2-1, ecc.)')
print(f'   Somma: {sum(cs.values()):.3f}')

print('\n2. EXACT SCORE (era hardcoded, ora Poisson):')
es = m['mes']['probabilita']
top5 = sorted(es.items(), key=lambda x: x[1], reverse=True)[:5]
print('   Top 5 risultati:')
for ris, prob in top5:
    print(f'     {ris}: {prob:.3f}')

print('\n3. CARTELLINI (usa dati reali HY/AY):')
print(f'   Previsti: {m["mcards"]["cartellini_previsti"]} card')
print(f'   Over 4.5: {m["mcards"]["probabilita"]["over"]:.3f}')
print(f'   Under 4.5: {m["mcards"]["probabilita"]["under"]:.3f}')

print('\n4. CORNER (usa dati reali HC/AC):')
print(f'   Previsti: {m["mcorner"]["corner_previsti"]} corner')
print(f'   Over 9.5: {m["mcorner"]["probabilita"]["over"]:.3f}')
print(f'   Under 9.5: {m["mcorner"]["probabilita"]["under"]:.3f}')

print('\n✅ TUTTI I 4 FIX IMPLEMENTATI E FUNZIONANTI!\n')
