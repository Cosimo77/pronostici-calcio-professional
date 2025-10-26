#!/usr/bin/env python3
"""
Test rapido per verificare la standardizzazione dei mercati Over/Under
"""

import sys
import os
sys.path.append('.')

from scripts.mercati_multipli import MercatiMultipli

def test_standardizzazione():
    print("🧪 Test standardizzazione mercati Over/Under")
    print("=" * 50)
    
    try:
        # Inizializza il sistema
        mercati = MercatiMultipli()
        
        # Test partita fittizia
        squadra_casa = "Como"
        squadra_ospite = "Napoli"
        
        print(f"🎯 Test partita: {squadra_casa} vs {squadra_ospite}")
        print()
        
                # Utilizza il metodo pubblico per ottenere tutti i mercati
        risultati = mercati.predici_tutti_mercati(squadra_casa, squadra_ospite)
        
        if not risultati:
            print("❌ Nessun mercato restituito")
            return
        
        # Test mercati Over/Under standardizzati
        mercati_test = [
            ('over_under', 'Over/Under 2.5'),
            ('over_under_15', 'Over/Under 1.5'),
            ('over_under_35', 'Over/Under 3.5'),
            ('primo_tempo_over_under', 'Primo Tempo Over/Under'),
            ('cartellini_over_under', 'Cartellini Over/Under'),
            ('calci_angolo_over_under', 'Corner Over/Under')
        ]
        
        print("📊 MERCATI OVER/UNDER STANDARDIZZATI:")
        print("-" * 40)
        
        for mercato_id, nome in mercati_test:
            if mercato_id in risultati:
                risultato = risultati[mercato_id]
                print(f"✅ {nome}")
                
                # Verifica struttura standardizzata
                if 'probabilita' in risultato:
                    prob = risultato['probabilita']
                    if isinstance(prob, dict) and 'Over' in prob and 'Under' in prob:
                        print(f"   📈 Struttura OK: Over={prob['Over']:.3f}, Under={prob['Under']:.3f}")
                    else:
                        print(f"   ❌ Struttura NON standardizzata: {prob}")
                else:
                    print(f"   ❌ Campo 'probabilita' mancante")
                    
                # Verifica predizione e confidenza
                if 'predizione' in risultato and 'confidenza' in risultato:
                    print(f"   🎯 Predizione: {risultato['predizione']}, Confidenza: {risultato['confidenza']:.1%}")
                else:
                    print(f"   ❌ Campi predizione/confidenza mancanti")
            else:
                print(f"❌ {nome} - Mercato non trovato")
            
            print()
        
        # Test mercati Totali
        mercati_totali = [
            ('cartellini_totali', 'Cartellini Totali'),
            ('calci_angolo_totali', 'Corner Totali')
        ]
        
        print("📋 MERCATI TOTALI STANDARDIZZATI:")
        print("-" * 40)
        
        for mercato_id, nome in mercati_totali:
            if mercato_id in risultati:
                risultato = risultati[mercato_id]
                print(f"✅ {nome}")
                
                # Verifica struttura standardizzata
                if 'probabilita' in risultato:
                    prob = risultato['probabilita']
                    if isinstance(prob, dict) and 'Over' in prob and 'Under' in prob:
                        print(f"   📈 Struttura OK: Over={prob['Over']:.3f}, Under={prob['Under']:.3f}")
                    else:
                        print(f"   ❌ Struttura NON standardizzata: {prob}")
                else:
                    print(f"   ❌ Campo 'probabilita' mancante")
                    
                # Verifica campi specifici
                if mercato_id == 'cartellini_totali':
                    if 'cartellini_attesi' in risultato:
                        print(f"   📋 Cartellini attesi: {risultato['cartellini_attesi']}")
                    else:
                        print(f"   ❌ Campo cartellini_attesi mancante")
                        
                elif mercato_id == 'calci_angolo_totali':
                    if 'corner_attesi' in risultato:
                        print(f"   ⚡ Corner attesi: {risultato['corner_attesi']}")
                    else:
                        print(f"   ❌ Campo corner_attesi mancante")
            else:
                print(f"❌ {nome} - Mercato non trovato")
            
            print()
        
        print("✅ Test standardizzazione completato!")
        print(f"📊 Totale mercati testati: {len(risultati)}")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_standardizzazione()