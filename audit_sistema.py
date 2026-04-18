#!/usr/bin/env python3
"""Audit chirurgico completo del sistema"""

import json
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

print("=" * 70)
print("🔍 AUDIT CHIRURGICO SISTEMA - 18 Aprile 2026")
print("=" * 70)
print()

# 1. Health Check Produzione
print("1️⃣ STATO PRODUZIONE RENDER")
print("-" * 70)
try:
    health = requests.get("https://pronostici-calcio-professional.onrender.com/api/health", timeout=10).json()
    print(f"✅ Sistema: {health['status']}")
    print(f"✅ Database: {health['database_records']} partite")
    print(f"✅ Squadre: {health['squadre_caricate']}")
    print(f"✅ Auto-tracking: {health.get('features', {}).get('auto_tracking_enabled', 'N/A')}")
    print(f"✅ Rate limiting: {health.get('features', {}).get('rate_limiting_enabled', 'N/A')}")
    print(f"✅ Security headers: {health.get('features', {}).get('security_headers_enabled', 'N/A')}")
    print(f"✅ Odds API key: {health.get('odds_api_key_configured', False)}")
    print(f"⏰ Last check: {health.get('last_check', 'N/A')[:19]}")
except Exception as e:
    print(f"❌ ERRORE health check: {e}")

print()

# 2. Monitoring Dashboard
print("2️⃣ METRICHE DASHBOARD")
print("-" * 70)
try:
    mon = requests.get(
        "https://pronostici-calcio-professional.onrender.com/api/monitoring/accuracy",
        timeout=10,
    ).json()
    print(f"📊 Status: {mon['status']} {mon['status_icon']}")
    print(f"📊 Pending 30d: {mon['pending_predictions_30d']}")
    print(f"📊 Accuracy lifetime: {mon['accuracy_lifetime_pct']}%")
    print(f"📊 Predictions lifetime: {mon['predictions_lifetime']}")
    print(f"📊 Correct lifetime: {mon.get('correct_lifetime', 'N/A')}")
    print(f"💰 ROI lifetime: {mon.get('roi_lifetime_pct', 'N/A')}%")
    print(f"💰 Profit lifetime: {mon.get('total_profit_lifetime', 'N/A')}")
    print(
        f"📈 vs Backtest: {mon['vs_backtest']['baseline_pct']}% baseline, diff: {mon['vs_backtest']['difference_pct']}%"
    )
except Exception as e:
    print(f"❌ ERRORE monitoring: {e}")

print()

# 3. Tracking CSV
print("3️⃣ TRACKING CSV STATUS")
print("-" * 70)
try:
    csv_resp = requests.get(
        "https://pronostici-calcio-professional.onrender.com/api/export_tracking_csv",
        timeout=10,
    ).json()
    print(f"✅ Total predictions: {csv_resp['total_predictions']}")
    print(f"✅ Last update: {csv_resp['last_update'][:19]}")

    df = pd.read_csv(StringIO(csv_resp["csv_content"]))
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    con_risultati = df["Risultato_Reale"].notna() & (df["Risultato_Reale"] != "")
    pending = ~con_risultati

    print(f"📊 Totale righe: {len(df)}")
    print(f"📊 Con risultati: {con_risultati.sum()}")
    print(f"📊 Pending: {pending.sum()}")
    print(f"📊 Righe con Data=NaT: {df['Data'].isna().sum()}")

    if con_risultati.sum() > 0:
        df_ris = df[con_risultati]
        corrette = (df_ris["Corretto"] == True) | (df_ris["Corretto"] == "True")

        print(f"✅ Corrette: {corrette.sum()}/{len(df_ris)} ({corrette.sum()/len(df_ris)*100:.1f}%)")

        if "Profit" in df_ris.columns:
            profit = pd.to_numeric(df_ris["Profit"], errors="coerce").sum()
            print(f"💰 Profit totale: {profit:.2f}")

except Exception as e:
    print(f"❌ ERRORE tracking CSV: {e}")

print()

# 4. Test Endpoint Critici
print("4️⃣ TEST ENDPOINT API")
print("-" * 70)

endpoints = [
    ("/api/health", "GET"),
    ("/api/dataset_info", "GET"),
    ("/api/monitoring/accuracy", "GET"),
    ("/api/export_tracking_csv", "GET"),
    ("/api/upcoming_matches", "GET"),
]

base_url = "https://pronostici-calcio-professional.onrender.com"

for endpoint, method in endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", timeout=10)
        status = "✅" if resp.status_code == 200 else "❌"
        print(f"{status} {endpoint}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ {endpoint}: {str(e)[:50]}")

print()

# 5. Dataset Info
print("5️⃣ DATASET & MODELLI")
print("-" * 70)
try:
    dataset = requests.get(f"{base_url}/api/dataset_info", timeout=10).json()
    print(f"📊 Partite totali: {dataset.get('total_matches', 'N/A')}")
    print(f"📊 Stagioni: {dataset.get('seasons', 'N/A')}")
    print(
        f"📊 Range date: {dataset.get('date_range', {}).get('min', 'N/A')} → {dataset.get('date_range', {}).get('max', 'N/A')}"
    )
    print(f"🧠 Modelli disponibili: {', '.join(dataset.get('models_available', []))}")
except Exception as e:
    print(f"❌ ERRORE dataset info: {e}")

print()
print("=" * 70)
print("✅ AUDIT COMPLETATO")
print("=" * 70)
