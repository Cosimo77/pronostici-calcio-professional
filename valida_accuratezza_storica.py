#!/usr/bin/env python3
"""
Validazione accuratezza storica del sistema su partite reali
"""
import sys
import os
sys.path.insert(0, 'web')

import pandas as pd
from datetime import datetime
from app_professional import ProfessionalCalculator

print('📊 VALIDAZIONE ACCURATEZZA STORICA')
print('=' * 70)

# 1. Carica dati
df = pd.read_csv('data/dataset_features.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

print(f'\n📁 Dataset caricato: {len(df)} partite')
print(f'   Periodo: {df["Date"].min().date()} → {df["Date"].max().date()}')

# 2. Seleziona ultimi N match per validazione
N_TEST = 100
df_test = df.tail(N_TEST).copy()

print(f'\n🎯 Test set: ultimi {N_TEST} match')
print(f'   Periodo test: {df_test["Date"].min().date()} → {df_test["Date"].max().date()}')

# 3. Inizializza calculator SENZA i match di test
print(f'\n⚙️  Inizializzazione calculator...')
calc = ProfessionalCalculator()

# Usa solo dati storici prima del test set
df_train = df.head(len(df) - N_TEST)
df_train.to_csv('data/temp_train.csv', index=False)
calc.carica_dati('data/temp_train.csv')

print(f'✅ Calculator pronto con {len(df_train)} partite training')

# 4. Esegui predizioni su test set
print(f'\n🔮 Esecuzione predizioni su {N_TEST} partite...')

risultati = []
correct = 0

for idx, row in df_test.iterrows():
    casa = row['HomeTeam']
    trasferta = row['AwayTeam']
    risultato_reale = row['FTR']
    
    try:
        pred, prob, conf = calc.predici_partita_deterministica(casa, trasferta)
        
        is_correct = (pred == risultato_reale)
        if is_correct:
            correct += 1
        
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
        
    except Exception as e:
        print(f'⚠️  Errore {casa} vs {trasferta}: {e}')

# 5. Calcola metriche
print(f'\n' + '=' * 70)
print('📈 RISULTATI VALIDAZIONE')
print('=' * 70)

df_risultati = pd.DataFrame(risultati)
accuracy = correct / len(risultati) * 100

print(f'\n🎯 ACCURATEZZA GLOBALE: {accuracy:.1f}% ({correct}/{len(risultati)})')

# Baseline (predire sempre H)
baseline_h = (df_test['FTR'] == 'H').sum() / len(df_test) * 100
print(f'📊 Baseline (sempre H): {baseline_h:.1f}%')
print(f'🚀 Miglioramento: +{accuracy - baseline_h:.1f} punti percentuali')

# Accuratezza per classe
print(f'\n📋 ACCURATEZZA PER RISULTATO:')
for classe in ['H', 'D', 'A']:
    df_classe = df_risultati[df_risultati['risultato_reale'] == classe]
    if len(df_classe) > 0:
        acc_classe = df_classe['corretto'].sum() / len(df_classe) * 100
        print(f'   {classe}: {acc_classe:.1f}% ({df_classe["corretto"].sum()}/{len(df_classe)})')

# Distribuzione predizioni vs reale
print(f'\n📊 DISTRIBUZIONE PREDIZIONI:')
print('\nPredetto:')
print(df_risultati['predizione'].value_counts())
print('\nReale:')
print(df_risultati['risultato_reale'].value_counts())

# Analisi per livello di confidenza
print(f'\n🎲 ANALISI PER CONFIDENZA:')
df_risultati['confidenza_bin'] = pd.cut(df_risultati['confidenza'], 
                                         bins=[0, 0.4, 0.5, 0.6, 1.0],
                                         labels=['Bassa (<40%)', 'Media (40-50%)', 'Alta (50-60%)', 'Molto Alta (>60%)'])

for conf_bin in df_risultati['confidenza_bin'].cat.categories:
    df_bin = df_risultati[df_risultati['confidenza_bin'] == conf_bin]
    if len(df_bin) > 0:
        acc_bin = df_bin['corretto'].sum() / len(df_bin) * 100
        print(f'   {conf_bin}: {acc_bin:.1f}% ({df_bin["corretto"].sum()}/{len(df_bin)}) partite')

# Top 10 predizioni migliori
print(f'\n✅ TOP 5 PREDIZIONI CORRETTE (alta confidenza):')
top_correct = df_risultati[df_risultati['corretto']].nlargest(5, 'confidenza')
for _, row in top_correct.iterrows():
    print(f'   {row["casa"]} vs {row["trasferta"]}: predetto {row["predizione"]} (conf {row["confidenza"]:.1%}) ✓')

# Top errori
print(f'\n❌ TOP 5 ERRORI (alta confidenza sbagliata):')
top_errors = df_risultati[~df_risultati['corretto']].nlargest(5, 'confidenza')
for _, row in top_errors.iterrows():
    print(f'   {row["casa"]} vs {row["trasferta"]}: predetto {row["predizione"]}, reale {row["risultato_reale"]} (conf {row["confidenza"]:.1%})')

# 6. Salva risultati
output_file = 'validazione_accuratezza.csv'
df_risultati.to_csv(output_file, index=False)
print(f'\n💾 Risultati salvati in: {output_file}')

# 7. Cleanup
os.remove('data/temp_train.csv')

# Risultato finale
print(f'\n' + '=' * 70)
if accuracy >= 50:
    print(f'✅ VALIDAZIONE SUPERATA: {accuracy:.1f}% accuracy')
    print('🎯 Sistema affidabile per uso reale')
elif accuracy >= 45:
    print(f'⚠️  VALIDAZIONE PARZIALE: {accuracy:.1f}% accuracy')
    print('Sistema funzionante ma con margine di miglioramento')
else:
    print(f'❌ VALIDAZIONE FALLITA: {accuracy:.1f}% accuracy')
    print('Sistema richiede ottimizzazione')
print('=' * 70)
