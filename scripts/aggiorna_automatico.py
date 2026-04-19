#!/usr/bin/env python3
"""
Script per automazione completa (cron job)
Controlla e aggiorna automaticamente senza input utente
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime
import subprocess
import logging

# Setup logging
log_file = '/Users/cosimomassaro/Desktop/pronostici_calcio/logs/aggiornamento_auto.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def should_update():
    """Determina se è necessario un aggiornamento"""
    logging.info("🔍 Controllo necessità aggiornamento...")
    
    try:
        # SEMPRE tenta download - lascia che lo script di download decida se c'è nuova partita
        # La logica vecchia era troppo conservativa e skippava download anche con nuovi dati
        
        # Controlla età delle features solo per logging
        if os.path.exists('data/dataset_features.csv'):
            df = pd.read_csv('data/dataset_features.csv', parse_dates=['Date'])
            ultima_partita = df['Date'].max()
            giorni_fa = (datetime.now() - ultima_partita).days
            
            logging.info(f"📅 Ultima partita nel dataset: {ultima_partita.strftime('%d/%m/%Y')} ({giorni_fa} giorni fa)")
        
        # SEMPRE ritorna True per forzare controllo nuovi dati
        logging.info("✅ Eseguo controllo nuovi dati da football-data.co.uk")
        return True
            
    except Exception as e:
        logging.error(f"❌ Errore nel controllo: {e}")
        return True

def run_update():
    """Esegue l'aggiornamento automatico"""
    logging.info("🚀 Avvio aggiornamento automatico...")
    
    # Vai nella directory corretta
    os.chdir('/Users/cosimomassaro/Desktop/pronostici_calcio')
    
    steps = [
        ('scripts/aggiorna_stagione_corrente.py', 'Aggiornamento dati stagione'),
        ('scripts/aggiorna_risultati_pending.py', 'Aggiornamento risultati predizioni pending'),
        ('scripts/analizza_dati.py', 'Creazione dataset pulito'),
        ('scripts/feature_engineering.py', 'Generazione features')
    ]
    
    success_count = 0
    
    for script, description in steps:
        logging.info(f"🔄 {description}...")
        try:
            result = subprocess.run([sys.executable, script], 
                                  capture_output=True, text=True, check=True)
            logging.info(f"✅ {description} completato")
            success_count += 1
            
            # Log solo le parti importanti dell'output
            if "partite" in result.stdout.lower():
                for line in result.stdout.split('\n'):
                    if 'partite' in line.lower() or 'ultima partita' in line.lower():
                        logging.info(f"📊 {line.strip()}")
                        
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Errore in {script}: {e}")
            if e.stdout:
                logging.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                logging.error(f"STDERR: {e.stderr}")
    
    # Riqualifica modelli solo se è domenica sera o se richiesto esplicitamente
    oggi = datetime.now().weekday()
    ora = datetime.now().hour
    
    if oggi == 6 and ora >= 20:  # Domenica sera
        logging.info("🤖 Domenica sera - riqualifica modelli...")
        try:
            result = subprocess.run([sys.executable, 'scripts/modelli_predittivi.py'], 
                                  capture_output=True, text=True, check=True)
            logging.info("✅ Modelli riqualificati")
            success_count += 1
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Errore riqualifica modelli: {e}")
    
    return success_count

def main():
    """Processo principale automatico"""
    
    logging.info("="*60)
    logging.info("🤖 AGGIORNAMENTO AUTOMATICO AVVIATO")
    logging.info("="*60)
    
    try:
        if should_update():
            success = run_update()
            if success >= 4:  # Almeno i 4 step base (era 3)
                logging.info("🎉 Aggiornamento automatico completato con successo!")
            else:
                logging.warning(f"⚠️  Aggiornamento parziale: {success} step completati")
        else:
            logging.info("✅ Nessun aggiornamento necessario")
            
    except Exception as e:
        logging.error(f"💥 Errore critico: {e}")
        sys.exit(1)
    
    logging.info("🏁 Aggiornamento automatico terminato")

if __name__ == "__main__":
    main()