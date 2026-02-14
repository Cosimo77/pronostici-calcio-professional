#!/usr/bin/env python3
"""Simulazione risultati per demo dashboard"""
import csv

# Leggi CSV
with open('tracking_fase2_febbraio2026.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    trades = list(reader)

# SIMULAZIONE: 3 trade chiusi (2 WIN, 1 LOSS)
print("🎬 SIMULAZIONE RISULTATI DEMO\n")

# 1. Roma vs Cagliari Over 2.5 @ 2.1 → WIN (finita 2-1 = 3 gol)
trades[0]['Risultato'] = 'WIN'
trades[0]['Note'] = 'SIMULAZIONE TEST - Finita 2-1 (3 gol totali)'
print("1. ✅ Roma-Cagliari Over 2.5: WIN (2-1, 3 gol)")

# 2. Inter vs Juventus DC 1X @ 1.41 → WIN (finita 1-1)
trades[2]['Risultato'] = 'WIN'
trades[2]['Note'] = 'SIMULAZIONE TEST - Finita 1-1 (pareggio)'
print("2. ✅ Inter-Juventus DC 1X: WIN (1-1, pareggio)")

# 3. Como vs Fiorentina DC 1X @ 1.32 → LOSS (finita 0-2, ospiti vince)
trades[3]['Risultato'] = 'LOSS'
trades[3]['Note'] = 'SIMULAZIONE TEST - Finita 0-2 (ospiti vincente)'
print("3. ❌ Como-Fiorentina DC 1X: LOSS (0-2, ospiti vince)")

# Salva
with open('tracking_fase2_febbraio2026.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
    writer.writeheader()
    writer.writerows(trades)

print("\n✅ CSV aggiornato con simulazione!")
print("📊 Ora esegui: python3 aggiorna_tracking_fase2.py")
