#!/usr/bin/env python3
"""
🤖 Background Automation per Flask
Esegue aggiornamenti automatici in thread separato senza processo dedicato
"""

import os
import sys
import subprocess
import threading
import time
import logging
import json
from datetime import datetime, time as dt_time, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class BackgroundAutomation:
    """Gestisce automazione background con persistenza stato"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.running = False
        self.thread = None
        
        # File persistenza stato
        self.state_file = self.root_dir / "logs" / "automation_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Carica stato salvato
        state = self._load_state()
        self.last_update = state.get('last_update')
        self.last_retrain = state.get('last_retrain')
    
    def _load_state(self):
        """Carica stato salvato da file JSON"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    
                # Converti stringhe ISO a datetime
                if data.get('last_update'):
                    data['last_update'] = datetime.fromisoformat(data['last_update'])
                if data.get('last_retrain'):
                    data['last_retrain'] = datetime.fromisoformat(data['last_retrain'])
                    
                logger.info(f"📂 Stato caricato: {data}")
                return data
        except Exception as e:
            logger.warning(f"⚠️ Errore caricamento stato: {e}")
        
        return {}
    
    def _save_state(self):
        """Salva stato su file JSON"""
        try:
            data = {
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'last_retrain': self.last_retrain.isoformat() if self.last_retrain else None,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"💾 Stato salvato: {self.state_file}")
        except Exception as e:
            logger.error(f"❌ Errore salvataggio stato: {e}", exc_info=True)
        
    def start(self):
        """Avvia thread automazione"""
        if self.running:
            logger.warning("⚠️ Automazione già attiva")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.thread.start()
        logger.info("✅ Background automation avviata")
    
    def stop(self):
        """Ferma thread automazione"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Background automation fermata")
    
    def _automation_loop(self):
        """Loop principale automazione"""
        logger.info("🔄 Automation loop started")
        
        while self.running:
            try:
                now = datetime.now(timezone.utc)
                logger.info(f"⏰ Check automation - UTC: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 🔄 Aggiornamento quotidiano alle 06:00
                should_update = self._should_run_daily_update(now)
                logger.info(f"📊 Daily update check: {should_update} (last_update: {self.last_update})")
                if should_update:
                    logger.info("✅ Condizione daily update soddisfatta, esecuzione...")
                    self._run_daily_update()
                
                # 🧠 Riaddestramento settimanale (Lunedì 02:00 UTC)
                should_retrain = self._should_run_weekly_retrain(now)
                logger.info(f"🧠 Weekly retrain check: {should_retrain} (last_retrain: {self.last_retrain}, weekday: {now.weekday()})")
                if should_retrain:
                    logger.info("✅ Condizione weekly retrain soddisfatta, esecuzione...")
                    self._run_weekly_retrain()
                
                # Sleep 5 minuti prima del prossimo check
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Errore automation loop: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 min on error
    
    def _should_run_daily_update(self, now):
        """Verifica se eseguire update quotidiano"""
        if self.last_update:
            # Assicura timezone-aware per confronto date
            last_update_aware = self.last_update if self.last_update.tzinfo else self.last_update.replace(tzinfo=timezone.utc)
            if last_update_aware.date() == now.date():
                return False  # Già fatto oggi
        
        # Esegui alle 06:00 (finestra 05:00-07:00 per garantire esecuzione)
        current_time = now.time()
        
        # Esegui tra le 05:00 e 07:00 se non già fatto oggi
        return (
            dt_time(5, 0) <= current_time <= dt_time(7, 0) and
            (not self.last_update or self.last_update.date() != now.date())
        )
    
    def _should_run_weekly_retrain(self, now):
        """Verifica se eseguire retrain settimanale"""
        if self.last_retrain:
            # Assicura entrambi timezone-aware per confronto
            last_retrain_aware = self.last_retrain if self.last_retrain.tzinfo else self.last_retrain.replace(tzinfo=timezone.utc)
            if (now - last_retrain_aware).days < 6:
                return False  # Già fatto questa settimana
        
        # Esegui Lunedì alle 02:00 UTC (era Domenica sera in Italia)
        # Lunedì = weekday 0 (Domenica = 6)
        is_monday = now.weekday() == 0
        target_time = dt_time(2, 0)
        current_time = now.time()
        
        return (
            is_monday and
            dt_time(1, 45) <= current_time <= dt_time(2, 15) and
            (not self.last_retrain or (now - self.last_retrain).days >= 6)
        )
    
    def _run_daily_update(self):
        """Esegue aggiornamento dati quotidiano"""
        logger.info(f"🔄 Avvio aggiornamento quotidiano - Last update: {self.last_update}")
        
        try:
            # Prova script minimale (sempre presente nel root)
            script_path = self.root_dir / "update_data_minimal.py"
            logger.info(f"📂 Script minimale: {script_path}")
            
            if not script_path.exists():
                # Fallback: scripts/aggiorna_quotidiano.py
                script_path = self.root_dir / "scripts" / "aggiorna_quotidiano.py"
                logger.info(f"📂 Tentativo script: {script_path}")
            
            if not script_path.exists():
                # Fallback: aggiorna_veloce.py
                script_path = self.root_dir / "aggiorna_veloce.py"
                logger.info(f"📂 Fallback script: {script_path}")
            
            if not script_path.exists():
                logger.error(f"❌ Nessuno script aggiornamento trovato in: {self.root_dir}")
                logger.error(f"❌ File esistenti: {list(self.root_dir.glob('*.py'))[:10]}")
                # Aggiorna comunque il timestamp per non bloccare
                self.last_update = datetime.now(timezone.utc)
                self._save_state()  # 💾 SALVA STATO SU FILE
                logger.warning(f"⚠️ Timestamp aggiornato senza eseguire script: {self.last_update}")
                return
            
            logger.info(f"▶️ Esecuzione: {script_path}")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 min timeout
            )
            
            if result.returncode == 0:
                self.last_update = datetime.now(timezone.utc)
                self._save_state()  # 💾 SALVA STATO SU FILE
                logger.info(f"✅ Aggiornamento quotidiano completato - timestamp: {self.last_update}")
                logger.info(f"📊 Output: {result.stdout[-200:]}")  # Ultimi 200 char
            else:
                logger.error(f"❌ Aggiornamento fallito (exit {result.returncode})")
                logger.error(f"📋 STDERR: {result.stderr[-500:]}")
                logger.error(f"📋 STDOUT: {result.stdout[-500:]}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout aggiornamento (>10 min)")
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento: {e}", exc_info=True)
    
    def _run_weekly_retrain(self):
        """Esegue riaddestramento modelli settimanale"""
        logger.info(f"🧠 Avvio riaddestramento modelli - Last retrain: {self.last_retrain}")
        
        try:
            script_path = self.root_dir / "riaddestra_modelli_rapido.py"
            logger.info(f"📂 Tentativo script: {script_path}")
            
            if not script_path.exists():
                script_path = self.root_dir / "allena_modelli_rapido.py"
                logger.info(f"📂 Fallback script: {script_path}")
            
            if not script_path.exists():
                logger.error(f"❌ Script riaddestramento non trovato in: {self.root_dir}")
                logger.error(f"❌ File esistenti: {list(self.root_dir.glob('*modelli*.py'))}")
                return
            
            logger.info(f"▶️ Esecuzione: {script_path}")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=1800  # 30 min timeout
            )
            
            if result.returncode == 0:
                self.last_retrain = datetime.now(timezone.utc)
                self._save_state()  # 💾 SALVA STATO SU FILE
                logger.info(f"✅ Riaddestramento completato - timestamp: {self.last_retrain}")
                logger.info(f"📊 Output: {result.stdout[-200:]}")
            else:
                logger.error(f"❌ Riaddestramento fallito (exit {result.returncode})")
                logger.error(f"📋 STDERR: {result.stderr[-500:]}")
                logger.error(f"📋 STDOUT: {result.stdout[-500:]}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout riaddestramento (>30 min)")
        except Exception as e:
            logger.error(f"❌ Errore riaddestramento: {e}", exc_info=True)
    
    def get_status(self):
        """Ritorna stato automazione"""
        return {
            'running': self.running,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'last_retrain': self.last_retrain.isoformat() if self.last_retrain else None,
            'next_update_estimate': self._estimate_next_update(),
            'next_retrain_estimate': self._estimate_next_retrain()
        }
    
    def _estimate_next_update(self):
        """Stima prossimo aggiornamento"""
        if not self.last_update:
            return "Oggi alle 06:00"
        
        next_date = self.last_update.date()
        from datetime import timedelta
        next_date += timedelta(days=1)
        return f"{next_date} alle 06:00"
    
    def _estimate_next_retrain(self):
        """Stima prossimo riaddestramento"""
        if not self.last_retrain:
            return "Prossima Domenica alle 02:00"
        
        # Assicura entrambi timezone-aware per confronto
        now_aware = datetime.now(timezone.utc)
        last_retrain_aware = self.last_retrain if self.last_retrain.tzinfo else self.last_retrain.replace(tzinfo=timezone.utc)
        days_since = (now_aware - last_retrain_aware).days
        days_until = 7 - days_since
        return f"Tra {days_until} giorni (Domenica 02:00)"


# Singleton globale
_automation = None

def get_automation(root_dir=None):
    """Ottieni istanza singleton automazione"""
    global _automation
    if _automation is None and root_dir:
        _automation = BackgroundAutomation(root_dir)
    return _automation
