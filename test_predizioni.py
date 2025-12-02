#!/usr/bin/env python3
"""Test completo sistema di predizione"""
import sys
from typing import Dict, Tuple, Any, Optional
sys.path.append('scripts')
from modelli_predittivi import PronosticiCalculator
import pandas as pd

print('=== TEST SISTEMA PREDIZIONE ===\n')

# Carica modelli
calc = PronosticiCalculator()
try:
    calc.carica_modelli()
    print('✅ Modelli caricati correttamente')
    print(f'   Modelli disponibili: {list(calc.models.keys())}')
    
    # Verifica calibrazione
    for nome, info in calc.models.items():
        accuracy = info.get('accuracy', info.get('test_accuracy', 'N/A'))
        log_loss = info.get('log_loss', 'N/A')
        print(f'   - {nome}: accuracy={accuracy}, log_loss={log_loss}')
    
except Exception as e:
    print(f'❌ Errore caricamento modelli: {e}')
    sys.exit(1)

# Carica dataset
df = pd.read_csv('data/dataset_features.csv')
print(f'\n✅ Dataset caricato: {len(df)} partite')

# Test predizioni
print('\n=== TEST PREDIZIONI ===')
partite_test = [
    ('Juventus', 'Inter'),
    ('Milan', 'Napoli'),
    ('Roma', 'Lazio')
]

for casa, ospite in partite_test:
    try:
        result = calc.predici_partita(casa, ospite, df)
        if result and len(result) == 2:
            pred, prob = result
            if isinstance(prob, dict):
                pred_str: str = pred[0] if isinstance(pred, list) else str(pred)
                
                prob_dict: Dict[str, float] = prob  # Type hint per Pylance
                prob_casa = prob_dict.get('H', 0.0)
                prob_pareggio = prob_dict.get('D', 0.0)
                prob_ospite = prob_dict.get('A', 0.0)
                
                # Verifica somma probabilità
                somma = prob_casa + prob_pareggio + prob_ospite
                
                risultato_map: Dict[str, str] = {'H': f'Vittoria {casa}', 'D': 'Pareggio', 'A': f'Vittoria {ospite}'}
                print(f'\n{casa} vs {ospite}:')
                # Assicura che pred_str sia una stringa valida prima di usarlo come chiave
                risultato_str = risultato_map[pred_str] if pred_str in risultato_map else "N/A"
                print(f'  Predizione: {risultato_str}')
                print(f'  Probabilità: Casa={prob_casa:.1%}, Pareggio={prob_pareggio:.1%}, Ospite={prob_ospite:.1%}')
                print(f'  Somma prob: {somma:.3f} {"✅" if abs(somma - 1.0) < 0.01 else "❌ ERRORE!"}')
            else:
                print(f'\n{casa} vs {ospite}: ❌ Formato probabilità non valido')
        else:
            print(f'\n{casa} vs {ospite}: ❌ Predizione fallita')
    except Exception as e:
        print(f'\n{casa} vs {ospite}: ❌ Errore - {e}')

print('\n✅ Test completato')
