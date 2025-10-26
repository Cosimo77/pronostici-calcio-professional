#!/usr/bin/env python3
"""
⚡ AGGIORNAMENTO RAPIDO - VERSIONE SEMPLICE
Script veloce che aggiorna tutto senza dipendenze complesse
"""

import os
import sys
import subprocess
import glob
from datetime import datetime
import time

def print_step(step_num, description):
    """Stampa step corrente"""
    print(f"\n🔄 STEP {step_num}: {description}")
    print("-" * 40)

def run_simple_command(command, description):
    """Esegue comando semplice"""
    print(f"💻 {description}...")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completato")
            if result.stdout.strip():
                # Mostra solo le ultime righe per brevità
                lines = result.stdout.strip().split('\n')
                for line in lines[-3:]:
                    if line.strip():
                        print(f"   {line}")
            return True
        else:
            print(f"❌ {description} fallito")
            if result.stderr:
                print(f"   Errore: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"💥 Errore: {e}")
        return False

def main():
    """Aggiornamento rapido"""
    print("⚡ AGGIORNAMENTO RAPIDO SISTEMA PRONOSTICI")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    success = 0
    
    # Step 1: Aggiorna dati
    print_step(1, "Aggiornamento dati Serie A")
    if run_simple_command("python3 scripts/aggiorna_quotidiano.py", "Download nuovi dati"):
        success += 1
    
    # Step 2: Rigenera features
    print_step(2, "Rigenerazione features ML")
    if run_simple_command("python3 scripts/feature_engineering.py", "Creazione features"):
        success += 1
    
    # Step 3: Riaddestra modelli
    print_step(3, "Riaddestramento modelli ML")
    if run_simple_command("python3 scripts/modelli_predittivi.py", "Training modelli"):
        success += 1
    
    # Step 4: Pulizia cache
    print_step(4, "Pulizia cache")
    try:
        cache_files = glob.glob("cache/*.json")
        for file in cache_files:
            os.remove(file)
        print(f"✅ Cache pulita: {len(cache_files)} file rimossi")
        success += 1
    except Exception as e:
        print(f"⚠️  Errore pulizia cache: {e}")
    
    # Riepilogo
    print("\n" + "="*50)
    print(f"📊 COMPLETATI: {success}/4 step")
    
    if success == 4:
        print("🎉 TUTTO AGGIORNATO CON SUCCESSO!")
        print("🚀 Il sistema è pronto per nuove predizioni")
    else:
        print("⚠️  Aggiornamento parziale")
    
    print("\n💡 Prossimo aggiornamento: lunedì prossimo")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interrotto")
    except Exception as e:
        print(f"💥 Errore: {e}")