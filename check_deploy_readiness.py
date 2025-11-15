#!/usr/bin/env python3
"""
Deploy Readiness Checker
Verifica tutti i requisiti per deploy in produzione
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


class DeployReadinessChecker:
    """Checker completo per verifica deploy readiness"""
    
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
        # Base dir è la directory del progetto, non parent
        self.base_dir = Path(__file__).parent
    
    def check_environment_variables(self):
        """Verifica variabili d'ambiente critiche"""
        required_vars = ['SECRET_KEY']
        optional_vars = ['FLASK_ENV', 'API_THE_ODDS', 'REDIS_URL']
        
        for var in required_vars:
            if os.environ.get(var):
                self.checks.append(f"✅ {var} configurata")
            else:
                self.errors.append(f"❌ {var} MANCANTE (critica)")
        
        for var in optional_vars:
            if os.environ.get(var):
                self.checks.append(f"✅ {var} configurata")
            else:
                self.warnings.append(f"⚠️  {var} non configurata (opzionale)")
    
    def check_required_files(self):
        """Verifica file critici presenti"""
        required_files = [
            'requirements.txt',
            'Procfile',
            'runtime.txt',
            'web/app_professional.py',
            'web/cache_manager.py',
            'web/monitoring.py'
        ]
        
        for file_path in required_files:
            full_path = self.base_dir / file_path
            if full_path.exists():
                self.checks.append(f"✅ {file_path} presente")
            else:
                self.errors.append(f"❌ {file_path} MANCANTE")
    
    def check_data_files(self):
        """Verifica dataset presenti"""
        data_dir = self.base_dir / 'data'
        
        if not data_dir.exists():
            self.errors.append("❌ Directory data/ MANCANTE")
            return
        
        required_datasets = [
            'dataset_features.csv',
            'I1_2425.csv'
        ]
        
        for dataset in required_datasets:
            if (data_dir / dataset).exists():
                self.checks.append(f"✅ {dataset} presente")
            else:
                self.warnings.append(f"⚠️  {dataset} non trovato")
    
    def check_models(self):
        """Verifica modelli ML presenti"""
        models_dir = self.base_dir / 'models' / 'enterprise'
        
        if not models_dir.exists():
            self.errors.append("❌ Directory models/enterprise/ MANCANTE")
            return
        
        model_files = list(models_dir.glob('*.joblib')) + list(models_dir.glob('*.pkl'))
        
        if len(model_files) > 0:
            self.checks.append(f"✅ {len(model_files)} modelli ML trovati")
        else:
            self.errors.append("❌ Nessun modello ML trovato in models/enterprise/")
    
    def check_dependencies(self):
        """Verifica dipendenze Python installate"""
        try:
            import flask
            import pandas
            import numpy
            import sklearn
            import redis
            
            self.checks.append("✅ Dipendenze Python principali installate")
            
            # Check versioni
            self.checks.append(f"   - Flask {flask.__version__}")
            self.checks.append(f"   - pandas {pandas.__version__}")
            self.checks.append(f"   - numpy {numpy.__version__}")
            self.checks.append(f"   - scikit-learn {sklearn.__version__}")
            self.checks.append(f"   - redis {redis.__version__}")
            
        except ImportError as e:
            self.errors.append(f"❌ Dipendenza mancante: {e}")
    
    def check_redis_connection(self):
        """Verifica connessione Redis (opzionale)"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
            r.ping()
            self.checks.append("✅ Redis disponibile (cache abilitata)")
        except Exception:
            self.warnings.append("⚠️  Redis non disponibile (cache disabilitata, ma OK)")
    
    def check_port_availability(self):
        """Verifica porta disponibile"""
        import socket
        
        port = int(os.environ.get('PORT', 5008))
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
            self.checks.append(f"✅ Porta {port} disponibile")
        except OSError:
            self.warnings.append(f"⚠️  Porta {port} già in uso (OK se server già attivo)")
    
    def check_disk_space(self):
        """Verifica spazio disco disponibile"""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free // (2**30)
            
            if free_gb > 1:
                self.checks.append(f"✅ Spazio disco: {free_gb}GB disponibili")
            else:
                self.warnings.append(f"⚠️  Spazio disco basso: {free_gb}GB")
        except Exception as e:
            self.warnings.append(f"⚠️  Impossibile verificare spazio disco: {e}")
    
    def check_security_config(self):
        """Verifica configurazioni sicurezza"""
        security_checks = {
            'SECRET_KEY': os.environ.get('SECRET_KEY'),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'development')
        }
        
        if security_checks['SECRET_KEY']:
            if len(security_checks['SECRET_KEY']) >= 32:
                self.checks.append("✅ SECRET_KEY sufficientemente sicura")
            else:
                self.warnings.append("⚠️  SECRET_KEY troppo corta (<32 caratteri)")
        
        if security_checks['FLASK_ENV'] == 'production':
            self.checks.append("✅ FLASK_ENV=production configurato")
        else:
            self.warnings.append("⚠️  FLASK_ENV non impostato su 'production'")
    
    def check_tests(self):
        """Verifica test suite"""
        tests_dir = self.base_dir / 'tests'
        
        if not tests_dir.exists():
            self.warnings.append("⚠️  Directory tests/ non trovata")
            return
        
        test_files = list(tests_dir.glob('test_*.py'))
        
        if len(test_files) > 0:
            self.checks.append(f"✅ {len(test_files)} file di test presenti")
        else:
            self.warnings.append("⚠️  Nessun file di test trovato")
    
    def run_all_checks(self):
        """Esegui tutti i check"""
        print("=" * 70)
        print("🚀 DEPLOY READINESS CHECKER")
        print("=" * 70)
        print()
        
        # Esegui check
        self.check_environment_variables()
        self.check_required_files()
        self.check_data_files()
        self.check_models()
        self.check_dependencies()
        self.check_redis_connection()
        self.check_port_availability()
        self.check_disk_space()
        self.check_security_config()
        self.check_tests()
        
        # Risultati
        print("✅ CHECKS PASSATI:")
        print("-" * 70)
        for check in self.checks:
            print(check)
        
        if self.warnings:
            print()
            print("⚠️  WARNINGS:")
            print("-" * 70)
            for warning in self.warnings:
                print(warning)
        
        if self.errors:
            print()
            print("❌ ERRORI CRITICI:")
            print("-" * 70)
            for error in self.errors:
                print(error)
        
        # Summary
        print()
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"Checks passati: {len(self.checks)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errori critici: {len(self.errors)}")
        print()
        
        # Decisione finale
        if self.errors:
            print("❌ DEPLOY NON PRONTO - Risolvere errori critici")
            return False
        elif len(self.warnings) > 5:
            print("⚠️  DEPLOY POSSIBILE CON CAUTELA - Molti warnings")
            return True
        else:
            print("✅ SISTEMA PRONTO PER DEPLOY!")
            return True
    
    def generate_report(self, output_file='deploy_readiness_report.json'):
        """Genera report JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'checks_passed': len(self.checks),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'ready_for_deploy': len(self.errors) == 0,
            'details': {
                'checks': self.checks,
                'warnings': self.warnings,
                'errors': self.errors
            }
        }
        
        output_path = self.base_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report salvato in: {output_path}")
        return report


def main():
    """Main function"""
    checker = DeployReadinessChecker()
    ready = checker.run_all_checks()
    checker.generate_report()
    
    # Exit code per CI/CD
    sys.exit(0 if ready else 1)


if __name__ == '__main__':
    main()
