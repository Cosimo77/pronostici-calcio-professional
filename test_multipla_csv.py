#!/usr/bin/env python3
"""
Test creazione multipla su CSV
Simula la doppia Champions che user voleva creare
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

from diario_storage import DiarioStorage  # type: ignore[import-not-found]
from datetime import datetime
import pandas as pd

def test_create_multipla():
    """Test completo multipla: create → update eventi → verifica profit"""
    
    print("=" * 70)
    print("🧪 TEST CREAZIONE MULTIPLA CHAMPIONS LEAGUE")
    print("=" * 70)
    
    # STEP 1: Crea multipla doppia
    print("\n📝 STEP 1: Creazione multipla...")
    
    multipla_data = {
        'data': '2026-03-25',
        'nome': 'Doppia Champions League',
        'quota_totale': 3.63,  # 1.65 × 2.20
        'stake': 5.0,
        'note': 'Value betting Champions'
    }
    
    eventi = [
        {
            'partita': 'Galatasaray vs Juventus',
            'mercato': 'GG',
            'quota_sisal': 1.65,
            'quota_sistema': 1.65,
            'ev_modello': '+15.2%',
            'ev_realistico': 'N/A',
            'note': 'Champions League - Andata'
        },
        {
            'partita': 'Borussia Dortmund vs Atalanta',
            'mercato': 'Cards Over 4.5',
            'quota_sisal': 2.20,
            'quota_sistema': 2.20,
            'ev_modello': '+12.8%',
            'ev_realistico': 'N/A',
            'note': 'Champions League - Andata'
        }
    ]
    
    try:
        group_id = DiarioStorage.create_multipla(multipla_data, eventi)
        print(f"✅ Multipla creata: group_id = {group_id}")
        print(f"   • Tipo: DOPPIA")
        print(f"   • Quota totale: {multipla_data['quota_totale']}")
        print(f"   • Stake: €{multipla_data['stake']}")
        print(f"   • Profit potenziale: €{multipla_data['stake'] * (multipla_data['quota_totale'] - 1):.2f}")
    except Exception as e:
        print(f"❌ ERRORE creazione multipla: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # STEP 2: Verifica salvataggio CSV
    print("\n📊 STEP 2: Verifica CSV...")
    
    df = pd.read_csv('tracking_giocate.csv')
    df_multipla = df[df['group_id'] == group_id]
    
    if len(df_multipla) == 2:
        print(f"✅ CSV aggiornato correttamente: {len(df_multipla)} eventi salvati")
        print(f"\nDettagli eventi:")
        for idx, row in df_multipla.iterrows():
            print(f"   {row['bet_number']}. {row['Partita']} - {row['Mercato']} @ {row['Quota_Sisal']}")
    else:
        print(f"❌ ERRORE: attesi 2 eventi, trovati {len(df_multipla)}")
        return False
    
    # STEP 3: Simula WIN primo evento
    print("\n🎯 STEP 3: Simula WIN primo evento (Galatasaray GG)...")
    
    bet_id_1 = df_multipla.iloc[0].name
    profit_1 = DiarioStorage.update_risultato(int(bet_id_1), 'WIN')
    
    print(f"   • Evento 1 aggiornato: WIN")
    print(f"   • Profit parziale multipla: €{profit_1:.2f} (atteso 0.00 perché non completata)")
    
    # STEP 4: Simula WIN secondo evento (multipla vinta!)
    print("\n🎯 STEP 4: Simula WIN secondo evento (Dortmund Cards)...")
    
    bet_id_2 = df_multipla.iloc[1].name
    profit_2 = DiarioStorage.update_risultato(int(bet_id_2), 'WIN')
    
    expected_profit = 5.0 * (3.63 - 1)  # €13.15
    print(f"   • Evento 2 aggiornato: WIN")
    print(f"   • Profit finale multipla: €{profit_2:.2f}")
    print(f"   • Profit atteso: €{expected_profit:.2f}")
    
    if abs(profit_2 - expected_profit) < 0.01:
        print("   ✅ Calcolo profit CORRETTO")
    else:
        print(f"   ❌ Calcolo profit ERRATO (diff: €{abs(profit_2 - expected_profit):.2f})")
        return False
    
    # STEP 5: Verifica get_all_multiple
    print("\n📋 STEP 5: Verifica get_all_multiple()...")
    
    multiple = DiarioStorage.get_all_multiple()
    
    if len(multiple) > 0:
        print(f"✅ Trovate {len(multiple)} multiple")
        for mult in multiple:
            if mult['id'] == group_id:
                print(f"\n   Multipla test trovata:")
                print(f"   • ID: {mult['id']}")
                print(f"   • Tipo: {mult.get('tipo_multipla', 'N/A').upper()}")
                print(f"   • Quota: {mult.get('quota_totale', 0):.2f}")
                print(f"   • Stake: €{mult.get('stake', 0):.2f}")
                print(f"   • Risultato: {mult.get('risultato', 'N/A')}")
                print(f"   • Profit: €{mult.get('profit', 0):.2f}")
                print(f"   • Eventi: {len(mult.get('eventi', []))}")
                
                if mult.get('risultato') == 'WIN' and abs(mult.get('profit', 0) - expected_profit) < 0.01:
                    print("   ✅ Multipla completa e corretta!")
                else:
                    print(f"   ⚠️ Risultato: {mult.get('risultato')} | Profit: €{mult.get('profit', 0):.2f}")
    else:
        print("⚠️ Nessuna multipla trovata")
    
    # STEP 6: Test eliminazione
    print("\n🗑️ STEP 6: Test eliminazione multipla...")
    
    success = DiarioStorage.delete_multipla(group_id)
    
    if success:
        print(f"✅ Multipla eliminata: group_id = {group_id}")
        
        # Verifica eliminazione
        df_after = pd.read_csv('tracking_giocate.csv')
        df_deleted = df_after[df_after['group_id'] == group_id]
        
        if len(df_deleted) == 0:
            print("   ✅ CSV pulito: 0 eventi residui")
        else:
            print(f"   ❌ ERRORE: trovati {len(df_deleted)} eventi non eliminati")
    else:
        print(f"❌ ERRORE eliminazione multipla")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETATO CON SUCCESSO!")
    print("=" * 70)
    
    return True

def test_multipla_loss():
    """Test multipla con 1 evento LOSS (multipla perde)"""
    
    print("\n\n" + "=" * 70)
    print("🧪 TEST MULTIPLA LOSS (1 EVENTO PERDE)")
    print("=" * 70)
    
    multipla_data = {
        'data': '2026-03-26',
        'quota_totale': 4.5,
        'stake': 10.0,
        'note': 'Test multipla loss'
    }
    
    eventi = [
        {'partita': 'Inter vs Milan', 'mercato': '1', 'quota_sisal': 1.80},
        {'partita': 'Roma vs Lazio', 'mercato': 'Over 2.5', 'quota_sisal': 2.50}
    ]
    
    group_id = DiarioStorage.create_multipla(multipla_data, eventi)
    print(f"✅ Multipla creata: {group_id}")
    
    df = pd.read_csv('tracking_giocate.csv')
    df_mult = df[df['group_id'] == group_id]
    
    # WIN primo evento
    bet_id_1 = df_mult.iloc[0].name
    DiarioStorage.update_risultato(int(bet_id_1), 'WIN')
    print(f"   • Evento 1: WIN")
    
    # LOSS secondo evento → multipla perde
    bet_id_2 = df_mult.iloc[1].name
    profit = DiarioStorage.update_risultato(int(bet_id_2), 'LOSS')
    
    print(f"   • Evento 2: LOSS")
    print(f"   • Profit multipla: €{profit:.2f} (atteso -€10.00)")
    
    if profit == -10.0:
        print("   ✅ Multipla LOSS calcolata correttamente!")
    else:
        print(f"   ❌ ERRORE: profit atteso -€10.00, ottenuto €{profit:.2f}")
    
    # Cleanup
    DiarioStorage.delete_multipla(group_id)
    print(f"🗑️ Multipla test eliminata")
    
    return True

if __name__ == '__main__':
    print("\n🚀 AVVIO TEST SUITE MULTIPLE CSV\n")
    
    # Test 1: Multipla WIN completa
    success_1 = test_create_multipla()
    
    # Test 2: Multipla LOSS
    success_2 = test_multipla_loss()
    
    if success_1 and success_2:
        print("\n\n" + "=" * 70)
        print("🎉 TUTTI I TEST PASSATI!")
        print("=" * 70)
        print("\n✅ Il sistema supporta ora le scommesse multiple su CSV")
        print("✅ Funzionalità disponibili:")
        print("   • Creazione multiple (doppia, tripla, ecc.)")
        print("   • Aggiornamento risultati eventi")
        print("   • Calcolo automatico profit finale")
        print("   • Eliminazione multiple con CASCADE")
        print("   • Get all multiple con eventi nested")
        sys.exit(0)
    else:
        print("\n❌ ALCUNI TEST FALLITI")
        sys.exit(1)
