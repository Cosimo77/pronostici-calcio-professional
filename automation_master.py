#!/usr/bin/env python3
"""
🤖 SISTEMA AUTOMAZIONE COMPLETO
Master script per automatizzare tutti i processi critici del sistema pronostici
"""

import os
import sys
import subprocess
import schedule  # type: ignore
import time
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import threading
import signal

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutomationMaster')

class AutomationMaster:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.logs_dir = self.root_dir / 'logs'
        self.cache_dir = self.root_dir / 'cache'
        self.data_dir = self.root_dir / 'data'
        self.models_dir = self.root_dir / 'models'
        self.scripts_dir = self.root_dir / 'scripts'
        
        # Crea directory se non esistono
        for dir_path in [self.logs_dir, self.cache_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.status = {
            'started_at': datetime.now().isoformat(),
            'last_daily_update': None,
            'last_weekly_retrain': None,
            'last_backup': None,
            'last_health_check': None,
            'errors': [],
            'running': True
        }
        
        self.save_status()
    
    def save_status(self):
        """Salva lo stato dell'automazione"""
        status_file = self.logs_dir / 'automation_status.json'
        with open(status_file, 'w') as f:
            json.dump(self.status, f, indent=2, default=str)
    
    def log_error(self, error_msg, process_name):
        """Registra un errore"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'process': process_name,
            'error': str(error_msg)
        }
        self.status['errors'].append(error_entry)
        logger.error(f"[{process_name}] {error_msg}")
        self.save_status()
    
    def run_script(self, script_path, description, timeout=300):
        """Esegue uno script Python con timeout"""
        logger.info(f"🚀 Avvio: {description}")
        
        try:
            script_full_path = self.scripts_dir / script_path
            if not script_full_path.exists():
                raise FileNotFoundError(f"Script non trovato: {script_full_path}")
            
            # Esegue lo script
            result = subprocess.run(
                [sys.executable, str(script_full_path)],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Completato: {description}")
                return True, result.stdout
            else:
                error_msg = f"Exit code {result.returncode}: {result.stderr}"
                self.log_error(error_msg, description)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout dopo {timeout}s"
            self.log_error(error_msg, description)
            return False, error_msg
        except Exception as e:
            self.log_error(str(e), description)
            return False, str(e)
    
    # ========================================
    # PROCESSI AUTOMAZIONE
    # ========================================
    
    def daily_data_update(self):
        """Aggiornamento dati quotidiano"""
        logger.info("📅 INIZIO AGGIORNAMENTO DATI QUOTIDIANO")
        
        success_count = 0
        total_tasks = 3
        
        # 1. Aggiornamento dati
        success, output = self.run_script(
            'aggiorna_quotidiano.py',
            'Aggiornamento dati quotidiano',
            timeout=600
        )
        if success:
            success_count += 1
        
        # 2. Rigenerazione features
        if success:
            success, output = self.run_script(
                'feature_engineering.py',
                'Rigenerazione features',
                timeout=300
            )
            if success:
                success_count += 1
        
        # 3. Validazione dati
        success, output = self.run_script(
            'monitor_scraper.py',
            'Validazione dati aggiornati',
            timeout=120
        )
        if success:
            success_count += 1
        
        self.status['last_daily_update'] = datetime.now().isoformat()
        self.save_status()
        
        logger.info(f"📅 COMPLETATO AGGIORNAMENTO QUOTIDIANO: {success_count}/{total_tasks} task riusciti")
        return success_count == total_tasks
    
    def weekly_model_retrain(self):
        """Ritraining modelli settimanale"""
        logger.info("📊 INIZIO RITRAINING MODELLI SETTIMANALE")
        
        success_count = 0
        total_tasks = 2
        
        # 1. Backup modelli attuali
        backup_dir = self.models_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        
        try:
            for model_file in self.models_dir.glob('*.pkl'):
                shutil.copy2(model_file, backup_dir)
            logger.info(f"✅ Backup modelli creato in: {backup_dir}")
            success_count += 1
        except Exception as e:
            self.log_error(f"Errore backup modelli: {e}", "Weekly Model Retrain")
        
        # 2. Ritraining
        success, output = self.run_script(
            'modelli_predittivi.py',
            'Ritraining modelli ML',
            timeout=1800  # 30 minuti
        )
        if success:
            success_count += 1
        
        self.status['last_weekly_retrain'] = datetime.now().isoformat()
        self.save_status()
        
        logger.info(f"📊 COMPLETATO RITRAINING SETTIMANALE: {success_count}/{total_tasks} task riusciti")
        return success_count == total_tasks
    
    def cache_cleanup(self):
        """Pulizia cache obsoleta"""
        logger.info("🧹 INIZIO PULIZIA CACHE")
        
        try:
            # Rimuove file cache più vecchi di 7 giorni
            cutoff_date = datetime.now() - timedelta(days=7)
            removed_count = 0
            
            for cache_file in self.cache_dir.glob('*.json'):
                if cache_file.stat().st_mtime < cutoff_date.timestamp():
                    cache_file.unlink()
                    removed_count += 1
            
            # Pulisce log più vecchi di 30 giorni
            log_cutoff = datetime.now() - timedelta(days=30)
            for log_file in self.logs_dir.glob('*.log'):
                if log_file.stat().st_mtime < log_cutoff.timestamp():
                    log_file.unlink()
                    removed_count += 1
            
            logger.info(f"🧹 PULIZIA CACHE COMPLETATA: {removed_count} file rimossi")
            return True
            
        except Exception as e:
            self.log_error(f"Errore pulizia cache: {e}", "Cache Cleanup")
            return False
    
    def backup_data(self):
        """Backup automatico dati e modelli"""
        logger.info("💾 INIZIO BACKUP AUTOMATICO")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_root = Path(f"backup_{timestamp}")
            backup_root.mkdir(exist_ok=True)
            
            # Backup dati
            data_backup = backup_root / "data"
            shutil.copytree(self.data_dir, data_backup, ignore=shutil.ignore_patterns('*.tmp'))
            
            # Backup modelli
            models_backup = backup_root / "models"
            shutil.copytree(self.models_dir, models_backup)
            
            # Backup configurazioni
            config_backup = backup_root / "config"
            config_backup.mkdir()
            
            # Copia file di configurazione importanti
            config_files = ['analisi_architettura.json', 'pyrightconfig.json']
            for config_file in config_files:
                config_path = self.root_dir / config_file
                if config_path.exists():
                    shutil.copy2(config_path, config_backup)
            
            # Comprimi il backup
            archive_name = f"backup_{timestamp}"
            shutil.make_archive(archive_name, 'zip', backup_root)
            
            # Rimuove directory temporanea
            shutil.rmtree(backup_root)
            
            self.status['last_backup'] = datetime.now().isoformat()
            self.save_status()
            
            logger.info(f"💾 BACKUP COMPLETATO: {archive_name}.zip")
            return True
            
        except Exception as e:
            self.log_error(f"Errore backup: {e}", "Data Backup")
            return False
    
    def health_check(self):
        """Controllo salute sistema"""
        logger.info("🔍 INIZIO HEALTH CHECK")
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'healthy'
        }
        
        # 1. Controlla file dati essenziali
        essential_files = [
            self.data_dir / 'dataset_features.csv',
            self.models_dir / 'randomforest_model.pkl',
            self.models_dir / 'metadata.pkl'
        ]
        
        for file_path in essential_files:
            file_healthy = file_path.exists() and file_path.stat().st_size > 0
            health_status['checks'][f'file_{file_path.name}'] = {
                'status': 'ok' if file_healthy else 'error',
                'exists': file_path.exists(),
                'size_mb': file_path.stat().st_size / (1024*1024) if file_path.exists() else 0
            }
            if not file_healthy:
                health_status['overall_status'] = 'degraded'
        
        # 2. Controlla spazio disco
        disk_usage = shutil.disk_usage(self.root_dir)
        free_space_gb = disk_usage.free / (1024**3)
        
        health_status['checks']['disk_space'] = {
            'status': 'ok' if free_space_gb > 1.0 else 'warning',
            'free_gb': round(free_space_gb, 2)
        }
        
        # 3. Controlla età dei dati
        dataset_file = self.data_dir / 'dataset_features.csv'
        if dataset_file.exists():
            file_age_days = (datetime.now().timestamp() - dataset_file.stat().st_mtime) / (24 * 3600)
            data_fresh = file_age_days < 7  # Dati più vecchi di 7 giorni sono stale
            
            health_status['checks']['data_freshness'] = {
                'status': 'ok' if data_fresh else 'warning',
                'age_days': round(file_age_days, 1)
            }
        
        # 4. Test API locale
        try:
            import requests
            response = requests.get('http://localhost:5008/api/squadre', timeout=10)
            api_healthy = response.status_code == 200
            
            health_status['checks']['api_server'] = {
                'status': 'ok' if api_healthy else 'error',
                'status_code': response.status_code if response else None
            }
        except Exception as e:
            health_status['checks']['api_server'] = {
                'status': 'error',
                'error': str(e)
            }
            health_status['overall_status'] = 'degraded'
        
        # Salva risultati health check
        health_file = self.logs_dir / 'health_check.json'
        with open(health_file, 'w') as f:
            json.dump(health_status, f, indent=2)
        
        self.status['last_health_check'] = datetime.now().isoformat()
        self.save_status()
        
        # Log risultati
        status_emoji = "✅" if health_status['overall_status'] == 'healthy' else "⚠️" if health_status['overall_status'] == 'degraded' else "❌"
        logger.info(f"🔍 HEALTH CHECK COMPLETATO: {status_emoji} {health_status['overall_status']}")
        
        return health_status['overall_status'] == 'healthy'
    
    # ========================================
    # SCHEDULER
    # ========================================
    
    def setup_scheduler(self):
        """Configura lo scheduler per tutti i processi"""
        logger.info("⏰ Configurazione scheduler automazione")
        
        # Aggiornamento dati quotidiano alle 6:00
        schedule.every().day.at("06:00").do(self.daily_data_update)
        
        # Ritraining modelli ogni domenica alle 2:00
        schedule.every().sunday.at("02:00").do(self.weekly_model_retrain)
        
        # Pulizia cache ogni giorno alle 3:00
        schedule.every().day.at("03:00").do(self.cache_cleanup)
        
        # Backup ogni giorno alle 4:00
        schedule.every().day.at("04:00").do(self.backup_data)
        
        # Health check ogni ora
        schedule.every().hour.do(self.health_check)
        
        logger.info("⏰ Scheduler configurato:")
        logger.info("   📅 Aggiornamento dati: ogni giorno alle 06:00")
        logger.info("   📊 Ritraining modelli: ogni domenica alle 02:00")
        logger.info("   🧹 Pulizia cache: ogni giorno alle 03:00")
        logger.info("   💾 Backup: ogni giorno alle 04:00")
        logger.info("   🔍 Health check: ogni ora")
    
    def run_automation(self):
        """Avvia il sistema di automazione"""
        logger.info("🤖 AVVIO SISTEMA AUTOMAZIONE MASTER")
        
        # Setup signal handlers per shutdown graceful
        def signal_handler(signum, frame):
            logger.info("📨 Ricevuto segnale shutdown")
            self.status['running'] = False
            self.save_status()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Configura scheduler
        self.setup_scheduler()
        
        # Health check iniziale
        self.health_check()
        
        # Loop principale
        logger.info("🔄 Loop principale automazione avviato")
        while self.status['running']:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check ogni minuto
                
            except KeyboardInterrupt:
                logger.info("⌨️ Interruzione da tastiera")
                break
            except Exception as e:
                self.log_error(f"Errore nel loop principale: {e}", "Main Loop")
                time.sleep(60)
        
        logger.info("🛑 Sistema automazione terminato")

def main():
    """Entry point principale"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🤖 SISTEMA AUTOMAZIONE PRONOSTICI CALCIO")
    print("=" * 50)
    print(f"📂 Directory: {root_dir}")
    print(f"📅 Avvio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Modalità test - esegue tutti i processi una volta
        print("🧪 MODALITÀ TEST - Esecuzione processi singola")
        automation = AutomationMaster(root_dir)
        
        print("\n1. Health Check...")
        automation.health_check()
        
        print("\n2. Cache Cleanup...")
        automation.cache_cleanup()
        
        print("\n3. Data Update (se richiesto)...")
        if input("Eseguire aggiornamento dati? (y/N): ").lower() == 'y':
            automation.daily_data_update()
        
        print("\n✅ Test completato")
    else:
        # Modalità normale - avvia daemon
        automation = AutomationMaster(root_dir)
        automation.run_automation()

if __name__ == "__main__":
    main()