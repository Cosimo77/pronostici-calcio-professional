#!/usr/bin/env python3
"""Calcola distribuzione completa risultati esatti Udinese vs Inter"""

import math
from scipy.stats import poisson

print("🎯 DISTRIBUZIONE RISULTATI ESATTI: Udinese vs Inter\n")

# Dati dalla predizione
prob_casa = 28.1 / 100
prob_x = 29.2 / 100
prob_trasferta = 42.7 / 100
gol_totali = 2.7
casa_segna = 59.0 / 100
ospite_segna = 72.7 / 100

# Stima lambda (media gol) per squadra
# Usando proporzioni basate su prob vittoria
lambda_casa = gol_totali * (prob_casa + 0.5 * prob_x) / (prob_casa + prob_x + prob_trasferta)
lambda_ospite = gol_totali * (prob_trasferta + 0.5 * prob_x) / (prob_casa + prob_x + prob_trasferta)

# Adjust per arrivare a 2.7 totali
lambda_casa = 1.05  # Udinese
lambda_ospite = 1.65  # Inter (più forte)

print(f"📊 Media gol attesi:")
print(f"   Udinese (casa): {lambda_casa:.2f}")
print(f"   Inter (trasferta): {lambda_ospite:.2f}")
print(f"   Totale: {lambda_casa + lambda_ospite:.2f}\n")

# Calcola probabilità risultati più comuni (0-0 fino a 4-4)
print("=" * 60)
print("TOP 15 RISULTATI ESATTI PIÙ PROBABILI:")
print("=" * 60)

risultati = []
for gol_casa in range(5):
    for gol_ospite in range(5):
        prob = poisson.pmf(gol_casa, lambda_casa) * poisson.pmf(gol_ospite, lambda_ospite)
        risultati.append((gol_casa, gol_ospite, prob * 100))

# Ordina per probabilità decrescente
risultati_sorted = sorted(risultati, key=lambda x: x[2], reverse=True)

# Mostra top 15
for i, (gc, go, prob) in enumerate(risultati_sorted[:15], 1):
    # Determina esito
    if gc > go:
        esito = "1️⃣ Casa"
    elif gc < go:
        esito = "2️⃣ Trasferta"
    else:
        esito = "❌ Pareggio"
    
    # Highlight risultato dichiarato (1-1)
    marker = " ⭐ DICHIARATO" if gc == 1 and go == 1 else ""
    
    print(f"{i:2d}. {gc}-{go}  {prob:5.1f}%  {esito}{marker}")

# Somma probabilità per esito
print("\n" + "=" * 60)
print("VERIFICA PROBABILITÀ PER ESITO:")
print("=" * 60)

prob_1_calc = sum(prob for gc, go, prob in risultati if gc > go)
prob_x_calc = sum(prob for gc, go, prob in risultati if gc == go)
prob_2_calc = sum(prob for gc, go, prob in risultati if gc < go)

print(f"Casa (1):      {prob_1_calc:5.1f}% (dichiarato: 28.1%)")
print(f"Pareggio (X):  {prob_x_calc:5.1f}% (dichiarato: 29.2%)")
print(f"Trasferta (2): {prob_2_calc:5.1f}% (dichiarato: 42.7%)")

# Confronto
print("\n" + "=" * 60)
print("COERENZA:")
print("=" * 60)
diff_1 = abs(prob_1_calc - 28.1)
diff_x = abs(prob_x_calc - 29.2)
diff_2 = abs(prob_2_calc - 42.7)

if diff_1 < 3 and diff_x < 3 and diff_2 < 3:
    print("✅ Distribuzione Poisson coerente con probabilità 1X2")
else:
    print(f"⚠️ Discrepanze: Casa {diff_1:.1f}%, X {diff_x:.1f}%, Trasferta {diff_2:.1f}%")

# Verifica 1-1
prob_1_1 = next(prob for gc, go, prob in risultati if gc == 1 and go == 1)
print(f"\n🎯 Risultato esatto 1-1:")
print(f"   Calcolato: {prob_1_1:.1f}%")
print(f"   Dichiarato: 14.9%")
if abs(prob_1_1 - 14.9) < 2:
    print("   ✅ Coerente")
else:
    print(f"   ⚠️ Differenza: {abs(prob_1_1 - 14.9):.1f}%")
