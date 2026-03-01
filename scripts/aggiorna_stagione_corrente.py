#!/usr/bin/env python3
"""
Script per scaricare dati aggiornati stagione corrente Serie A
Chiamato da aggiorna_automatico.py
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# Determina stagione corrente
now = datetime.now()
if now.month >= 8:  # Da agosto in poi è la nuova stagione
    season = f"{str(now.year)[2:]}{str(now.year + 1)[2:]}"
else:  # Prima di agosto è ancora la stagione passata
    season = f"{str(now.year - 1)[2:]}{str(now.year)[2:]}"

URL = f'https://www.football-data.co.uk/mmz4281/{season}/I1.csv'
OUTPUT_FILE = f'data/I1_{season}.csv'

def download_stagione_corrente():
    """Scarica CSV stagione corrente"""
    print(f"📥 Download Serie A stagione {season}...")
    print(f"   URL: {URL}")
    
    try:
        # Download
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        
        # Salva
        os.makedirs('data', exist_ok=True)
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(response.content)
        
        # Verifica
        df = pd.read_csv(OUTPUT_FILE)
        num_partite = len(df)
        
        if 'Date' in df.columns:
            ultima_data = df['Date'].iloc[-1] if len(df) > 0 else 'N/A'
            print(f"✅ Download completato: {num_partite} partite")
            print(f"   Ultima partita: {ultima_data}")
        else:
            print(f"✅ Download completato: {num_partite} righe")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore download: {e}")
        return False

if __name__ == "__main__":
    success = download_stagione_corrente()
    sys.exit(0 if success else 1)
