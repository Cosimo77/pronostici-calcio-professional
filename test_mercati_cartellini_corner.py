#!/usr/bin/env python3
"""
Test specifico per i nuovi mercati cartellini e corner
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from scripts.mercati_multipli import MercatiMultipli
import json

def test_nuovi_mercati():
    print("🧪 TEST MERCATI CARTELLINI E CORNER")
    print("=" * 50)
    
    try:
        # Inizializza il sistema
        mercati = MercatiMultipli()
        print("✅ Sistema MercatiMultipli inizializzato")
        
        # Test con una partita
        squadra_casa = "Atalanta"
        squadra_ospite = "Inter"
        
        print(f"\n🔍 Test per: {squadra_casa} vs {squadra_ospite}")
        
        # Ottieni tutti i mercati
        risultati = mercati.predici_tutti_mercati(squadra_casa, squadra_ospite)
        
        # Conta i mercati totali
        mercati_count = len([k for k in risultati.keys() if k not in ['metadata', 'raccomandazioni']])
        print(f"📊 Mercati totali disponibili: {mercati_count}")
        
        # Verifica i nuovi mercati
        print("\n🆕 MERCATI CARTELLINI:")
        if 'cartellini_totali' in risultati:
            cartellini = risultati['cartellini_totali']
            print(f"  ✓ Cartellini Totali:")
            print(f"    - Cartellini previsti: {cartellini.get('cartellini_attesi', 'N/A')}")
            prob = cartellini.get('probabilita', {})
            print(f"    - Probabilità >3.5: {prob.get('Over', 0):.1%}")
            print(f"    - Affidabilità: {cartellini.get('affidabilita', 'N/A')}")
        else:
            print("  ❌ Cartellini Totali NON trovato")
            
        if 'cartellini_over_under' in risultati:
            cartellini_ou = risultati['cartellini_over_under']
            print(f"  ✓ Cartellini Over/Under: {len(cartellini_ou)} soglie")
            for soglia, data in cartellini_ou.items():
                print(f"    - {soglia}: Over {data.get('over', 0):.1%} | Under {data.get('under', 0):.1%}")
        else:
            print("  ❌ Cartellini Over/Under NON trovato")
        
        print("\n🚩 MERCATI CORNER:")
        if 'calci_angolo_totali' in risultati:
            corner = risultati['calci_angolo_totali']
            print(f"  ✓ Corner Totali:")
            print(f"    - Corner previsti: {corner.get('corner_attesi', 'N/A')}")
            prob = corner.get('probabilita', {})
            print(f"    - Probabilità >10.5: {prob.get('Over', 0):.1%}")
            print(f"    - Affidabilità: {corner.get('affidabilita', 'N/A')}")
        else:
            print("  ❌ Corner Totali NON trovato")
            
        if 'calci_angolo_over_under' in risultati:
            corner_ou = risultati['calci_angolo_over_under']
            print(f"  ✓ Corner Over/Under: {len(corner_ou)} soglie")
            for soglia, data in corner_ou.items():
                print(f"    - {soglia}: Over {data.get('over', 0):.1%} | Under {data.get('under', 0):.1%}")
        else:
            print("  ❌ Corner Over/Under NON trovato")
        
        # Salva risultati per debug
        with open('test_risultati_nuovi_mercati.json', 'w') as f:
            json.dump(risultati, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Risultati salvati in test_risultati_nuovi_mercati.json")
        print("✅ Test completato con successo!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nuovi_mercati()