#!/usr/bin/env python3
"""
Script per download automatico dati Serie A da football-data.co.uk
Usato da GitHub Actions per aggiornamenti quotidiani
"""

import pandas as pd
import requests
from datetime import datetime
import sys

def download_and_merge():
    """Scarica dati aggiornati e merge con dataset esistente"""
    
    # URL dataset Serie A 2024-25
    url = 'https://www.football-data.co.uk/mmz4281/2425/I1.csv'
    
    try:
        print(f"📡 Download da {url}...")
        
        # Download dati aggiornati
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Salva temporaneamente
        with open('I1_new.csv', 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Download completato: {len(response.content)} bytes")
        
        # Carica dataset esistente
        df_old = pd.read_csv('data/dataset_pulito.csv')
        records_old = len(df_old)
        print(f"📊 Dataset esistente: {records_old} partite")
        
        # Carica nuovi dati
        df_new = pd.read_csv('I1_new.csv')
        print(f"📊 Nuovi dati: {len(df_new)} partite")
        
        # Merge ed eliminazione duplicati
        if 'Date' in df_old.columns and 'Date' in df_new.columns:
            df_merged = pd.concat([df_old, df_new], ignore_index=True)
            df_merged = df_merged.drop_duplicates(
                subset=['Date', 'HomeTeam', 'AwayTeam'], 
                keep='last'
            )
            
            # Salva dataset aggiornato
            df_merged.to_csv('data/dataset_pulito.csv', index=False)
            
            records_new = len(df_merged)
            added = records_new - records_old
            
            print(f"✅ Dataset aggiornato: {records_old} → {records_new} (+{added} partite)")
            
            # Scrivi numero partite aggiunte per GitHub Actions
            with open('update_info.txt', 'w') as f:
                f.write(f"{added}")
            
            return added
        else:
            print("❌ Colonna Date non trovata nei dataset")
            with open('update_info.txt', 'w') as f:
                f.write("0")
            return 0
            
    except Exception as e:
        print(f"❌ Errore: {e}", file=sys.stderr)
        with open('update_info.txt', 'w') as f:
            f.write("0")
        return 0

if __name__ == '__main__':
    added = download_and_merge()
    sys.exit(0 if added >= 0 else 1)
