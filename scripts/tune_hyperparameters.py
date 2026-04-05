#!/usr/bin/env python3
"""
🎯 HYPERPARAMETER TUNING - GridSearchCV Profondo
Ottimizza parametri Random Forest e LightGBM
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.utils.class_weight import compute_class_weight

try:
    import lightgbm as lgb

    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

print("=" * 70)
print("🎯 HYPERPARAMETER TUNING - GridSearchCV")
print("=" * 70)

# 1. CARICA DATASET
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

# 4. RANDOM FOREST TUNING
print("\n🌲 RANDOM FOREST - GridSearchCV")
print("-" * 70)

param_grid_rf = {
    "n_estimators": [200, 300, 500],
    "max_depth": [15, 20, 25, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2"],
    "class_weight": [class_weights_custom],
}

print(f"   Parametri da testare: {np.prod([len(v) for v in param_grid_rf.values()])} combinazioni")

rf_base = RandomForestClassifier(random_state=42, n_jobs=-1)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid_rf = GridSearchCV(rf_base, param_grid_rf, cv=cv, scoring="accuracy", n_jobs=-1, verbose=1)

print("   🔧 Training in corso...")
grid_rf.fit(X_train, y_train)

print(f"\n   ✅ Best Score (CV): {grid_rf.best_score_:.4f}")
print(f"   📋 Best Params:")
for param, value in grid_rf.best_params_.items():
    if param != "class_weight":
        print(f"      {param}: {value}")

# Test accuracy
y_pred_rf = grid_rf.best_estimator_.predict(X_test)
acc_rf_tuned = accuracy_score(y_test, y_pred_rf)
print(f"\n   🎯 Test Accuracy: {acc_rf_tuned:.4f} ({acc_rf_tuned*100:.2f}%)")

# 5. LIGHTGBM TUNING (se disponibile)
if HAS_LIGHTGBM:
    print("\n🚀 LIGHTGBM - GridSearchCV")
    print("-" * 70)

    # Map labels
    label_map = {"H": 0, "D": 1, "A": 2}
    y_train_numeric = y_train.map(label_map)
    y_test_numeric = y_test.map(label_map)

    # Sample weights
    lgb_weights = np.ones(len(y_train_numeric))
    for label, weight in class_weights_custom.items():
        lgb_weights[y_train_numeric == label_map[label]] = weight

    param_grid_lgb = {
        "num_leaves": [20, 31, 50],
        "max_depth": [10, 15, 20],
        "learning_rate": [0.01, 0.05, 0.1],
        "n_estimators": [100, 200, 300],
        "min_child_samples": [10, 20, 30],
        "subsample": [0.8, 0.9, 1.0],
        "colsample_bytree": [0.8, 0.9, 1.0],
    }

    print(f"   Parametri da testare: {np.prod([len(v) for v in param_grid_lgb.values()])} combinazioni")

    lgb_base = lgb.LGBMClassifier(objective="multiclass", num_class=3, random_state=42, verbose=-1)

    grid_lgb = GridSearchCV(lgb_base, param_grid_lgb, cv=cv, scoring="accuracy", n_jobs=-1, verbose=1)

    print("   🔧 Training in corso...")
    grid_lgb.fit(X_train, y_train_numeric, sample_weight=lgb_weights)

    print(f"\n   ✅ Best Score (CV): {grid_lgb.best_score_:.4f}")
    print(f"   📋 Best Params:")
    for param, value in grid_lgb.best_params_.items():
        print(f"      {param}: {value}")

    # Test accuracy
    y_pred_lgb = grid_lgb.best_estimator_.predict(X_test)
    y_pred_lgb_labels = pd.Series(y_pred_lgb).map({0: "H", 1: "D", 2: "A"})
    acc_lgb_tuned = accuracy_score(y_test, y_pred_lgb_labels)
    print(f"\n   🎯 Test Accuracy: {acc_lgb_tuned:.4f} ({acc_lgb_tuned*100:.2f}%)")

# 6. CALIBRAZIONE MODELLO MIGLIORE
print("\n" + "=" * 70)
print("🎯 CALIBRAZIONE FINALE")
print("=" * 70)

best_model = grid_rf.best_estimator_
best_acc = acc_rf_tuned
model_name = "Random Forest"

if HAS_LIGHTGBM and acc_lgb_tuned > acc_rf_tuned:
    best_model = grid_lgb.best_estimator_
    best_acc = acc_lgb_tuned
    model_name = "LightGBM"
    y_train_for_calib = y_train_numeric
else:
    y_train_for_calib = y_train

print(f"   🏆 Modello migliore: {model_name} ({best_acc:.4f})")

# Calibrazione isotonic
print("   🔧 Calibrazione isotonic...")
calibrated = CalibratedClassifierCV(best_model, cv=3, method="isotonic")
calibrated.fit(X_train, y_train_for_calib)

# Predizioni finali
if model_name == "LightGBM":
    y_pred_final = calibrated.predict(X_test)
    y_pred_final_labels = pd.Series(y_pred_final).map({0: "H", 1: "D", 2: "A"})
else:
    y_pred_final_labels = calibrated.predict(X_test)

acc_final = accuracy_score(y_test, y_pred_final_labels)

print(f"\n   ✅ Accuracy Calibrato: {acc_final:.4f} ({acc_final*100:.2f}%)")
print(f"   📈 Miglioramento: {(acc_final - best_acc)*100:+.2f}pp")

# 7. SALVATAGGIO
print("\n💾 Salvataggio modello ottimizzato...")
joblib.dump(calibrated, "models/enterprise/tuned_model.pkl")
joblib.dump(feature_cols, "models/enterprise/feature_columns.pkl")

if acc_final > 0.51:  # Se supera baseline
    joblib.dump(calibrated, "models/enterprise/random_forest.pkl")
    print("   ✅ Sostituito modello principale!")
else:
    print("   ⚠️  Salvato come tuned_model.pkl (non migliore)")

print("\n✅ Tuning completato!")
