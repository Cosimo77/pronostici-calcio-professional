#!/usr/bin/env python3
"""
🚀 BUILD MODELS FOR RENDER DEPLOYMENT
Script veloce per rigenerare modelli calibrati al deploy (~2 min)
"""
import os
import sys
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

print("=" * 70)
print("🚀 RENDER BUILD: Generazione Modelli ML")
print("=" * 70)

# 1. DATASET
print("\n📂 Caricamento dataset...")
try:
    df = pd.read_csv("data/dataset_features.csv")
    print(f"   ✅ Dataset caricato: {len(df)} righe")
except FileNotFoundError:
    print("   ❌ Dataset non trovato - usando fallback vuoto")
    sys.exit(1)

# Features
feature_cols = [
    c
    for c in df.columns
    if c not in ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
]
X = df[feature_cols].fillna(0)
y = df["FTR"]

print(f"   Features: {len(feature_cols)}")

# 2. SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. CLASS WEIGHTS (fix bias trasferta)
class_weights_auto = compute_class_weight(
    class_weight="balanced", classes=np.unique(y_train), y=y_train
)

class_weights_custom = {
    "H": class_weights_auto[1] * 0.8,  # Casa -20%
    "D": class_weights_auto[0] * 1.3,  # Pareggio +30%
    "A": class_weights_auto[2] * 1.2,  # Trasferta +20%
}

print("\n⚖️  Class weights personalizzati:")
for k, v in class_weights_custom.items():
    print(f"   {k}: {v:.3f}")

# 4. RANDOM FOREST (parametri ottimizzati da quick_tuning)
print("\n🌲 Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=300,  # Balance speed/accuracy
    max_depth=22,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features="sqrt",
    class_weight=class_weights_custom,
    random_state=42,
    n_jobs=-1,  # Use all cores
)

rf.fit(X_train, y_train)
print("   ✅ Training completato")

# 5. CALIBRAZIONE SIGMOID (Brier -4.3%)
print("\n🎯 Calibrazione Sigmoid...")
calibrated = CalibratedClassifierCV(rf, cv=3, method="sigmoid")
calibrated.fit(X_train, y_train)

# Test accuracy
from sklearn.metrics import accuracy_score

y_pred = calibrated.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"   ✅ Accuracy: {acc:.4f} ({acc*100:.2f}%)")

# 6. SALVA MODELLI
print("\n💾 Salvataggio modelli...")

# Crea directory se non esiste
os.makedirs("models/enterprise", exist_ok=True)
os.makedirs("models/backup", exist_ok=True)

# Salva modello principale
joblib.dump(calibrated, "models/enterprise/random_forest.pkl")
joblib.dump(feature_cols, "models/enterprise/feature_columns.pkl")

print("   ✅ models/enterprise/random_forest.pkl")
print("   ✅ models/enterprise/feature_columns.pkl")

# 7. VALIDAZIONE VELOCE
print("\n✅ Validazione modello...")
test_load = joblib.load("models/enterprise/random_forest.pkl")
test_features = joblib.load("models/enterprise/feature_columns.pkl")

if hasattr(test_load, "predict_proba"):
    print("   ✅ Modello caricabile e funzionante")
    print(f"   ✅ {len(test_features)} features salvate")
else:
    print("   ❌ Errore: modello non valido")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ BUILD COMPLETATO - Modelli pronti per produzione")
print("=" * 70)
