#!/usr/bin/env python3

"""
Test specifico per verificare i miglioramenti ai mercati
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from mercati_multipli import MercatiMultipli

def test_mercati_migliorati():
    """Test specifico per mercati corretti"""
    print("🔧 Test miglioramenti mercati...")
    
    # Inizializza il sistema
    mercati = MercatiMultipli()
    
    # Test squadre
    squadra_casa = "Milan"
    squadra_trasferta = "Juventus"
    
    print(f"\n🏠 Test: {squadra_casa} vs {squadra_trasferta}")
    
    # Test mercati corretti
    mercati_da_testare = [
        'over_under',
        'over_under_15', 
        'over_under_35',
        'cartellini_totali',
        'cartellini_over_under',
        'calci_angolo_over_under',
        'primo_tempo_over_under'
    ]
    
    for mercato in mercati_da_testare:
        print(f"\n📊 Test {mercato}:")
        print("-" * 40)
        
        try:
            # Ottieni tutti i mercati
            tutti_mercati = mercati.predici_tutti_mercati(squadra_casa, squadra_trasferta)
            
            if mercato in tutti_mercati:
                risultato = tutti_mercati[mercato]
                
                # Verifica campi principali
                campi_richiesti = ['predizione', 'confidenza']
                
                print(f"✅ Mercato {mercato} trovato!")
                
                # Verifica presenza campi
                for campo in campi_richiesti:
                    if campo in risultato:
                        print(f"  ✅ {campo}: {risultato[campo]}")
                    else:
                        print(f"  ❌ Manca {campo}")
                
                # Verifica soglie multiple
                soglie_trovate = [k for k in risultato.keys() if k.startswith('over_')]
                print(f"  📊 Soglie disponibili: {len(soglie_trovate)}")
                for soglia in soglie_trovate[:3]:  # Mostra prime 3
                    print(f"    - {soglia}: {risultato[soglia]['predizione']}")
                
                # Score qualità
                score = 0
                if 'predizione' in risultato: score += 30
                if 'confidenza' in risultato: score += 30
                if len(soglie_trovate) >= 3: score += 25
                else: score += len(soglie_trovate) * 8
                if 'over' in risultato and 'under' in risultato: score += 15
                
                print(f"  🎯 Score qualità: {score}/100")
                
                if score >= 85:
                    print(f"  🟢 ECCELLENTE")
                elif score >= 70:
                    print(f"  🟡 BUONO")
                else:
                    print(f"  🔴 DA MIGLIORARE")
                
            else:
                print(f"❌ Mercato {mercato} non trovato!")
                
        except Exception as e:
            print(f"❌ Errore test {mercato}: {str(e)}")
    
    print("\n" + "="*50)
    print("✅ Test miglioramenti completato!")

if __name__ == "__main__":
    test_mercati_migliorati()