#!/usr/bin/env python3
"""Analizza distribuzione EV vs ROI per trovare sweet spot"""

import pandas as pd
import numpy as np

# Carica risultati backtest
df = pd.read_csv('backtest_fase2_risultati.csv')

# Analisi 1: Distribuzione EV
df['ev_bucket'] = pd.cut(df['ev'], bins=[0, 15, 20, 25, 30, 100], 
                          labels=['10-15%', '15-20%', '20-25%', '25-30%', '>30%'])

print('=' * 80)
print('📊 ANALISI EV vs ROI per FASCIA (CRITICAL)')
print('=' * 80)
print()

for bucket in ['10-15%', '15-20%', '20-25%', '25-30%', '>30%']:
    subset = df[df['ev_bucket'] == bucket]
    if len(subset) == 0:
        continue
    
    roi = (subset['profit'].sum() / len(subset) * 100)
    wr = ((subset['risultato'] == 'WIN').sum() / len(subset) * 100)
    ev_medio = subset['ev'].mean()
    odds_media = subset['odds'].mean()
    
    marker = '✅' if roi > 0 else '❌'
    
    print(f'{marker} EV {bucket}:')
    print(f'   Trade: {len(subset)}')
    print(f'   Win Rate: {wr:.1f}%')
    print(f'   ROI: {roi:+.2f}%')
    print(f'   EV Medio: {ev_medio:.1f}%')
    print(f'   Quota Media: {odds_media:.2f}')
    print()

print('=' * 80)
print('🔬 ANALISI STRATEGIA x EV (Sweet Spot)')
print('=' * 80)
print()

# Test varie soglie EV
for soglia in [12, 15, 18, 20, 25]:
    df_filtered = df[df['ev'] >= soglia]
    
    if len(df_filtered) == 0:
        continue
    
    roi_totale = (df_filtered['profit'].sum() / len(df_filtered) * 100)
    wr_totale = ((df_filtered['risultato'] == 'WIN').sum() / len(df_filtered) * 100)
    
    marker = '🎯' if roi_totale > 0 else '⚠️'
    
    print(f'{marker} EV ≥{soglia}%: {len(df_filtered)} trade, WR {wr_totale:.1f}%, ROI {roi_totale:+.2f}%')

print()
print('=' * 80)
print('📈 STRATEGIA MIGLIORE per FASCIA EV')
print('=' * 80)
print()

# Analizza ogni strategia per fascia EV
for strat in ['DC_X2', 'DC_1X', 'OVER_25', 'UNDER_25']:
    df_strat = df[df['strategia'] == strat]
    
    if len(df_strat) == 0:
        continue
    
    print(f'🎲 {strat}')
    
    for bucket in ['10-15%', '15-20%', '20-25%', '25-30%', '>30%']:
        subset = df_strat[df_strat['ev_bucket'] == bucket]
        if len(subset) == 0:
            continue
        
        roi = (subset['profit'].sum() / len(subset) * 100)
        wr = ((subset['risultato'] == 'WIN').sum() / len(subset) * 100)
        
        marker = '✅' if roi > 0 else '❌'
        print(f'   {marker} EV {bucket}: {len(subset)} trade, WR {wr:.1f}%, ROI {roi:+.2f}%')
    
    print()

print('=' * 80)
print('💡 RACCOMANDAZIONI MATEMATICHE')
print('=' * 80)
print()

# Trova best performing bucket
best_roi = -100
best_bucket = None

for bucket in ['10-15%', '15-20%', '20-25%', '25-30%', '>30%']:
    subset = df[df['ev_bucket'] == bucket]
    if len(subset) < 20:  # Serve sample size minimo
        continue
    
    roi = (subset['profit'].sum() / len(subset) * 100)
    if roi > best_roi:
        best_roi = roi
        best_bucket = bucket

if best_bucket:
    print(f'✅ Sweet Spot Identificato: EV {best_bucket} (ROI {best_roi:+.2f}%)')
    
    # Trova range esatto
    df_best = df[df['ev_bucket'] == best_bucket]
    ev_min = df_best['ev'].min()
    ev_max = df_best['ev'].max()
    
    print(f'   Range EV consigliato: {ev_min:.1f}% - {ev_max:.1f}%')
    print(f'   Trade disponibili: {len(df_best)}')
    
    # Strategie profittevoli in quel range
    print()
    print('   Strategie profittevoli in questo range:')
    for strat in df_best['strategia'].unique():
        subset = df_best[df_best['strategia'] == strat]
        roi = (subset['profit'].sum() / len(subset) * 100)
        if roi > 0:
            print(f'   ✅ {strat}: ROI {roi:+.2f}% ({len(subset)} trade)')
else:
    print('❌ Nessun sweet spot profittevole trovato')

print()
