#!/usr/bin/env python3
"""
Validazione TUTTI i mercati principali post-hoc
"""
import pandas as pd
import sys
sys.path.insert(0, 'web')
from web.app_professional import ProfessionalCalculator, _calcola_mercati_deterministici

print('📊 VALIDAZIONE MERCATI MULTIPLI')
print('=' * 70)

# Carica risultati backtest
df_backtest = pd.read_csv('validazione_accuratezza_completa.csv')
df_backtest['data'] = pd.to_datetime(df_backtest['data'])
print(f'📁 Backtest: {len(df_backtest)} partite')

# Carica dataset per gol
df_dataset = pd.read_csv('data/dataset_features.csv')
df_dataset['Date'] = pd.to_datetime(df_dataset['Date'])

# Inizializza calculator
calc = ProfessionalCalculator()
calc.carica_dati('data/dataset_features.csv')
print('✅ Calculator inizializzato\n')

# Merge
df_merged = df_backtest.merge(
    df_dataset[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']],
    left_on=['data', 'casa', 'trasferta'],
    right_on=['Date', 'HomeTeam', 'AwayTeam'],
    how='left'
)

total_gol = df_merged['FTHG'].notna().sum()
print(f'✅ Partite con dati completi: {total_gol}/{len(df_merged)}\n')

# Contatori per mercati
results = {
    'over_under_25': {'correct': 0, 'total': 0},
    'double_chance': {'correct': 0, 'total': 0},
    'goal_nogoal': {'correct': 0, 'total': 0}
}

for idx_raw, row in df_merged.iterrows():
    idx = int(idx_raw) if isinstance(idx_raw, (int, float)) else 0  # Type fix per Pylance
    if pd.notna(row['FTHG']) and pd.notna(row['FTAG']):
        fthg = int(row['FTHG'])
        ftag = int(row['FTAG'])
        ftr = row['FTR']
        
        # Predizione
        prob = {'H': row['prob_h'], 'D': row['prob_d'], 'A': row['prob_a']}
        mercati = _calcola_mercati_deterministici(row['casa'], row['trasferta'], prob)
        
        # 1. Over/Under 2.5
        gol_tot = fthg + ftag
        over25_reale = 'over' if gol_tot > 2.5 else 'under'
        over25_pred = mercati['mou25']['consiglio']
        if over25_pred == over25_reale:
            results['over_under_25']['correct'] += 1
        results['over_under_25']['total'] += 1
        
        # 2. Double Chance
        # Mappiamo FTR -> Double Chance reale
        # 1X: Casa o Pareggio
        # X2: Pareggio o Trasferta  
        # 12: Casa o Trasferta
        dc_pred = mercati['mdc']['consiglio']  # es: '1X', 'X2', '12'
        dc_match = False
        if dc_pred == '1X' and ftr in ['H', 'D']:
            dc_match = True
        elif dc_pred == 'X2' and ftr in ['D', 'A']:
            dc_match = True
        elif dc_pred == '12' and ftr in ['H', 'A']:
            dc_match = True
        
        if dc_match:
            results['double_chance']['correct'] += 1
        results['double_chance']['total'] += 1
        
        # 3. Goal/NoGoal (entrambe segnano?)
        gg_reale = 'goal' if (fthg > 0 and ftag > 0) else 'nogoal'  # Capitalizzato corretto
        gg_pred = mercati['mgg']['consiglio']
        if gg_pred == gg_reale:
            results['goal_nogoal']['correct'] += 1
        results['goal_nogoal']['total'] += 1
    
    if (idx + 1) % 100 == 0:
        print(f'   Processate: {idx + 1}/{len(df_merged)}')

# Risultati finali
print(f'\n' + '=' * 70)
print('📈 RISULTATI VALIDAZIONE MERCATI')
print('=' * 70)

for mercato, data in results.items():
    if data['total'] > 0:
        acc = (data['correct'] / data['total'] * 100)
        nome = mercato.replace('_', ' ').title()
        print(f'\n✅ {nome}:')
        print(f'   Accuratezza: {acc:.1f}%')
        print(f'   Corrette: {data["correct"]}/{data["total"]}')

print('\n' + '=' * 70)
print('\n📝 VALORI DA AGGIORNARE IN app_professional.py:')
print('-' * 70)
for mercato, data in results.items():
    if data['total'] > 0:
        acc = data['correct'] / data['total']
        print(f'{mercato}: {acc:.3f}  # ✅ VALIDATO su {data["total"]} partite')
print('=' * 70)
