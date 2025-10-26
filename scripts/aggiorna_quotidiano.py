#!/usr/bin/env python3
"""
Script di aggiornamento quotidiano intelligente
Controlla se ci sono nuovi dati prima di aggiornare tutto
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
import subprocess

def controlla_nuovi_dati():
    """Controlla se ci sono nuovi dati disponibili online"""
    print("🔍 Controllo disponibilità nuovi dati...")
    
    try:
        # Scarica solo l'header del file per controllare la dimensione
        url = 'https://www.football-data.co.uk/mmz4281/2526/I1.csv'
        response = requests.head(url)
        response.raise_for_status()
        
        # Controlla la data di modifica dal server (se disponibile)
        if 'last-modified' in response.headers:
            server_date = response.headers['last-modified']
            print(f"📅 Ultima modifica server: {server_date}")
        
        # Controlla la dimensione del file
        if 'content-length' in response.headers:
            server_size = int(response.headers['content-length'])
            print(f"📏 Dimensione file server: {server_size} bytes")
            
            # Confronta con il file locale
            local_file = 'data/I1_2526.csv'
            if os.path.exists(local_file):
                local_size = os.path.getsize(local_file)
                print(f"📏 Dimensione file locale: {local_size} bytes")
                
                if server_size != local_size:
                    print("🆕 Rilevata differenza di dimensione - probabili nuovi dati!")
                    return True
                else:
                    print("✅ Dimensione uguale - nessun nuovo dato rilevato")
                    return False
            else:
                print("❓ File locale non trovato - download necessario")
                return True
        else:
            print("⚠️  Impossibile determinare dimensione server")
            return True
            
    except Exception as e:
        print(f"❌ Errore nel controllo: {e}")
        print("🔄 Procedo con l'aggiornamento per sicurezza")
        return True

def controlla_eta_dati():
    """Controlla quando sono stati aggiornati l'ultima volta i dati"""
    try:
        if os.path.exists('data/dataset_features.csv'):
            df = pd.read_csv('data/dataset_features.csv', parse_dates=['Date'])
            ultima_partita = df['Date'].max()
            giorni_fa = (datetime.now() - ultima_partita).days
            
            print(f"🗓️  Ultima partita nelle features: {ultima_partita.strftime('%d/%m/%Y')}")
            print(f"⏰ {giorni_fa} giorni fa")
            
            # Se l'ultima partita è più vecchia di 3 giorni, aggiorna
            if giorni_fa > 3:
                print("⚠️  Dati troppo vecchi - aggiornamento necessario")
                return True
            else:
                print("✅ Dati abbastanza recenti")
                return False
        else:
            print("❓ File features non trovato - aggiornamento necessario")
            return True
            
    except Exception as e:
        print(f"❌ Errore nel controllo età: {e}")
        return True

def aggiornamento_rapido():
    """Esegue solo l'aggiornamento essenziale senza riqualificare i modelli"""
    print("\n🚀 AGGIORNAMENTO RAPIDO")
    print("=" * 40)
    
    success = 0
    
    # Solo dati e features, non modelli
    scripts = [
        ('scripts/aggiorna_stagione_corrente.py', 'Aggiorna dati stagione corrente'),
        ('scripts/analizza_dati.py', 'Ricrea dataset pulito'),
        ('scripts/feature_engineering.py', 'Rigenera features')
    ]
    
    for script, desc in scripts:
        print(f"\n🔄 {desc}...")
        try:
            result = subprocess.run([sys.executable, script], 
                                  capture_output=True, text=True, check=True)
            print("✅ Completato")
            success += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ Errore: {e}")
            return False
    
    return success == len(scripts)

def main():
    """Processo principale intelligente"""
    
    print("🤖 AGGIORNAMENTO QUOTIDIANO INTELLIGENTE")
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    # Vai nella directory corretta
    os.chdir('/Users/cosimomassaro/Desktop/pronostici_calcio')
    
    # Controlla se servono aggiornamenti
    nuovi_dati = controlla_nuovi_dati()
    dati_vecchi = controlla_eta_dati()
    
    if nuovi_dati or dati_vecchi:
        print("\n🔄 Aggiornamento necessario!")
        
        # Chiedi se fare aggiornamento completo o rapido
        print("\nOpzioni:")
        print("1. 🚀 Aggiornamento RAPIDO (solo dati e features)")
        print("2. 🎯 Aggiornamento COMPLETO (include riqualifica modelli)")
        print("3. ❌ Salta aggiornamento")
        
        scelta = input("\nScegli (1/2/3): ").strip()
        
        if scelta == "1":
            if aggiornamento_rapido():
                print("\n🎉 Aggiornamento rapido completato!")
            else:
                print("\n💥 Aggiornamento rapido fallito")
        elif scelta == "2":
            print("\n🎯 Avvio aggiornamento completo...")
            subprocess.run([sys.executable, 'scripts/aggiorna_tutto.py'])
        else:
            print("\n⏭️  Aggiornamento saltato")
    else:
        print("\n✅ Nessun aggiornamento necessario")
        print("📊 I dati sono già aggiornati")

if __name__ == "__main__":
    main()