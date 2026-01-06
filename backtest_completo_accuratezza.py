#!/usr/bin/env python3
"""
Backtest completo su TUTTE le partite validabili per metriche reali
"""
import sys
import os
sys.path.insert(0, 'web')

import pandas as pd
from datetime import datetime
from web.app_professional import ProfessionalCalculator

print('📊 BACKTEST COMPLETO - VALIDAZIONE ACCURATEZZA')
print('=' * 80)

# 1. Carica dataset completo
df = pd.read_csv('data/dataset_features.csv')

# 2. Filtra solo partite validabili (con risultato + quote complete)
df_valid = df[
    df['FTR'].notna() &
    df['B365H'].notna() &
    df['B365D'].notna() &
    df['B365A'].notna()
].copy()

df_valid['Date'] = pd.to_datetime(df_valid['Date'])
df_valid = df_valid.sort_values('Date')

print(f'\n📁 Dataset totale: {len(df)} partite')
print(f'📊 Partite validabili: {len(df_valid)} partite')
print(f'   Periodo: {df_valid["Date"].min().date()} → {df_valid["Date"].max().date()}')

# 3. Usa 80% training, 20% test (split temporale)
split_idx = int(len(df_valid) * 0.8)
df_train = df_valid.iloc[:split_idx].copy()
df_test = df_valid.iloc[split_idx:].copy()

print(f'\n🎯 Training set: {len(df_train)} partite')
print(f'   Periodo: {df_train["Date"].min().date()} → {df_train["Date"].max().date()}')
print(f'🎯 Test set: {len(df_test)} partite')
print(f'   Periodo: {df_test["Date"].min().date()} → {df_test["Date"].max().date()}')

# 4. Inizializza calculator con training data
print(f'\n⚙️  Inizializzazione calculator...')
calc = ProfessionalCalculator()

df_train.to_csv('data/temp_train_full.csv', index=False)
calc.carica_dati('data/temp_train_full.csv')

print(f'✅ Calculator pronto')

# 5. Esegui predizioni su test set
print(f'\n🔮 Esecuzione predizioni su {len(df_test)} partite...')
print('   (Questo richiederà qualche minuto...)')

risultati = []
correct = 0
confidenze = []

for idx, (i, row) in enumerate(df_test.iterrows()):
    casa = row['HomeTeam']
    trasferta = row['AwayTeam']
    risultato_reale = row['FTR']
    
    try:
        pred, prob, conf = calc.predici_partita_deterministica(casa, trasferta)
        
        is_correct = (pred == risultato_reale)
        if is_correct:
            correct += 1
        
        confidenze.append(conf)
        
        risultati.append({
            'data': row['Date'],
            'casa': casa,
            'trasferta': trasferta,
            'risultato_reale': risultato_reale,
            'predizione': pred,
            'prob_h': prob['H'],
            'prob_d': prob['D'],
            'prob_a': prob['A'],
            'confidenza': conf,
            'corretto': is_correct
        })
        
        # Progress indicator
        if (idx + 1) % 50 == 0:
            print(f'   Processate: {idx + 1}/{len(df_test)} ({(idx+1)/len(df_test)*100:.1f}%)')
        
    except Exception as e:
        print(f'⚠️  Errore {casa} vs {trasferta}: {e}')

# 6. Calcola metriche finali
print(f'\n' + '=' * 80)
print('📈 RISULTATI BACKTEST COMPLETO')
print('=' * 80)

df_risultati = pd.DataFrame(risultati)
accuracy = correct / len(risultati) * 100
confidenza_media = sum(confidenze) / len(confidenze) * 100

print(f'\n🎯 ACCURATEZZA COMPLESSIVA: {accuracy:.1f}% ({correct}/{len(risultati)})')
print(f'🎲 CONFIDENZA MEDIA: {confidenza_media:.1f}%')

# Predizioni corrette
predizioni_corrette = correct

print(f'\n📊 METRICHE CHIAVE:')
print(f'   • Partite analizzate: {len(risultati)}')
print(f'   • Predizioni corrette: {predizioni_corrette}')
print(f'   • Accuratezza: {accuracy:.1f}%')
print(f'   • Confidenza media: {confidenza_media:.1f}%')

# Accuratezza per classe
print(f'\n📋 ACCURATEZZA PER RISULTATO:')
for classe in ['H', 'D', 'A']:
    df_classe = df_risultati[df_risultati['risultato_reale'] == classe]
    if len(df_classe) > 0:
        acc_classe = df_classe['corretto'].sum() / len(df_classe) * 100
        print(f'   {classe}: {acc_classe:.1f}% ({df_classe["corretto"].sum()}/{len(df_classe)})')

# Distribuzione predizioni
print(f'\n📊 DISTRIBUZIONE PREDIZIONI:')
print('\nPredetto:')
for cls in ['H', 'D', 'A']:
    count = len(df_risultati[df_risultati['predizione'] == cls])
    pct = count / len(df_risultati) * 100
    print(f'   {cls}: {count} ({pct:.1f}%)')

print('\nReale:')
for cls in ['H', 'D', 'A']:
    count = len(df_risultati[df_risultati['risultato_reale'] == cls])
    pct = count / len(df_risultati) * 100
    print(f'   {cls}: {count} ({pct:.1f}%)')

# 7. Salva risultati
output_file = 'validazione_accuratezza_completa.csv'
df_risultati.to_csv(output_file, index=False)
print(f'\n💾 Risultati salvati in: {output_file}')

# 8. Cleanup
os.remove('data/temp_train_full.csv')

# 9. Mostra valori da aggiornare
print(f'\n' + '=' * 80)
print('📝 VALORI DA AGGIORNARE IN app_professional.py:')
print('=' * 80)
print(f'\naccuratezza_complessiva: {accuracy:.1f}')
print(f'partite_analizzate: {len(risultati)}')
print(f'predizioni_corrette: {predizioni_corrette}')
print(f'confidenza_media: {confidenza_media:.1f}')
print(f'\n' + '=' * 80)

# Risultato finale
if accuracy >= 50:
    print(f'✅ VALIDAZIONE SUPERATA: {accuracy:.1f}% accuracy')
else:
    print(f'⚠️  VALIDAZIONE PARZIALE: {accuracy:.1f}% accuracy')
print('=' * 80)
