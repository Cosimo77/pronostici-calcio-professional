#!/usr/bin/env python3
"""
🚀 LAUNCHER SISTEMA PROFESSIONALE
Script unificato per avviare il sistema completo

Uso:
  python3 RUN_SISTEMA_PROFESSIONALE.py
"""

import os
import sys
import time
import subprocess
import signal
import json
from datetime import datetime

def print_logo():
    """Logo del sistema professionale"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ⚽ SISTEMA PRONOSTICI CALCIO PROFESSIONALE v2.0 ⚽         ║
║                                                               ║
║    🎯 Sistema Deterministico • 100% Affidabile               ║
║    🔬 Machine Learning Avanzato • Predizioni Coerenti        ║
║    📊 Analisi Multimercato • Validazione Matematica         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

def check_requirements():
    """Verifica requisiti sistema"""
    print("🔍 Verifica requisiti sistema...")
    
    # Verifica Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ richiesto")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}")
    
    # Verifica file critici
    file_critici = [
        'web/app_professional.py',
        'config.json',
        'requirements.txt',
        'data/dataset_features.csv',
        'models/metadata.pkl'
    ]
    
    for file in file_critici:
        if not os.path.exists(file):
            print(f"❌ File mancante: {file}")
            return False
        print(f"✅ {file}")
    
    return True

def kill_existing_processes():
    """Termina processi esistenti"""
    print("🔄 Terminazione processi esistenti...")
    
    try:
        # Termina processi su porta 5001
        subprocess.run(['pkill', '-f', 'app_professional.py'], 
                      capture_output=True)
        subprocess.run(['lsof', '-ti:5001'], 
                      capture_output=True, 
                      stdout=subprocess.PIPE)
        time.sleep(2)
        print("✅ Processi terminati")
    except:
        print("⚠️  Nessun processo da terminare")

def start_professional_system():
    """Avvia sistema professionale"""
    print("🚀 Avvio Sistema Professionale...")
    
    # Cambia directory
    os.chdir('/Users/cosimomassaro/Desktop/pronostici_calcio')
    
    # Comando di avvio
    cmd = [
        'python3', 
        'web/app_professional.py'
    ]
    
    print(f"💻 Comando: {' '.join(cmd)}")
    print("🌐 Server: http://localhost:5001")
    print("📊 Dashboard disponibile dopo avvio")
    print("\n" + "="*50)
    print("🔄 AVVIO IN CORSO... (Ctrl+C per terminare)")
    print("="*50 + "\n")
    
    # Avvia processo
    try:
        process = subprocess.Popen(cmd)
        return process
    except KeyboardInterrupt:
        print("\n⚠️  Avvio interrotto dall'utente")
        return None
    except Exception as e:
        print(f"❌ Errore durante l'avvio: {e}")
        return None

def show_system_info():
    """Mostra informazioni sistema"""
    print("\n" + "="*50)
    print("📋 INFORMAZIONI SISTEMA")
    print("="*50)
    
    # Config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print(f"📊 Versione: {config['system']['version']}")
        print(f"🕐 Timezone: {config['system']['timezone']}")
        print(f"🔧 Debug: {config['system']['debug']}")
    except:
        pass
    
    # Modelli
    if os.path.exists('models'):
        models = [f for f in os.listdir('models') if f.endswith('.pkl')]
        print(f"🤖 Modelli: {len(models)} disponibili")
    
    # Dataset
    if os.path.exists('data'):
        datasets = [f for f in os.listdir('data') if f.endswith('.csv')]
        print(f"📈 Dataset: {len(datasets)} disponibili")
    
    print(f"🕐 Avviato: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*50)

def main():
    """Funzione principale"""
    try:
        print_logo()
        
        # Verifica requisiti
        if not check_requirements():
            print("\n❌ REQUISITI NON SODDISFATTI")
            print("🔧 Esegui prima l'installazione delle dipendenze")
            return 1
        
        # Termina processi esistenti
        kill_existing_processes()
        
        # Mostra info sistema
        show_system_info()
        
        # Avvia sistema
        process = start_professional_system()
        
        if process:
            try:
                # Attendi terminazione
                process.wait()
            except KeyboardInterrupt:
                print("\n⚠️  Sistema terminato dall'utente")
                process.terminate()
                process.wait()
                
        print("\n👋 Sistema terminato")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRORE CRITICO: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)