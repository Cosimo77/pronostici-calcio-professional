#!/usr/bin/env python3
"""Verifica stato aggiornamenti automatici"""

import json
import os
from datetime import datetime
from pathlib import Path

print("\n" + "="*60)
print("📊 VERIFICA AGGIORNAMENTI AUTOMATICI")
print("="*60 + "\n")

# 1. Analizza automation_status.json
automation_log = Path("logs/automation_status.json")
if automation_log.exists():
    with open(automation_log) as f:
        lines = f.readlines()
    
    print("📋 ULTIMI 10 TASK AUTOMATICI:")
    print("-" * 60)
    for line in lines[-10:]:
        try:
            event = json.loads(line.strip())
            timestamp = event.get('timestamp', 'N/A')
            task = event.get('task', 'N/A')
            success = '✅' if event.get('success') else '❌'
            duration = event.get('duration', 0)
            
            if timestamp != 'N/A':
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp_str = dt.strftime('%d/%m %H:%M')
            else:
                timestamp_str = 'N/A'
            
            print(f"{success} {timestamp_str} - {task:25s} ({duration:6.2f}s)")
        except Exception as e:
            continue
    
    # Trova ultimo daily_data_update
    print("\n🔄 AGGIORNAMENTO DATI GIORNALIERO:")
    print("-" * 60)
    found = False
    for line in reversed(lines):
        try:
            event = json.loads(line.strip())
            if event.get('task') == 'daily_data_update':
                timestamp = event.get('timestamp', 'N/A')
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                result = event.get('result', '{}')
                print(f"  Ultimo aggiornamento: {dt.strftime('%d/%m/%Y %H:%M')}")
                
                # Parse result
                if isinstance(result, str):
                    try:
                        result_dict = eval(result)
                        print(f"  Partite aggiornate: {result_dict.get('matches_updated', 0)}")
                        print(f"  Squadre aggiornate: {result_dict.get('teams_updated', 0)}")
                        print(f"  Nuovi dati: {result_dict.get('new_data_points', 0)}")
                    except:
                        print(f"  Risultato: {result}")
                
                found = True
                break
        except:
            continue
    
    if not found:
        print("  ⚠️ Nessun aggiornamento dati trovato nei log")
else:
    print("❌ File automation_status.json non trovato")

# 2. Timestamp file dati
print("\n📁 TIMESTAMP FILE DATI:")
print("-" * 60)
data_files = [
    'data/dataset_features.csv',
    'data/dataset_pulito.csv',
    'data/I1_2526.csv',
    'data/I1_2425.csv'
]

for filepath in data_files:
    path = Path(filepath)
    if path.exists():
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        size_kb = path.stat().st_size / 1024
        giorni_fa = (datetime.now() - mtime).days
        
        status = "🟢" if giorni_fa <= 7 else "🟡" if giorni_fa <= 30 else "🔴"
        print(f"{status} {path.name:30s} - {mtime.strftime('%d/%m/%Y %H:%M')} ({giorni_fa}gg fa, {size_kb:.0f}KB)")
    else:
        print(f"❌ {filepath} - NON TROVATO")

# 3. Timestamp modelli ML
print("\n🤖 TIMESTAMP MODELLI ML:")
print("-" * 60)
models_dir = Path("models/enterprise")
if models_dir.exists():
    model_files = list(models_dir.glob("*.pkl"))
    if model_files:
        # Prendi il più recente
        latest = max(model_files, key=lambda p: p.stat().st_mtime)
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        giorni_fa = (datetime.now() - mtime).days
        
        status = "🟢" if giorni_fa <= 7 else "🟡" if giorni_fa <= 30 else "🔴"
        print(f"{status} Ultimo aggiornamento: {mtime.strftime('%d/%m/%Y %H:%M')} ({giorni_fa} giorni fa)")
        print(f"   File più recente: {latest.name}")
        print(f"   Totale modelli: {len(model_files)}")
    else:
        print("⚠️ Nessun modello trovato")
else:
    print("❌ Directory models/enterprise non trovata")

# 4. Backup recenti
print("\n💾 BACKUP AUTOMATICI:")
print("-" * 60)
backups_dir = Path("backups")
if backups_dir.exists():
    backup_dirs = sorted([d for d in backups_dir.iterdir() if d.is_dir()], 
                        key=lambda p: p.stat().st_mtime, reverse=True)
    
    if backup_dirs:
        print(f"  Totale backup: {len(backup_dirs)}")
        print(f"  Ultimi 5 backup:")
        for backup in backup_dirs[:5]:
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            giorni_fa = (datetime.now() - mtime).days
            print(f"    - {backup.name} ({giorni_fa} giorni fa)")
    else:
        print("⚠️ Nessun backup trovato")
else:
    print("❌ Directory backups non trovata")

# 5. Processi attivi
print("\n⚙️ PROCESSI AUTOMAZIONE:")
print("-" * 60)
import subprocess
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    automation_procs = [l for l in lines if 'automation_master' in l or 'aggiorna_automatico' in l]
    automation_procs = [l for l in automation_procs if 'grep' not in l]
    
    if automation_procs:
        print("  ✅ Processi automazione attivi:")
        for proc in automation_procs:
            # Estrai solo info rilevanti
            parts = proc.split()
            if len(parts) > 10:
                print(f"    PID {parts[1]}: {' '.join(parts[10:13])}")
    else:
        print("  ⚠️ Nessun processo automazione attivo")
        print("  Nota: L'automazione potrebbe essere gestita da cron o essere inattiva")
except Exception as e:
    print(f"  ⚠️ Impossibile verificare processi: {e}")

# 6. Configurazione automazione
print("\n⚙️ CONFIGURAZIONE AUTOMAZIONE:")
print("-" * 60)
config_file = Path("config/automation_config.json")
if config_file.exists():
    with open(config_file) as f:
        config = json.load(f)
    
    print(f"  Aggiornamento giornaliero: {config.get('daily_update', 'N/A')}")
    print(f"  Riaddestramento settimanale: {config.get('weekly_retrain', 'N/A')}")
    print(f"  Rotazione backup: {config.get('backup_rotation', 'N/A')} giorni")
    print(f"  Health check: {config.get('health_check', 'N/A')}")
else:
    print("  ⚠️ File config/automation_config.json non trovato")

# 7. Sommario finale
print("\n" + "="*60)
print("📊 SOMMARIO")
print("="*60)

# Controlla se ci sono problemi
issues = []
warnings = []

# Dati vecchi?
dataset_features = Path('data/dataset_features.csv')
if dataset_features.exists():
    giorni_fa = (datetime.now() - datetime.fromtimestamp(dataset_features.stat().st_mtime)).days
    if giorni_fa > 7:
        issues.append(f"Dataset features non aggiornato da {giorni_fa} giorni")
    elif giorni_fa > 3:
        warnings.append(f"Dataset features non aggiornato da {giorni_fa} giorni")

# Modelli vecchi?
if models_dir.exists() and model_files:
    giorni_fa = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).days
    if giorni_fa > 30:
        issues.append(f"Modelli ML non aggiornati da {giorni_fa} giorni")
    elif giorni_fa > 14:
        warnings.append(f"Modelli ML non aggiornati da {giorni_fa} giorni")

# Backup vecchi?
if backups_dir.exists() and backup_dirs:
    giorni_fa = (datetime.now() - datetime.fromtimestamp(backup_dirs[0].stat().st_mtime)).days
    if giorni_fa > 7:
        warnings.append(f"Ultimo backup {giorni_fa} giorni fa")

if not issues and not warnings:
    print("✅ SISTEMA FUNZIONANTE")
    print("   Tutti gli aggiornamenti automatici sono operativi")
elif issues:
    print("❌ PROBLEMI RILEVATI:")
    for issue in issues:
        print(f"   - {issue}")
    if warnings:
        print("\n⚠️ AVVISI:")
        for warning in warnings:
            print(f"   - {warning}")
else:
    print("⚠️ AVVISI:")
    for warning in warnings:
        print(f"   - {warning}")
    print("\n💡 Suggerimento: Controlla i log per ulteriori dettagli")

print("\n" + "="*60 + "\n")
