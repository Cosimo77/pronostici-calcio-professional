#!/usr/bin/env python3
"""
🧪 TEST SUITE COMPLETO SISTEMA PROFESSIONALE
Verifica completa di tutte le funzionalità

Uso:
  python3 TEST_SISTEMA_COMPLETO.py
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime

def print_test_header():
    """Header dei test"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    🧪 TEST SUITE SISTEMA PROFESSIONALE                       ║
║                                                               ║
║    🔬 Verifica Completa • Tutti i Componenti                 ║
║    ✅ Test Automatizzati • Report Dettagliato               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

class TestSuiteProfessionale:
    def __init__(self):
        self.base_url = "http://localhost:5001"
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'details': []
        }
        
    def log_test(self, test_name, passed, details=""):
        """Log risultato test"""
        self.results['total_tests'] += 1
        if passed:
            self.results['passed'] += 1
            status = "✅ PASS"
        else:
            self.results['failed'] += 1
            status = "❌ FAIL"
            self.results['errors'].append(f"{test_name}: {details}")
        
        self.results['details'].append({
            'test': test_name,
            'status': status,
            'details': details
        })
        
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
    
    def test_file_structure(self):
        """Test 1: Struttura file"""
        print("\n🔍 TEST 1: STRUTTURA FILE")
        print("-" * 40)
        
        file_critici = [
            ('web/app_professional.py', 'Sistema principale'),
            ('web/templates/index.html', 'Template principale'),
            ('web/static/js/main.js', 'JavaScript frontend'),
            ('web/static/css/style.css', 'Stili CSS'),
            ('config.json', 'Configurazione'),
            ('data/dataset_features.csv', 'Dataset features'),
            ('models/metadata.pkl', 'Metadati modelli')
        ]
        
        for file_path, description in file_critici:
            exists = os.path.exists(file_path)
            self.log_test(f"File {description}", exists, file_path if exists else f"Missing: {file_path}")
    
    def test_api_endpoints(self):
        """Test 2: API Endpoints"""
        print("\n🔌 TEST 2: API ENDPOINTS")
        print("-" * 40)
        
        endpoints = [
            ('/api/predici', 'POST', {'squadra_casa': 'Inter', 'squadra_ospite': 'Milan'}),
            ('/api/mercati', 'POST', {'squadra_casa': 'Inter', 'squadra_ospite': 'Milan'}),
            ('/api/statistiche', 'GET', None),
            ('/api/forma', 'POST', {'squadra': 'Inter'}),
            ('/api/test_coerenza', 'GET', None)
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=10)
                
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                
                if success and endpoint == '/api/predici':
                    # Test aggiuntivo per predizione
                    result = response.json()
                    if 'modalita' in result and result['modalita'] == 'professional_deterministic':
                        details += " • Modalità professionale ✓"
                    else:
                        success = False
                        details += " • Modalità non professionale ✗"
                
                self.log_test(f"API {endpoint}", success, details)
                
            except Exception as e:
                self.log_test(f"API {endpoint}", False, str(e))
    
    def test_deterministic_predictions(self):
        """Test 3: Predizioni deterministiche"""
        print("\n🎯 TEST 3: PREDIZIONI DETERMINISTICHE")
        print("-" * 40)
        
        test_data = {'squadra_casa': 'Inter', 'squadra_ospite': 'Milan'}
        
        try:
            # Fai 3 predizioni identiche
            predictions = []
            for i in range(3):
                response = requests.post(f"{self.base_url}/api/predici", json=test_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    predictions.append({
                        'predizione': result.get('predizione_text'),
                        'confidenza': result.get('confidenza'),
                        'prob_casa': result.get('probabilita', {}).get('casa', 0)
                    })
                time.sleep(0.5)  # Piccola pausa
            
            # Verifica coerenza
            if len(predictions) == 3:
                all_same = all(p['predizione'] == predictions[0]['predizione'] for p in predictions)
                conf_same = all(abs(p['confidenza'] - predictions[0]['confidenza']) < 0.001 for p in predictions)
                
                deterministic = all_same and conf_same
                details = f"Predizioni: {[p['predizione'] for p in predictions]}"
                
                self.log_test("Determinismo predizioni", deterministic, details)
            else:
                self.log_test("Determinismo predizioni", False, "Non tutte le richieste sono riuscite")
                
        except Exception as e:
            self.log_test("Determinismo predizioni", False, str(e))
    
    def print_final_report(self):
        """Report finale"""
        print("\n" + "="*60)
        print("📊 REPORT FINALE TEST SUITE")
        print("="*60)
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        
        print(f"📈 Test totali: {self.results['total_tests']}")
        print(f"✅ Successi: {self.results['passed']}")
        print(f"❌ Fallimenti: {self.results['failed']}")
        print(f"📊 Tasso successo: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n❌ ERRORI RILEVATI:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print(f"\n🕐 Test completati: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        if success_rate >= 90:
            print("🎉 SISTEMA PROFESSIONALE VALIDATO!")
        elif success_rate >= 70:
            print("⚠️  SISTEMA PARZIALMENTE FUNZIONANTE")
        else:
            print("🚨 SISTEMA RICHIEDE ATTENZIONE")
        
        print("="*60)

def main():
    """Funzione principale"""
    print_test_header()
    
    # Cambia directory
    os.chdir('/Users/cosimomassaro/Desktop/pronostici_calcio')
    
    # Inizializza test suite
    test_suite = TestSuiteProfessionale()
    
    try:
        # Esegui tutti i test
        test_suite.test_file_structure()
        test_suite.test_api_endpoints()
        test_suite.test_deterministic_predictions()
        
        # Report finale
        test_suite.print_final_report()
        
        return 0 if test_suite.results['failed'] == 0 else 1
        
    except Exception as e:
        print(f"\n❌ ERRORE CRITICO TEST SUITE: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)