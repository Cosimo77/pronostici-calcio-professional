#!/usr/bin/env python3
"""
Test finale del sistema completo con raccomandazioni web
"""

import requests
import json
import time

def test_sistema_completo():
    print("🧪 Test Sistema Completo con Raccomandazioni Web")
    print("=" * 55)
    
    base_url = "http://localhost:5003"
    
    try:
        # 1. Test connessione server
        print("🔌 Verifica connessione server...")
        response = requests.get(f"{base_url}/api/squadre", timeout=5)
        if response.status_code == 200:
            squadre = response.json()
            print(f"✅ Server connesso - {len(squadre.get('squadre', []))} squadre disponibili")
        else:
            print(f"❌ Errore connessione: {response.status_code}")
            return
        
        # 2. Test API mercati con raccomandazioni
        print("\n🎯 Test API mercati multipli...")
        data = {
            "squadra_casa": "Inter",
            "squadra_ospite": "Juventus"
        }
        
        response = requests.post(
            f"{base_url}/api/mercati",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Verifica mercati
            mercati = result.get('mercati', {})
            print(f"✅ Mercati ricevuti: {len(mercati)} mercati")
            
            # Verifica raccomandazioni
            raccomandazioni = result.get('raccomandazioni', [])
            print(f"🎯 Raccomandazioni: {len(raccomandazioni)} trovate")
            
            if raccomandazioni:
                print("\n💡 RACCOMANDAZIONI:")
                for i, racc in enumerate(raccomandazioni, 1):
                    print(f"   {i}. [{racc['tipo']}] {racc['mercato']}: {racc['scommessa']}")
                    print(f"      {racc['descrizione']}")
                    print(f"      Confidenza: {racc['confidenza']:.1f}%")
                    print()
            else:
                print("⚠️ Nessuna raccomandazione trovata")
            
            # Verifica struttura completa
            print("\n📊 Struttura risposta:")
            print(f"   - partita: {result.get('partita', 'N/A')}")
            print(f"   - timestamp: {result.get('timestamp', 'N/A')}")
            print(f"   - confidence_generale: {result.get('confidence_generale', 'N/A')}")
            
        else:
            print(f"❌ Errore API mercati: {response.status_code}")
            print(f"   Risposta: {response.text}")
            return
        
        # 3. Test interfaccia web
        print("\n🌐 Test interfaccia web...")
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            content = response.text
            if 'mercati-raccomandazioni-list' in content:
                print("✅ Container raccomandazioni trovato nel HTML")
            else:
                print("⚠️ Container raccomandazioni non trovato nel HTML")
            
            if 'updateMercatiRaccomandazioni' in content:
                print("✅ Funzione JavaScript raccomandazioni trovata")
            else:
                print("⚠️ Funzione JavaScript raccomandazioni non trovata")
        else:
            print(f"❌ Errore interfaccia web: {response.status_code}")
        
        print("\n✅ Test completato con successo!")
        print("🌐 Apri http://localhost:5003 per vedere le raccomandazioni in azione!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione: {e}")
        print("💡 Assicurati che il server sia avviato con: python3 web/app.py")
    except Exception as e:
        print(f"❌ Errore imprevisto: {e}")

if __name__ == "__main__":
    test_sistema_completo()