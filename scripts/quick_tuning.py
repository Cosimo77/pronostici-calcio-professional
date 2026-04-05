#!/usr/bin/env python3
"""
🎯 QUICK TUNING - Hyperparameters essenziali (5-10 min)
Ottimizzazione veloce focalizzata su parametri chiave
"""
import os
import shutil
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.utils.class_weight import compute_class_weight

print("=" * 70)
print("🚀 QUICK TUNING - Randomized Search (Veloce)")
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

# 3. CLASS WEIGHTS (stessi filtri bias)
class_weights_auto = compute_class_weight(class_weight="balanced", classes=np.unique(y_train), y=y_train)

class_weights_custom = {
    "H": class_weights_auto[1] * 0.8,
    "D": class_weights_auto[0] * 1.3,
    "A": class_weights_auto[2] * 1.2,
}

# 4. RANDOMIZED SEARCH (più veloce di Grid)
print("\n🌲 RANDOM FOREST - RandomizedSearchCV")
print("-" * 70)

# Distribuzioni parametri (campionamento random)
param_distributions = {
    "n_estimators": [150, 200, 300, 400],
    "max_depth": [18, 22, 25, None],
    "min_samples_split": [2, 5, 8],
    "min_samples_leaf": [1, 2, 3],
    "max_features": ["sqrt", "log2", 0.8],
    "class_weight": [class_weights_custom],
}

print(f"   Testing 30 combinazioni random (vs 216 complete)")

rf_base = RandomForestClassifier(random_state=42, n_jobs=-1)

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)  # 3 folds (vs 5)

random_search = RandomizedSearchCV(
    rf_base,
    param_distributions,
    n_iter=30,  # Solo 30 combinazioni random
    cv=cv,
    scoring="accuracy",
    n_jobs=-1,
    random_state=42,
    verbose=2,
)

print("   🔧 Training...")
random_search.fit(X_train, y_train)

print(f"\n   ✅ Best CV Score: {random_search.best_score_:.4f}")
print(f"   📋 Best Params:")
for param, value in random_search.best_params_.items():
    if param != "class_weight":
        print(f"      {param}: {value}")

# Test
y_pred = random_search.best_estimator_.predict(X_test)
acc_tuned = accuracy_score(y_test, y_pred)
print(f"\n   🎯 Test Accuracy: {acc_tuned:.4f} ({acc_tuned*100:.2f}%)")

# 5. CALIBRAZIONE ISOTONIC (upgrade da sigmoid)
print("\n🎯 CALIBRAZIONE ISOTONIC")
print("-" * 70)

print("   🔧 Calibrating probabilities...")
calibrated = CalibratedClassifierCV(random_search.best_estimator_, cv=3, method="isotonic")
calibrated.fit(X_train, y_train)

y_pred_cal = calibrated.predict(X_test)
acc_final = accuracy_score(y_test, y_pred_cal)

print(f"   ✅ Accuracy Calibrato: {acc_final:.4f} ({acc_final*100:.2f}%)")
print(f"   📈 Delta calibrazione: {(acc_final - acc_tuned)*100:+.2f}pp")

# 6. CONFRONTO DISTRIBUZIONE
pred_dist = pd.Series(y_pred_cal).value_counts(normalize=True) * 100
print(f"\n📊 Distribuzione Predizioni:")
print(f"   Casa (H):      {pred_dist.get('H', 0):.1f}% (target 41%)")
print(f"   Pareggio (D):  {pred_dist.get('D', 0):.1f}% (target 27%)")
print(f"   Trasferta (A): {pred_dist.get('A', 0):.1f}% (target 32%)")

# 7. SALVA
print("\n💾 Salvataggio modello...")

# Backup se esiste
if os.path.exists("models/enterprise/random_forest.pkl"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"models/backup/random_forest_{timestamp}.pkl"
    import shutil

    shutil.copy("models/enterprise/random_forest.pkl", backup_path)
    print(f"   📦 Backup creato: {backup_path}")

# Save tuned model
joblib.dump(calibrated, "models/enterprise/tuned_quick.pkl")
joblib.dump(feature_cols, "models/enterprise/feature_columns.pkl")

# If accuracy > 51%, replace main
if acc_final > 0.51:
    joblib.dump(calibrated, "models/enterprise/random_forest.pkl")
    print(f"   ✅ Sostituito modello principale! ({acc_final:.4f} > 0.51)")
else:
    print(f"   ⚠️  Salvato come tuned_quick.pkl ({acc_final:.4f} ≤ 0.51)")

print("\n✅ QUICK TUNING COMPLETATO!")
