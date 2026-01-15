#!/usr/bin/env python3
"""
Sistema automazione reale per Render
Questo script deve girare LOCALMENTE come cron job e fare push su GitHub
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_cron.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_command(cmd, cwd=None):
    """Esegue comando shell e ritorna output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Errore esecuzione comando: {e}")
        return False, "", str(e)

def aggiorna_dati():
    """Aggiorna dataset da football-data.co.uk"""
    logger.info("🔄 Inizio aggiornamento dati...")
    
    base_dir = Path(__file__).parent
    
    # Esegui script aggiornamento
    success, stdout, stderr = run_command(
        "python3 scripts/scraper_dati.py",
        cwd=base_dir
    )
    
    if success:
        logger.info("✅ Dati aggiornati correttamente")
        return True
    else:
        logger.error(f"❌ Errore aggiornamento dati: {stderr}")
        return False

def riaddestra_modelli():
    """Riaddestra modelli ML (opzionale, sistema usa ProfessionalCalculator)"""
    logger.info("🤖 Riaddestramento modelli...")
    
    base_dir = Path(__file__).parent
    
    success, stdout, stderr = run_command(
        "python3 scripts/modelli_predittivi.py",
        cwd=base_dir
    )
    
    if success:
        logger.info("✅ Modelli riaddestrati")
        return True
    else:
        logger.warning(f"⚠️ Modelli non riaddestrati: {stderr}")
        return False  # Non blocca, modelli opzionali

def push_to_github():
    """Push modifiche su GitHub (trigger deploy Render)"""
    logger.info("📤 Push su GitHub...")
    
    base_dir = Path(__file__).parent
    
    # Check modifiche
    success, stdout, _ = run_command("git status --porcelain", cwd=base_dir)
    
    if not stdout.strip():
        logger.info("ℹ️ Nessuna modifica da committare")
        return True
    
    # Add modifiche
    run_command("git add data/", cwd=base_dir)
    
    # Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    success, _, stderr = run_command(
        f'git commit -m "🔄 Auto-update dati {timestamp}"',
        cwd=base_dir
    )
    
    if not success and "nothing to commit" not in stderr:
        logger.error(f"❌ Errore commit: {stderr}")
        return False
    
    # Push
    success, stdout, stderr = run_command("git push origin main", cwd=base_dir)
    
    if success:
        logger.info("✅ Push completato - Render deploy automatico attivato")
        return True
    else:
        logger.error(f"❌ Errore push: {stderr}")
        return False

def main():
    """Funzione principale automazione"""
    logger.info("="*60)
    logger.info("🚀 INIZIO AUTOMAZIONE GIORNALIERA")
    logger.info("="*60)
    
    # 1. Aggiorna dati
    if not aggiorna_dati():
        logger.error("❌ Automazione fallita: aggiornamento dati")
        sys.exit(1)
    
    # 2. Push su GitHub (trigger Render)
    if not push_to_github():
        logger.error("❌ Automazione fallita: push GitHub")
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("✅ AUTOMAZIONE COMPLETATA CON SUCCESSO")
    logger.info("="*60)
    
    # Scrivi timestamp per API
    timestamp_file = Path(__file__).parent / "logs" / "last_automation.txt"
    timestamp_file.write_text(datetime.now().isoformat())

if __name__ == "__main__":
    main()
