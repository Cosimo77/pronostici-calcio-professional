#!/usr/bin/env python3
"""Test date conversion fix for monitoring endpoint"""
from datetime import datetime, timedelta

import pandas as pd

# Simula il CSV tracking
df = pd.read_csv("tracking_predictions_live.csv")

print(f"📊 CSV loaded: {len(df)} rows")
print(f"Data type PRIMA conversione: {df['Data'].dtype}")

# CONVERSIONE SUBITO (come nel fix)
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
print(f"Data type DOPO conversione: {df['Data'].dtype}")

# Filtra pending
df_pending = df[df["Risultato_Reale"].isna() | (df["Risultato_Reale"] == "")]
print(f"\n⏳ Predizioni pending: {len(df_pending)}")

# Conta recent (test confronto datetime)
today = datetime.now()
seven_days_ago = today - timedelta(days=7)

try:
    df_pending_recent = df_pending[df_pending["Data"] >= seven_days_ago]
    print(f"✅ Confronto datetime funziona!")
    print(f"📅 Pending ultimi 7 giorni: {len(df_pending_recent)}")
except TypeError as e:
    print(f"❌ Errore confronto: {e}")

# 30 giorni
thirty_days_ago = today - timedelta(days=30)
df_pending_30d = df_pending[df_pending["Data"] >= thirty_days_ago]
print(f"📅 Pending ultimi 30 giorni: {len(df_pending_30d)}")
