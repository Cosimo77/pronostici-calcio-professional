#!/usr/bin/env python3
"""Verifica stato reale diario betting"""

import pandas as pd

df = pd.read_csv('tracking_giocate.csv')
print('📊 STATO REALE CSV:\n')
print(f'Totale righe: {len(df)}')
print(f'PENDING: {len(df[df["Risultato"] == "PENDING"])}')
print(f'WIN: {len(df[df["Risultato"] == "WIN"])}')
print(f'LOSS: {len(df[df["Risultato"] == "LOSS"])}')

stake_totale = df['Stake'].sum()
profit_totale = df[df['Risultato'] != 'PENDING']['Profit'].sum()
print(f'\nStake totale: €{stake_totale:.2f}')
print(f'Profit (completate): €{profit_totale:.2f}')
print(f'Bankroll teorico: €{100 + profit_totale:.2f}')

completed = df[df['Risultato'] != 'PENDING']
if len(completed) > 0:
    wins = len(completed[completed['Risultato'] == 'WIN'])
    win_rate = (wins / len(completed)) * 100
    roi = (profit_totale / completed['Stake'].sum()) * 100 if completed['Stake'].sum() > 0 else 0
    print(f'\nBet completate: {len(completed)}')
    print(f'Win Rate: {win_rate:.1f}%')
    print(f'ROI: {roi:.1f}%')
else:
    print('\n⚠️ Nessuna bet completata')

print('\n' + '='*60)
print('CONFRONTO CON DIARIO UI:')
print('='*60)
print('UI mostra: 11 puntate, ROI 126.2%, Win Rate 100%, Bankroll €116.40')
print(f'CSV reale: {len(df)} puntate, Bankroll teorico €{100 + profit_totale:.2f}')
print('\n❌ MISMATCH: Dati UI non corrispondono CSV!')
