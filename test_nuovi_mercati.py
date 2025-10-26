#!/usr/bin/env python3
"""
Test dei nuovi mercati aggiunti al sistema
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from mercati_multipli import MercatiMultipli
import json

def test_nuovi_mercati():
    print("🎯 Testing dei nuovi mercati di scommesse")
    print("=" * 60)
    
    # Crea predittore
    predittore = MercatiMultipli()
    
    # Test con partite realistiche
    partite_test = [
        ('Inter', 'Milan'),  # Derby della Madonnina
        ('Juventus', 'Napoli'),  # Big match
        ('Atalanta', 'Roma'),  # Squadre offensive
        ('Cagliari', 'Cremonese'),  # Squadre con stili diversi
        ('Fiorentina', 'Lazio')  # Match equilibrato
    ]
    
    print(f"📊 Testando {len(partite_test)} partite con i nuovi mercati:")
    print()
    
    for i, (casa, trasferta) in enumerate(partite_test, 1):
        print(f"🏆 PARTITA {i}: {casa} vs {trasferta}")
        print("-" * 50)
        
        try:
            # Predici tutti i mercati
            mercati = predittore.predici_tutti_mercati(casa, trasferta)
            
            # Mostra i nuovi mercati aggiunti
            nuovi_mercati = [
                'over_under_15', 'over_under_35', 'prima_squadra_gol', 
                'clean_sheet', 'primo_tempo_1x2', 'primo_tempo_over_under'
            ]
            
            for mercato in nuovi_mercati:
                if mercato in mercati:
                    print(f"  {mercato.upper().replace('_', ' ')}: {mercati[mercato]['predizione']}")
                    print(f"    Confidenza: {mercati[mercato]['confidenza']:.1%}")
                    print(f"    Valore: {mercati[mercato]['valore_scommessa']}")
                    print()
                else:
                    print(f"  ❌ {mercato} non trovato")
                    
        except Exception as e:
            print(f"  ❌ Errore: {e}")
            
        print()
    
    # Test del totale mercati
    print(f"📈 RIASSUNTO MERCATI TOTALI")
    print("-" * 30)
    try:
        mercati_test = predittore.predici_tutti_mercati('Inter', 'Milan')
        print(f"✅ Mercati totali implementati: {len(mercati_test)}")
        print(f"📋 Lista mercati:")
        for nome_mercato in mercati_test.keys():
            print(f"   - {nome_mercato}")
    except Exception as e:
        print(f"❌ Errore nel test totale: {e}")

if __name__ == "__main__":
    test_nuovi_mercati()