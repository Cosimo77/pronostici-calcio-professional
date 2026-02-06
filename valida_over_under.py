#!/usr/bin/env python3
"""
Validazione Over/Under 2.5 post-hoc sui risultati backtest
"""
import pandas as pd
import sys
sys.path.insert(0, 'web')
from web.app_professional import ProfessionalCalculator, _calcola_mercati_deterministici

print('📊 VALIDAZIONE OVER/UNDER 2.5')
print('=' * 70)

# Carica risultati backtest
df_backtest = pd.read_csv('validazione_accuratezza_completa.csv')
df_backtest['data'] = pd.to_datetime(df_backtest['data'])  # Converti anche backtest
print(f'📁 Backtest: {len(df_backtest)} partite')

# Carica dataset per gol
df_dataset = pd.read_csv('data/dataset_features.csv')
df_dataset['Date'] = pd.to_datetime(df_dataset['Date'])

# Inizializza calculator
calc = ProfessionalCalculator()
calc.carica_dati('data/dataset_features.csv')
print('✅ Calculator inizializzato')

# Merge
df_merged = df_backtest.merge(
    df_dataset[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']],
    left_on=['data', 'casa', 'trasferta'],
    right_on=['Date', 'HomeTeam', 'AwayTeam'],
    how='left'
)

total_gol = df_merged['FTHG'].notna().sum()
print(f'✅ Partite con gol: {total_gol}/{len(df_merged)}')

# Calcola accuratezza
correct = 0
total = 0

for _, row in df_merged.iterrows():
    if pd.notna(row['FTHG']) and pd.notna(row['FTAG']):
        # Reale
        gol_tot = row['FTHG'] + row['FTAG']
        reale = 'Over' if gol_tot > 2.5 else 'Under'
        
        # Predizione
        prob = {'H': row['prob_h'], 'D': row['prob_d'], 'A': row['prob_a']}
        mercati = _calcola_mercati_deterministici(row['casa'], row['trasferta'], prob)
        pred_lower = mercati['mou25']['consiglio']  # 'over' o 'under' (minuscolo)
        pred = 'Over' if pred_lower == 'over' else 'Under'  # Capitalizza
        
        if pred == reale:
            correct += 1
        total += 1
    
    if total % 100 == 0 and total > 0:
        print(f'   Processate: {total}')

# Risultati
acc = (correct / total * 100) if total > 0 else 0
print(f'\n' + '=' * 70)
print(f'✅ ACCURATEZZA OVER/UNDER 2.5: {acc:.1f}%')
print(f'   Corrette: {correct}/{total}')
print('=' * 70)
