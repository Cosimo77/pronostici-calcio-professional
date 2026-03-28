#!/usr/bin/env python3
"""
Test validazione ML semplificato - solo predizioni
"""
import joblib  # Usa joblib invece di pickle
import pandas as pd
import numpy as np
import sys
import os

# Cambia directory se necessario
os.chdir('/Users/cosimomassaro/Desktop/pronostici_calcio')

# Carica dataset e modelli
print("📁 Caricamento dataset e modelli...")
df = pd.read_csv('data/dataset_features.csv')
model = joblib.load('models/enterprise/random_forest.pkl')  # joblib.load
print(f"   ✅ Dataset: {len(df)} partite")
print(f"   ✅ Modello: {type(model).__name__}")

# Features: stessa logica del training
exclude_cols = ['FTR', 'Date', 'HomeTeam', 'AwayTeam', 'Referee', 'HTR', 'Div', 
                'FTHG', 'FTAG', 'HTHG', 'HTAG'] 
feature_cols = [c for c in df.columns if c not in exclude_cols and df[c].dtype in ['float64', 'int64']]
print(f"   📊 Features ML: {len(feature_cols)} colonne\n")

def predict_match(home, away):
    """Predici partita usando ML"""
    # Statistiche home/away
    home_matches = df[(df['HomeTeam'] == home) | (df['AwayTeam'] == home)].tail(10)
    away_matches = df[(df['HomeTeam'] == away) | (df['AwayTeam'] == away)].tail(10)
    
    if len(home_matches) < 2 or len(away_matches) < 2:
        raise ValueError(f"Dati insufficienti")
    
    # Media features ultimi 10 match
    home_features = home_matches[feature_cols].mean()
    away_features = away_matches[feature_cols].mean()
    combined = (home_features + away_features) / 2
    
    # Normalizza con mean/std del dataset completo (inline StandardScaler)
    X = combined.values.reshape(1, -1)
    X_mean = df[feature_cols].mean().values
    X_std = df[feature_cols].std().values
    X_scaled = (X - X_mean) / (X_std + 1e-8)  # type: ignore[operator]
    
    # Predici
    pred_proba = model.predict_proba(X_scaled)[0]
    pred_class = model.predict(X_scaled)[0]
    
    # Mapping risultati (0=A, 1=D, 2=H nel dataset)
    outcome_map = {0: 'Trasferta', 1: 'Pareggio', 2: 'Casa'}
    pred_label = outcome_map.get(pred_class, 'Casa')
    
    probs = {
        'H': pred_proba[2] if len(pred_proba) == 3 else 0.33,
        'D': pred_proba[1] if len(pred_proba) >= 2 else 0.33,
        'A': pred_proba[0] if len(pred_proba) >= 1 else 0.33
    }
    
    return pred_label, probs, max(pred_proba)

# Partite test
matches = [
    ("Verona", "Genoa", "A"),
    ("Pisa", "Cagliari", "H"),
    ("Sassuolo", "Bologna", "A"),
    ("Como", "Roma", "H"),
    ("Lazio", "Milan", "H"),
    ("Cremonese", "Fiorentina", "A")
]

print("\n" + "="*70)
print("  🔬 VALIDAZIONE ML - Partite Reali 15-16 Marzo")
print("="*70)

correct = 0
total = len(matches)

real_map = {'H': 'Casa', 'D': 'Pareggio', 'A': 'Trasferta'}

for home, away, real in matches:
    try:
        pred, probs, conf = predict_match(home, away)
        real_label = real_map[real]
        
        is_correct = pred == real_label
        correct += int(is_correct)
        
        icon = "✅" if is_correct else "❌"
        print(f"\n{icon} {home} vs {away}")
        print(f"   Predetto: {pred} ({conf:.1%})")
        print(f"   Reale: {real_label}")
        print(f"   Prob: H={probs['H']:.1%} D={probs['D']:.1%} A={probs['A']:.1%}")
        
    except Exception as e:
        print(f"\n⚠️  {home} vs {away}: {str(e)}")

print(f"\n" + "="*70)
print(f"  📊 ACCURACY 1X2: {correct}/{total} = {correct/total*100:.1f}%")

baseline = 39.5
diff = (correct/total*100) - baseline
icon = "🟢" if diff > 0 else "🔴"
print(f"\n{icon} vs Baseline (39.5%): {diff:+.1f}%")

if correct/total >= 0.45:
    print(f"  ✅ ML VALIDATO! Accuracy ≥45%")
elif correct/total >= 0.35:
    print(f"  🟡 ML accettabile (35-45%). Considera tuning.")
else:
    print(f"  🔴 ML sotto soglia. Auto-rollback consigliato.")

print("="*70 + "\n")
