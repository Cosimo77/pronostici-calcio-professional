#!/usr/bin/env python3
"""
Test completo ProfessionalCalculator per validazione presentazione
"""
import sys
import os
sys.path.insert(0, 'web')

import pandas as pd
from datetime import datetime

# Import classe dalla webapp
from app_professional import ProfessionalCalculator

print('🧪 TEST PROFESSIONAL CALCULATOR')
print('=' * 70)

# 1. Inizializza calculator
calc = ProfessionalCalculator()
print('\n📊 Caricamento dati...')
if calc.carica_dati('data/dataset_features.csv'):
    print(f'✅ Dati caricati: {len(calc.df_features)} partite')
    print(f'✅ Squadre disponibili: {len(calc.squadre_disponibili)}')
else:
    print('❌ Errore caricamento dati')
    sys.exit(1)

# 2. Test predizioni su big match
print('\n⚽ TEST PREDIZIONI BIG MATCH')
print('=' * 70)

test_matches = [
    ('Inter', 'Milan', 'Derby Milano'),
    ('Juventus', 'Napoli', 'Sfida Scudetto'),
    ('Roma', 'Lazio', 'Derby Capitale'),
    ('Atalanta', 'Fiorentina', 'Match Europa'),
    ('Bologna', 'Torino', 'Scontro Salvezza')
]

risultati = []

for casa, trasferta, desc in test_matches:
    print(f'\n{desc}: {casa} vs {trasferta}')
    try:
        pred, prob, conf = calc.predici_partita_deterministica(casa, trasferta)
        
        risultati.append({
            'casa': casa,
            'trasferta': trasferta,
            'predizione': pred,
            'confidenza': conf,
            'prob_h': prob['H'],
            'prob_d': prob['D'],
            'prob_a': prob['A'],
            'status': 'OK'
        })
        
        print(f'  Predizione: {pred}')
        print(f'  Confidenza: {conf:.1f}%')
        print(f'  Probabilità: H {prob["H"]:.1%} | D {prob["D"]:.1%} | A {prob["A"]:.1%}')
        print(f'  ✅ OK')
        
    except Exception as e:
        print(f'  ❌ Errore: {e}')
        risultati.append({
            'casa': casa,
            'trasferta': trasferta,
            'status': 'ERRORE',
            'errore': str(e)
        })

# 3. Statistiche finali
print('\n' + '=' * 70)
print('📊 STATISTICHE TEST')
print('=' * 70)

ok_count = sum(1 for r in risultati if r['status'] == 'OK')
print(f'\nPredizioni completate: {ok_count}/{len(test_matches)}')

if ok_count > 0:
    df_risultati = pd.DataFrame([r for r in risultati if r['status'] == 'OK'])
    
    print(f'\nConfidenza media: {df_risultati["confidenza"].mean():.1f}%')
    print(f'Confidenza min: {df_risultati["confidenza"].min():.1f}%')
    print(f'Confidenza max: {df_risultati["confidenza"].max():.1f}%')
    
    print(f'\nDistribuzione predizioni:')
    pred_dist = df_risultati['predizione'].value_counts()
    for pred, count in pred_dist.items():
        print(f'  {pred}: {count} ({count/len(df_risultati)*100:.1f}%)')

# 4. Verifica coerenza
print('\n🔍 VERIFICA COERENZA')
print('=' * 70)

# Test stessa partita 3 volte (deve dare stesso risultato)
test_casa, test_trasferta = 'Inter', 'Milan'
print(f'\nTest coerenza: {test_casa} vs {test_trasferta} (3 volte)')

predictions = []
for i in range(3):
    pred, prob, conf = calc.predici_partita_deterministica(test_casa, test_trasferta)
    predictions.append((pred, conf, prob['H']))
    
# Verifica che siano identici
if len(set(predictions)) == 1:
    print(f'✅ Sistema deterministico: 3/3 predizioni identiche')
    print(f'   Predizione: {predictions[0][0]}')
    print(f'   Confidenza: {predictions[0][1]:.1f}%')
else:
    print(f'⚠️  Sistema non deterministico: risultati diversi')
    for i, p in enumerate(predictions, 1):
        print(f'   Run {i}: {p[0]} - {p[1]:.1f}%')

# 5. Risultato finale
print('\n' + '=' * 70)
if ok_count == len(test_matches):
    print('✅ TUTTI I TEST SUPERATI')
    print('🚀 Sistema pronto per presentazione!')
elif ok_count > len(test_matches) * 0.8:
    print(f'⚠️  {ok_count}/{len(test_matches)} test superati (>{80}%)')
    print('Sistema operativo ma con alcune limitazioni')
else:
    print(f'❌ Solo {ok_count}/{len(test_matches)} test superati')
    print('Sistema richiede ulteriore debug')

print('=' * 70)
