#!/usr/bin/env python3
"""
Script di aggiornamento quotidiano AUTOMATICO (non-interattivo)
Per uso con cron/automation - esegue aggiornamento rapido se necessario
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aggiornamento_auto.log'),
        logging.StreamHandler()
    ]
)

def controlla_nuovi_dati():
    """Controlla se ci sono nuovi dati disponibili online"""
    logging.info("🔍 Controllo disponibilità nuovi dati...")
    
    try:
        # Scarica solo l'header del file per controllare la dimensione
        url = 'https://www.football-data.co.uk/mmz4281/2526/I1.csv'
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        
        # Controlla la data di modifica dal server (se disponibile)
        if 'last-modified' in response.headers:
            server_date = response.headers['last-modified']
            logging.info(f"📅 Ultima modifica server: {server_date}")
        
        # Controlla la dimensione del file
        if 'content-length' in response.headers:
            server_size = int(response.headers['content-length'])
            logging.info(f"📏 Dimensione file server: {server_size} bytes")
            
            # Confronta con il file locale
            local_file = 'data/I1_2526.csv'
            if os.path.exists(local_file):
                local_size = os.path.getsize(local_file)
                logging.info(f"📏 Dimensione file locale: {local_size} bytes")
                
                if server_size != local_size:
                    logging.info("🆕 Rilevata differenza di dimensione - probabili nuovi dati!")
                    return True
                else:
                    logging.info("✅ Dimensione uguale - nessun nuovo dato rilevato")
                    return False
            else:
                logging.info("❓ File locale non trovato - download necessario")
                return True
        else:
            logging.warning("⚠️  Impossibile determinare dimensione server")
            return True
            
    except Exception as e:
        logging.error(f"❌ Errore nel controllo: {e}")
        logging.info("🔄 Procedo con l'aggiornamento per sicurezza")
        return True

def controlla_eta_dati():
    """Controlla quando sono stati aggiornati l'ultima volta i dati"""
    try:
        if os.path.exists('data/dataset_features.csv'):
            df = pd.read_csv('data/dataset_features.csv', parse_dates=['Date'])
            ultima_partita = df['Date'].max()
            giorni_fa = (datetime.now() - ultima_partita).days
            
            logging.info(f"🗓️  Ultima partita nelle features: {ultima_partita.strftime('%d/%m/%Y')}")
            logging.info(f"⏰ {giorni_fa} giorni fa")
            
            # Se l'ultima partita è più vecchia di 3 giorni, aggiorna
            if giorni_fa > 3:
                logging.warning("⚠️  Dati troppo vecchi - aggiornamento necessario")
                return True
            else:
                logging.info("✅ Dati abbastanza recenti")
                return False
        else:
            logging.warning("❓ File features non trovato - aggiornamento necessario")
            return True
            
    except Exception as e:
        logging.error(f"❌ Errore nel controllo età: {e}")
        return True

def controlla_ultima_esecuzione():
    """Verifica quando è stato eseguito l'ultimo aggiornamento"""
    status_file = 'logs/automation_status.json'
    try:
        if os.path.exists(status_file):
            import json
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            last_update = status.get('last_daily_update', None)
            if last_update:
                last_time = datetime.fromisoformat(last_update)
                ore_fa = (datetime.now() - last_time).total_seconds() / 3600
                
                logging.info(f"🕐 Ultimo aggiornamento: {ore_fa:.1f} ore fa")
                
                # Evita di aggiornare più di una volta ogni 6 ore
                if ore_fa < 6:
                    logging.info("⏸️  Troppo presto per nuovo aggiornamento (min 6 ore)")
                    return False
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Errore verifica ultima esecuzione: {e}")
        return True

def aggiornamento_rapido():
    """Esegue solo l'aggiornamento essenziale senza riqualificare i modelli"""
    logging.info("\n🚀 AGGIORNAMENTO RAPIDO AUTOMATICO")
    logging.info("=" * 50)
    
    success = 0
    
    # Solo dati e features, non modelli
    scripts = [
        ('scripts/aggiorna_stagione_corrente.py', 'Aggiorna dati stagione corrente'),
        ('scripts/analizza_dati.py', 'Ricrea dataset pulito'),
        ('scripts/feature_engineering.py', 'Rigenera features')
    ]
    
    for script, desc in scripts:
        logging.info(f"\n🔄 {desc}...")
        try:
            result = subprocess.run(
                [sys.executable, script], 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=300  # 5 minuti max per script
            )
            logging.info("✅ Completato")
            if result.stdout:
                logging.debug(result.stdout)
            success += 1
        except subprocess.TimeoutExpired:
            logging.error(f"❌ Timeout: {script} ha impiegato troppo tempo")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Errore in {script}: {e}")
            if e.stderr:
                logging.error(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            logging.error(f"❌ Errore imprevisto: {e}")
            return False
    
    return success == len(scripts)

def aggiorna_status_automation():
    """Aggiorna il file di status dell'automazione"""
    try:
        import json
        status_file = 'logs/automation_status.json'
        
        status = {}
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status = json.load(f)
        
        status['last_daily_update'] = datetime.now().isoformat()
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logging.info("✅ Status automazione aggiornato")
        
    except Exception as e:
        logging.error(f"❌ Errore aggiornamento status: {e}")

def main():
    """Processo principale automatico (non-interattivo)"""
    
    logging.info("🤖 AGGIORNAMENTO QUOTIDIANO AUTOMATICO")
    logging.info(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logging.info("=" * 60)
    
    # Vai nella directory corretta
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    logging.info(f"📂 Working directory: {os.getcwd()}")
    
    # Crea directory logs se non esiste
    os.makedirs('logs', exist_ok=True)
    
    # 1. Controlla se è passato abbastanza tempo dall'ultimo aggiornamento
    if not controlla_ultima_esecuzione():
        logging.info("⏭️  Aggiornamento saltato (troppo presto)")
        return 0
    
    # 2. Controlla se servono aggiornamenti
    nuovi_dati = controlla_nuovi_dati()
    dati_vecchi = controlla_eta_dati()
    
    if nuovi_dati or dati_vecchi:
        logging.info("\n🔄 Aggiornamento necessario - AVVIO AUTOMATICO")
        
        # Esegue SEMPRE aggiornamento rapido in modalità automatica
        if aggiornamento_rapido():
            logging.info("\n🎉 Aggiornamento rapido completato con successo!")
            aggiorna_status_automation()
            return 0
        else:
            logging.error("\n💥 Aggiornamento rapido fallito")
            return 1
    else:
        logging.info("\n✅ Nessun aggiornamento necessario")
        logging.info("📊 I dati sono già aggiornati")
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logging.error(f"💥 ERRORE FATALE: {e}", exc_info=True)
        sys.exit(1)
