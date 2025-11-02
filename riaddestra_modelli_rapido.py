#!/usr/bin/env python3
"""
Script rapido per ri-addestramento modelli compatibili
Risolve problema incompatibilità versioni sklearn/numpy
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import json
import os
from datetime import datetime

print("🤖 RI-ADDESTRAMENTO RAPIDO MODELLI")
print("=" * 70)

# 1. CARICA DATASET FEATURES
print("\n📊 Caricamento dataset...")
df = pd.read_csv('data/dataset_features.csv')
print(f"✅ Caricato: {len(df)} partite")

# 2. PREPARA DATI
print("\n🔧 Preparazione dati...")
# Escludi colonne non-feature
exclude_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 
                'HTHG', 'HTAG', 'HTR', 'Div', 'Time']
feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['float64', 'int64']]

X = df[feature_cols].fillna(0)
y = df['FTR']

print(f"✅ Features: {len(feature_cols)}")
print(f"✅ Target distribution: {dict(y.value_counts())}")

# 3. SPLIT E SCALING
print("\n✂️  Split e scaling...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✅ Training: {len(X_train)} | Test: {len(X_test)}")

# 4. ADDESTRA MODELLI (configurazione ottimizzata rapida)
print("\n🚀 Addestramento modelli...")

models = {
    'RandomForest': RandomForestClassifier(
        n_estimators=150,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),
    'GradientBoosting': GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    ),
    'LogisticRegression': LogisticRegression(
        C=1.0,
        penalty='l2',
        solver='lbfgs',
        max_iter=1000,
        random_state=42,
        n_jobs=-1
    )
}

results = {}
trained_models = {}

for name, model in models.items():
    print(f"\n  📈 {name}...")
    
    # Usa dati scalati solo per LogisticRegression
    X_tr = X_train_scaled if name == 'LogisticRegression' else X_train
    X_te = X_test_scaled if name == 'LogisticRegression' else X_test
    
    # Training
    model.fit(X_tr, y_train)
    
    # Predizioni
    y_pred_train = model.predict(X_tr)
    y_pred_test = model.predict(X_te)
    
    # Metriche
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    results[name] = {
        'train_accuracy': float(train_acc),
        'test_accuracy': float(test_acc),
        'confusion_matrix': confusion_matrix(y_test, y_pred_test).tolist()
    }
    
    trained_models[name] = model
    
    print(f"     Train accuracy: {train_acc:.3f}")
    print(f"     Test accuracy:  {test_acc:.3f}")

# 5. SALVA MODELLI
print("\n💾 Salvataggio modelli...")
os.makedirs('models', exist_ok=True)

# Salva modelli individuali
for name, model in trained_models.items():
    filename = f'models/{name.lower()}_model.pkl'
    joblib.dump(model, filename)
    print(f"  ✅ {filename}")

# Salva scaler
joblib.dump(scaler, 'models/scaler.pkl')
print(f"  ✅ models/scaler.pkl")

# Salva metadata
metadata = {
    'feature_columns': feature_cols,
    'models': list(models.keys()),
    'training_date': datetime.now().isoformat(),
    'dataset_size': len(df),
    'train_size': len(X_train),
    'test_size': len(X_test),
    'results': results,
    'python_version': '3.12',
    'sklearn_version': '1.6.1'
}

with open('models/metadata.pkl', 'wb') as f:
    joblib.dump(metadata, f)
print(f"  ✅ models/metadata.pkl")

# 6. REPORT FINALE
print("\n" + "=" * 70)
print("✅ RI-ADDESTRAMENTO COMPLETATO!")
print("=" * 70)
print(f"\n📊 METRICHE FINALI:")
for name, res in results.items():
    print(f"\n  {name}:")
    print(f"    Training accuracy:  {res['train_accuracy']:.1%}")
    print(f"    Test accuracy:      {res['test_accuracy']:.1%}")

print(f"\n📦 Modelli salvati in: models/")
print(f"   - RandomForest, GradientBoosting, LogisticRegression")
print(f"   - Scaler e Metadata")
print(f"\n🎯 Sistema pronto per predizioni!")
