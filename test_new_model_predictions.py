#!/usr/bin/env python3
"""Test predizioni nuovo modello calibrato"""
import joblib
import pandas as pd

# Carica modello deployato
model = joblib.load("models/enterprise/random_forest.pkl")
features = joblib.load("models/enterprise/feature_columns.pkl")

print("=" * 70)
print("🎯 TEST NUOVO MODELLO CALIBRATO (Sigmoid)")
print("=" * 70)

# Dataset ultimo match
df = pd.read_csv("data/dataset_features.csv")
ultimo_match = df.tail(1)

# Estrai features
X = ultimo_match[features].fillna(0)

# Predizioni
y_pred = model.predict(X)[0]
y_proba = model.predict_proba(X)[0]

# Map probabilities to labels
classes = model.classes_
prob_dict = {classes[i]: y_proba[i] for i in range(len(classes))}

print(f"\n📊 Ultimo Match Test:")
print(f"   Casa: {ultimo_match['HomeTeam'].values[0]}")
print(f"   Trasferta: {ultimo_match['AwayTeam'].values[0]}")
print(f"   Risultato Reale: {ultimo_match['FTR'].values[0]}")

print(f"\n🎯 Predizione: {y_pred}")

print(f"\n📊 Probabilità (Calibrate Sigmoid):")
for label, prob in sorted(prob_dict.items(), key=lambda x: x[1], reverse=True):
    label_name = {"H": "Casa", "D": "Pareggio", "A": "Trasferta"}[label]
    print(f"   {label_name:12} {prob*100:5.1f}%")

print(f"\n✅ Somma probabilità: {sum(prob_dict.values()):.4f} (deve essere ~1.0)")

# Test value betting simulation
print(f"\n💰 VALUE BETTING SIMULATION (quote simulate):")
quote_pareggio = 3.15  # Media Serie A
implied_prob = 1 / quote_pareggio
ev = (prob_dict["D"] * quote_pareggio) - 1
ev_pct = ev * 100

print(f"   Quota Pareggio: {quote_pareggio}")
print(f"   Prob Implicita: {implied_prob*100:.1f}%")
print(f"   Prob Modello: {prob_dict['D']*100:.1f}%")
print(f"   Expected Value: {ev_pct:+.1f}%")

if prob_dict["D"] >= 0.25 and ev_pct >= 25:
    print(f"   ✅ TRADE FASE1 VALIDO (EV ≥25%, Prob ≥25%)")
else:
    print(f"   ❌ Filtrato (Prob {prob_dict['D']*100:.1f}% < 25% o EV {ev_pct:.1f}% < 25%)")

print("\n" + "=" * 70)
print("✅ MODELLO FUNZIONANTE!")
print("=" * 70)
