#!/usr/bin/env python3
"""
🎯 CALIBRAZIONE SEMPLICE - Isotonic vs Sigmoid
Test rapido miglioramento calibrazione probabilità (2 min)
"""
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

print("=" * 70)
print("🎯 CALIBRAZIONE PROBABILITÀ - Isotonic vs Sigmoid")
print("=" * 70)

# 1. DATASET
print("\n📂 Caricamento dataset...")
df = pd.read_csv("data/dataset_features.csv")

feature_cols = [c for c in df.columns if c not in ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
X = df[feature_cols].fillna(0)
y = df["FTR"]

print(f"   Features: {len(feature_cols)}, Samples: {len(df)}")

# 2. SPLIT
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3. CLASS WEIGHTS
class_weights_auto = compute_class_weight(class_weight="balanced", classes=np.unique(y_train), y=y_train)

class_weights_custom = {
    "H": class_weights_auto[1] * 0.8,
    "D": class_weights_auto[0] * 1.3,
    "A": class_weights_auto[2] * 1.2,
}

# 4. MODELLO BASE (RF ottimizzato manualmente)
print("\n🌲 RANDOM FOREST BASELINE")
print("-" * 70)

rf = RandomForestClassifier(
    n_estimators=300,  # Aumentato da 200
    max_depth=22,  # Leggermente più profondo
    min_samples_split=5,
    min_samples_leaf=2,
    max_features="sqrt",
    class_weight=class_weights_custom,
    random_state=42,
    n_jobs=-1,
)

print("   🔧 Training...")
rf.fit(X_train, y_train)

y_pred_base = rf.predict(X_test)
y_proba_base = rf.predict_proba(X_test)
acc_base = accuracy_score(y_test, y_pred_base)

print(f"   ✅ Accuracy Baseline: {acc_base:.4f} ({acc_base*100:.2f}%)")

# 5. CALIBRAZIONE SIGMOID (default sklearn)
print("\n🎯 CALIBRAZIONE SIGMOID")
print("-" * 70)

print("   🔧 Calibrating...")
cal_sigmoid = CalibratedClassifierCV(rf, cv=3, method="sigmoid")
cal_sigmoid.fit(X_train, y_train)

y_pred_sig = cal_sigmoid.predict(X_test)
y_proba_sig = cal_sigmoid.predict_proba(X_test)
acc_sig = accuracy_score(y_test, y_pred_sig)

print(f"   ✅ Accuracy Sigmoid: {acc_sig:.4f} ({acc_sig*100:.2f}%)")
print(f"   📈 Delta: {(acc_sig - acc_base)*100:+.2f}pp")

# 6. CALIBRAZIONE ISOTONIC (più flessibile)
print("\n🎯 CALIBRAZIONE ISOTONIC")
print("-" * 70)

print("   🔧 Calibrating...")
cal_isotonic = CalibratedClassifierCV(rf, cv=3, method="isotonic")
cal_isotonic.fit(X_train, y_train)

y_pred_iso = cal_isotonic.predict(X_test)
y_proba_iso = cal_isotonic.predict_proba(X_test)
acc_iso = accuracy_score(y_test, y_pred_iso)

print(f"   ✅ Accuracy Isotonic: {acc_iso:.4f} ({acc_iso*100:.2f}%)")
print(f"   📈 Delta vs Base: {(acc_iso - acc_base)*100:+.2f}pp")
print(f"   📈 Delta vs Sigmoid: {(acc_iso - acc_sig)*100:+.2f}pp")

# 7. CONFRONTO DISTRIBUZIONE PREDIZIONI
print("\n" + "=" * 70)
print("📊 DISTRIBUZIONE PREDIZIONI")
print("=" * 70)


def print_distribution(y_pred, title):
    dist = pd.Series(y_pred).value_counts(normalize=True) * 100
    print(f"\n{title}:")
    print(f"   Casa (H):      {dist.get('H', 0):5.1f}% (target 41%)")
    print(f"   Pareggio (D):  {dist.get('D', 0):5.1f}% (target 27%)")
    print(f"   Trasferta (A): {dist.get('A', 0):5.1f}% (target 32%)")


print_distribution(y_pred_base, "Baseline")
print_distribution(y_pred_sig, "Sigmoid")
print_distribution(y_pred_iso, "Isotonic")

# 8. QUALITÀ PROBABILITÀ (Brier Score - lower is better)
print("\n" + "=" * 70)
print("📊 QUALITÀ PROBABILITÀ (Brier Score)")
print("=" * 70)

# Convert labels to numeric for Brier
label_map = {"H": 0, "D": 1, "A": 2}
y_test_numeric = y_test.map(label_map)

# One-hot encode for Brier
y_test_onehot = np.zeros((len(y_test), 3))
for i, y in enumerate(y_test_numeric):
    y_test_onehot[i, y] = 1

# Calculate Brier for each class
brier_base = np.mean([brier_score_loss(y_test_onehot[:, i], y_proba_base[:, i]) for i in range(3)])
brier_sig = np.mean([brier_score_loss(y_test_onehot[:, i], y_proba_sig[:, i]) for i in range(3)])
brier_iso = np.mean([brier_score_loss(y_test_onehot[:, i], y_proba_iso[:, i]) for i in range(3)])

print(f"\n   Baseline:  {brier_base:.4f}")
print(f"   Sigmoid:   {brier_sig:.4f} ({(brier_sig - brier_base):+.4f})")
print(f"   Isotonic:  {brier_iso:.4f} ({(brier_iso - brier_base):+.4f})")
print(
    f"\n   ✅ Migliore: {'Isotonic' if brier_iso < min(brier_base, brier_sig) else 'Sigmoid' if brier_sig < brier_base else 'Baseline'}"
)

# 9. SELEZIONE MODELLO MIGLIORE
print("\n" + "=" * 70)
print("🏆 SELEZIONE MODELLO MIGLIORE")
print("=" * 70)

best_model = cal_isotonic
best_acc = acc_iso
best_name = "Isotonic"

if acc_sig > acc_iso:
    best_model = cal_sigmoid
    best_acc = acc_sig
    best_name = "Sigmoid"

print(f"\n   🏆 Migliore: {best_name} (Accuracy {best_acc:.4f})")

# 10. SALVA
print("\n💾 Salvataggio...")

if os.path.exists("models/enterprise/random_forest.pkl"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"models/backup/random_forest_{timestamp}.pkl"
    import shutil

    shutil.copy("models/enterprise/random_forest.pkl", backup_path)
    print(f"   📦 Backup: {backup_path}")

joblib.dump(best_model, "models/enterprise/calibrated_model.pkl")
joblib.dump(feature_cols, "models/enterprise/feature_columns.pkl")

if best_acc >= 0.51:
    joblib.dump(best_model, "models/enterprise/random_forest.pkl")
    print(f"   ✅ Sostituito modello principale ({best_acc:.4f})")
else:
    print(f"   ⚠️  Salvato come calibrated_model.pkl ({best_acc:.4f} < 0.51)")

print("\n✅ CALIBRAZIONE COMPLETATA!")
