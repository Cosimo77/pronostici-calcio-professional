#!/usr/bin/env python3
"""
Test completo delle metriche dei sistemi di pronostici
Verifica che tutte le API metriche siano disponibili e funzionanti
"""

import requests
import json
from datetime import datetime

def test_api_endpoint(url, description):
    """Test di un endpoint API"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data, f"✅ {description}: OK"
        else:
            return False, None, f"❌ {description}: HTTP {response.status_code}"
    except Exception as e:
        return False, None, f"❌ {description}: {str(e)}"

def main():
    """Test principale delle metriche"""
    
    print("=" * 60)
    print("🔍 TEST COMPLETO METRICHE SISTEMI PRONOSTICI")
    print("=" * 60)
    
    # URLs dei sistemi
    professional_base = "http://localhost:5008"
    enterprise_base = "http://localhost:5009"
    
    # Test Sistema Professional
    print(f"\n📊 SISTEMA PROFESSIONAL ({professional_base})")
    print("-" * 40)
    
    professional_endpoints = [
        ("/api/status", "Status sistema"),
        ("/api/model_performance", "Performance modello"),
        ("/api/accuracy_report", "Report accuratezza"),
        ("/api/health", "Controllo salute"),
        ("/api/metrics_summary", "Riassunto metriche"),
        ("/api/squadre", "Lista squadre"),
        ("/api/statistiche", "Statistiche generali")
    ]
    
    professional_results = {}
    for endpoint, desc in professional_endpoints:
        success, data, message = test_api_endpoint(f"{professional_base}{endpoint}", desc)
        print(message)
        if success:
            professional_results[endpoint] = data
    
    # Test Sistema Enterprise
    print(f"\n🚀 SISTEMA ENTERPRISE ({enterprise_base})")
    print("-" * 40)
    
    enterprise_endpoints = [
        ("/api/status", "Status sistema"),
        ("/api/model_performance", "Performance modello"),
        ("/api/health", "Controllo salute")
    ]
    
    enterprise_results = {}
    for endpoint, desc in enterprise_endpoints:
        success, data, message = test_api_endpoint(f"{enterprise_base}{endpoint}", desc)
        print(message)
        if success:
            enterprise_results[endpoint] = data
    
    # Confronto metriche
    print(f"\n📈 CONFRONTO PRESTAZIONI")
    print("-" * 40)
    
    try:
        prof_perf = professional_results.get('/api/model_performance', {})
        ent_perf = enterprise_results.get('/api/model_performance', {})
        
        print(f"Accuratezza Professional: {prof_perf.get('overall_accuracy', 0)*100:.1f}%")
        print(f"Accuratezza Enterprise:   {ent_perf.get('accuracy', 0)*100:.1f}%")
        
        prof_summary = professional_results.get('/api/metrics_summary', {})
        if prof_summary:
            perf_data = prof_summary.get('performance', {})
            print(f"Mercati Professional:     {perf_data.get('mercati_supportati', 0)}")
            print(f"Dataset Professional:     {perf_data.get('partite_analizzate', 0)} partite")
        
        ent_samples = ent_perf.get('training_samples', 0)
        print(f"Dataset Enterprise:       {ent_samples} campioni training")
        
    except Exception as e:
        print(f"❌ Errore nel confronto: {e}")
    
    # Test predizioni
    print(f"\n🎯 TEST PREDIZIONI")
    print("-" * 40)
    
    test_prediction_data = {
        "squadra_casa": "Inter",
        "squadra_ospite": "Milan"
    }
    
    # Test Professional
    try:
        response = requests.post(f"{professional_base}/api/predici", 
                               json=test_prediction_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Professional predizione: {data.get('predizione_text', 'N/A')} (conf: {data.get('confidenza', 0):.3f})")
        else:
            print(f"❌ Professional predizione: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Professional predizione: {e}")
    
    # Test Enterprise
    try:
        response = requests.post(f"{enterprise_base}/api/predict_enterprise", 
                               json=test_prediction_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enterprise predizione: {data.get('prediction_name', 'N/A')} (conf: {data.get('confidence', 0):.3f})")
        else:
            print(f"❌ Enterprise predizione: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Enterprise predizione: {e}")
    
    # Riepilogo finale
    print(f"\n📋 RIEPILOGO FINALE")
    print("-" * 40)
    
    prof_endpoints_ok = len([e for e in professional_endpoints if f"{professional_base}{e[0]}" in [url for url, _, _ in 
                            [test_api_endpoint(f"{professional_base}{ep[0]}", ep[1]) for ep in professional_endpoints] if _]])
    ent_endpoints_ok = len([e for e in enterprise_endpoints if f"{enterprise_base}{e[0]}" in [url for url, _, _ in 
                           [test_api_endpoint(f"{enterprise_base}{ep[0]}", ep[1]) for ep in enterprise_endpoints] if _]])
    
    print(f"Sistema Professional: {prof_endpoints_ok}/{len(professional_endpoints)} API operative")
    print(f"Sistema Enterprise:   {ent_endpoints_ok}/{len(enterprise_endpoints)} API operative")
    
    if prof_endpoints_ok == len(professional_endpoints) and ent_endpoints_ok == len(enterprise_endpoints):
        print("🎉 TUTTI I SISTEMI OPERATIVI - METRICHE COMPLETE DISPONIBILI!")
    else:
        print("⚠️  Alcuni endpoint non sono disponibili")
    
    print(f"\nTest completato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()