#!/usr/bin/env python3
"""
Test realistico del Value Betting
Verifica se il metodo batte davvero i bookmaker
"""
import sys
sys.path.append('scripts')
import pandas as pd
import numpy as np
from modelli_predittivi import PronosticiCalculator

print('='*70)
print('TEST REALISTICO VALUE BETTING')
print('='*70)

# Carica modelli
calc = PronosticiCalculator()
calc.carica_modelli()
print(f'\n✅ Modelli caricati: {list(calc.models.keys())}')

# Carica dataset con quote
df = pd.read_csv('data/dataset_pulito.csv')
df['Date'] = pd.to_datetime(df['Date'])
print(f'✅ Dataset caricato: {len(df)} partite')

# Verifica se ci sono quote
if 'AvgH' not in df.columns:
    print('\n❌ ERRORE: Dataset non ha colonne con quote dei bookmaker!')
    print('   Il value betting RICHIEDE le quote per calcolare expected value.')
    print('   Senza quote, possiamo solo fare predizioni standard.')
    sys.exit(1)

# Seleziona solo partite con quote complete
df_con_quote = df[df['AvgH'].notna() & df['AvgD'].notna() & df['AvgA'].notna()].copy()
print(f'✅ Partite con quote complete: {len(df_con_quote)}')

# Split train/test (80/20)
split_idx = int(len(df_con_quote) * 0.8)
df_test = df_con_quote.iloc[split_idx:].copy()
print(f'✅ Test set: {len(df_test)} partite')

print('\n' + '='*70)
print('BACKTEST SU DATI REALI')
print('='*70)

# Prepara risultati
risultati = {
    'STRATEGIA 1 - Sempre Favorito Bookmaker': {
        'scommesse': 0,
        'vinte': 0,
        'roi_totale': 0,
        'roi_list': []
    },
    'STRATEGIA 2 - Sempre Nostro Modello': {
        'scommesse': 0,
        'vinte': 0,
        'roi_totale': 0,
        'roi_list': []
    },
    'STRATEGIA 3 - Value Betting (EV > 5%)': {
        'scommesse': 0,
        'vinte': 0,
        'roi_totale': 0,
        'roi_list': []
    }
}

for idx, row in df_test.iterrows():
    casa = row['HomeTeam']
    ospite = row['AwayTeam']
    risultato_reale = row['FTR']
    
    odds_h = row['AvgH']
    odds_d = row['AvgD']
    odds_a = row['AvgA']
    
    # Probabilità bookmaker (normalizzate)
    prob_book_h = 1 / odds_h
    prob_book_d = 1 / odds_d
    prob_book_a = 1 / odds_a
    total = prob_book_h + prob_book_d + prob_book_a
    prob_book_h /= total
    prob_book_d /= total
    prob_book_a /= total
    
    # Predizione nostro modello
    try:
        pred, prob_dict = calc.predici_partita(casa, ospite, df)
        if not pred or not prob_dict:
            continue
        
        pred_str = pred[0] if isinstance(pred, list) else pred
        prob_model_h = prob_dict.get('H', 0.33)
        prob_model_d = prob_dict.get('D', 0.33)
        prob_model_a = prob_dict.get('A', 0.33)
        
    except:
        continue
    
    # STRATEGIA 1: Scommetti sempre sul favorito bookmaker
    favorito_book = max([('H', prob_book_h, odds_h), 
                         ('D', prob_book_d, odds_d), 
                         ('A', prob_book_a, odds_a)], 
                        key=lambda x: x[1])
    
    risultati['STRATEGIA 1 - Sempre Favorito Bookmaker']['scommesse'] += 1
    if favorito_book[0] == risultato_reale:
        risultati['STRATEGIA 1 - Sempre Favorito Bookmaker']['vinte'] += 1
        roi = favorito_book[2] - 1
    else:
        roi = -1
    risultati['STRATEGIA 1 - Sempre Favorito Bookmaker']['roi_totale'] += roi
    risultati['STRATEGIA 1 - Sempre Favorito Bookmaker']['roi_list'].append(roi)
    
    # STRATEGIA 2: Scommetti sempre sulla nostra predizione
    odds_nostro = {'H': odds_h, 'D': odds_d, 'A': odds_a}[pred_str]
    
    risultati['STRATEGIA 2 - Sempre Nostro Modello']['scommesse'] += 1
    if pred_str == risultato_reale:
        risultati['STRATEGIA 2 - Sempre Nostro Modello']['vinte'] += 1
        roi = odds_nostro - 1
    else:
        roi = -1
    risultati['STRATEGIA 2 - Sempre Nostro Modello']['roi_totale'] += roi
    risultati['STRATEGIA 2 - Sempre Nostro Modello']['roi_list'].append(roi)
    
    # STRATEGIA 3: Value Betting (scommetti solo se EV > 5%)
    ev_h = prob_model_h * odds_h - 1
    ev_d = prob_model_d * odds_d - 1
    ev_a = prob_model_a * odds_a - 1
    
    best_ev = max([('H', ev_h, odds_h), ('D', ev_d, odds_d), ('A', ev_a, odds_a)], 
                  key=lambda x: x[1])
    
    if best_ev[1] > 0.05:  # EV > 5%
        risultati['STRATEGIA 3 - Value Betting (EV > 5%)']['scommesse'] += 1
        if best_ev[0] == risultato_reale:
            risultati['STRATEGIA 3 - Value Betting (EV > 5%)']['vinte'] += 1
            roi = best_ev[2] - 1
        else:
            roi = -1
        risultati['STRATEGIA 3 - Value Betting (EV > 5%)']['roi_totale'] += roi
        risultati['STRATEGIA 3 - Value Betting (EV > 5%)']['roi_list'].append(roi)

# Stampa risultati
print('\n📊 RISULTATI BACKTEST:\n')
for strategia, stats in risultati.items():
    if stats['scommesse'] > 0:
        win_rate = stats['vinte'] / stats['scommesse'] * 100
        roi_medio = stats['roi_totale'] / stats['scommesse'] * 100
        profitto = stats['roi_totale']
        
        print(f'{strategia}')
        print(f'  Scommesse: {stats["scommesse"]}')
        print(f'  Win rate: {win_rate:.1f}%')
        print(f'  ROI medio: {roi_medio:+.2f}%')
        print(f'  Profit/Loss: {profitto:+.2f}€ (su {stats["scommesse"]}€ giocati)')
        
        if roi_medio > 0:
            print(f'  ✅ Strategia PROFITTEVOLE')
        else:
            print(f'  ❌ Strategia IN PERDITA')
        print()

# Conclusioni
print('='*70)
print('CONCLUSIONI')
print('='*70)

migliore = max(risultati.items(), 
               key=lambda x: x[1]['roi_totale'] / x[1]['scommesse'] if x[1]['scommesse'] > 0 else -999)

if migliore[1]['scommesse'] > 0 and migliore[1]['roi_totale'] > 0:
    print(f'\n🏆 MIGLIORE STRATEGIA: {migliore[0]}')
    print(f'   ROI: {migliore[1]["roi_totale"] / migliore[1]["scommesse"] * 100:+.2f}%')
else:
    print('\n❌ NESSUNA STRATEGIA È PROFITTEVOLE!')
    print('   I bookmaker hanno un vantaggio matematico (margine 4-7%)')
    print('   Battere il mercato richiede:')
    print('   1. Informazioni non pubbliche')
    print('   2. Errori sistematici dei bookmaker')
    print('   3. Modelli superiori al consenso del mercato')
