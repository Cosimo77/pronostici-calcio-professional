#!/usr/bin/env python3
"""
Test per verificare che forma squadra mostri SOLO partite stagione corrente
"""

import pandas as pd

def test_solo_stagione_corrente():
    """Test che verifica solo partite stagione corrente 2025-26"""
    print("🧪 TEST FORMA SQUADRA - SOLO STAGIONE CORRENTE")
    print("=" * 60)
    
    try:
        squadra = "Atalanta"
        print(f"🏟️ Analizzando squadra: {squadra}")
        
        # Carica dataset
        df_work = pd.read_csv('data/dataset_features.csv')
        df_work['Date'] = pd.to_datetime(df_work['Date'], errors='coerce')
        
        # Filtra partite della squadra
        partite_squadra = df_work[
            (df_work['HomeTeam'] == squadra) | 
            (df_work['AwayTeam'] == squadra)
        ].copy()
        
        print(f"📊 Partite totali {squadra}: {len(partite_squadra)}")
        
        # NUOVA STRATEGIA: Solo stagione corrente
        stagione_corrente = partite_squadra[
            partite_squadra['Date'] >= '2025-08-01'
        ].sort_values('Date').copy()
        
        print(f"📅 Partite stagione 2025-26: {len(stagione_corrente)}")
        
        # Usa SOLO le partite della stagione corrente
        partite_finali = stagione_corrente.copy()
        
        print(f"\n🎯 PARTITE FINALI (SOLO STAGIONE CORRENTE): {len(partite_finali)}")
        print("=" * 60)
        
        if len(partite_finali) == 0:
            print("⚠️ Nessuna partita nella stagione corrente")
            return
        
        # Mostra tutte le partite della stagione corrente
        vittorie = pareggi = sconfitte = 0
        gol_fatti = gol_subiti = 0
        
        for i, (_, row) in enumerate(partite_finali.iterrows(), 1):
            is_home = row['HomeTeam'] == squadra
            
            if is_home:
                gol_squadra = int(row['FTHG'])
                gol_avversario = int(row['FTAG'])
                avversario = row['AwayTeam']
                casa_fuori = "CASA"
            else:
                gol_squadra = int(row['FTAG'])
                gol_avversario = int(row['FTHG'])
                avversario = row['HomeTeam']
                casa_fuori = "FUORI"
            
            gol_fatti += gol_squadra
            gol_subiti += gol_avversario
            
            if gol_squadra > gol_avversario:
                vittorie += 1
                risultato = "V"
            elif gol_squadra == gol_avversario:
                pareggi += 1
                risultato = "P"
            else:
                sconfitte += 1
                risultato = "S"
            
            data_str = row['Date'].strftime('%d/%m/%Y') if pd.notna(row['Date']) else 'N/A'
            
            # Verifica che sia davvero stagione 2025-26
            if row['Date'] < pd.to_datetime('2025-08-01'):
                print(f"❌ ERRORE: Partita {data_str} non è stagione corrente!")
            else:
                print(f"{i:2d}. {data_str} | {squadra} vs {avversario:12s} ({casa_fuori:5s}) | {gol_squadra}-{gol_avversario} | {risultato}")
        
        print("=" * 60)
        print(f"📈 STATISTICHE STAGIONE CORRENTE 2025-26:")
        print(f"   🏆 Vittorie: {vittorie}")
        print(f"   ⚖️ Pareggi: {pareggi}")
        print(f"   💔 Sconfitte: {sconfitte}")
        print(f"   ⚽ Goal fatti: {gol_fatti}")
        print(f"   🥅 Goal subiti: {gol_subiti}")
        if len(partite_finali) > 0:
            print(f"   📊 Media goal fatti: {gol_fatti/len(partite_finali):.2f}")
            print(f"   📊 Media goal subiti: {gol_subiti/len(partite_finali):.2f}")
        print(f"   🎯 Punti totali: {vittorie*3 + pareggi}")
        
        # Verifica date
        prima_data = partite_finali['Date'].min()
        ultima_data = partite_finali['Date'].max()
        print(f"   📅 Prima partita: {prima_data.strftime('%d/%m/%Y')}")
        print(f"   📅 Ultima partita: {ultima_data.strftime('%d/%m/%Y')}")
        
        if prima_data >= pd.to_datetime('2025-08-01'):
            print("   ✅ TUTTE LE PARTITE SONO DELLA STAGIONE 2025-26")
        else:
            print("   ❌ ALCUNE PARTITE NON SONO DELLA STAGIONE CORRENTE")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_solo_stagione_corrente()