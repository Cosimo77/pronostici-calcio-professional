#!/usr/bin/env python3
"""
Script GitHub Actions-Friendly per download automatico dati
Nessun path assoluto, compatibile con CI/CD
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime

def download_serie_a_data():
    """Scarica dati Serie A dalla stagione corrente"""
    print("🔄 Download dati Serie A in corso...")
    
    # Determina stagione corrente (es: 2025-26)
    now = datetime.now()
    if now.month >= 8:
        year1 = now.year % 100
        year2 = (now.year + 1) % 100
    else:
        year1 = (now.year - 1) % 100
        year2 = now.year % 100
    
    season_code = f"{year1:02d}{year2:02d}"
    
    # URL football-data.co.uk
    url = f"https://www.football-data.co.uk/mmz4281/{season_code}/I1.csv"
    
    print(f"📊 Stagione: 20{year1}-{year2}")
    print(f"🌐 URL: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Salva CSV
        output_path = f"data/I1_{season_code}.csv"
        os.makedirs("data", exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        # Conta partite
        df = pd.read_csv(output_path)
        partite_count = len(df)
        
        print(f"✅ Download completato: {partite_count} partite")
        
        # Controlla se ci sono nuove partite rispetto al dataset esistente
        if os.path.exists('data/dataset_features.csv'):
            df_old = pd.read_csv('data/dataset_features.csv', parse_dates=['Date'])
            ultima_partita_old = df_old['Date'].max()
            
            df_new = pd.read_csv(output_path)
            df_new['Date'] = pd.to_datetime(df_new['Date'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
            ultima_partita_new = df_new['Date'].max()
            
            if pd.notna(ultima_partita_new) and pd.notna(ultima_partita_old):
                if ultima_partita_new > ultima_partita_old:
                    nuove_partite = len(df_new[df_new['Date'] > ultima_partita_old])
                    print(f"🆕 Nuove partite: {nuove_partite}")
                    
                    # Scrivi info per commit message
                    with open('update_info.txt', 'w') as f:
                        f.write(str(nuove_partite))
                    
                    return True
                else:
                    print("ℹ️  Nessuna nuova partita dal dataset esistente")
                    with open('update_info.txt', 'w') as f:
                        f.write('0')
                    return False
            else:
                print("⚠️  Warning: Date parsing issues, assuming update needed")
                with open('update_info.txt', 'w') as f:
                    f.write(str(partite_count))
                return True
        else:
            # Primo download, considera tutto come nuovo
            print(f"🆕 Primo download: tutte le {partite_count} partite sono nuove")
            with open('update_info.txt', 'w') as f:
                f.write(str(partite_count))
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore download: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore inatteso: {e}")
        sys.exit(1)

def main():
    """Entry point script"""
    print("=" * 60)
    print("🤖 AUTO-DOWNLOAD DATI SERIE A")
    print("=" * 60)
    
    try:
        has_updates = download_serie_a_data()
        
        if has_updates:
            print("\n✅ Dati aggiornati con successo")
            sys.exit(0)
        else:
            print("\n✅ Dati già aggiornati")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
