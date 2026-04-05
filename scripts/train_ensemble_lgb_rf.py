#!/usr/bin/env python3
"""
🎯 ENSEMBLE STACKING: LightGBM + Random Forest
Combina predizioni multiple modelli per accuracy superiore
"""
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.utils.class_weight import compute_class_weight

try:
    import lightgbm as lgb

    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    print("⚠️  LightGBM non installato - installare con: pip install lightgbm")

print("=" * 70)
print("🎯 ENSEMBLE STACKING - LightGBM + Random Forest")
print("=" * 70)

# 1. CARICA DATASET
print("\n📂 Caricamento dataset...")
df = pd.read_csv("data/dataset_features.csv")

# Feature preparation
feature_cols = [c for c in df.columns if c not in ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
X = df[feature_cols].fillna(0)
y = df["FTR"]

print(f"   Features: {len(feature_cols)}")
print(f"   Samples: {len(df)}")

# 2. SPLIT STRATIFICATO
print("\n✂️  Split stratificato train/test (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"   Train: {len(X_train)} samples")
print(f"   Test:  {len(X_test)} samples")

# 3. CLASS WEIGHTS (stessi fix bias)
print("\n⚖️  Calcolo class weights...")
class_weights_auto = compute_class_weight(class_weight="balanced", classes=np.unique(y_train), y=y_train)

class_weights_custom = {
    "H": class_weights_auto[1] * 0.8,  # -20% Casa
    "D": class_weights_auto[0] * 1.3,  # +30% Pareggio (FASE1)
    "A": class_weights_auto[2] * 1.2,  # +20% Trasferta
}

print("   Class Weights:")
for k, v in class_weights_custom.items():
    print(f"      {k}: {v:.3f}")

# 4. BASE ESTIMATORS
print("\n🌲 Creazione base estimators...")

# Random Forest (baseline ottimizzato)
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight=class_weights_custom,
    random_state=42,
    n_jobs=-1,
)

if HAS_LIGHTGBM:
    # LightGBM (cattura pattern diversi)
    lgb_params = {
        "objective": "multiclass",
        "num_class": 3,
        "boosting_type": "gbdt",
        "num_leaves": 31,
        "learning_rate": 0.05,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "max_depth": 15,
        "min_data_in_leaf": 20,
        "verbose": -1,
        "random_state": 42,
    }

    # Map labels to numeric
    label_map = {"H": 0, "D": 1, "A": 2}
    y_train_numeric = y_train.map(label_map)
    y_test_numeric = y_test.map(label_map)

    # Class weights for LightGBM
    lgb_weights = np.ones(len(y_train_numeric))
    for label, weight in class_weights_custom.items():
        lgb_weights[y_train_numeric == label_map[label]] = weight

    # Train LightGBM
    print("   🚀 Training LightGBM...")
    lgb_model = lgb.LGBMClassifier(**lgb_params)
    lgb_model.fit(X_train, y_train_numeric, sample_weight=lgb_weights)

    # Predictions
    y_pred_lgb = lgb_model.predict(X_test)
    y_pred_lgb_labels = pd.Series(y_pred_lgb).map({0: "H", 1: "D", 2: "A"})
    acc_lgb = accuracy_score(y_test, y_pred_lgb_labels)
    print(f"      ✅ Accuracy LightGBM: {acc_lgb:.4f}")

# Train Random Forest
print("   🌲 Training Random Forest...")
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
acc_rf = accuracy_score(y_test, y_pred_rf)
print(f"      ✅ Accuracy Random Forest: {acc_rf:.4f}")

# 5. STACKING ENSEMBLE (if LightGBM available)
if HAS_LIGHTGBM:
    print("\n🎯 Creazione Stacking Ensemble...")

    # Convert class_weights to numeric (for stacking with numeric labels)
    class_weights_numeric = {
        0: class_weights_custom["H"],  # H → 0
        1: class_weights_custom["D"],  # D → 1
        2: class_weights_custom["A"],  # A → 2
    }

    # RF for stacking (with numeric class weights)
    rf_stack = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight=class_weights_numeric,
        random_state=42,
        n_jobs=-1,
    )

    # Meta-learner: Logistic Regression
    estimators = [("rf", rf_stack), ("lgb", lgb_model)]

    stacking_clf = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(max_iter=1000, random_state=42),
        cv=5,
        stack_method="predict_proba",
        n_jobs=-1,
    )

    print("   🔧 Training stacking ensemble...")
    stacking_clf.fit(X_train, y_train_numeric)

    # Predictions
    y_pred_stack = stacking_clf.predict(X_test)
    y_pred_stack_labels = pd.Series(y_pred_stack).map({0: "H", 1: "D", 2: "A"})
    acc_stack = accuracy_score(y_test, y_pred_stack_labels)

    print(f"      ✅ Accuracy Stacking: {acc_stack:.4f}")

    # 6. CALIBRAZIONE ISOTONIC
    print("\n🎯 Calibrazione Isotonic (upgrade da sigmoid)...")
    stacking_calibrated = CalibratedClassifierCV(stacking_clf, cv=3, method="isotonic")  # Più flessibile di sigmoid
    stacking_calibrated.fit(X_train, y_train_numeric)

    y_pred_final = stacking_calibrated.predict(X_test)
    y_pred_final_labels = pd.Series(y_pred_final).map({0: "H", 1: "D", 2: "A"})
    acc_final = accuracy_score(y_test, y_pred_final_labels)

    print(f"      ✅ Accuracy Finale (calibrato): {acc_final:.4f}")

    # 7. VALUTAZIONE DETTAGLIATA
    print("\n" + "=" * 70)
    print("📊 RISULTATI ENSEMBLE")
    print("=" * 70)

    print(f"\n✅ Accuracy Finale: {acc_final:.4f} ({acc_final*100:.2f}%)")

    # Distribuzione predizioni
    pred_dist = y_pred_final_labels.value_counts(normalize=True) * 100
    print(f"\n📊 Distribuzione Predizioni:")
    print(f"   Casa (H):      {pred_dist.get('H', 0):.1f}%")
    print(f"   Pareggio (D):  {pred_dist.get('D', 0):.1f}%")
    print(f"   Trasferta (A): {pred_dist.get('A', 0):.1f}%")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred_final_labels, labels=["A", "D", "H"])
    print(f"\n📋 Confusion Matrix:")
    print("              Pred_A  Pred_D  Pred_H")
    for i, label in enumerate(["True_A", "True_D", "True_H"]):
        print(f"   {label:8} {cm[i][0]:7} {cm[i][1]:7} {cm[i][2]:7}")

    # Classification Report
    print(f"\n📈 Classification Report:")
    print(classification_report(y_test, y_pred_final_labels, target_names=["Trasferta", "Pareggio", "Casa"]))

    # 8. CONFRONTO MODELLI
    print("\n" + "=" * 70)
    print("🏆 CONFRONTO MODELLI")
    print("=" * 70)
    print(f"   Random Forest:        {acc_rf:.4f}")
    print(f"   LightGBM:            {acc_lgb:.4f}")
    print(f"   Stacking (no calib): {acc_stack:.4f}")
    print(f"   🏆 Stacking Calibrato: {acc_final:.4f}")

    improvement = (acc_final - acc_rf) * 100
    print(f"\n📈 Miglioramento vs RF: {improvement:+.2f}pp")

    # 9. SALVA MODELLO MIGLIORE
    print("\n" + "=" * 70)
    print("💾 SALVATAGGIO MODELLO")
    print("=" * 70)

    # Backup old model
    if os.path.exists("models/enterprise/random_forest.pkl"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"models/backup/random_forest_{timestamp}.pkl"
        os.rename("models/enterprise/random_forest.pkl", backup_path)
        print(f"   📦 Backup vecchio modello: {backup_path}")

    # Save ensemble
    joblib.dump(stacking_calibrated, "models/enterprise/ensemble_stacked.pkl")
    joblib.dump(feature_cols, "models/enterprise/feature_columns.pkl")

    # If better, replace main model
    if acc_final > acc_rf:
        joblib.dump(stacking_calibrated, "models/enterprise/random_forest.pkl")
        print(f"   ✅ Ensemble salvato come modello principale (migliore di {improvement:.2f}pp)")
    else:
        print(f"   ⚠️  Ensemble salvato separatamente (non migliore)")

    print("\n✅ Training completato!")

else:
    # Fallback: solo RF calibrato
    print("\n⚠️  LightGBM non disponibile - training solo RF calibrato")

    rf_calibrated = CalibratedClassifierCV(rf, cv=3, method="isotonic")
    rf_calibrated.fit(X_train, y_train)

    y_pred_final = rf_calibrated.predict(X_test)
    acc_final = accuracy_score(y_test, y_pred_final)

    print(f"\n✅ Accuracy RF Calibrato: {acc_final:.4f}")

    # Save
    joblib.dump(rf_calibrated, "models/enterprise/random_forest.pkl")
    joblib.dump(feature_cols, "models/enterprise/feature_columns.pkl")

    print("✅ Modello salvato!")
