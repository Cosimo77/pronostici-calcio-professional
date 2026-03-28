#!/usr/bin/env python3
"""Test diagnostici predizione Milan vs Torino"""

import sys
sys.path.append('.')
from web.app_professional import ProfessionalCalculator
import pandas as pd

calculator = ProfessionalCalculator()
print('📂 Caricamento dati...')
df_features = pd.read_csv('data/dataset_features.csv')
df_current = pd.read_csv('data/I1_2526.csv')
calculator.df_features = pd.concat([df_features, df_current], ignore_index=True)
print(f'✅ Dataset caricato: {len(calculator.df_features)} partite\n')

# Test 1: Statistiche Milan casa
print('🔍 Test 1: Statistiche Milan casa')
stats_milan = calculator._calcola_statistiche_squadra('Milan', in_casa=True)
print(f'   Vittorie: {stats_milan["vittorie"]:.1%}')
print(f'   Pareggi: {stats_milan["pareggi"]:.1%}')
print(f'   Sconfitte: {stats_milan["sconfitte"]:.1%}')
print(f'   Partite totali: {stats_milan["partite_totali"]}\n')

# Test 2: Statistiche Torino trasferta
print('🔍 Test 2: Statistiche Torino trasferta')
stats_torino = calculator._calcola_statistiche_squadra('Torino', in_casa=False)
print(f'   Vittorie: {stats_torino["vittorie"]:.1%}')
print(f'   Pareggi: {stats_torino["pareggi"]:.1%}')
print(f'   Sconfitte: {stats_torino["sconfitte"]:.1%}')
print(f'   Partite totali: {stats_torino["partite_totali"]}\n')

# Test 3: Predizione completa
print('🔍 Test 3: Predizione Milan vs Torino')
try:
    predizione, probabilita, confidenza = calculator.predici_partita_deterministica('Milan', 'Torino')
    print(f'   Predizione: {predizione}')
    print(f'   Confidenza: {confidenza:.1%}')
    print(f'   Probabilità:')
    print(f'     Casa (Milan): {probabilita["H"]:.1%}')
    print(f'     Pareggio: {probabilita["D"]:.1%}')
    print(f'     Trasferta (Torino): {probabilita["A"]:.1%}')
except Exception as e:
    print(f'   ❌ Errore: {e}')

print('\n' + '='*60)
print('📊 CONFRONTO CON QUOTE MERCATO')
print('='*60)
print('Quote mercato:')
print('  Milan casa: 1.36 (73% prob implicita)')
print('  Torino trasferta: 9.27 (11% prob implicita)')
print('\nPredizione sistema vs mercato:')
print(f'  Milan: {probabilita["H"]:.1%} vs 73% → Differenza: {probabilita["H"]*100 - 73:.1f}%')
print(f'  Torino: {probabilita["A"]:.1%} vs 11% → Differenza: {probabilita["A"]*100 - 11:.1f}%')
