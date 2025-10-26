#!/usr/bin/env python3
"""
Test completo del sistema con raccomandazioni
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.append(os.path.dirname(__file__))

from scripts.mercati_multipli import MercatiMultipli
import json

def test_raccomandazioni():
    print("🧪 Test Sistema Raccomandazioni")
    print("=" * 50)
    
    try:
        # Inizializza il sistema
        mercati = MercatiMultipli()
        
        # Test con una partita
        squadra_casa = "Inter"
        squadra_trasferta = "Cremonese"
        
        print(f"🏆 Analisi: {squadra_casa} vs {squadra_trasferta}")
        print("-" * 30)
        
        # Genera pronostici
        risultato = mercati.predici_tutti_mercati(squadra_casa, squadra_trasferta)
        
        print(f"\n🔍 Debug risultato completo:")
        print(f"   Tipo: {type(risultato)}")
        print(f"   Chiavi: {list(risultato.keys()) if isinstance(risultato, dict) else 'Non è un dict'}")
        print(f"   Contenuto: {risultato}")
        
        if risultato and not risultato.get('errore'):
            # Mostra i mercati
            print("\n📊 MERCATI:")
            mercati_keys = [k for k in risultato.keys() if k not in ['metadata', 'raccomandazioni', 'errore']]
            for nome_mercato in mercati_keys:
                dati = risultato[nome_mercato]
                if isinstance(dati, dict) and 'predizione' in dati:
                    confidenza = dati.get('confidenza', 0) * 100 if dati.get('confidenza', 0) <= 1 else dati.get('confidenza', 0)
                    print(f"  {nome_mercato}: {dati['predizione']} ({confidenza:.1f}%)")
            
            # Mostra le raccomandazioni
            print("\n💡 RACCOMANDAZIONI:")
            raccomandazioni = risultato.get('raccomandazioni', [])
            
            if raccomandazioni:
                for i, racc in enumerate(raccomandazioni, 1):
                    print(f"  {i}. [{racc['tipo']}] {racc['mercato']}: {racc['scommessa']}")
                    print(f"     {racc['descrizione']}")
                    print()
            else:
                print("  Nessuna raccomandazione generata")
            
            # Salva il risultato completo
            with open('test_raccomandazioni_result.json', 'w', encoding='utf-8') as f:
                json.dump(risultato, f, indent=2, ensure_ascii=False)
            
            print("✅ Test completato con successo!")
            print(f"📄 Risultati salvati in: test_raccomandazioni_result.json")
            
        else:
            print("❌ Errore: nessun risultato generato")
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_raccomandazioni()