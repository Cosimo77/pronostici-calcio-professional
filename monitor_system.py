#!/usr/bin/env python3
"""
Script di Monitoraggio Sistema Professionale
Controlla stato, performance e aggiornamenti dati
"""

import requests
import json
import time
from datetime import datetime
import sys

class SystemMonitor:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.endpoints = {
            'health': '/api/health',
            'metrics': '/api/metrics_summary', 
            'performance': '/api/model_performance',
            'accuracy': '/api/accuracy_report'
        }
    
    def check_health(self):
        """Controllo stato sistema"""
        try:
            response = requests.get(f"{self.base_url}{self.endpoints['health']}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sistema: {data['status']}")
                print(f"📊 Records DB: {data['database_records']}")
                print(f"🏆 Squadre: {data['squadre_caricate']}")
                print(f"💾 Cache: {data['cache_entries']} predizioni")
                print(f"🌍 Environment: {data['environment']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False
    
    def check_metrics(self):
        """Controllo metriche performance"""
        try:
            response = requests.get(f"{self.base_url}{self.endpoints['metrics']}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                perf = data['performance']
                print(f"🎯 Accuratezza: {perf['accuratezza_complessiva']}%")
                print(f"📈 Partite analizzate: {perf['partite_analizzate']}")
                print(f"✅ Predizioni corrette: {perf['predizioni_corrette']}")
                print(f"📊 Mercati supportati: {perf['mercati_supportati']}")
                return True
            else:
                print(f"❌ Metrics check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Errore metrics: {e}")
            return False
    
    def test_prediction(self):
        """Test predizione real-time"""
        try:
            test_data = {
                "home_team": "Juventus",
                "away_team": "Milan"
            }
            response = requests.post(
                f"{self.base_url}/api/predict_enterprise", 
                json=test_data,
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                print(f"🔮 Test predizione: {data['predizione']} ({data['probabilita']:.1f}%)")
                return True
            else:
                print(f"❌ Prediction test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Errore test predizione: {e}")
            return False
    
    def full_check(self):
        """Controllo completo sistema"""
        print(f"\n🔍 MONITORAGGIO SISTEMA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        health_ok = self.check_health()
        print()
        
        metrics_ok = self.check_metrics()
        print()
        
        prediction_ok = self.test_prediction()
        print()
        
        if health_ok and metrics_ok and prediction_ok:
            print("🎉 SISTEMA COMPLETAMENTE OPERATIVO!")
            return True
        else:
            print("⚠️  RILEVATI PROBLEMI NEL SISTEMA")
            return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python monitor_system.py <URL_RENDER>")
        print("Esempio: python monitor_system.py https://tuoapp.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1]
    monitor = SystemMonitor(url)
    
    # Controllo singolo
    if len(sys.argv) == 2:
        monitor.full_check()
    
    # Controllo continuo (opzionale)
    # while True:
    #     monitor.full_check()
    #     time.sleep(300)  # Ogni 5 minuti

if __name__ == "__main__":
    main()