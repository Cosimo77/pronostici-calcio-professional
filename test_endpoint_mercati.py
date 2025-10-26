#!/usr/bin/env python3
"""
Test veloce dell'endpoint mercati multipli
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app

def test_endpoint_mercati():
    """Testa che l'endpoint mercati sia registrato"""
    print("🔍 Test registrazione endpoint mercati")
    print("=" * 40)
    
    # Lista tutti gli endpoint Flask
    print("\n📋 Endpoint registrati:")
    for rule in app.url_map.iter_rules():
        methods = ','.join((rule.methods or set()) - {'HEAD', 'OPTIONS'})
        print(f"   {rule.rule} [{methods}]")
    
    # Cerca specificamente l'endpoint mercati
    mercati_found = False
    for rule in app.url_map.iter_rules():
        if '/api/mercati' in rule.rule:
            mercati_found = True
            print(f"\n✅ Endpoint mercati trovato: {rule.rule}")
            print(f"   Metodi: {rule.methods}")
            break
    
    if not mercati_found:
        print("\n❌ Endpoint /api/mercati NON trovato!")
        print("Gli endpoint API disponibili sono:")
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                print(f"   {rule.rule}")
    
    print("\n🔍 Controllo variabili globali:")
    from web.app import MERCATI_AVAILABLE, mercati_sistema
    print(f"   MERCATI_AVAILABLE: {MERCATI_AVAILABLE}")
    print(f"   mercati_sistema: {mercati_sistema is not None}")
    
    if MERCATI_AVAILABLE:
        print("✅ Sistema mercati abilitato")
    else:
        print("❌ Sistema mercati NON abilitato")

if __name__ == "__main__":
    test_endpoint_mercati()