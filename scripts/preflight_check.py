#!/usr/bin/env python3
"""
Pre-flight check prima dell'ottimizzazione
Valida che tutti i setup siano corretti
"""

import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split

print("=" * 70)
print("  PRE-FLIGHT CHECK - OTTIMIZZAZIONE MODELLI")
print("=" * 70)
print()

# 1. Verifica dataset
print("[1/5] Verifica dataset...")
try:
    df = pd.read_csv('data/dataset_features.csv')
    print(f"   ✓ Dataset caricato: {len(df)} partite")
    print(f"   ✓ Shape: {df.shape}")
except Exception as e:
    print(f"   ❌ ERRORE: {e}")
    exit(1)

# 2. Verifica features
print("\n[2/5] Verifica features...")
exclude_cols = ['FTR', 'Date', 'HomeTeam', 'AwayTeam', 'Referee', 'HTR', 'Div',
                'FTHG', 'FTAG', 'HTHG', 'HTAG']
feature_cols = [c for c in df.columns if c not in exclude_cols and df[c].dtype in ['float64', 'int64']]
print(f"   ✓ Features disponibili: {len(feature_cols)}")
print(f"   ✓ Colonne escluse: {len(exclude_cols)}")

# Check missing values
X = df[feature_cols].fillna(0)
missing_before = df[feature_cols].isnull().sum().sum()
print(f"   ✓ Missing values fillati: {missing_before}")

# 3. Verifica split consistency
print("\n[3/5] Verifica split consistency...")
y = df['FTR'].map({'H': 1, 'D': 0, 'A': 2})
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"   ✓ Train size: {len(X_train)}")
print(f"   ✓ Test size: {len(X_test)}")
print(f"   ✓ Distribuzione train: D={np.bincount(y_train)[0]}, H={np.bincount(y_train)[1]}, A={np.bincount(y_train)[2]}")
print(f"   ✓ Distribuzione test: D={np.bincount(y_test)[0]}, H={np.bincount(y_test)[1]}, A={np.bincount(y_test)[2]}")

# 4. Verifica modelli baseline esistenti
print("\n[4/5] Verifica modelli baseline...")
models_found = []
models_missing = []

for model_name in ['random_forest', 'lightgbm', 'xgboost']:
    path = f'models/enterprise/{model_name}.pkl'
    try:
        model = joblib.load(path)
        acc = model.score(X_test, y_test)
        models_found.append((model_name, acc))
        print(f"   ✓ {model_name}: accuracy={acc:.4f}")
    except:
        models_missing.append(model_name)
        print(f"   ❌ {model_name}: NON TROVATO")

if models_missing:
    print(f"\n   ⚠️  WARNING: {len(models_missing)} modelli mancanti")
    print("   Ottimizzazione procederà senza baseline comparison")

# 5. Verifica requirements
print("\n[5/5] Verifica requirements...")
try:
    import sklearn
    print(f"   ✓ scikit-learn: {sklearn.__version__}")
except:
    print("   ❌ scikit-learn non installato")
    exit(1)

try:
    import lightgbm
    print(f"   ✓ lightgbm: {lightgbm.__version__}")
except:
    print("   ❌ lightgbm non installato")
    exit(1)

try:
    import xgboost
    print(f"   ✓ xgboost: {xgboost.__version__}")
except:
    print("   ❌ xgboost non installato")
    exit(1)

# Summary
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print(f"✓ Dataset: {len(df)} partite, {len(feature_cols)} features")
print(f"✓ Split: {len(X_train)} train, {len(X_test)} test")
print(f"✓ Modelli baseline: {len(models_found)}/3 disponibili")

if models_found:
    avg_baseline = np.mean([acc for _, acc in models_found])
    print(f"✓ Accuracy media baseline: {avg_baseline:.4f}")
    print(f"\n🎯 Target ottimizzazione: {avg_baseline + 0.02:.4f} - {avg_baseline + 0.05:.4f} (+2-5%)")

print()
print("✅ PRE-FLIGHT CHECK PASSED")
print("Pronto per eseguire: python3 scripts/optimize_models.py")
print("=" * 70)
