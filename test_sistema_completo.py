#!/usr/bin/env python3
"""
Test Completo Sistema Pronostici
Verifica tutte le funzionalità del sistema
"""

import requests
import json
import sys
import time

def test_api(url, nome_test):
    """Testa una singola API"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {nome_test}: OK")
            return True, data
        else:
            print(f"❌ {nome_test}: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ {nome_test}: Errore - {e}")
        return False, None

def test_webpage(url, nome_test):
    """Testa una pagina web"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {nome_test}: OK ({len(response.text)} bytes)")
            return True
        else:
            print(f"❌ {nome_test}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {nome_test}: Errore - {e}")
        return False

def main():
    """Test principale"""
    print("🚀 Test Completo Sistema Pronostici Serie A")
    print("=" * 60)
    
    base_url = "http://localhost:5003"
    successi = 0
    test_totali = 0
    
    # Test API
    print("\n📊 Test API:")
    
    test_totali += 1
    success, data = test_api(f"{base_url}/api/statistiche", "API Statistiche")
    if success and data:
        successi += 1
        print(f"   📈 Partite totali: {data['stats_generali']['totale_partite']}")
        print(f"   ⚽ Media gol: {data['stats_generali']['media_gol_partita']}")
    
    test_totali += 1
    success, data = test_api(f"{base_url}/api/squadre", "API Squadre")
    if success and data:
        successi += 1
        print(f"   🏆 Squadre Serie A: {len(data['squadre'])}")
        if 'Pisa' in data['squadre']:
            print(f"   ✅ Pisa presente nel campionato")
        else:
            print(f"   ⚠️ Pisa non trovata")
    
    test_totali += 1
    success, data = test_api(f"{base_url}/api/forma/Pisa", "API Forma Pisa")
    if success and data:
        successi += 1
        print(f"   📊 Forma Pisa: {data['forma']}")
        print(f"   📈 Record: {data['vittorie']}V-{data['pareggi']}P-{data['sconfitte']}S")
    
    test_totali += 1
    success, data = test_api(f"{base_url}/api/forma/Inter", "API Forma Inter")
    if success and data:
        successi += 1
        print(f"   📊 Forma Inter: {data['forma']}")
    
    # Test Pagine Web
    print("\n🌐 Test Pagine Web:")
    
    test_totali += 1
    if test_webpage(f"{base_url}/", "Pagina Principale"):
        successi += 1
    
    test_totali += 1
    if test_webpage(f"{base_url}/test_finale.html", "Pagina Test"):
        successi += 1
    
    test_totali += 1
    if test_webpage(f"{base_url}/web/templates/index.html", "Interfaccia Web"):
        successi += 1
    
    # Risultati finali
    print("\n" + "=" * 60)
    print(f"📊 RISULTATI: {successi}/{test_totali} test superati")
    
    if successi == test_totali:
        print("🎉 TUTTI I TEST SUPERATI! Sistema completamente funzionante!")
        print("\n🌐 Accedi al sistema:")
        print(f"   • Interfaccia principale: {base_url}/web/templates/index.html")
        print(f"   • Test API: {base_url}/test_finale.html")
        print(f"   • Pagina root: {base_url}/")
        return 0
    else:
        print(f"⚠️ {test_totali - successi} test falliti. Controlla il server.")
        return 1

if __name__ == "__main__":
    sys.exit(main())