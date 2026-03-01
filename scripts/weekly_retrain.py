#!/usr/bin/env python3
"""
Weekly Model Retraining - Eseguito Domenica 02:00
Riaddestra tutti i modelli ML con dati aggiornati
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Setup
BASE_DIR = Path(__file__).parent.parent
LOG_FILE = BASE_DIR / 'logs' / 'weekly_retrain.log'

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def run_training():
    """Esegue ritraining completo modelli"""
    logging.info("=" * 60)
    logging.info("🎯 WEEKLY MODEL RETRAINING")
    logging.info("=" * 60)
    
    try:
        # Verifica che esistano dati freschi
        dataset_path = BASE_DIR / 'data' / 'dataset_features.csv'
        if not dataset_path.exists():
            logging.error("❌ Dataset features non trovato")
            return False
        
        logging.info("📊 Dataset trovato, inizio training...")
        
        # Esegui script di training
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / 'scripts' / 'modelli_predittivi.py')],
            capture_output=True,
            text=True,
            check=True,
            timeout=1800  # 30 minuti max
        )
        
        # Log output
        for line in result.stdout.split('\n'):
            if line.strip() and any(keyword in line.lower() for keyword in ['accuracy', 'score', 'salvato', 'error', 'warning']):
                logging.info(f"   {line.strip()}")
        
        logging.info("✅ Ritraining completato con successo")
        return True
        
    except subprocess.TimeoutExpired:
        logging.error("❌ Timeout: training richiesto più di 30 minuti")
        return False
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Errore training: {e}")
        if e.stdout:
            logging.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logging.error(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"❌ Errore imprevisto: {e}")
        return False

def backup_old_models():
    """Crea backup dei modelli precedenti"""
    models_dir = BASE_DIR / 'models'
    if not models_dir.exists():
        return
    
    backup_dir = BASE_DIR / 'backups' / f"models_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        import shutil
        shutil.copytree(models_dir, backup_dir)
        logging.info(f"💾 Backup modelli salvato in: {backup_dir.name}")
    except Exception as e:
        logging.warning(f"⚠️  Backup modelli fallito: {e}")

def main():
    """Processo completo weekly retraining"""
    start_time = datetime.now()
    
    # Backup modelli esistenti
    backup_old_models()
    
    # Ritraining
    success = run_training()
    
    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    logging.info("-" * 60)
    logging.info(f"⏱️  Tempo totale: {elapsed:.1f} secondi")
    logging.info(f"📅 Prossimo retraining: Domenica {(datetime.now()).strftime('%d/%m/%Y')} ore 02:00")
    logging.info("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
