#!/usr/bin/env python3
"""
🚀 AGGIORNAMENTO COMPLETO - COMANDO UNICO
Script master che aggiorna tutto il sistema con un solo comando
"""

import os
import sys
import subprocess
import shutil
import glob
from datetime import datetime
import time

def print_header():
    """Stampa header dello script"""
    print("🚀 AGGIORNAMENTO COMPLETO SISTEMA PRONOSTICI")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🎯 Obiettivo: Aggiornare tutto in sequenza")
    print()

def step_banner(step_num, step_name):
    """Banner per ogni step"""
    print(f"\n{'='*20} STEP {step_num}: {step_name} {'='*20}")

def run_command(command, description, timeout=300):
    """Esegue un comando con output in tempo reale"""
    print(f"🔄 {description}...")
    print(f"💻 Comando: {command}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        # Esegui comando con output in tempo reale
        process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stampa output in tempo reale
        if process.stdout:
            for line in process.stdout:
                print(line.rstrip())
        
        process.wait()
        elapsed = time.time() - start_time
        
        if process.returncode == 0:
            print(f"✅ {description} completato in {elapsed:.1f}s")
            return True
        else:
            print(f"❌ {description} fallito (exit code: {process.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timeout dopo {timeout}s")
        process.kill()
        return False
    except Exception as e:
        print(f"💥 Errore durante {description}: {e}")
        return False

def cleanup_cache():
    """Pulisce la cache"""
    step_banner(4, "PULIZIA CACHE")
    
    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        print("📁 Directory cache non trovata, creazione...")
        os.makedirs(cache_dir)
        print("✅ Cache pulita (directory creata)")
        return True
    
    # File da rimuovere
    patterns = [
        "cache/*.json",
        "cache/*.log",
        "cache/*_status.json",
        "cache/predizioni_*"
    ]
    
    removed_count = 0
    for pattern in patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"🗑️  Rimosso: {file}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Errore rimozione {file}: {e}")
    
    print(f"✅ Cache pulita: {removed_count} file rimossi")
    return True

def restart_web_server():
    """Riavvia il server web se in esecuzione"""
    step_banner(5, "RIAVVIO SERVER WEB")
    
    print("🔍 Controllo server in esecuzione...")
    
    # Cerca processi Python con app.py
    try:
        result = subprocess.run(
            ["pgrep", "-f", "python.*app.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"📍 Trovati {len(pids)} processi server")
            
            for pid in pids:
                if pid.strip():
                    print(f"🛑 Fermando processo {pid}")
                    subprocess.run(["kill", "-TERM", pid.strip()])
            
            time.sleep(2)
            print("✅ Server fermato")
        else:
            print("ℹ️  Nessun server in esecuzione")
        
        # Opzionalmente riavvia il server
        restart = input("🚀 Vuoi riavviare il server web? (y/N): ").lower().strip()
        if restart == 'y':
            print("🌐 Avvio server web...")
            subprocess.Popen([sys.executable, "web/app.py"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print("✅ Server web avviato in background")
            print("🌍 Disponibile su: http://localhost:5003")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Errore gestione server: {e}")
        return True  # Non blocchiamo per questo

def main():
    """Funzione principale"""
    print_header()
    
    # Verifica di essere nella directory corretta
    if not os.path.exists("web/app.py"):
        print("❌ Errore: Esegui lo script dalla directory principale del progetto")
        print("💡 Uso: cd /Users/cosimomassaro/Desktop/pronostici_calcio && python3 aggiorna_tutto_completo.py")
        sys.exit(1)
    
    success_count = 0
    total_steps = 5
    
    # STEP 1: Aggiornamento dati automatico
    step_banner(1, "AGGIORNAMENTO DATI")
    if run_command("python3 automation_master.py --auto", "Aggiornamento dati automatico"):
        success_count += 1
    else:
        # Fallback con script quotidiano
        print("🔄 Fallback: uso script quotidiano...")
        if run_command("python3 scripts/aggiorna_quotidiano.py", "Aggiornamento quotidiano"):
            success_count += 1
    
    # STEP 2: Rigenerazione features (se non fatto da automation_master)
    step_banner(2, "RIGENERAZIONE FEATURES")
    if run_command("python3 scripts/feature_engineering.py", "Rigenerazione features"):
        success_count += 1
    
    # STEP 3: Riaddestramento modelli ML
    step_banner(3, "RIADDESTRAMENTO MODELLI ML")
    if run_command("python3 scripts/modelli_predittivi.py", "Riaddestramento modelli"):
        success_count += 1
    
    # STEP 4: Pulizia cache
    if cleanup_cache():
        success_count += 1
    
    # STEP 5: Gestione server web
    if restart_web_server():
        success_count += 1
    
    # Riepilogo finale
    print("\n" + "="*60)
    print("📊 RIEPILOGO AGGIORNAMENTO COMPLETO")
    print("="*60)
    print(f"✅ Completati: {success_count}/{total_steps} step")
    print(f"📅 Tempo totale: {datetime.now().strftime('%H:%M:%S')}")
    
    if success_count == total_steps:
        print("🎉 AGGIORNAMENTO COMPLETATO CON SUCCESSO!")
        print("🚀 Il sistema è pronto con i dati più aggiornati")
    else:
        print("⚠️  Aggiornamento parziale - controlla i log sopra")
        
    print("\n💡 Prossimo aggiornamento consigliato: lunedì prossimo")
    print("🎯 Comando: python3 aggiorna_tutto_completo.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Aggiornamento interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Errore critico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)