#!/usr/bin/env python3
"""
AGGIORNA TRACKING FASE 2 - Calcola P&L in base ai risultati
Legge tracking_fase2_febbraio2026.csv e aggiorna Profit/Loss e Bankroll
"""
import csv
import os
from datetime import datetime

def aggiorna_tracking():
    """Ricalcola P&L e bankroll in base ai risultati aggiornati"""
    
    input_file = 'tracking_fase2_febbraio2026.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ File {input_file} non trovato!")
        print("   Esegui prima: python genera_tracking_fase2.py")
        return False
    
    # Leggi CSV
    trades = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        trades = list(reader)
    
    print(f"📊 Caricati {len(trades)} trade da {input_file}\n")
    
    # Calcola P&L SOLO su trade effettivamente giocati
    bankroll = 500.0
    wins = 0
    losses = 0
    pending = 0
    skipped = 0
    total_pl = 0.0
    
    for trade in trades:
        giocata = trade.get('Giocata', 'NO').upper()
        
        # Se NON giocata, salta (P&L = 0, bankroll invariato)
        if giocata == 'NO':
            trade['Profit_Loss'] = 0.0
            trade['Bankroll'] = round(bankroll, 2)
            skipped += 1
            continue
        
        # SOLO se giocata: calcola P&L reale
        risultato = trade.get('Risultato', 'PENDING').upper()
        stake = float(trade.get('Stake_Suggerito', 10.0))
        quota = float(trade.get('Quota', 0))
        
        if risultato == 'WIN':
            profit = stake * (quota - 1)
            trade['Profit_Loss'] = round(profit, 2)
            bankroll += profit
            wins += 1
            total_pl += profit
        elif risultato == 'LOSS':
            trade['Profit_Loss'] = round(-stake, 2)
            bankroll -= stake
            losses += 1
            total_pl -= stake
        elif risultato == 'VOID':
            trade['Profit_Loss'] = 0.0
        else:  # PENDING
            trade['Profit_Loss'] = 0.0
            pending += 1
        
        trade['Bankroll'] = round(bankroll, 2)
    
    # Salva CSV aggiornato
    fieldnames = list(trades[0].keys())
    with open(input_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trades)
    
    print(f"✅ Aggiornato {input_file}\n")
    
    # Stampa metriche
    giocati = len(trades) - skipped
    closed_trades = wins + losses
    win_rate = (wins / closed_trades * 100) if closed_trades > 0 else 0
    roi = (total_pl / (closed_trades * 10) * 100) if closed_trades > 0 else 0
    
    print("=" * 60)
    print("📈 PERFORMANCE FASE 2")
    print("=" * 60)
    print(f"Total Trade: {len(trades)}")
    print(f"  • Giocati: {giocati} (usati per P&L)")
    print(f"  • Saltati: {skipped} (ignorati)")
    print(f"  • Chiusi: {closed_trades} (Win: {wins}, Loss: {losses})")
    print(f"  • Pending: {pending}")
    print(f"\nWin Rate: {win_rate:.1f}% (atteso 50.6%)")
    print(f"ROI: {roi:+.1f}% (backtest +29.0%)")
    print(f"\nP&L Totale: €{total_pl:+.2f}")
    print(f"Bankroll Finale: €{bankroll:.2f} (Iniziale: €500.00)")
    print(f"Variazione: {(bankroll/500 - 1)*100:+.1f}%")
    print("=" * 60)
    
    if pending > 0:
        print(f"\n⏳ {pending} trade ancora in sospeso")
        print("   Aggiorna la colonna 'Risultato' con WIN/LOSS e ri-esegui questo script")
    
    return True

if __name__ == '__main__':
    aggiorna_tracking()
