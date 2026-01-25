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
        
        # VALIDAZIONE: verifica che i nuovi dati siano ragionevoli
        if len(df_new) < 50 or len(df_new) > 500:
            print(f"⚠️  Nuovi dati sospetti: {len(df_new)} partite (atteso 100-400)")
            with open('update_info.txt', 'w') as f:
                f.write("0")
            return 0
        
        # VALIDAZIONE: verifica colonne essenziali
        required_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
        missing_cols = [col for col in required_cols if col not in df_new.columns]
        if missing_cols:
            print(f"❌ Colonne mancanti nei nuovi dati: {missing_cols}")
            with open('update_info.txt', 'w') as f:
                f.write("0")
            return 0
        
        # Merge ed eliminazione duplicati
        if 'Date' in df_old.columns and 'Date' in df_new.columns:
            # SOLO nuove partite (non già presenti)
            df_merged = pd.concat([df_old, df_new], ignore_index=True)
            df_merged = df_merged.drop_duplicates(
                subset=['Date', 'HomeTeam', 'AwayTeam'], 
                keep='first'  # Mantieni versione vecchia (più affidabile)
            )
            
            records_new = len(df_merged)
            added = records_new - records_old
            
            # VALIDAZIONE: non accettare riduzioni massicce
            if added < -100:
                print(f"❌ Merge eliminerebbe {-added} partite! Operazione annullata.")
                with open('update_info.txt', 'w') as f:
                    f.write("0")
                return 0
            
            # Salva SOLO se ci sono aggiunte effettive
            if added > 0:
                df_merged.to_csv('data/dataset_pulito.csv', index=False)
                # Aggiorna anche dataset_features
                df_merged.to_csv('data/dataset_features.csv', index=False)
                print(f"✅ Dataset aggiornato: {records_old} → {records_new} (+{added} partite)")
            else:
                print(f"ℹ️  Nessuna partita nuova trovata")
            
            # Scrivi numero partite aggiunte per GitHub Actions
            with open('update_info.txt', 'w') as f:
                f.write(f"{max(0, added)}")
            
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
