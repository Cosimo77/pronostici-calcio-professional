#!/usr/bin/env python3
"""
Script per convertire le 12 scommesse PENDING con formato risultato partita
Logica: Se Predizione == Risultato_Reale → WIN, altrimenti → LOSS
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from database import get_db_connection, is_db_available

def convert_pending_to_wl():
    """Converte le 12 bet PENDING con formato risultato partita H/D/A/GG/NG/Over/Under"""
    
    # 1. Carica CSV per mappare predizione → risultato reale
    csv_path = "tracking_predictions_live.csv"
    df = pd.read_csv(csv_path)
    
    # Filtra solo scommesse con formato diverso da W/L
    other_format = df[df['Risultato_Reale'].notna() & 
                      ~df['Risultato_Reale'].isin(['W', 'L'])]
    
    print(f"🔍 Trovate {len(other_format)} scommesse con formato risultato partita\n")
    
    # 2. Connetti al database
    if not is_db_available():
        print("❌ Database non disponibile")
        return False
    
    # 3. Mapping termini ITA → ENG per 1X2
    mapping_1x2 = {
        'Casa': 'H',    # Home
        'Pareggio': 'D', # Draw
        'Ospite': 'A',   # Away
        'Trasferta': 'A'
    }
    
    # 4. Per ogni scommessa, determina WIN/LOSS
    updates = []
    
    for idx, row in other_format.iterrows():
        casa = str(row.get('Casa', ''))
        ospite = str(row.get('Ospite', ''))
        data = str(row.get('Data', ''))
        mercato = str(row.get('Mercato', ''))
        predizione = str(row.get('Predizione', ''))
        risultato_reale = str(row.get('Risultato_Reale', ''))
        profit = float(row.get('Profit', 0))
        
        # Normalizza predizione se è 1X2
        predizione_norm = mapping_1x2.get(predizione, predizione)
        
        # Logica conversione: predizione normalizzata == risultato reale
        if predizione_norm == risultato_reale:
            nuovo_risultato = 'WIN'
        else:
            nuovo_risultato = 'LOSS'
        
        # VERIFICA COERENZA: Se profit positivo DEVE essere WIN
        if profit > 0 and nuovo_risultato == 'LOSS':
            print(f"⚠️  INCOERENZA: profit +{profit:.2f}€ ma risultato LOSS!")
            print(f"    Forzo a WIN (profit positivo = scommessa vinta)")
            nuovo_risultato = 'WIN'
        elif profit < 0 and nuovo_risultato == 'WIN':
            print(f"⚠️  INCOERENZA: profit {profit:.2f}€ ma risultato WIN!")
            print(f"    Forzo a LOSS (profit negativo = scommessa persa)")
            nuovo_risultato = 'LOSS'
        
        # Build partita string per matching
        partita = f"{casa} vs {ospite}"
        
        updates.append({
            'data': data,
            'partita': partita,
            'mercato': mercato,
            'predizione': predizione,
            'risultato_reale': risultato_reale,
            'nuovo_risultato': nuovo_risultato,
            'profit': profit
        })
        
        status_emoji = "✅" if nuovo_risultato == 'WIN' else "❌"
        print(f"{status_emoji} {data} | {casa} vs {ospite}")
        print(f"   Mercato: {mercato} | Predizione: {predizione} → {predizione_norm}")
        print(f"   Risultato partita: {risultato_reale}")
        print(f"   Match: {predizione_norm} == {risultato_reale} → {nuovo_risultato}")
        print(f"   Profit: {profit:+.2f}€\n")
    
    # 4. Conferma utente
    win_count = sum(1 for u in updates if u['nuovo_risultato'] == 'WIN')
    loss_count = sum(1 for u in updates if u['nuovo_risultato'] == 'LOSS')
    total_profit = sum(u['profit'] for u in updates)
    
    print("=" * 80)
    print(f"📊 RIEPILOGO CONVERSIONE:")
    print(f"   Totale: {len(updates)} scommesse")
    print(f"   WIN: {win_count} | LOSS: {loss_count}")
    print(f"   Profit: {total_profit:+.2f}€")
    print("=" * 80)
    
    risposta = input("\n✋ Procedo con l'aggiornamento database? (y/n): ")
    if risposta.lower() != 'y':
        print("❌ Operazione annullata")
        return False
    
    # 5. Aggiorna database
    updated_count = 0
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for update in updates:
                # Match su data + partita + mercato (le PENDING sono marzo)
                cur.execute("""
                    UPDATE bets 
                    SET risultato = %s
                    WHERE risultato = 'PENDING'
                      AND partita LIKE %s
                      AND mercato LIKE %s
                    RETURNING id;
                """, (
                    update['nuovo_risultato'],
                    f"%{update['partita'].split(' vs ')[0]}%",  # Match casa
                    f"%{update['mercato']}%"
                ))
                
                result = cur.fetchone()
                if result:
                    updated_count += 1
                    print(f"✅ Aggiornata bet ID {result[0]}: {update['partita']} → {update['nuovo_risultato']}")
                else:
                    print(f"⚠️  Non trovata: {update['partita']} - {update['mercato']}")
            
            conn.commit()
    
    print(f"\n🎉 COMPLETATO: {updated_count}/{len(updates)} bet aggiornate!")
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("CONVERSIONE BET PENDING → WIN/LOSS")
    print("=" * 80)
    print()
    
    success = convert_pending_to_wl()
    
    if success:
        print("\n✅ Verifica con: curl .../api/diario/stats")
        print("   Dovresti vedere: total: 28, completed: 28")
