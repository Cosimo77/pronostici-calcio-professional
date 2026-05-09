#!/usr/bin/env python3
"""Verifica accuracy lifetime dashboard"""

from io import StringIO

import pandas as pd
import requests

# Get monitoring data
mon = requests.get("https://pronostici-calcio-professional.onrender.com/api/monitoring/accuracy").json()

print("📊 METRICHE DASHBOARD:")
print(f"  Accuracy lifetime: {mon.get('accuracy_lifetime_pct', 'N/A')}%")
print(f"  Predictions lifetime: {mon.get('predictions_lifetime', 'N/A')}")
print(f"  Correct lifetime: {mon.get('correct_lifetime', 'N/A')}")
print(f"  Total profit: {mon.get('total_profit_lifetime', 'N/A')}")
print()

# Get CSV data
csv_resp = requests.get("https://pronostici-calcio-professional.onrender.com/api/export_tracking_csv").json()
df = pd.read_csv(StringIO(csv_resp["csv_content"]))

print("📁 CSV REALE:")
print(f"  Totale righe: {len(df)}")
con_risultati = df["Risultato_Reale"].notna() & (df["Risultato_Reale"] != "")
print(f"  Con risultati: {con_risultati.sum()}")
print(f"  Pending: {(~con_risultati).sum()}")

if con_risultati.sum() > 0:
    df_risultati = df[con_risultati]
    corrette = (df_risultati["Corretto"] == True) | (df_risultati["Corretto"] == "True")
    print(f"  Corrette: {corrette.sum()}")
    print(f"  Accuracy calcolata: {corrette.sum() / len(df_risultati) * 100:.1f}%")
    print()
    print("  Prime 5 righe con risultati:")
    print(df_risultati[["Data", "Casa", "Ospite", "Risultato_Reale", "Corretto"]].head().to_string())
