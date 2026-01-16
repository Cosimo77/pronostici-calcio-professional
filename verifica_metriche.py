#!/usr/bin/env python3
"""Verifica coerenza metriche performance"""

import requests

print("🔍 VERIFICA METRICHE PERFORMANCE\n")

base = "https://pronostici-calcio-professional.onrender.com"

# Metriche dichiarate
partite_analizzate = 200
predizioni_corrette = 86
accuratezza_dichiarata = 43.2
mercati_dichiarati = 27
confidenza_media = 44.9

# 1. Verifica matematica
print("1️⃣ Coerenza Matematica:")
accuratezza_calcolata = (predizioni_corrette / partite_analizzate) * 100
print(f"   86/200 = {accuratezza_calcolata:.1f}%")
print(f"   Dichiarato: {accuratezza_dichiarata}%")
if abs(accuratezza_calcolata - accuratezza_dichiarata) < 0.5:
    print("   ✅ Coerente")
else:
    print(f"   ❌ Discrepanza: {abs(accuratezza_calcolata - accuratezza_dichiarata):.1f}%")

# 2. Confronto con dataset totale
print("\n2️⃣ Confronto Dataset:")
r = requests.get(f"{base}/api/health", timeout=10)
h = r.json()
db_total = h.get('database_records', 0)
print(f"   Dataset totale: {db_total} partite")
print(f"   Partite analizzate: {partite_analizzate}")
percentuale = (partite_analizzate / db_total * 100) if db_total > 0 else 0
print(f"   Copertura: {percentuale:.1f}%")

if percentuale < 10:
    print(f"   ⚠️ PROBLEMA: Solo {partite_analizzate}/{db_total} partite!")
    print(f"   Le metriche sono su campione ridotto (test set?)")

# 3. Mercati supportati
print("\n3️⃣ Mercati Supportati:")
try:
    r = requests.post(
        f"{base}/api/predict_enterprise",
        json={"squadra_casa": "Juventus", "squadra_ospite": "Inter"},
        timeout=15
    )
    p = r.json()
    mercati = p.get('mercati', {})
    mercati_reali = len(mercati)
    print(f"   API restituisce: {mercati_reali} mercati")
    print(f"   Dashboard mostra: {mercati_dichiarati}")
    
    if mercati_reali != mercati_dichiarati:
        print(f"   ⚠️ Discrepanza: {abs(mercati_reali - mercati_dichiarati)}")
    else:
        print("   ✅ Coerente")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

# 4. Riepilogo
print("\n" + "="*50)
print("\n📊 RIEPILOGO AUDIT:")
print(f"   • Accuratezza 43.2%: ✅ Matematicamente corretta")
print(f"   • Dataset coverage: {percentuale:.1f}% ({partite_analizzate}/{db_total})")
print(f"   • Mercati: Verifica {mercati_reali} vs {mercati_dichiarati}")
print(f"   • Confidenza media {confidenza_media}%: Non verificabile via API")

print("\n⚠️ NOTA: Le metriche performance sembrano riferite")
print("   al test set (200 partite) non all'intero dataset.")
