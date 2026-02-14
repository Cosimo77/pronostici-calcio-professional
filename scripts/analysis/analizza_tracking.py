#!/usr/bin/env python3
"""
Aggiorna risultati giocate real-time dopo partite giocate
"""

import pandas as pd
from datetime import datetime

# Carica tracking
df = pd.read_csv('tracking_giocate.csv')

print("\n📊 TRACKING GIOCATE LIVE\n" + "="*60)

# Filtra pending
pending = df[df['Risultato'] == 'PENDING']
completate = df[df['Risultato'] != 'PENDING']

print(f"\n🎯 Giocate attive: {len(pending)}")
for _, row in pending.iterrows():
    print(f"\n{row['Data']} - {row['Partita']}")
    print(f"  Mercato: {row['Mercato']} @ {row['Quota_Sistema']}")
    print(f"  Stake: €{row['Stake']}")
    print(f"  EV Realistico: {row['EV_Realistico']}")
    print(f"  Note: {row['Note']}")

if len(completate) > 0:
    print(f"\n\n✅ Giocate completate: {len(completate)}")
    
    total_stake = completate['Stake'].sum()
    total_profit = completate['Profit'].sum()
    roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
    
    wins = len(completate[completate['Risultato'] == 'WIN'])
    wr = (wins / len(completate) * 100) if len(completate) > 0 else 0
    
    print(f"\n📈 PERFORMANCE REALE:")
    print(f"  Stake totale: €{total_stake:.2f}")
    print(f"  Profit: €{total_profit:+.2f}")
    print(f"  ROI: {roi:+.1f}%")
    print(f"  Win Rate: {wr:.1f}%")
    
    print(f"\n📊 CONFRONTO EV MODELLO VS REALE:")
    ev_medio_modello = completate['EV_Modello'].str.rstrip('%').astype(float).mean()
    print(f"  EV medio sistema: +{ev_medio_modello:.1f}%")
    print(f"  ROI reale: {roi:+.1f}%")
    print(f"  Shrinkage: {(roi/ev_medio_modello*100):.0f}%")

print("\n\n💡 AGGIORNA MANUALMENTE RISULTATI:")
print("1. Apri: tracking_giocate.csv")
print("2. Cambia PENDING → WIN/LOSS")
print("3. Inserisci profit (+0.45 per win @1.45, -1.00 per loss)")
print("4. Riesegui: python3 analizza_tracking.py")
print()
