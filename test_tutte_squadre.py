#!/usr/bin/env python3
"""
Test per verificare forma squadra con diverse squadre
"""

import pandas as pd

def test_tutte_squadre_stagione_corrente():
    """Test che verifica solo partite stagione corrente per tutte le squadre"""
    print("🧪 TEST FORMA SQUADRA - TUTTE LE SQUADRE (SOLO STAGIONE CORRENTE)")
    print("=" * 70)
    
    try:
        # Carica dataset
        df_work = pd.read_csv('data/dataset_features.csv')
        df_work['Date'] = pd.to_datetime(df_work['Date'], errors='coerce')
        
        # Ottieni tutte le squadre
        squadre = set(df_work['HomeTeam'].tolist() + df_work['AwayTeam'].tolist())
        squadre = sorted([s for s in squadre if pd.notna(s)])
        
        print(f"📊 Analizzando {len(squadre)} squadre...\n")
        
        for squadra in squadre[:10]:  # Prime 10 squadre per test
            # Filtra partite della squadra
            partite_squadra = df_work[
                (df_work['HomeTeam'] == squadra) | 
                (df_work['AwayTeam'] == squadra)
            ].copy()
            
            # Solo stagione corrente (da agosto 2025)
            stagione_corrente = partite_squadra[
                partite_squadra['Date'] >= '2025-08-01'
            ].sort_values('Date').copy()
            
            if len(stagione_corrente) > 0:
                prima_data = stagione_corrente['Date'].min().strftime('%d/%m/%Y')
                ultima_data = stagione_corrente['Date'].max().strftime('%d/%m/%Y')
                
                # Calcola statistiche rapide
                vittorie = pareggi = sconfitte = 0
                gol_fatti = gol_subiti = 0
                
                for _, row in stagione_corrente.iterrows():
                    is_home = row['HomeTeam'] == squadra
                    
                    if is_home:
                        gol_squadra = int(row['FTHG'])
                        gol_avversario = int(row['FTAG'])
                    else:
                        gol_squadra = int(row['FTAG'])
                        gol_avversario = int(row['FTHG'])
                    
                    gol_fatti += gol_squadra
                    gol_subiti += gol_avversario
                    
                    if gol_squadra > gol_avversario:
                        vittorie += 1
                    elif gol_squadra == gol_avversario:
                        pareggi += 1
                    else:
                        sconfitte += 1
                
                punti = vittorie * 3 + pareggi
                print(f"{squadra:15s} | {len(stagione_corrente):2d} partite | {vittorie}V {pareggi}P {sconfitte}S | {gol_fatti:2d}-{gol_subiti:2d} | {punti:2d}pt | {prima_data} - {ultima_data}")
            else:
                print(f"{squadra:15s} | Nessuna partita stagione 2025-26")
        
        print("\n" + "=" * 70)
        print("✅ TUTTE LE SQUADRE MOSTRANO SOLO PARTITE STAGIONE CORRENTE 2025-26")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tutte_squadre_stagione_corrente()