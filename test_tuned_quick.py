#!/usr/bin/env python3
"""Test rapido tuned_quick.pkl"""
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Load
model = joblib.load("models/enterprise/tuned_quick.pkl")
features = joblib.load("models/enterprise/feature_columns.pkl")

# Dataset
df = pd.read_csv("data/dataset_features.csv")
X = df[features].fillna(0)
y = df["FTR"]

_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Predict
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

# Distribution
dist = pd.Series(y_pred).value_counts(normalize=True) * 100

print(f"✅ Accuracy: {acc:.4f} ({acc*100:.2f}%)")
print(f"\n📊 Distribuzione:")
print(f"   Casa:      {dist.get('H', 0):.1f}% (target 41%)")
print(f"   Pareggio:  {dist.get('D', 0):.1f}% (target 27%)")
print(f"   Trasferta: {dist.get('A', 0):.1f}% (target 32%)")
