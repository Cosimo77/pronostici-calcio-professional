#!/usr/bin/env python3
"""
Consolida tutti i dati tracking da FASE1 + FASE2 in un unico CSV
Recupera tutte le bet disponibili dai file locali
"""

import pandas as pd
from datetime import datetime

def consolidate_tracking_files():
    """Unisce tracking_giocate.csv + tracking_fase2_febbraio2026.csv"""
    
    print("🔄 Consolidamento dati tracking...")
    print("="*60)
    
    all_bets = []
    
    # 1. Carica FASE 1 (tracking_giocate.csv)
    try:
        df_fase1 = pd.read_csv('tracking_giocate.csv')
        print(f"\n📂 tracking_giocate.csv (FASE 1):")
        print(f"   Righe: {len(df_fase1)}")
        
        # Converti in formato standardizzato
        for _, row in df_fase1.iterrows():
            all_bets.append({
                'Data': row['Data'],
                'Partita': row['Partita'],
                'Mercato': row['Mercato'],
                'Quota': row.get('Quota_Sisal', row.get('Quota_Sistema', 0)),
                'EV_Modello': row.get('EV_Modello', 'N/A'),
                'EV_Realistico': row.get('EV_Realistico', 'N/A'),
                'Stake': row.get('Stake', 0),
                'Risultato': row.get('Risultato', 'PENDING'),
                'Profit': row.get('Profit', 0.0),
                'Note': row.get('Note', ''),
                'Fonte': 'FASE1'
            })
    except FileNotFoundError:
        print("   ⚠️  File non trovato")
    
    # 2. Carica FASE 2 (tracking_fase2_febbraio2026.csv)
    try:
        df_fase2 = pd.read_csv('tracking_fase2_febbraio2026.csv')
        print(f"\n📂 tracking_fase2_febbraio2026.csv (FASE 2):")
        print(f"   Righe totali: {len(df_fase2)}")
        
        # Filtra solo bet GIOCATE (colonna Giocata=SI o Risultato!=PENDING)
        giocate = df_fase2[
            (df_fase2['Giocata'].str.upper() == 'SI') | 
            (df_fase2['Risultato'].str.upper() != 'PENDING')
        ]
        print(f"   Bet giocate: {len(giocate)}")
        
        for _, row in giocate.iterrows():
            partita = f"{row['Casa']} vs {row['Ospite']}"
            mercato = f"{row['Mercato']} - {row['Esito']}" if row['Mercato'] != "1X2" else row['Esito']
            
            all_bets.append({
                'Data': row['Data'],
                'Partita': partita,
                'Mercato': mercato,
                'Quota': row['Quota'],
                'EV_Modello': f"+{row['EV_%']}%" if row['EV_%'] > 0 else f"{row['EV_%']}%",
                'EV_Realistico': 'N/A',
                'Stake': row.get('Stake_Suggerito', 10.0),
                'Risultato': row['Risultato'],
                'Profit': row.get('Profit_Loss', 0.0),
                'Note': row.get('Note', ''),
                'Fonte': 'FASE2'
            })
    except FileNotFoundError:
        print("   ⚠️  File non trovato")
    
    # 3. Crea DataFrame consolidato
    df_consolidated = pd.DataFrame(all_bets)
    
    print(f"\n📊 Totale bet consolidate: {len(df_consolidated)}")
    print(f"   - FASE1: {len(df_consolidated[df_consolidated['Fonte']=='FASE1'])}")
    print(f"   - FASE2: {len(df_consolidated[df_consolidated['Fonte']=='FASE2'])}")
    
    # Breakdown per status
    pending = len(df_consolidated[df_consolidated['Risultato']=='PENDING'])
    completed = len(df_consolidated[df_consolidated['Risultato']!='PENDING'])
    print(f"\n   Status:")
    print(f"   - PENDING: {pending}")
    print(f"   - Completate: {completed}")
    
    if completed > 0:
        wins = len(df_consolidated[df_consolidated['Risultato']=='WIN'])
        losses = len(df_consolidated[df_consolidated['Risultato']=='LOSS'])
        win_rate = (wins / completed * 100) if completed > 0 else 0
        total_profit = df_consolidated['Profit'].sum()
        
        print(f"   - WIN: {wins}")
        print(f"   - LOSS: {losses}")
        print(f"   - Win Rate: {win_rate:.1f}%")
        print(f"   - Profit totale: €{total_profit:.2f}")
    
    # 4. Backup file esistente
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        import os
        os.rename('tracking_giocate.csv', f'tracking_giocate_backup_{timestamp}.csv')
        print(f"\n💾 Backup creato: tracking_giocate_backup_{timestamp}.csv")
    except FileNotFoundError:
        pass
    
    # 5. Salva consolidato (formato FASE1 per compatibilità)
    df_output = df_consolidated[[
        'Data', 'Partita', 'Mercato', 'Quota', 'EV_Modello', 
        'EV_Realistico', 'Stake', 'Risultato', 'Profit', 'Note'
    ]].copy()
    
    # Rinomina colonne per compatibilità
    df_output.columns = [
        'Data', 'Partita', 'Mercato', 'Quota_Sisal', 'EV_Modello',
        'EV_Realistico', 'Stake', 'Risultato', 'Profit', 'Note'
    ]
    df_output['Quota_Sistema'] = df_output['Quota_Sisal']
    
    # Riordina colonne
    df_output = df_output[[
        'Data', 'Partita', 'Mercato', 'Quota_Sistema', 'Quota_Sisal',
        'EV_Modello', 'EV_Realistico', 'Stake', 'Risultato', 'Profit', 'Note'
    ]]
    
    df_output.to_csv('tracking_giocate.csv', index=False)
    print(f"\n✅ Salvato tracking_giocate.csv con {len(df_output)} bet")
    
    print("\n" + "="*60)
    print("🎉 Consolidamento completato!")
    print("\n📋 Prossimi step:")
    print("   1. Verifica tracking_giocate.csv consolidato")
    print("   2. Disabilita DATABASE_URL su Render")
    print("   3. App userà CSV come storage permanente (GRATIS)")

if __name__ == '__main__':
    consolidate_tracking_files()
