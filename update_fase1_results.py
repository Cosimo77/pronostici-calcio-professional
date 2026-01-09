#!/usr/bin/env python3
"""Aggiorna risultati tracking FASE1"""

import pandas as pd

# Carica tracking
df = pd.read_csv('tracking_fase1_gennaio2026.csv')

# Risultati reali dal CSV football-data.co.uk
risultati = {
    ('Bologna', 'Atalanta'): ('A', '0-2'),      # Trasferta
    ('Lazio', 'Fiorentina'): ('D', '2-2'),      # Pareggio WIN
    ('Torino', 'Udinese'): ('A', '1-2'),        # Trasferta
    ('Cremonese', 'Cagliari'): ('D', '2-2')     # Pareggio WIN
}

bankroll = 500.00
profit_tot = 0
n = 0

for idx, row in df.iterrows():
    key = (row['Casa'], row['Ospite'])
    
    if key in risultati:
        esito, score = risultati[key]
        quota = float(row['Quota_X'])
        stake = float(row['Stake'])
        
        # Calcola profit
        if esito == 'D':  # Pareggio = WIN
            profit = stake * (quota - 1)
        else:  # Altro = LOSS
            profit = -stake
        
        profit_tot += profit
        bankroll += profit
        n += 1
        roi = (profit_tot / (stake * n)) * 100
        
        # Aggiorna riga
        df.at[idx, 'Risultato'] = esito
        df.at[idx, 'Profit_Loss'] = f"{profit:.2f}"
        df.at[idx, 'Bankroll'] = f"{bankroll:.2f}"
        df.at[idx, 'ROI_%'] = f"{roi:.2f}"
        df.at[idx, 'Note'] = f"{'WIN' if esito == 'D' else 'LOSS'} - {score}"

# Salva
df.to_csv('tracking_fase1_gennaio2026.csv', index=False)

# Report
wins = sum(1 for _, (e, _) in risultati.items() if e == 'D')
print("✅ TRACKING FASE1 AGGIORNATO!")
print()
print(f"📊 Performance 4 partite (7-8 Gennaio):")
print(f"   ✅ Lazio 2-2 Fiorentina @3.00")
print(f"   ✅ Cremonese 2-2 Cagliari @3.07")
print(f"   ❌ Bologna 0-2 Atalanta")
print(f"   ❌ Torino 1-2 Udinese")
print()
print(f"   Win Rate: {wins}/4 = {wins/4*100:.0f}%")
print(f"   Profit: €{profit_tot:+.2f}")
print(f"   Bankroll: €{bankroll:.2f}")
print(f"   ROI: {roi:+.2f}%")
print()
print("🎯 vs Target FASE1:")
print(f"   Win Rate: 50% (target 31%) → +19pp ✅")
print(f"   ROI: {roi:+.2f}% (target +7.17%) → {roi-7.17:+.2f}pp")
