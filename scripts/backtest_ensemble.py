#!/usr/bin/env python3
"""
🎯 BACKTEST ENSEMBLE - Validation ROI FASE1
Confronta nuovo ensemble vs modello baseline su trade storici
"""
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd

print("=" * 70)
print("🎯 BACKTEST ENSEMBLE - Validation ROI")
print("=" * 70)

# 1. CARICA MODELLI
print("\n📂 Caricamento modelli...")

models_to_test = []

# Ensemble stacking
if os.path.exists("models/enterprise/ensemble_stacked.pkl"):
    ensemble = joblib.load("models/enterprise/ensemble_stacked.pkl")
    models_to_test.append(("Ensemble Stacking", ensemble))
    print("   ✅ Ensemble stacked caricato")

# Tuned model
if os.path.exists("models/enterprise/tuned_model.pkl"):
    tuned = joblib.load("models/enterprise/tuned_model.pkl")
    models_to_test.append(("Tuned Model", tuned))
    print("   ✅ Tuned model caricato")

# Baseline (backup)
baseline_files = [f for f in os.listdir("models/backup/") if f.startswith("random_forest_")]
if baseline_files:
    baseline_path = f"models/backup/{sorted(baseline_files)[-1]}"
    baseline = joblib.load(baseline_path)
    models_to_test.append(("Baseline RF", baseline))
    print(f"   ✅ Baseline caricato: {baseline_files[-1]}")

if not models_to_test:
    print("   ❌ Nessun modello trovato!")
    exit(1)

feature_cols = joblib.load("models/enterprise/feature_columns.pkl")

# 2. CARICA DATASET STORICO
print("\n📂 Caricamento dataset storico...")
df = pd.read_csv("data/dataset_features.csv")

# Ultimi 510 match (simula FASE1 backtest)
df_backtest = df.tail(510).copy()

X_backtest = df_backtest[feature_cols].fillna(0)
y_true = df_backtest["FTR"]

print(f"   Match backtest: {len(df_backtest)}")

# 3. SIMULA TRADING FASE1 PER OGNI MODELLO
print("\n" + "=" * 70)
print("📊 BACKTEST ROI - FASE1 STRATEGY")
print("=" * 70)

results = {}

for model_name, model in models_to_test:
    print(f"\n🔍 {model_name}")
    print("-" * 70)

    # Predizioni probabilistiche
    try:
        # Handle different model types
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_backtest)
        else:
            # For some calibrated models
            probs = model.predict_proba(X_backtest)

        # Map to labels (H, D, A)
        if isinstance(probs, np.ndarray):
            # Check if numeric labels (0,1,2) or string (H,D,A)
            classes = model.classes_ if hasattr(model, "classes_") else ["H", "D", "A"]

            # Create probability dict for each row
            trades = []
            for i, row in df_backtest.iterrows():
                prob_dict = {}
                for j, cls in enumerate(classes):
                    # Map numeric to string if needed
                    if isinstance(cls, (int, np.integer)):
                        label = {0: "H", 1: "D", 2: "A"}[cls]
                    else:
                        label = cls
                    prob_dict[label] = probs[len(trades), j]

                # FASE1 filter: Solo pareggi
                prob_draw = prob_dict.get("D", 0)

                # Simula quote pareggio (media Serie A: 3.0-3.3)
                implied_prob = 1 / 3.15  # ~31.7%

                # Expected Value
                ev = (prob_draw * 3.15) - 1
                ev_pct = ev * 100

                # FASE1 filters
                if prob_draw >= 0.25 and ev_pct >= 25:  # EV ≥25%
                    # Simula trade
                    actual_result = row["FTR"]
                    win = 1 if actual_result == "D" else 0
                    profit = 3.15 - 1 if win else -1

                    trades.append({"prob_draw": prob_draw, "ev": ev_pct, "win": win, "profit": profit})

        # Calcola metriche
        if trades:
            df_trades = pd.DataFrame(trades)

            n_trades = len(df_trades)
            win_rate = df_trades["win"].mean() * 100
            total_profit = df_trades["profit"].sum()
            roi = (total_profit / n_trades) * 100

            print(f"   Trade eseguiti: {n_trades}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Profit totale: {total_profit:+.2f} unità")
            print(f"   🎯 ROI: {roi:+.2f}%")

            results[model_name] = {"trades": n_trades, "win_rate": win_rate, "roi": roi, "profit": total_profit}
        else:
            print("   ⚠️  Nessun trade FASE1 (filtri troppo stretti)")
            results[model_name] = None

    except Exception as e:
        print(f"   ❌ Errore: {e}")
        results[model_name] = None

# 4. CONFRONTO FINALE
print("\n" + "=" * 70)
print("🏆 CONFRONTO MODELLI")
print("=" * 70)

valid_results = {k: v for k, v in results.items() if v is not None}

if valid_results:
    # Ordina per ROI
    sorted_models = sorted(valid_results.items(), key=lambda x: x[1]["roi"], reverse=True)

    print(f"\n{'Modello':<25} {'Trades':>8} {'Win Rate':>10} {'ROI':>10}")
    print("-" * 70)

    for model_name, metrics in sorted_models:
        print(f"{model_name:<25} {metrics['trades']:>8} {metrics['win_rate']:>9.1f}% {metrics['roi']:>9.2f}%")

    # Best model
    best_model = sorted_models[0]
    print(f"\n🏆 MIGLIORE: {best_model[0]} (ROI {best_model[1]['roi']:+.2f}%)")

    # Confronto con baseline
    if "Baseline RF" in results and results["Baseline RF"]:
        baseline_roi = results["Baseline RF"]["roi"]
        best_roi = best_model[1]["roi"]
        improvement = best_roi - baseline_roi

        print(f"\n📈 Miglioramento vs Baseline: {improvement:+.2f}pp ROI")

        if improvement >= 2.0:
            print("   ✅ DEPLOY CONSIGLIATO (miglioramento ≥2%)")
        elif improvement >= 1.0:
            print("   ⚠️  DEPLOY OPZIONALE (miglioramento moderato)")
        else:
            print("   ❌ NO DEPLOY (miglioramento insufficiente)")
else:
    print("   ⚠️  Nessun modello ha generato trade validi")

print("\n✅ Backtest completato!")
