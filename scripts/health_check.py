#!/usr/bin/env python3
"""
Health Check Sistema - Eseguito ogni ora da cron
Verifica stato componenti critici e scrive JSON di monitoraggio
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Setup
BASE_DIR = Path(__file__).parent.parent
LOG_FILE = BASE_DIR / 'logs' / 'health_check.json'
RENDER_URL = "https://pronostici-calcio-pro.onrender.com"

def check_render_api():
    """Verifica che il server Render risponda"""
    try:
        response = requests.get(f"{RENDER_URL}/api/health", timeout=30)
        return {
            "status": "healthy" if response.status_code == 200 else "degraded",
            "http_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000)
        }
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Server non risponde entro 30s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_data_freshness():
    """Verifica che i dati siano aggiornati (max 7 giorni)"""
    try:
        import pandas as pd
        df = pd.read_csv(BASE_DIR / 'data' / 'dataset_features.csv', parse_dates=['Date'])
        ultima_partita = df['Date'].max()
        giorni_fa = (datetime.now() - ultima_partita).days
        
        return {
            "status": "healthy" if giorni_fa <= 7 else "stale",
            "last_match": ultima_partita.strftime('%Y-%m-%d'),
            "days_old": giorni_fa
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_disk_space():
    """Verifica spazio disco disponibile"""
    try:
        import psutil
        disk = psutil.disk_usage(str(BASE_DIR))
        percent_used = disk.percent
        
        return {
            "status": "healthy" if percent_used < 90 else "critical",
            "percent_used": percent_used,
            "free_gb": round(disk.free / (1024**3), 2)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_cron_daemon():
    """Verifica che cron daemon sia attivo"""
    try:
        import subprocess
        result = subprocess.run(['pgrep', 'cron'], capture_output=True)
        is_running = result.returncode == 0
        
        return {
            "status": "healthy" if is_running else "stopped",
            "running": is_running
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    """Esegue tutti i check e salva risultato"""
    print(f"🏥 Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "components": {
            "render_api": check_render_api(),
            "data_freshness": check_data_freshness(),
            "disk_space": check_disk_space(),
            "cron_daemon": check_cron_daemon()
        }
    }
    
    # Determina status globale
    statuses = [comp["status"] for comp in health_status["components"].values()]
    if "error" in statuses or "critical" in statuses:
        health_status["overall"] = "unhealthy"
    elif "degraded" in statuses or "timeout" in statuses or "stale" in statuses:
        health_status["overall"] = "degraded"
    else:
        health_status["overall"] = "healthy"
    
    # Salva JSON
    os.makedirs(LOG_FILE.parent, exist_ok=True)
    with open(LOG_FILE, 'w') as f:
        json.dump(health_status, f, indent=2)
    
    # Output console
    emoji = "✅" if health_status["overall"] == "healthy" else "⚠️" if health_status["overall"] == "degraded" else "❌"
    print(f"{emoji} Status: {health_status['overall'].upper()}")
    
    for component, data in health_status["components"].items():
        status_emoji = "✅" if data["status"] == "healthy" else "⚠️" if data["status"] in ["degraded", "stale", "timeout"] else "❌"
        print(f"  {status_emoji} {component}: {data['status']}")
    
    # Exit code basato su overall status
    sys.exit(0 if health_status["overall"] in ["healthy", "degraded"] else 1)

if __name__ == "__main__":
    main()
