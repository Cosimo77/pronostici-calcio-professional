#!/usr/bin/env python3
"""
Test API Mercati con curl per verificare risposta JSON
"""
import json
import subprocess
import time
import sys

def test_api_call():
    print("🧪 TEST API MERCATI VIA CURL")
    print("=" * 40)
    
    # Attende che il server sia pronto
    time.sleep(2)
    
    try:
        # Esegue chiamata API
        curl_cmd = [
            'curl', '-s', 
            'http://localhost:5040/api/mercati',
            '-X', 'POST',
            '-H', 'Content-Type: application/json',
            '-d', '{"squadra_casa":"Atalanta","squadra_ospite":"Inter"}'
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Errore curl: {result.stderr}")
            return
        
        # Parse JSON
        data = json.loads(result.stdout)
        
        print("✅ Risposta API ricevuta")
        print(f"📊 Mercati totali: {len([k for k in data.keys() if k not in ['metadata', 'raccomandazioni']])}")
        
        # Test cartellini
        if 'cartellini_over_under' in data:
            print("\n🆕 CARTELLINI OVER/UNDER:")
            cartellini = data['cartellini_over_under']
            for soglia, vals in cartellini.items():
                over_val = vals.get('over', 'MANCANTE')
                under_val = vals.get('under', 'MANCANTE')
                print(f"  {soglia}: Over={over_val}, Under={under_val}")
        else:
            print("❌ cartellini_over_under NON TROVATO")
        
        # Test corner
        if 'calci_angolo_over_under' in data:
            print("\n🚩 CORNER OVER/UNDER:")
            corner = data['calci_angolo_over_under']
            for soglia, vals in corner.items():
                over_val = vals.get('over', 'MANCANTE')
                under_val = vals.get('under', 'MANCANTE')
                print(f"  {soglia}: Over={over_val}, Under={under_val}")
        else:
            print("❌ calci_angolo_over_under NON TROVATO")
        
        print("\n✅ Test completato")
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout - Server non risponde")
    except json.JSONDecodeError as e:
        print(f"❌ Errore JSON: {e}")
        print(f"Response: {result.stdout[:500]}")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    test_api_call()