#!/usr/bin/env python3
"""Analisi Juventus vs Sassuolo"""

import sys
sys.path.append('.')
from web.app_professional import ProfessionalCalculator
import pandas as pd

calculator = ProfessionalCalculator()
df_features = pd.read_csv('data/dataset_features.csv')
df_current = pd.read_csv('data/I1_2526.csv')
calculator.df_features = pd.concat([df_features, df_current], ignore_index=True)

print('='*70)
print('📊 JUVENTUS vs SASSUOLO - Analisi Dati')
print('='*70)

# Juventus casa
stats_juve = calculator._calcola_statistiche_squadra('Juventus', in_casa=True)
print(f'\n⚪ Juventus casa:')
print(f'   Vittorie: {stats_juve["vittorie"]:.1%}')
print(f'   Pareggi: {stats_juve["pareggi"]:.1%}')
print(f'   Sconfitte: {stats_juve["sconfitte"]:.1%}')
print(f'   Partite: {stats_juve["partite_totali"]}')

# Sassuolo trasferta
stats_sass = calculator._calcola_statistiche_squadra('Sassuolo', in_casa=False)
print(f'\n⚫ Sassuolo trasferta:')
print(f'   Vittorie: {stats_sass["vittorie"]:.1%}')
print(f'   Pareggi: {stats_sass["pareggi"]:.1%}')
print(f'   Sconfitte: {stats_sass["sconfitte"]:.1%}')
print(f'   Partite: {stats_sass["partite_totali"]}')

# Predizione
pred, prob, conf = calculator.predici_partita_deterministica('Juventus', 'Sassuolo')
print(f'\n🤖 Predizione Calcolata:')
print(f'   Casa (Juventus): {prob["H"]:.1%}')
print(f'   Pareggio: {prob["D"]:.1%}')
print(f'   Trasferta (Sassuolo): {prob["A"]:.1%}')
print(f'   Confidenza: {conf:.1%}')

print('\n💎 Confronto con Mercato:')
print(f'   Mercato Casa: 77.5% | Modello: {prob["H"]:.1%} → Diff {prob["H"]*100-77.5:+.1f}%')
print(f'   Mercato Trasferta: 9.7% | Modello: {prob["A"]:.1%} → Diff {prob["A"]*100-9.7:+.1f}%')

print('\n' + '='*70)
