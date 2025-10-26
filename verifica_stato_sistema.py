#!/usr/bin/env python3
"""
🔍 VERIFICA STATO SISTEMA PROFESSIONALE
Controlla se dataset, modelli e sistema sono tutti aggiornati
"""

import os
import sys
import json
import joblib
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

class SystemStatusChecker:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.dataset_path = self.base_path / "data" / "dataset_features.csv"
        self.models_dir = self.base_path / "models"
        self.config_path = self.base_path / "config" / "auto_update.json"
        self.logs_dir = self.base_path / "logs"
        
    def check_dataset_freshness(self):
        """Verifica se il dataset è aggiornato"""
        print("📊 STATO DATASET:")
        print("-" * 40)
        
        if not self.dataset_path.exists():
            print("❌ Dataset non trovato!")
            return False
            
        # Info dataset
        dataset_mtime = os.path.getmtime(self.dataset_path)
        dataset_date = datetime.fromtimestamp(dataset_mtime)
        hours_old = (datetime.now() - dataset_date).total_seconds() / 3600
        
        # Carica dataset per analisi
        df = pd.read_csv(self.dataset_path)
        
        print(f"📁 File: {self.dataset_path.name}")
        print(f"📅 Ultima modifica: {dataset_date.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏰ Età: {hours_old:.1f} ore")
        print(f"📊 Partite totali: {len(df)}")
        
        if 'Date' in df.columns:
            latest_match = df['Date'].max()
            print(f"🏆 Partita più recente: {latest_match}")
            
        # Valutazione freshness
        if hours_old < 24:
            print("✅ Dataset FRESCO (< 24h)")
            return True
        elif hours_old < 72:
            print("⚠️ Dataset ACCETTABILE (< 72h)")
            return True
        else:
            print("❌ Dataset OBSOLETO (> 72h)")
            return False
    
    def check_models_sync(self):
        """Verifica se i modelli sono sincronizzati con il dataset"""
        print("\n🤖 STATO MODELLI:")
        print("-" * 40)
        
        if not self.dataset_path.exists():
            print("❌ Impossibile verificare: dataset mancante")
            return False
            
        dataset_mtime = os.path.getmtime(self.dataset_path)
        dataset_date = datetime.fromtimestamp(dataset_mtime)
        
        main_models = [
            'randomforest_model.pkl',
            'gradientboosting_model.pkl', 
            'logisticregression_model.pkl'
        ]
        
        all_synced = True
        models_status = {}
        
        for model_file in main_models:
            model_path = self.models_dir / model_file
            
            if model_path.exists():
                model_mtime = os.path.getmtime(model_path)
                model_date = datetime.fromtimestamp(model_mtime)
                
                is_synced = model_mtime >= dataset_mtime
                time_diff = (model_mtime - dataset_mtime) / 3600  # ore
                
                status = "✅ SINCRONIZZATO" if is_synced else "❌ OBSOLETO"
                models_status[model_file] = is_synced
                
                print(f"🔧 {model_file}")
                print(f"   📅 {model_date.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"   🔄 {status} ({time_diff:+.1f}h dal dataset)")
                
                if not is_synced:
                    all_synced = False
            else:
                print(f"❌ {model_file}: MANCANTE")
                models_status[model_file] = False
                all_synced = False
        
        # Verifica metadata
        metadata_path = self.models_dir / "metadata.pkl"
        if metadata_path.exists():
            try:
                metadata = joblib.load(metadata_path)
                print(f"\n📋 METADATA TRAINING:")
                if 'training_date' in metadata:
                    print(f"   📅 Ultimo training: {metadata['training_date']}")
                if 'dataset_size' in metadata:
                    print(f"   📊 Dataset size: {metadata['dataset_size']} partite")
                if 'model_performance' in metadata:
                    print(f"   🎯 Performance:")
                    for model_name, perf in metadata['model_performance'].items():
                        if isinstance(perf, dict) and 'accuracy' in perf:
                            print(f"      • {model_name}: {perf['accuracy']:.1%}")
            except Exception as e:
                print(f"⚠️ Errore lettura metadata: {e}")
        
        return all_synced
    
    def check_automation_status(self):
        """Verifica stato automazione"""
        print("\n🔄 STATO AUTOMAZIONE:")
        print("-" * 40)
        
        if not self.config_path.exists():
            print("❌ Configurazione automazione mancante")
            return False
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Verifica schedule
            if 'schedule' in config:
                schedule = config['schedule']
                print("📅 SCHEDULE CONFIGURATO:")
                print(f"   🌅 Aggiornamento dati: {schedule.get('daily_data_update', 'N/A')}")
                print(f"   🧠 Training modelli: {schedule.get('weekly_model_retrain', 'N/A')}")
                print(f"   ⚡ Live scores: {schedule.get('hourly_live_scores', 'N/A')}")
            
            # Verifica sorgenti dati
            if 'data_sources' in config:
                sources = config['data_sources']
                active_sources = sum(1 for s in sources.values() if isinstance(s, dict) and s.get('enabled', False))
                print(f"\n📡 SORGENTI DATI: {active_sources} attive")
                
                for name, source in sources.items():
                    if isinstance(source, dict):
                        enabled = "✅" if source.get('enabled', False) else "❌"
                        priority = source.get('priority', '?')
                        print(f"   {enabled} {name} (priorità: {priority})")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore lettura configurazione: {e}")
            return False
    
    def check_last_activities(self):
        """Verifica ultime attività del sistema"""
        print("\n📝 ULTIME ATTIVITÀ:")
        print("-" * 40)
        
        # Cerca file di log recenti
        if self.logs_dir.exists():
            log_files = list(self.logs_dir.glob("*.log"))
            
            if log_files:
                # Log più recente
                latest_log = max(log_files, key=lambda x: os.path.getmtime(x))
                log_mtime = os.path.getmtime(latest_log)
                log_date = datetime.fromtimestamp(log_mtime)
                hours_ago = (datetime.now() - log_date).total_seconds() / 3600
                
                print(f"📋 Ultimo log: {latest_log.name}")
                print(f"📅 Data: {log_date.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"⏰ {hours_ago:.1f} ore fa")
            else:
                print("⚠️ Nessun file di log trovato")
        
        # Verifica backup
        backup_dir = self.base_path / "backups"
        if backup_dir.exists():
            backup_dirs = [d for d in backup_dir.iterdir() if d.is_dir()]
            if backup_dirs:
                latest_backup = max(backup_dirs, key=lambda x: os.path.getmtime(x))
                backup_mtime = os.path.getmtime(latest_backup)
                backup_date = datetime.fromtimestamp(backup_mtime)
                
                print(f"💾 Ultimo backup: {latest_backup.name}")
                print(f"📅 Data: {backup_date.strftime('%d/%m/%Y %H:%M:%S')}")
    
    def generate_status_report(self):
        """Genera report completo dello stato"""
        print("🏆 SISTEMA PROFESSIONALE - REPORT STATO")
        print("=" * 60)
        print(f"📅 Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Esegui tutti i controlli
        dataset_ok = self.check_dataset_freshness()
        models_ok = self.check_models_sync()
        automation_ok = self.check_automation_status()
        
        self.check_last_activities()
        
        # Verdetto finale
        print("\n" + "=" * 60)
        print("🎯 VERDETTO FINALE:")
        print("-" * 60)
        
        if dataset_ok and models_ok and automation_ok:
            print("🎉 SISTEMA COMPLETAMENTE AGGIORNATO E OPERATIVO!")
            print("✅ Dataset fresco")
            print("✅ Modelli sincronizzati") 
            print("✅ Automazione configurata")
            print("\n🚀 Il sistema è PRONTO per l'uso professionale!")
            return True
        else:
            print("⚠️ SISTEMA NECESSITA ATTENZIONE:")
            if not dataset_ok:
                print("❌ Dataset obsoleto - eseguire aggiornamento dati")
            if not models_ok:
                print("❌ Modelli non sincronizzati - eseguire training")
            if not automation_ok:
                print("❌ Automazione non configurata - verificare config")
            
            print("\n🔧 AZIONI CONSIGLIATE:")
            if not dataset_ok:
                print("   python aggiornamento_dati_reali.py")
            if not models_ok:
                print("   python allena_modelli_rapido.py")
            
            return False

def main():
    """Funzione principale"""
    checker = SystemStatusChecker()
    system_ok = checker.generate_status_report()
    
    # Exit code per scripts automatici
    sys.exit(0 if system_ok else 1)

if __name__ == "__main__":
    main()