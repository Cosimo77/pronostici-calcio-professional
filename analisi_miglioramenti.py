#!/usr/bin/env python3
"""Analisi performance modelli e suggerimenti miglioramento"""
import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from collections import Counter

print("="*70)
print("ANALISI PERFORMANCE & MARGINI DI MIGLIORAMENTO")
print("="*70)
print()

# Carica dataset
df = pd.read_csv('data/dataset_features.csv')

# Prepara features
exclude_cols = ['FTR', 'Date', 'HomeTeam', 'AwayTeam', 'Referee', 'HTR', 'Div', 
                'FTHG', 'FTAG', 'HTHG', 'HTAG']
feature_cols = [c for c in df.columns if c not in exclude_cols and df[c].dtype in ['float64', 'int64']]
X = df[feature_cols].fillna(0)
y = df['FTR'].map({'H': 1, 'D': 0, 'A': 2})

# Split uguale al training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Dataset: {len(df)} partite")
print(f"Train: {len(X_train)} | Test: {len(X_test)}")
print(f"Features: {len(feature_cols)}")
print()

# Test modelli
print("PERFORMANCE ATTUALI:")
print("-" * 70)

models = {
    'Random Forest': 'models/enterprise/random_forest.pkl',
    'LightGBM': 'models/enterprise/lightgbm.pkl',
    'XGBoost': 'models/enterprise/xgboost.pkl'
}

results = {}
for name, path in models.items():
    model = joblib.load(path)
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    results[name] = {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}
    
    print(f"\n{name}:")
    print(f"  Accuracy:  {acc*100:.2f}%")
    print(f"  Precision: {prec*100:.2f}%")
    print(f"  Recall:    {rec*100:.2f}%")
    print(f"  F1-Score:  {f1*100:.2f}%")

print()
print("-" * 70)

# Analisi distribuzione
print("\nDISTRIBUZIONE RISULTATI (dataset completo):")
print(f"  Casa (H):     {(y==1).sum():4d} ({(y==1).sum()/len(y)*100:.1f}%)")
print(f"  Pareggio (D): {(y==0).sum():4d} ({(y==0).sum()/len(y)*100:.1f}%)")
print(f"  Ospite (A):   {(y==2).sum():4d} ({(y==2).sum()/len(y)*100:.1f}%)")

# Baseline
most_common = Counter(y_test).most_common(1)[0]
baseline_acc = most_common[1] / len(y_test)
print(f"\nBASELINE (predire sempre classe piu frequente): {baseline_acc*100:.1f}%")

best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
improvement = (best_model[1]['accuracy'] - baseline_acc) * 100
print(f"Miglior modello: {best_model[0]} ({best_model[1]['accuracy']*100:.2f}%)")
print(f"Miglioramento su baseline: +{improvement:.1f} punti percentuali")

print()
print("="*70)
print("AREE DI MIGLIORAMENTO IDENTIFICATE")
print("="*70)
print()

# 1. Accuracy ottimale per calcio
print("1. ACCURATEZZA NEL CALCIO")
print("   Contesto: Il calcio e altamente imprevedibile")
print(f"   - Attuale: {best_model[1]['accuracy']*100:.1f}%")
print("   - Baseline: 41.5% (predire sempre Casa)")
print("   - Target realistico: 55-60% (stato dell'arte)")
print("   - Gap potenziale: +5-10 punti percentuali")
print()

# 2. Feature engineering
missing_features = [
    "Assenze giocatori chiave",
    "Condizioni meteo",
    "Viaggi infrasettimanali",
    "Minutaggio giocatori",
    "xG (Expected Goals) ultimi 5 match",
    "Pressione difensiva avversaria",
    "Forma portiere (clean sheets)",
    "Sequenze win/loss recenti"
]

print("2. FEATURE ENGINEERING AVANZATO")
print(f"   Features attuali: {len(feature_cols)}")
print("   Features mancanti potenzialmente utili:")
for i, feat in enumerate(missing_features, 1):
    print(f"   {i}. {feat}")
print()

# 3. Hyperparameters
print("3. HYPERPARAMETER TUNING")
print("   Attuale: Parametri default (n_estimators=100)")
print("   Miglioramenti:")
print("   - GridSearchCV su parametri chiave")
print("   - n_estimators: 200-500 (piu alberi)")
print("   - max_depth: 15-30 (profondita albero)")
print("   - learning_rate: 0.01-0.1 (per gradient boosting)")
print("   - min_samples_split: 5-20")
print("   Guadagno stimato: +2-4%")
print()

# 4. Ensemble
print("4. ENSEMBLE AVANZATO")
print("   Attuale: Modelli indipendenti")
print("   Miglioramenti:")
print("   - Stacking (meta-learner)")
print("   - Voting classifier pesato")
print("   - Blending con calibrazione probabilita")
print("   Guadagno stimato: +1-3%")
print()

# 5. Class imbalance
print("5. BILANCIAMENTO CLASSI")
y_dist = Counter(y)
print(f"   Casa: {y_dist[1]/len(y)*100:.1f}% | Pareggio: {y_dist[0]/len(y)*100:.1f}% | Ospite: {y_dist[2]/len(y)*100:.1f}%")
print("   Tecniche:")
print("   - SMOTE (oversampling pareggi)")
print("   - class_weight='balanced'")
print("   - Stratified sampling migliore")
print("   Guadagno su pareggi: +5-10%")
print()

# 6. More data
print("6. PIU DATI")
print(f"   Attuali: {len(df)} partite Serie A")
print("   Potenziali:")
print("   - Coppe europee (Champions, Europa League)")
print("   - Altri campionati top (Premier, Liga, Bundesliga)")
print("   - Partite amichevoli con peso ridotto")
print("   Target: 10000+ partite")
print("   Guadagno stimato: +3-5%")
print()

print("="*70)
print("ROADMAP MIGLIORAMENTI PRIORITARI")
print("="*70)
print()
print("FASE 1 (Rapida - 1-2 giorni):")
print("  1. Hyperparameter tuning GridSearchCV")
print("  2. Class weights per bilanciare pareggi")
print("  3. Ensemble voting pesato")
print("  Guadagno stimato: +3-5%")
print()
print("FASE 2 (Media - 1 settimana):")
print("  4. Feature engineering avanzato (xG, forma portiere)")
print("  5. SMOTE per oversampling")
print("  6. Stacking ensemble con meta-learner")
print("  Guadagno stimato: +4-6%")
print()
print("FASE 3 (Lunga - 2-4 settimane):")
print("  7. Integrazione dati campionati europei")
print("  8. Neural networks (LSTM per sequenze)")
print("  9. Calibrazione probabilita Platt scaling")
print("  Guadagno stimato: +5-8%")
print()
print("TARGET FINALE: 60-65% accuracy (eccellente per calcio)")
print("="*70)
