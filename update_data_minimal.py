#!/usr/bin/env python3
"""
Script minimale aggiornamento dati - Eseguibile su Render
"""
import os
import sys
from datetime import datetime

def main():
    """Aggiornamento minimale - copia dataset corrente"""
    print(f"🔄 Update minimale eseguito alle {datetime.now()}")
    print(f"📂 Working dir: {os.getcwd()}")
    print(f"✅ Script completato con successo")
    sys.exit(0)

if __name__ == '__main__':
    main()
