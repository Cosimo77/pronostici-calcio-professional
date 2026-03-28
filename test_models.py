#!/usr/bin/env python3
"""Test modelli ML con predizione reale"""
import pandas as pd
import joblib
import numpy as np

print("="*60)
print("TEST MODELLI ML - PREDIZIONE REALE")
print("="*60)
print()

# Carica dataset
df = pd.read_csv('data/dataset_features.csv')
print(f"Dataset caricato: {len(df)} partite")
print(f"Periodo: {df['Date'].min()} -> {df['Date'].max()}")
print()

# Prepara feature (stesso processo del training)
exclude_cols = ['FTR', 'Date', 'HomeTeam', 'AwayTeam', 'Referee', 'HTR', 'Div', 
                'FTHG', 'FTAG', 'HTHG', 'HTAG']
feature_cols = [c for c in df.columns if c not in exclude_cols and df[c].dtype in ['float64', 'int64']]

# Prendi una partita REALE recente per test (Lazio-Sassuolo 2-1)
X_test = df[feature_cols].iloc[-1:].fillna(0)
y_true = df['FTR'].iloc[-1]
match_info = df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']].iloc[-1]

print("PARTITA TEST (REALE):")
print(f"  Data: {match_info['Date']}")
print(f"  Match: {match_info['HomeTeam']} vs {match_info['AwayTeam']}")
print(f"  Risultato reale: {match_info['FTHG']}-{match_info['FTAG']} ({y_true})")
print(f"  Features usate: {len(feature_cols)}")
print()

# Test modelli
models_to_test = {
    'Random Forest': 'models/enterprise/random_forest.pkl',
    'LightGBM': 'models/enterprise/lightgbm.pkl',
    'XGBoost': 'models/enterprise/xgboost.pkl'
}

print("PREDIZIONI MODELLI:")
print("-" * 60)

labels = {1: 'H (Casa)', 0: 'D (Pareggio)', 2: 'A (Ospite)'}

for name, path in models_to_test.items():
    try:
        model = joblib.load(path)
        
        # Predizione
        pred = model.predict(X_test)[0]
        proba = model.predict_proba(X_test)[0]
        
        # Ordina probabilità per classe
        proba_dict = {labels[i]: proba[i] for i in range(3)}
        
        print(f"\n{name}:")
        print(f"  Predizione: {labels[pred]}")
        print(f"  Probabilita:")
        for outcome, prob in sorted(proba_dict.items(), key=lambda x: x[1], reverse=True):
            print(f"    {outcome}: {prob*100:.1f}%")
        
        # Verifica correttezza
        if pred == {'H': 1, 'D': 0, 'A': 2}[y_true]:
            print(f"  CORRETTO!")
        else:
            print(f"  Sbagliato (reale: {labels[{'H': 1, 'D': 0, 'A': 2}[y_true]]})")
            
    except Exception as e:
        print(f"\n{name}: ERRORE - {e}")

print()
print("="*60)
print("TEST COMPLETATO")
print("="*60)
