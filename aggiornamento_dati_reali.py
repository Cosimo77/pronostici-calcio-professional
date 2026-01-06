#!/usr/bin/env python3
"""
📡 AGGIORNAMENTO DATI REALI
Scarica dati veri da fonti online per aggiornamento professionale
"""

import os
import sys
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json

def print_step(step, message):
    """Print formattato per i passi"""
    print(f"📡 {step}/4: {message}")

def scarica_dati_reali():
    """Scarica dati reali da fonti online"""
    
    print("📡 AGGIORNAMENTO CON DATI REALI")
    print("=" * 50)
    
    # Step 1: Carica dataset esistente
    print_step(1, "Caricamento dataset esistente...")
    
    if not os.path.exists('data/dataset_features.csv'):
        print("❌ Dataset non trovato!")
        return False
    
    df = pd.read_csv('data/dataset_features.csv')
    original_size = len(df)
    print(f"   📊 Dataset esistente: {original_size} partite")
    
    # Step 2: Scraping dati reali
    print_step(2, "Download dati reali da fonti online...")
    
    new_data = []
    
    try:
        # Fonte 1: Football-data.co.uk (CSV Serie A 2024-25)
        print("   🔗 Tentativo download da football-data.co.uk...")
        
        # URL Serie A stagione corrente 2025-26
        url_serie_a = "https://www.football-data.co.uk/mmz4281/2526/I1.csv"
        response = requests.get(url_serie_a, timeout=15)
        
        if response.status_code == 200:
            # Salva file temporaneo
            with open('temp_serie_a_2526.csv', 'wb') as f:
                f.write(response.content)
            
            # Carica e processa
            df_new = pd.read_csv('temp_serie_a_2526.csv')
            print(f"   ✅ Scaricate {len(df_new)} partite Serie A 2024-25")
            
            # Pulizia e standardizzazione
            if not df_new.empty:
                # Rinomina colonne per compatibilità
                column_mapping = {
                    'Date': 'Date',
                    'HomeTeam': 'HomeTeam', 
                    'AwayTeam': 'AwayTeam',
                    'FTHG': 'FTHG',
                    'FTAG': 'FTAG', 
                    'FTR': 'FTR',
                    'HTHG': 'HTHG',
                    'HTAG': 'HTAG',
                    'HTR': 'HTR'
                }
                
                # Mantieni solo colonne che esistono
                available_cols = [col for col in column_mapping.keys() if col in df_new.columns]
                df_new = df_new[available_cols].copy()
                
                # Converti data
                df_new['Date'] = pd.to_datetime(df_new['Date'], dayfirst=True)
                df_new['Date'] = df_new['Date'].dt.strftime('%Y-%m-%d')
                
                # Aggiungi features di base (compatibili con dataset esistente)
                for col in df.columns:
                    if col not in df_new.columns:
                        if 'prob' in col.lower():
                            df_new[col] = 0.33  # Valore neutro
                        elif col.startswith('B365'):
                            df_new[col] = 2.0   # Quote neutre
                        else:
                            df_new[col] = 0     # Valore di default
                
                new_data.append(df_new)
            
            # Rimuovi file temporaneo
            os.remove('temp_serie_a_2526.csv')
        
    except Exception as e:
        print(f"   ⚠️ Errore download football-data.co.uk: {e}")
    
    # Fonte 2: API alternative (se disponibili)
    try:
        print("   🔗 Tentativo API alternative...")
        # Placeholder per altre API
        print("   ℹ️ API alternative non configurate (richiede API key)")
        
    except Exception as e:
        print(f"   ⚠️ Errore API alternative: {e}")
    
    # Step 3: Integrazione dati
    print_step(3, "Integrazione nuovi dati reali...")
    
    if new_data:
        # Combina tutti i nuovi dati
        df_combined = pd.concat(new_data, ignore_index=True)
        
        # Rimuovi duplicati con dataset esistente
        df_existing_dates = set(zip(df['Date'], df['HomeTeam'], df['AwayTeam']))
        
        # Filtra solo partite nuove
        mask = ~df_combined.apply(
            lambda row: (row['Date'], row['HomeTeam'], row['AwayTeam']) in df_existing_dates, 
            axis=1
        )
        df_new_only = df_combined[mask]
        
        if not df_new_only.empty:
            # Merge con dataset esistente
            df_updated = pd.concat([df, df_new_only], ignore_index=True)
            
            # Ordina per data
            df_updated['Date'] = pd.to_datetime(df_updated['Date'])
            df_updated = df_updated.sort_values('Date')
            df_updated['Date'] = df_updated['Date'].dt.strftime('%Y-%m-%d')
            
            print(f"   📈 Aggiunte {len(df_new_only)} partite reali nuove")
            print(f"   📊 Dataset aggiornato: {len(df_updated)} partite totali")
        else:
            df_updated = df
            print("   ℹ️ Nessuna partita nuova trovata")
    else:
        df_updated = df
        print("   ⚠️ Nessun dato nuovo scaricato")
    
    # Step 4: Salvataggio
    print_step(4, "Salvataggio dataset aggiornato...")
    
    # Backup
    backup_file = f"data/dataset_backup_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(backup_file, index=False)
    
    # Salva aggiornato
    df_updated.to_csv('data/dataset_features.csv', index=False)
    df_updated.to_csv('data/dataset_pulito.csv', index=False)
    
    # Summary
    new_matches = len(df_updated) - original_size
    
    print("=" * 50)
    print("✅ AGGIORNAMENTO REALE COMPLETATO!")
    print("=" * 50)
    print(f"📊 Partite totali: {len(df_updated)}")
    print(f"📈 Nuove partite REALI: +{new_matches}")
    print(f"📅 Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"💾 Backup salvato: {backup_file}")
    
    if new_matches > 0:
        print("🎉 DATI REALI AGGIUNTI CON SUCCESSO!")
    else:
        print("ℹ️ Nessun nuovo dato disponibile al momento")
    
    return True

def main():
    """Funzione principale"""
    print("🎯 SCEGLI TIPO DI AGGIORNAMENTO:")
    print("=" * 40)
    print("1. 📡 DATI REALI (da internet)")
    print("2. ⚡ DATI SIMULATI (veloce)")
    print("3. ❌ Annulla")
    
    choice = input("\nScegli opzione (1-3): ").strip()
    
    if choice == "1":
        print("\n🌐 AVVIO DOWNLOAD DATI REALI...")
        scarica_dati_reali()
    elif choice == "2":
        print("\n⚡ Usa: python aggiornamento_veloce.py")
    else:
        print("❌ Operazione annullata")

if __name__ == "__main__":
    main()