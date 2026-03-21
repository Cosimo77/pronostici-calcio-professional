#!/usr/bin/env python3
"""
Cache Cleanup & Backup Rotation - Eseguito ogni 3 giorni
Pulisce cache Redis, vecchi log e ruota backup
"""

import os
import sys
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup
BASE_DIR = Path(__file__).parent.parent
LOG_FILE = BASE_DIR / 'logs' / 'cleanup.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def cleanup_redis_cache():
    """Pulisce cache Redis se disponibile"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test connessione
        r.ping()
        
        # Conta chiavi prima
        keys_before = int(r.dbsize())
        
        # Pulisce chiavi scadute
        r.execute_command('MEMORY', 'PURGE')
        
        keys_after = int(r.dbsize())
        freed = keys_before - keys_after
        
        logging.info(f"🧹 Redis: {freed} chiavi rimosse ({keys_after} rimanenti)")
        return True
        
    except ImportError:
        logging.warning("⚠️  Redis non installato, skip cache cleanup")
        return False
    except Exception as e:
        logging.warning(f"⚠️  Redis non raggiungibile: {e}")
        return False

def cleanup_old_logs():
    """Rimuove log più vecchi di 30 giorni"""
    logs_dir = BASE_DIR / 'logs'
    if not logs_dir.exists():
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=30)
    removed = 0
    
    for log_file in logs_dir.glob('*.log'):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_date:
                size_mb = log_file.stat().st_size / (1024 * 1024)
                log_file.unlink()
                removed += 1
                logging.info(f"🗑️  Rimosso log vecchio: {log_file.name} ({size_mb:.2f} MB)")
        except Exception as e:
            logging.warning(f"⚠️  Errore rimozione {log_file.name}: {e}")
    
    return removed

def rotate_backups():
    """Mantiene solo ultimi 7 backup, rimuove i più vecchi"""
    backups_dir = BASE_DIR / 'backups'
    if not backups_dir.exists():
        return 0
    
    # Trova tutti i backup (directories con timestamp)
    backups = sorted([d for d in backups_dir.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
    
    if len(backups) <= 7:
        logging.info(f"💾 Backup: {len(backups)} presenti (< 7, nessuna rotazione)")
        return 0
    
    # Rimuovi backup oltre il 7°
    removed = 0
    for old_backup in backups[7:]:
        try:
            shutil.rmtree(old_backup)
            removed += 1
            logging.info(f"🗑️  Backup rimosso: {old_backup.name}")
        except Exception as e:
            logging.warning(f"⚠️  Errore rimozione backup {old_backup.name}: {e}")
    
    return removed

def cleanup_temp_files():
    """Rimuove file temporanei"""
    temp_patterns = ['*.tmp', '*.cache', '__pycache__']
    removed = 0
    
    for pattern in temp_patterns:
        for temp_file in BASE_DIR.rglob(pattern):
            try:
                if temp_file.is_file():
                    temp_file.unlink()
                    removed += 1
                elif temp_file.is_dir():
                    shutil.rmtree(temp_file)
                    removed += 1
            except Exception as e:
                logging.warning(f"⚠️  Errore rimozione {temp_file}: {e}")
    
    if removed > 0:
        logging.info(f"🧹 File temporanei rimossi: {removed}")
    
    return removed

def get_disk_usage():
    """Calcola spazio disco utilizzato dal progetto"""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(BASE_DIR):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
        
        size_mb = total_size / (1024 * 1024)
        size_gb = size_mb / 1024
        
        if size_gb > 1:
            logging.info(f"💽 Spazio utilizzato: {size_gb:.2f} GB")
        else:
            logging.info(f"💽 Spazio utilizzato: {size_mb:.2f} MB")
        
    except Exception as e:
        logging.warning(f"⚠️  Errore calcolo spazio: {e}")

def main():
    """Esegue cleanup completo"""
    logging.info("=" * 60)
    logging.info("🧹 CLEANUP & BACKUP ROTATION")
    logging.info("=" * 60)
    
    # Redis cache
    cleanup_redis_cache()
    
    # Log vecchi
    logs_removed = cleanup_old_logs()
    if logs_removed > 0:
        logging.info(f"✅ Log rimossi: {logs_removed}")
    
    # Backup rotation
    backups_removed = rotate_backups()
    if backups_removed > 0:
        logging.info(f"✅ Backup ruotati: {backups_removed} rimossi")
    
    # File temporanei
    cleanup_temp_files()
    
    # Spazio disco
    get_disk_usage()
    
    logging.info("=" * 60)
    logging.info("✅ Cleanup completato")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
