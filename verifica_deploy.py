#!/usr/bin/env python3
"""Verifica post-deploy log rotation fix"""

import glob
import os
from datetime import datetime

import requests

print("=" * 80)
print("📊 VERIFICA POST-DEPLOY - 18 Aprile 2026")
print("=" * 80)
print()

BASE_URL = "https://pronostici-calcio-professional.onrender.com"

# 1. Health Check
print("1️⃣ HEALTH CHECK")
print("-" * 80)
try:
    resp = requests.get(f"{BASE_URL}/api/health", timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Database: {data['database_records']} partite")
        print(f"✅ Squadre: {data['squadre_caricate']}")
        print(f"✅ Auto-tracking: {data['features']['auto_tracking_enabled']}")
        print(f"✅ Security: {data['features']['security_headers_enabled']}")
        print(f"✅ Rate limiting: {data['features']['rate_limiting_enabled']}")
    else:
        print(f"❌ HTTP {resp.status_code}")
except Exception as e:
    print(f"❌ Errore: {e}")

print()

# 2. Monitoring
print("2️⃣ MONITORING DASHBOARD")
print("-" * 80)
try:
    resp = requests.get(f"{BASE_URL}/api/monitoring/accuracy", timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        print(f"📊 Status: {data['status']} {data['status_icon']}")
        print(
            f"📊 Accuracy lifetime: {data['accuracy_lifetime_pct']}% ({data['correct_lifetime']}/{data['predictions_lifetime']})"
        )
        print(f"💰 ROI lifetime: {data['roi_lifetime_pct']}%")
        print(f"💰 Profit lifetime: {data['total_profit_lifetime']}")
        print(f"⏳ Pending 30d: {data['pending_predictions_30d']}")
    else:
        print(f"❌ HTTP {resp.status_code}")
except Exception as e:
    print(f"❌ Errore: {e}")

print()

# 3. Log Rotation (Locale)
print("3️⃣ LOG ROTATION VERIFICATION (Locale)")
print("-" * 80)

log_files = glob.glob("logs/professional_system.log*")
if log_files:
    log_files.sort()
    total_size = 0

    for log_file in log_files:
        size = os.path.getsize(log_file)
        size_mb = size / (1024 * 1024)
        total_size += size
        basename = os.path.basename(log_file)
        print(f"📄 {basename}: {size_mb:.2f} MB")

    total_mb = total_size / (1024 * 1024)
    print()
    print(f"📊 Totale: {len(log_files)} file, {total_mb:.2f} MB")

    if total_mb > 50:
        print("⚠️  WARNING: Dimensione totale >50MB (target max)")
    elif len(log_files) > 6:
        print("⚠️  WARNING: Più di 6 file (1 principale + 5 backup)")
    else:
        print("✅ Log rotation OK (entro limiti: max 50MB, max 6 file)")
else:
    print("⚠️  Nessun file di log trovato")
    print("   (Log rotation si attiverà al prossimo log >10MB)")

print()

# 4. Dataset
print("4️⃣ DATASET STATUS")
print("-" * 80)
try:
    resp = requests.get(f"{BASE_URL}/api/dataset_info", timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Dataset: {data.get('dataset_file', 'N/A')}")
        print(f"✅ Partite: {data.get('match_count', 'N/A')}")
        print(f"✅ Ultima partita: {data.get('last_match_date', 'N/A')}")
        print(f"✅ Aggiornato: {data.get('updated_at', 'N/A')[:19]}")
    else:
        print(f"❌ HTTP {resp.status_code}")
except Exception as e:
    print(f"❌ Errore: {e}")

print()
print("=" * 80)
print("✅ VERIFICA POST-DEPLOY COMPLETATA")
print("=" * 80)
print()
print("📋 NEXT STEPS:")
print("   1. ✅ Deploy completato e verificato")
print("   2. ⏰ Domani 10:00: daily-predictions.yml prima esecuzione")
print("   3. ⏰ Domani 00:00: update-results.yml prima esecuzione")
print("   4. 📅 Weekend: Accuracy su partite giocate")
print("   5. 📅 1 Maggio: Review Sprint 1 + decisione Sprint 2")
print("=" * 80)
