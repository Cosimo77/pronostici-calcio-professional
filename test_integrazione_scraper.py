#!/usr/bin/env python3
"""
Test di integrazione scraper nel sistema web
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import inizializza_sistema, enhanced_predittore, calculator
import json

def test_integrazione():
    print("🧪 TEST INTEGRAZIONE SCRAPER NEL WEB")
    print("=" * 50)
    
    # Inizializza sistema
    print("1. Inizializzazione sistema...")
    success = inizializza_sistema()
    print(f"   Inizializzazione: {'✅' if success else '❌'}")
    
    # Verifica componenti
    print("\n2. Verifica componenti:")
    print(f"   Calculator disponibile: {'✅' if calculator else '❌'}")
    print(f"   Enhanced predittore: {'✅' if enhanced_predittore else '❌'}")
    
    if enhanced_predittore:
        print(f"   Tipo enhanced: {type(enhanced_predittore).__name__}")
    if calculator:
        print(f"   Tipo calculator: {type(calculator).__name__}")
    
    # Test predizione enhanced
    if enhanced_predittore:
        print("\n3. Test predizione enhanced con scraper:")
        try:
            risultato = enhanced_predittore.predici_con_enhancement('Inter', 'Juventus')
            
            print("   📊 RISULTATO ENHANCED:")
            print(f"   Predizione: {risultato['predizione_enhanced']}")
            print(f"   Confidenza: {risultato['confidenza_enhanced']}%")
            print(f"   Probabilità Casa: {risultato['probabilita_enhanced']['vittoria_casa']}%")
            print(f"   Probabilità Pareggio: {risultato['probabilita_enhanced']['pareggio']}%")
            print(f"   Probabilità Trasferta: {risultato['probabilita_enhanced']['vittoria_trasferta']}%")
            
            # Verifica dati scraper integrati
            dati_scraped = risultato.get('dati_scraped', {})
            print(f"\n   🔍 DATI SCRAPER INTEGRATI:")
            print(f"   Quote live: {'✅' if dati_scraped.get('quote_live') else '❌ Vuote'}")
            print(f"   Classifica: {'✅' if dati_scraped.get('classifica') else '❌ Vuota'}")
            print(f"   Infortuni: {len(dati_scraped.get('infortuni', {}).get('casa', []))} casa, {len(dati_scraped.get('infortuni', {}).get('trasferta', []))} trasferta")
            print(f"   Meteo: {dati_scraped.get('meteo', {}).get('condizione', 'N/A')} - {dati_scraped.get('meteo', {}).get('temperatura', 'N/A')}°C")
            print(f"   Sentiment Casa: {dati_scraped.get('sentiment', {}).get('casa', {}).get('mood', 'N/A')}")
            print(f"   Sentiment Trasferta: {dati_scraped.get('sentiment', {}).get('trasferta', {}).get('mood', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Errore test enhanced: {e}")
            import traceback
            traceback.print_exc()
    
    # Test predizione standard (quella che userebbe il web se enhanced non c'è)
    if calculator:
        print("\n4. Test predizione standard (senza scraper):")
        try:
            if hasattr(calculator, 'models'):
                pred, prob = calculator.predici_partita('Inter', 'Juventus', None)
                confidenza = max(prob.values()) if isinstance(prob, dict) else 0.5
            else:
                pred, prob, confidenza = calculator.predici_partita('Inter', 'Juventus')
            
            print("   📊 RISULTATO STANDARD:")
            print(f"   Predizione: {pred}")
            print(f"   Confidenza: {confidenza * 100:.1f}%")
            print(f"   Probabilità: {prob}")
            
        except Exception as e:
            print(f"   ❌ Errore test standard: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completato!")

if __name__ == "__main__":
    test_integrazione()