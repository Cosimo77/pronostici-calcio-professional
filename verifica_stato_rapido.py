#!/usr/bin/env python3
"""
Script rapido per verificare stato sistema
"""
import pandas as pd
from datetime import datetime
import os
import json

print("\n" + "="*70)
print("📊 STATO SISTEMA PRONOSTICI CALCIO")
print("="*70)

# DATI
try:
    df = pd.read_csv('data/dataset_features.csv', parse_dates=['Date'])
    ultima_partita = df['Date'].max()
    giorni_fa = (datetime.now() - ultima_partita).days
    
    status_dati = "✅ FRESH" if giorni_fa <= 7 else "⚠️ VECCHI"
    
    print(f"\n📊 DATI: {status_dati}")
    print(f"   Ultima partita: {ultima_partita.strftime('%d/%m/%Y')} ({giorni_fa} giorni fa)")
    print(f"   Totale partite: {len(df)}")
    print(f"   Dimensione: {os.path.getsize('data/dataset_features.csv')/1024:.1f} KB")
except Exception as e:
    print(f"\n❌ ERRORE DATI: {e}")

# MODELLI
try:
    import pickle
    with open('models/metadata.pkl', 'rb') as f:
        meta = pickle.load(f)
    
    print(f"\n🤖 MODELLI:")
    if 'models_info' in meta:
        for name, info in meta['models_info'].items():
            acc = info.get('accuracy', info.get('test_accuracy', 0))
            model_name = name.split('_')[0][:8]
            print(f"   {model_name:12s}: {acc*100:5.1f}% accuracy")
    
    # Data training
    for fname in ['randomforest_model.pkl']:
        if os.path.exists(f'models/{fname}'):
            mtime = os.path.getmtime(f'models/{fname}')
            dt = datetime.fromtimestamp(mtime)
            days_ago = (datetime.now() - dt).days
            print(f"   Training: {dt.strftime('%d/%m/%Y %H:%M')} ({days_ago} giorni fa)")
            break
            
except Exception as e:
    print(f"\n❌ ERRORE MODELLI: {e}")

# AUTOMAZIONE
try:
    if os.path.exists('logs/automation_status.json'):
        with open('logs/automation_status.json') as f:
            status = json.load(f)
        
        print(f"\n⚙️  AUTOMAZIONE:")
        
        last_update = status.get('last_daily_update', 'N/A')
        if last_update != 'N/A':
            dt = datetime.fromisoformat(last_update[:19])
            ore_fa = (datetime.now() - dt).total_seconds() / 3600
            print(f"   Ultimo update: {dt.strftime('%d/%m/%Y %H:%M')} ({ore_fa:.1f}h fa)")
        
        last_train = status.get('last_weekly_retrain', 'N/A')
        if last_train != 'N/A':
            dt = datetime.fromisoformat(last_train[:19])
            giorni_fa = (datetime.now() - dt).days
            print(f"   Ultimo training: {dt.strftime('%d/%m/%Y %H:%M')} ({giorni_fa}d fa)")
        
        errors = status.get('errors', [])
        if errors:
            print(f"   ⚠️  Errori recenti: {len(errors)}")
            # Mostra ultimo errore
            last_err = errors[-1]
            print(f"      Ultimo: {last_err['process']}")
            
except Exception as e:
    print(f"\n❌ ERRORE AUTOMAZIONE: {e}")

# HEALTH CHECK
try:
    if os.path.exists('logs/health_check.json'):
        with open('logs/health_check.json') as f:
            health = json.load(f)
        
        overall = health.get('overall_status', 'unknown')
        status_icon = "✅" if overall == "healthy" else "❌"
        
        print(f"\n🏥 HEALTH: {status_icon} {overall.upper()}")
        
        checks = health.get('checks', {})
        if 'data_freshness' in checks:
            age = checks['data_freshness'].get('age_days', 0)
            print(f"   Dati: {age:.1f} giorni")
        
        if 'disk_space' in checks:
            free = checks['disk_space'].get('free_gb', 0)
            print(f"   Disco: {free:.1f} GB liberi")
            
except Exception as e:
    print(f"\n❌ ERRORE HEALTH: {e}")

print("\n" + "="*70)

# Raccomandazioni
if giorni_fa > 7:
    print("⚠️  RACCOMANDAZIONE: Esegui aggiornamento dati")
    print("   → python3 scripts/aggiorna_quotidiano_auto.py")
else:
    print("✅ Sistema operativo e aggiornato")

print("="*70 + "\n")
