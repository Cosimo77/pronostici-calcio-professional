#!/usr/bin/env python3
"""
Feature Engineering per Pareggi - Quick Win
============================================

Aggiungiamo features che catturano pattern tipici dei pareggi:
- Squadre equilibrate (poca differenza forza)
- Entrambe difensive
- Storia head-to-head pareggiosa
"""

import numpy as np
import pandas as pd

print("=" * 70)
print("🔧 FEATURE ENGINEERING - Focus Pareggi")
print("=" * 70)

# Carica dataset
print("\n📂 Caricamento dataset...")
df = pd.read_csv("data/dataset_features.csv")

print(f"   Righe originali: {len(df)}")
print(
    f"   Features originali: {len([c for c in df.columns if c not in ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']])}"
)

# FEATURE 1: Equilibrio Forza (squadre simili → più pareggi)
print("\n✨ Creando feature 'Equilibrio Squadre'...")

# Proxy forza: media gol fatti
try:
    df["GoalBalance_Home"] = df["FTHG"] - df["FTAG"]  # Bilancio gol casa
    df["GoalBalance_Away"] = df["FTAG"] - df["FTHG"]  # Bilancio gol trasferta

    # Differenza assoluta xG (se disponibile)
    if "HxG" in df.columns and "AxG" in df.columns:
        df["xG_Diff"] = abs(df["HxG"] - df["AxG"])  # Piccola diff → equilibrio
        print("   ✅ xG_Diff creata")

    # Differenza tiri
    if "HS" in df.columns and "AS" in df.columns:
        df["Shots_Diff"] = abs(df["HS"] - df["AS"])  # Equilibrio tiri
        print("   ✅ Shots_Diff creata")

    # Differenza tiri porta
    if "HST" in df.columns and "AST" in df.columns:
        df["ShotsOnTarget_Diff"] = abs(df["HST"] - df["AST"])
        print("   ✅ ShotsOnTarget_Diff creata")

except Exception as e:
    print(f"   ⚠️  Errore: {e}")

# FEATURE 2: Squadre Difensive (pochi gol → più pareggi)
print("\n✨ Creando feature 'Difensività'...")

try:
    # Media gol fatti/subiti
    if "FTHG" in df.columns and "FTAG" in df.columns:
        df["LowScoring"] = ((df["FTHG"] + df["FTAG"]) <= 2).astype(int)  # ≤2 gol totali
        print("   ✅ LowScoring creata")

    # Match equilibrato (diff gol ≤1)
    df["CloseMatch"] = (abs(df["FTHG"] - df["FTAG"]) <= 1).astype(int)
    print("   ✅ CloseMatch creata")

except Exception as e:
    print(f"   ⚠️  Errore: {e}")

# FEATURE 3: Statistiche Pareggi (rolling)
print("\n✨ Creando rolling stats pareggi...")

try:
    # Ordina per data
    df_sorted = df.sort_values("Date") if "Date" in df.columns else df

    # % pareggi ultimi N match (difficile senza groupby per squadra)
    # Per ora skippo, serve logica più complessa

    print("   ⚠️  Rolling stats pareggi skippate (serve refactor)")

except Exception as e:
    print(f"   ⚠️  Errore: {e}")

# FEATURE 4: Indicatori decisione pareggio
print("\n✨ Creando decision features...")

try:
    # Goal Probability Product (sotto threshold → pareggio)
    # Se xG casa e trasferta bassi → più probabile pareggio
    if "HxG" in df.columns and "AxG" in df.columns:
        df["Both_Low_xG"] = ((df["HxG"] < 1.2) & (df["AxG"] < 1.2)).astype(int)
        print("   ✅ Both_Low_xG creata")

    # Equilibrio possesso
    if "HP" in df.columns and "AP" in df.columns:
        df["Possession_Balanced"] = (abs(df["HP"] - df["AP"]) < 10).astype(int)
        print("   ✅ Possession_Balanced creata")

except Exception as e:
    print(f"   ⚠️  Errore: {e}")

# Salva dataset aggiornato
print("\n💾 Salvataggio dataset arricchito...")

new_features = [c for c in df.columns if c not in ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
print(f"   Features totali: {len(new_features)} (+{len(new_features) - 32} nuove)")

df.to_csv("data/dataset_features_enhanced.csv", index=False)
print("   ✅ Salvato: data/dataset_features_enhanced.csv")

# Verifica correlazione con pareggi
print("\n📊 Correlazione nuove features con pareggi...")

df_with_target = df.copy()
df_with_target["IS_DRAW"] = (df["FTR"] == "D").astype(int)

new_feature_cols = [
    "xG_Diff",
    "Shots_Diff",
    "ShotsOnTarget_Diff",
    "LowScoring",
    "CloseMatch",
    "Both_Low_xG",
    "Possession_Balanced",
]

existing_cols = [c for c in new_feature_cols if c in df_with_target.columns]

if existing_cols:
    correlations = df_with_target[existing_cols + ["IS_DRAW"]].corr()["IS_DRAW"].sort_values(ascending=False)

    print("\   Top features correlate con pareggi:")
    for feat in existing_cols:
        if feat in correlations:
            corr_val = correlations[feat]
            print(f"      {feat:<25} {corr_val:>6.3f}")

print("\n" + "=" * 70)
print("✅ FEATURE ENGINEERING COMPLETATO!")
print("=" * 70)

print(f"\n🎯 NEXT: Retraining modello con dataset arricchito")
print(f"   python3 scripts/train_balanced_model.py")
print(f"   (usa dataset_features_enhanced.csv)")
print()
