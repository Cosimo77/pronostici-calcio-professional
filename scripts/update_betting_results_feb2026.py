#!/usr/bin/env python3
"""
Aggiorna tracking_giocate.csv con risultati reali partite febbraio 2026
"""

import pandas as pd
import csv

# Risultati reali da dataset I1_2526.csv
results = {
    'Como vs Fiorentina': {
        'data': '2026-02-14',
        'risultato_reale': '1-2',  # Away win
        'ftr': 'A'
    },
    'Udinese vs Sassuolo': {
        'data': '2026-02-15',
        'risultato_reale': '1-2',  # Away win
        'ftr': 'A'
    },
    'Parma vs Verona': {
        'data': '2026-02-15',
        'risultato_reale': '2-1',  # Home win (3 gol totali)
        'ftr': 'H'
    },
    'Cremonese vs Genoa': {
        'data': '2026-02-15',
        'risultato_reale': '0-0',  # Draw
        'ftr': 'D'
    },
    'Napoli vs Roma': {
        'data': '2026-02-15',
        'risultato_reale': '2-2',  # Draw
        'ftr': 'D'
    }
}

def evaluate_bet(partita, mercato, quota, stake, ftr, gol_totali):
    """Valuta esito puntata"""
    
    # X2 (Draw or Away)
    if mercato == 'X2':
        win = ftr in ['D', 'A']
        profit = (stake * quota - stake) if win else -stake
        return 'WIN' if win else 'LOSS', profit
    
    # 1X (Home or Draw)
    if mercato == '1X':
        win = ftr in ['H', 'D']
        profit = (stake * quota - stake) if win else -stake
        return 'WIN' if win else 'LOSS', profit
    
    # Pareggio
    if mercato == 'Pareggio':
        win = ftr == 'D'
        profit = (stake * quota - stake) if win else -stake
        return 'WIN' if win else 'LOSS', profit
    
    # Over/Under 2.5
    if 'Over/Under 2.5' in mercato:
        if 'Over' in mercato:
            win = gol_totali > 2.5
        else:  # Under
            win = gol_totali < 2.5
        profit = (stake * quota - stake) if win else -stake
        return 'WIN' if win else 'LOSS', profit
    
    # Double Chance - 1X
    if 'Double Chance' in mercato and '1X' in mercato:
        win = ftr in ['H', 'D']
        profit = (stake * quota - stake) if win else -stake
        return 'WIN' if win else 'LOSS', profit
    
    return 'PENDING', 0.0

# Leggi tracking
df = pd.read_csv('tracking_giocate.csv')

print("🔄 Aggiornamento risultati puntate febbraio 2026...\n")

updated = 0
total_profit_change = 0.0

for idx, row in df.iterrows():
    partita = row['Partita']
    
    if partita in results and row['Risultato'] == 'PENDING':
        info = results[partita]
        mercato = row['Mercato']
        quota = float(row['Quota_Sisal'])
        stake = float(row['Stake'])
        
        # Parse gol totali
        gol_casa, gol_ospite = map(int, info['risultato_reale'].split('-'))
        gol_totali = gol_casa + gol_ospite
        
        # Valuta puntata
        esito, profit = evaluate_bet(partita, mercato, quota, stake, info['ftr'], gol_totali)
        
        # Aggiorna riga
        df.at[idx, 'Risultato'] = esito
        df.at[idx, 'Profit'] = profit
        
        simbolo = '✅' if esito == 'WIN' else '❌'
        print(f"{simbolo} {partita} ({info['risultato_reale']})")
        print(f"   Mercato: {mercato} @ {quota}")
        print(f"   Stake: €{stake:.2f} → Esito: {esito}")
        print(f"   Profit: {profit:+.2f}€\n")
        
        updated += 1
        total_profit_change += profit

# Salva
df.to_csv('tracking_giocate.csv', index=False)

print(f"{'='*60}")
print(f"✅ Aggiornamento completato: {updated} puntate")
print(f"💰 Profit totale aggiunto: {total_profit_change:+.2f}€")
print(f"{'='*60}")

# Statistiche finali
completate = df[df['Risultato'] != 'PENDING']
wins = len(completate[completate['Risultato'] == 'WIN'])
losses = len(completate[completate['Risultato'] == 'LOSS'])
win_rate = (wins / len(completate) * 100) if len(completate) > 0 else 0
profit_totale = completate['Profit'].sum()
roi = (profit_totale / completate['Stake'].sum() * 100) if completate['Stake'].sum() > 0 else 0

print(f"\n📊 Statistiche finali:")
print(f"   Puntate completate: {len(completate)}")
print(f"   Win/Loss: {wins}W - {losses}L")
print(f"   Win Rate: {win_rate:.1f}%")
print(f"   Profit totale: {profit_totale:+.2f}€")
print(f"   ROI: {roi:+.1f}%")
