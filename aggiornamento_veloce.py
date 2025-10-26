#!/usr/bin/env python3
"""
⚠️  SCRIPT DEPRECATO - REINDIRIZZAMENTO A DATI REALI
Questo script ora punta all'aggiornamento con dati reali
"""

import os
import sys
import subprocess

def main():
    """Reindirizza all'aggiornamento dati reali"""
    print("⚠️  AVVISO: aggiornamento_veloce.py è DEPRECATO")
    print("🔄 Reindirizzamento a aggiornamento DATI REALI...")
    print("=" * 60)
    
    # Lancia aggiornamento dati reali
    try:
        cmd = [sys.executable, "aggiornamento_dati_reali.py"]
        
        # Passa automaticamente opzione 1 (dati reali)
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, text=True)
        
        # Invia "1" per dati reali
        stdout, _ = process.communicate(input="1\n")
        
        print(stdout)
        
        if process.returncode == 0:
            print("\n✅ AGGIORNAMENTO COMPLETATO CON DATI REALI!")
        else:
            print("\n❌ Errore durante l'aggiornamento")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()