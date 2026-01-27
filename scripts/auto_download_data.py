#!/usr/bin/env python3
"""
Script per download automatico dati Serie A da football-data.co.uk
Usato da GitHub Actions per aggiornamenti quotidiani
FIXED: Validazione date, stagione corretta, blocco corruzione
"""

import pandas as pd
import requests
from datetime import datetime
import sys

def download_and_merge():
    """Scarica dati aggiornati e merge con dataset esistente"""
    
    # Determina stagione corrente (2025-26 se siamo dopo agosto 2025)
    now = datetime.now()
    if now.month >= 8:
        season = f"{str(now.year)[2:]}{str(now.year + 1)[2:]}"  # es. 2526
    else:
        season = f"{str(now.year - 1)[2:]}{str(now.year)[2:]}"  # es. 2425
    
    url = f'https://www.football-data.co.uk/mmz4281/{season}/I1.csv'
    
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
        
        # VALIDAZIONE DATE: Converti e verifica
        try:
            df_old['Date'] = pd.to_datetime(df_old['Date'], format='%Y-%m-%d', errors='coerce')
            df_new['Date'] = pd.to_datetime(df_new['Date'], format='%d/%m/%Y', errors='coerce')
            
            # Rimuovi righe con date invalide
            df_old = df_old.dropna(subset=['Date'])
            df_new = df_new.dropna(subset=['Date'])
            
            # VALIDAZIONE: Ultima data del vecchio dataset
            last_date_old = df_old['Date'].max()
            first_date_new = df_new['Date'].min()
            last_date_new = df_new['Date'].max()
            
            print(f"📅 Date vecchio dataset: {df_old['Date'].min().date()} → {last_date_old.date()}")
            print(f"📅 Date nuovi dati: {first_date_new.date()} → {last_date_new.date()}")
            
            # BLOCCO: Se le date dei nuovi dati sono PRIMA dell'ultimo del vecchio
            if last_date_new < last_date_old:
                print(f"❌ CORRUZIONE RILEVATA: Nuovi dati hanno date VECCHIE!")
                print(f"   Ultimo vecchio: {last_date_old.date()}")
                print(f"   Ultimo nuovo: {last_date_new.date()}")
                print(f"   Merge BLOCCATO per prevenire corruzione")
                with open('update_info.txt', 'w') as f:
                    f.write("0")
                return 0
                
        except Exception as e:
            print(f"❌ Errore parsing date: {e}")
            with open('update_info.txt', 'w') as f:
                f.write("0")
            return 0
        
        # Merge ed eliminazione duplicati (SOLO se validazione OK)
        if 'Date' in df_old.columns and 'Date' in df_new.columns:
            # Formatta date uniform (YYYY-MM-DD)
            df_old['Date'] = df_old['Date'].dt.strftime('%Y-%m-%d')
            df_new['Date'] = df_new['Date'].dt.strftime('%Y-%m-%d')
            
            # SOLO nuove partite (non già presenti)
            df_merged = pd.concat([df_old, df_new], ignore_index=True)
            df_merged = df_merged.drop_duplicates(
                subset=['Date', 'HomeTeam', 'AwayTeam'], 
                keep='first'  # Mantieni versione vecchia (più affidabile)
            )
            
            # Ordina per data crescente
            df_merged = df_merged.sort_values('Date').reset_index(drop=True)
            
            records_new = len(df_merged)
            added = records_new - records_old
            
            # VALIDAZIONE: non accettare riduzioni massicce
            if added < -100:
                print(f"❌ Merge eliminerebbe {-added} partite! Operazione annullata.")
                with open('update_info.txt', 'w') as f:
                    f.write("0")
                return 0
            
            # VALIDAZIONE: Non accettare aggiunte troppo grandi (>100 in un giorno)
            if added > 100:
                print(f"⚠️  Aggiunte sospette: +{added} partite in un aggiornamento!")
                print(f"   Possibile duplicazione o errore. Merge BLOCCATO.")
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
