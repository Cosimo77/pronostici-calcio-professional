#!/usr/bin/env python3
"""
Test debug per API mercati - verifica campi cartellini e corner over/under
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from scripts.mercati_multipli import MercatiMultipli
import json

def test_api_mercati_debug():
    print("🔍 DEBUG API MERCATI - CARTELLINI E CORNER")
    print("=" * 55)
    
    try:
        mercati = MercatiMultipli()
        
        # Test Atalanta vs Inter
        risultati = mercati.predici_tutti_mercati("Atalanta", "Inter")
        
        print("\n📋 STRUTTURA CARTELLINI:")
        if 'cartellini_over_under' in risultati:
            cartellini_ou = risultati['cartellini_over_under']
            print(f"Chiavi disponibili: {list(cartellini_ou.keys())}")
            
            for soglia, data in cartellini_ou.items():
                print(f"\n  {soglia}:")
                print(f"    Campi: {list(data.keys())}")
                print(f"    Over: {data.get('over', 'MANCANTE')}")
                print(f"    Under: {data.get('under', 'MANCANTE')}")
        
        print("\n🚩 STRUTTURA CORNER:")
        if 'calci_angolo_over_under' in risultati:
            corner_ou = risultati['calci_angolo_over_under']
            print(f"Chiavi disponibili: {list(corner_ou.keys())}")
            
            for soglia, data in corner_ou.items():
                print(f"\n  {soglia}:")
                print(f"    Campi: {list(data.keys())}")
                print(f"    Over: {data.get('over', 'MANCANTE')}")
                print(f"    Under: {data.get('under', 'MANCANTE')}")
        
        # Salva per debug
        debug_data = {
            'cartellini_over_under': risultati.get('cartellini_over_under', {}),
            'calci_angolo_over_under': risultati.get('calci_angolo_over_under', {})
        }
        
        with open('debug_mercati_ou.json', 'w') as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Debug salvato in debug_mercati_ou.json")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_mercati_debug()