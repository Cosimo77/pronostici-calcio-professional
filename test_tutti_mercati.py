#!/usr/bin/env python3
"""Test completo di tutti i mercati"""

import requests
import json

url = "https://pronostici-calcio-professional.onrender.com/api/predict_enterprise"
data = {"squadra_casa": "Juventus", "squadra_ospite": "Inter"}

print("🔍 VERIFICA TUTTI I MERCATI - Juventus vs Inter")
print("=" * 70)

response = requests.post(url, json=data)
result = response.json()

mercati = result.get('mercati', {})
print(f"\n📊 Totale mercati trovati: {len(mercati)}")
print("=" * 70)

# Test ogni mercato
errori = []
ok = []

for i, (key, mercato) in enumerate(sorted(mercati.items()), 1):
    nome = mercato.get('nome', 'N/A')
    prob = mercato.get('probabilita', {})
    consiglio = mercato.get('consiglio', 'N/A')
    confidenza = mercato.get('confidenza', 0)
    
    print(f"\n{i:2d}. [{key.upper()}] {nome}")
    print(f"    🎯 Consiglio: {consiglio}")
    print(f"    📈 Confidenza: {confidenza:.1%}")
    
    # Verifica probabilità
    if isinstance(prob, dict):
        somma = sum(prob.values())
        print(f"    📊 Probabilità: {prob}")
        
        if abs(somma - 1.0) > 0.01:
            errore = f"{key}: Somma prob = {somma:.4f} (dovrebbe essere 1.0)"
            print(f"    ❌ ERRORE: {errore}")
            errori.append(errore)
        else:
            print(f"    ✅ Somma probabilità = {somma:.4f}")
            ok.append(key)
    else:
        print(f"    💡 Valore singolo: {prob}")
        ok.append(key)

# Riepilogo
print("\n" + "=" * 70)
print("📊 RIEPILOGO VERIFICA")
print("=" * 70)
print(f"✅ Mercati funzionanti: {len(ok)}/{len(mercati)}")
print(f"❌ Mercati con errori: {len(errori)}/{len(mercati)}")

if errori:
    print("\n⚠️  ERRORI TROVATI:")
    for e in errori:
        print(f"  - {e}")
else:
    print("\n🎉 TUTTI I MERCATI FUNZIONANO CORRETTAMENTE!")

# Lista mercati funzionanti
print(f"\n✅ Mercati OK: {', '.join(ok)}")
