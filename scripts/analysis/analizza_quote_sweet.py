#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('backtest_fase2_risultati.csv')

# Filtra sweet spot EV 20-25%
df_sweet = df[(df['ev'] >= 20) & (df['ev'] <= 25)]

print('=' * 80)
print('🔍 ANALISI QUOTE nel SWEET SPOT 20-25% EV')
print('=' * 80)
print()

for strat in ['DC_X2', 'DC_1X', 'UNDER_25']:
    subset = df_sweet[df_sweet['strategia'] == strat]
    if len(subset) == 0:
        continue
    
    roi = (subset['profit'].sum() / len(subset) * 100)
    wr = ((subset['risultato'] == 'WIN').sum() / len(subset) * 100)
    
    print(f'{strat}: {len(subset)} trade, WR {wr:.1f}%, ROI {roi:+.2f}%')
    print(f'  Quote Range: {subset["odds"].min():.2f} - {subset["odds"].max():.2f}')
    print(f'  Quote Media: {subset["odds"].mean():.2f}')
    print(f'  Quote Mediana: {subset["odds"].median():.2f}')
    
    # Trova trade profittevoli
    wins = subset[subset['risultato'] == 'WIN']
    if len(wins) > 0:
        print(f'  Quote su WIN: {wins["odds"].min():.2f} - {wins["odds"].max():.2f} (media {wins["odds"].mean():.2f})')
    print()
