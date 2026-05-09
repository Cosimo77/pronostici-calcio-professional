#!/usr/bin/env python3
"""Debug monitoring endpoint logic"""
from datetime import datetime, timedelta

import pandas as pd

# Simula il CSV
df = pd.read_csv("tracking_predictions_live.csv")

print("=" * 60)
print("DEBUG MONITORING LOGIC")
print("=" * 60)

# Segui lo stesso flusso del monitoring endpoint
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

df_risultati = df[df["Risultato_Reale"].notna() & (df["Risultato_Reale"] != "")]
df_pending = df[df["Risultato_Reale"].isna() | (df["Risultato_Reale"] == "")]

print(f"\nTotal rows: {len(df)}")
print(f"Con risultato: {len(df_risultati)}")
print(f"Pending: {len(df_pending)}")

# Check se ci sono risultati
if len(df_risultati) == 0:
    print("\n✅ df_risultati == 0, entro in blocco pending")

    # Questo è il blocco che mostra pending
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    # PRIMA controlla 7 giorni
    df_pending_7d = df_pending[df_pending["Data"] >= seven_days_ago]
    print(f"\nPending ultimi 7 giorni: {len(df_pending_7d)}")

    if len(df_pending_7d) > 0:
        print("mostro: {len(df_pending_7d)} predizioni ultimi 7 giorni")
    else:
        print("⚠️ Nessuna pending 7 giorni, provo 30 giorni...")
        # Solo se 0 nei 7 giorni, controlla 30
        thirty_days_ago = today - timedelta(days=30)
        df_pending_30d = df_pending[df_pending["Data"] >= thirty_days_ago]
        print(f"Pending ultimi 30 giorni: {len(df_pending_30d)}")

# Check risultati ultimi 7-30 giorni
today = datetime.now()
seven_days_ago = today - timedelta(days=7)
df_7d = df_risultati[df_risultati["Data"] >= seven_days_ago]

print(f"\n📊 df_risultati ultimi 7 giorni: {len(df_7d)}")

if len(df_7d) == 0:
    thirty_days_ago = today - timedelta(days=30)
    df_30d = df_risultati[df_risultati["Data"] >= thirty_days_ago]
    print(f"📊 df_risultati ultimi 30 giorni: {len(df_30d)}")

    if len(df_30d) == 0:
        print("\n⚠️ QUESTO è il problema!")
        print("   df_risultati ultimi 30 giorni = 0")
        print("   Quindi entra nel blocco pending_30d")

        # MA guarda cosa conta
        df_pending_30d = df_pending[df_pending["Data"] >= thirty_days_ago]
        print(f"\n   df_pending FILTRATO >30 giorni fa: {len(df_pending_30d)}")
        print(f"   Ma df_pending TOTALE: {len(df_pending)}")

        # Debug: mostra date pending
        print(f"\n   Date pending min: {df_pending['Data'].min()}")
        print(f"   Date pending max: {df_pending['Data'].max()}")
        print(f"   Cutoff 30 giorni: {thirty_days_ago}")

        # Quante sono REALMENTE recenti?
        recent = df_pending[df_pending["Data"] >= thirty_days_ago]
        print(f"\n   ✅ REALMENTE pending ultimi 30gg: {len(recent)}")
