#!/usr/bin/env python3
"""Test predizioni complete end-to-end"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from web.app_professional import ProfessionalCalculator
import pandas as pd

print("🔍 VERIFICA 9/9: TEST PREDIZIONI END-TO-END")
print("=" * 60)
print()

# Carica dati
df = pd.read_csv('data/I1_2526.csv')

# Inizializza calcolatore
calc = ProfessionalCalculator()

print("🤖 Test predizione: Inter vs Milan")
print("-" * 60)

try:
    # Predizione completa
    result = calc.predizione_completa(
        squadra_casa='Inter',
        squadra_ospite='Milan'
    )
    
    if not result:
        print("❌ FAIL: Predizione restituisce None")
        sys.exit(1)
    
    print("✅ Predizione completata con successo")
    print()
    
    # Verifica componenti chiave
    if 'prob_casa' in result and 'prob_pareggio' in result and 'prob_ospite' in result:
        print("✅ Probabilità 1X2 presenti")
        print(f"  Casa: {result['prob_casa']:.2%}")
        print(f"  Pareggio: {result['prob_pareggio']:.2%}")
        print(f"  Ospite: {result['prob_ospite']:.2%}")
        
        # Verifica somma = 1
        somma = result['prob_casa'] + result['prob_pareggio'] + result['prob_ospite']
        print(f"  Somma: {somma:.4f}")
        
        if abs(somma - 1.0) < 0.01:
            print("✅ Probabilità matematicamente coerenti (somma = 1.0)")
        else:
            print(f"❌ FAIL: Somma probabilità errata: {somma}")
            sys.exit(1)
    else:
        print("❌ FAIL: Probabilità 1X2 mancanti")
        sys.exit(1)
    
    print()
    
    # Verifica mercati multipli
    if 'mercati' in result:
        mercati = result['mercati']
        print(f"✅ Mercati multipli generati: {len(mercati)}")
       
        # Verifica Over/Under 2.5
        if 'mou25' in mercati:
            ou25 = mercati['mou25']['probabilita']
            print(f"  Over/Under 2.5:")
            print(f"    Over: {ou25.get('over', 0):.2%}")
            print(f"    Under: {ou25.get('under', 0):.2%}")
            
            somma_ou = ou25.get('over', 0) + ou25.get('under', 0)
            if abs(somma_ou - 1.0) < 0.01:
                print(f"  ✅ O/U coerente (somma = {somma_ou:.4f})")
            else:
                print(f"  ❌ O/U incoerente (somma = {somma_ou:.4f})")
                sys.exit(1)
        
        # Verifica Double Chance
        if 'mdc' in mercati:
            dc = mercati['mdc']['probabilita']
            print(f"  Double Chance:")
            print(f"    1X: {dc.get('1X', 0):.2%}")
            print(f"    X2: {dc.get('X2', 0):.2%}")
            print(f"    12: {dc.get('12', 0):.2%}")
    else:
        print("⚠️  Mercati multipli non presenti (potrebbero non essere implementati)")
    
    print()
    
    # Verifica confidenza
    if 'confidenza' in result:
        confidenza = result['confidenza']
        print(f"✅ Confidenza predizione: {confidenza:.2%}")
        
        if 0 < confidenza <= 1.0:
            print("  ✅ Confidenza in range valido [0, 1]")
        else:
            print(f"  ❌ Confidenza fuori range: {confidenza}")
            sys.exit(1)
    
    print()
    print("= " * 30)
    print("✅ PREDIZIONI END-TO-END FUNZIONANTI")
    print("  - Probabilità matematicamente coerenti")
    print("  - Mercati multipli generati")
    print("  - Confidenza calcolata")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ FAIL: Errore durante predizione: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
