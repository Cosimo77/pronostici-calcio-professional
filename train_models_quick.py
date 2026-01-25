#!/usr/bin/env python3
"""Training rapido modelli ML con dataset aggiornato"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Carica dataset
print('Caricamento dataset...')
df = pd.read_csv('data/dataset_features.csv')
print(f'Dataset caricato: {len(df)} partite')

# Prepara features/target (solo numeriche, ESCLUDE DATA LEAKAGE)
# CRITICO: FTHG, FTAG, HTHG, HTAG, HTR contengono info del risultato finale!
exclude_cols = ['FTR', 'Date', 'HomeTeam', 'AwayTeam', 'Referee', 'HTR', 'Div', 
                'FTHG', 'FTAG', 'HTHG', 'HTAG']  # Escludi gol/risultati che causano leakage
feature_cols = [c for c in df.columns if c not in exclude_cols and df[c].dtype in ['float64', 'int64']]
X = df[feature_cols].fillna(0)  # Riempi NaN con 0

# Codifica target: H=1, D=0, A=2 (standard per calcio)
y = df['FTR'].map({'H': 1, 'D': 0, 'A': 2})

print(f'Features selezionate: {len(feature_cols)}')
print(f'Features usate: {feature_cols[:10]}...')  # Mostra prime 10
print(f'Forma dati: X={X.shape}, y={y.shape}')

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train modelli
print('Training modelli...')
models = {
    'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'logistic_regression': LogisticRegression(random_state=42, max_iter=500),
    'xgboost': XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='mlogloss'),
    'lightgbm': LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
}

for name, model in models.items():
    print(f'  Training {name}...')
    if 'logistic' in name:
        model.fit(X_train_scaled, y_train)
        score = model.score(X_test_scaled, y_test)
    else:
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
    print(f'    Accuracy: {score:.3f}')
    
    # Salva
    path = f'models/enterprise/{name}.pkl'
    joblib.dump(model, path)
    print(f'    Salvato: {path}')

# Salva scaler
joblib.dump(scaler, 'models/enterprise/scaler.pkl')
print('Tutti i modelli salvati in models/enterprise/')
