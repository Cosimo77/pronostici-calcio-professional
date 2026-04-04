#!/usr/bin/env python3
"""
Training Modello con Fix Bias Casa/Trasferta
==============================================

PROBLEMA: Modello predice troppo Casa (57.5%), quasi mai Trasferta (3.9%)
SOLUZIONE: Class weighting aggressivo + calibrazione probabilità

Target:
- Accuracy: 51% → 54-56%
- Distribuzione predizioni bilanciata (±5% da distribuzione reale)
- ROI: +7.17% → +10-12%
"""

from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

print("=" * 70)
print("🎯 TRAINING MODELLO BILANCIATO - Fix Bias Casa/Trasferta")
print("=" * 70)

# 1. CARICA DATI
print("\n📂 Caricamento dataset...")
df = pd.read_csv("data/dataset_features_enhanced.csv")  # ← Dataset arricchito!

# Distributioneoriginale
dist_orig = df["FTR"].value_counts(normalize=True) * 100
print(f"\n📊 Distribuzione Dataset:")
print(f"   Casa (H):      {dist_orig['H']:.1f}%")
print(f"   Pareggio (D):  {dist_orig['D']:.1f}%")
print(f"   Trasferta (A): {dist_orig['A']:.1f}%")

# 2. PREPARA FEATURES
print("\n🔧 Preparazione features...")
feature_cols = [col for col in df.columns if col not in ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]

X = df[feature_cols].fillna(0)
y = df["FTR"]

print(f"   Features: {len(feature_cols)}")
print(f"   Samples: {len(X)}")

# 3. SPLIT STRATIFICATO (mantiene distribuzione)
print("\n✂️  Split stratificato train/test (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"   Train: {len(X_train)} samples")
print(f"   Test:  {len(X_test)} samples")

# 4. CALCOLA CLASS WEIGHTS AGGRESSIVI
print("\n⚖️  Calcolo class weights personalizzati...")

# Calcola pesi automatici
class_weights_auto = compute_class_weight(class_weight="balanced", classes=np.unique(y_train), y=y_train)

# Aggiungi penalty extra per Casa (riduce bias)
# e bonus per Trasferta (aumenta predizioni)
# IMPORTANTE: Pareggi devono essere favoriti (strategia FASE1 ROI +7.17%)
class_weights_custom = {
    "H": class_weights_auto[1] * 0.8,  # Penalizza Casa lieve (-20%)
    "D": class_weights_auto[0] * 1.3,  # BONUS Pareggio (+30%) ← FASE1!
    "A": class_weights_auto[2] * 1.2,  # Bonus Trasferta moderato (+20%)
}

print(f"   ⚖️  Weights applicati:")
print(f"      Casa (H):      {class_weights_custom['H']:.3f} (penalizzata -20%)")
print(f"      Pareggio (D):  {class_weights_custom['D']:.3f} (BONUS +30% per FASE1)")
print(f"      Trasferta (A): {class_weights_custom['A']:.3f} (bonus +20%)")

# 5. TRAIN RANDOM FOREST CON WEIGHTS
print("\n🌲 Training Random Forest...")

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight=class_weights_custom,  # ← FIX PRINCIPALE
    random_state=42,
    n_jobs=-1,
)

rf.fit(X_train, y_train)
print("   ✅ Training completato")

# 6. CALIBRA PROBABILITÀ (fix overconfidence)
print("\n🎯 Calibrazione probabilità...")

# Sigmoid calibration per probabilità più accurate
rf_calibrated = CalibratedClassifierCV(rf, cv=3, method="sigmoid")
rf_calibrated.fit(X_train, y_train)
print("   ✅ Calibrazione completata")

# 7. VALUTA PERFORMANCE
print("\n📊 VALUTAZIONE MODELLO")
print("=" * 70)

y_pred_cal = rf_calibrated.predict(X_test)
acc_cal = accuracy_score(y_test, y_pred_cal)

print(f"\n✅ Accuracy (calibrato): {acc_cal:.4f} ({acc_cal*100:.2f}%)")

# Distribuzione predizioni
pred_dist = pd.Series(y_pred_cal).value_counts(normalize=True) * 100
print(f"\n📊 Distribuzione Predizioni:")
print(f"   Casa (H):      {pred_dist.get('H', 0):.1f}% (target ~41%)")
print(f"   Pareggio (D):  {pred_dist.get('D', 0):.1f}% (target ~27%)")
print(f"   Trasferta (A): {pred_dist.get('A', 0):.1f}% (target ~32%)")

# Confusion matrix
print(f"\n📋 Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred_cal, labels=["A", "D", "H"])
print("              Pred_A  Pred_D  Pred_H")
print(f"   True_A  {cm[0][0]:>7} {cm[0][1]:>7} {cm[0][2]:>7}")
print(f"   True_D  {cm[1][0]:>7} {cm[1][1]:>7} {cm[1][2]:>7}")
print(f"   True_H  {cm[2][0]:>7} {cm[2][1]:>7} {cm[2][2]:>7}")

# Classification report
print(f"\n📈 Classification Report:")
print(classification_report(y_test, y_pred_cal, target_names=["Trasferta", "Pareggio", "Casa"]))

# 8. CONFRONTO BASELINE
print("\n🎯 CONFRONTO CON BASELINE")
print("=" * 70)

try:
    # Carica modello vecchio per confronto
    old_model = joblib.load("models/enterprise/random_forest.pkl")
    y_pred_old = old_model.predict(X_test)
    acc_old = accuracy_score(y_test, y_pred_old)

    pred_dist_old = pd.Series(y_pred_old).value_counts(normalize=True) * 100

    print(f"\n   Baseline Accuracy: {acc_old:.4f} ({acc_old*100:.2f}%)")
    print(f"   Nuovo Accuracy:    {acc_cal:.4f} ({acc_cal*100:.2f}%)")
    print(f"   Delta:             {(acc_cal - acc_old):.4f} ({(acc_cal - acc_old)*100:+.2f}%)")

    print(f"\n   Distribuzione Baseline vs Nuovo:")
    print(f"   Casa:      {pred_dist_old.get('H', 0):>5.1f}% → {pred_dist.get('H', 0):>5.1f}%")
    print(f"   Pareggio:  {pred_dist_old.get('D', 0):>5.1f}% → {pred_dist.get('D', 0):>5.1f}%")
    print(f"   Trasferta: {pred_dist_old.get('A', 0):>5.1f}% → {pred_dist.get('A', 0):>5.1f}%")

except FileNotFoundError:
    print("   ⚠️  Modello baseline non trovato (prima volta)")

# 9. SALVA MODELLO
print("\n💾 Salvataggio modelli...")

# Backup vecchio modello
import os

os.makedirs("models/backup", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

try:
    os.rename("models/enterprise/random_forest.pkl", f"models/backup/random_forest_{timestamp}.pkl")
    print(f"   ✅ Backup vecchio modello: random_forest_{timestamp}.pkl")
except FileNotFoundError:
    pass

# Salva nuovo modello calibrato
joblib.dump(rf_calibrated, "models/enterprise/random_forest.pkl")
joblib.dump(feature_cols, "models/enterprise/feature_columns.pkl")

print(f"   ✅ Nuovo modello salvato: random_forest.pkl (calibrato)")

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETATO!")
print("=" * 70)

print(f"\n📋 SUMMARY:")
print(f"   Accuracy:        {acc_cal*100:.2f}%")
print(f"   Bias fix:        Class weights + calibrazione")
print(f"   Predizioni Casa: {pred_dist.get('H', 0):.1f}% (vs 57.5% prima)")
print(f"   Predizioni Trsf: {pred_dist.get('A', 0):.1f}% (vs 3.9% prima)")

print(f"\n🚀 PROSSIMI STEP:")
print(f"   1. Testa predizioni su partite prossime")
print(f"   2. Confronta ROI su backtest")
print(f"   3. Se migliore → deploy su Render")

print()
