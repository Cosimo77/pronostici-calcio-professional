#!/usr/bin/env python3
"""
🎯 RIGENERA BACKTEST PROFESSIONALE
Ricalcola backtest_trades.csv con le nuove predizioni fixate

AGGIORNAMENTI APPLICATI:
- Smoothing bayesiano 20% (era 50-100%)
- Confronto diretto team-vs-team
- Form weight 10x ultimi 10 match
- Asian/European Handicap da probabilità FT
- Cards/Corners logiche corrette
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from pathlib import Path

# Aggiungi il path web/ per importare ProfessionalCalculator
web_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
if web_path not in sys.path:
    sys.path.insert(0, web_path)

from app_professional import ProfessionalCalculator  # type: ignore

def rigenera_backtest_completo():
    """Rigenera backtest con predizioni aggiornate"""
    
    print('\n' + '='*80)
    print('🎯 RIGENERAZIONE BACKTEST PROFESSIONALE')
    print('='*80)
    
    # Carica calculator con nuove fix
    calc = ProfessionalCalculator()
    calc.carica_dati()
    
    print(f'\n📊 Dataset caricato: {len(calc.df_features)} partite')
    
    # Carica dataset completo con quote
    df = pd.read_csv('data/dataset_completo_con_quote.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filtra partite con quote disponibili
    df_con_quote = df[df['B365H'].notna() & df['B365D'].notna() & df['B365A'].notna()].copy()
    
    print(f'📈 Partite con quote: {len(df_con_quote)}')
    print(f'📅 Periodo: {df_con_quote["Date"].min().strftime("%Y-%m-%d")} → {df_con_quote["Date"].max().strftime("%Y-%m-%d")}')
    
    # Inizializza backtest
    initial_bankroll = 1000
    bankroll = initial_bankroll
    trades = []
    
    kelly_fraction = 0.125  # 1/8 Kelly conservativo
    min_ev = 5  # EV minimo 5%
    min_prob = 0.35  # Probabilità minima 35%
    
    print('\n🎲 Parametri backtest:')
    print(f'   Bankroll iniziale: €{initial_bankroll}')
    print(f'   Kelly fraction: {kelly_fraction}')
    print(f'   EV minimo: {min_ev}%')
    print(f'   Prob minima: {min_prob}')
    
    print('\n🔄 Simulazione in corso...\n')
    
    for idx, row in df_con_quote.iterrows():
        casa = row['HomeTeam']
        ospite = row['AwayTeam']
        date = row['Date']
        actual = row['FTR']
        
        # Ottieni quote reali
        odds_h = row['B365H']
        odds_d = row['B365D']
        odds_a = row['B365A']
        
        # Predici con nuovo sistema
        try:
            pred, prob, conf = calc.predici_partita_deterministica(casa, ospite)
            
            prob_h = prob['H']
            prob_d = prob['D']
            prob_a = prob['A']
            
            # Calcola EV per ogni mercato
            ev_h = (prob_h * odds_h - 1) * 100
            ev_d = (prob_d * odds_d - 1) * 100
            ev_a = (prob_a * odds_a - 1) * 100
            
            # Trova best value bet
            best_ev = max(ev_h, ev_d, ev_a)
            
            if best_ev == ev_h:
                prediction = 'H'
                prob_bet = prob_h
                odds_bet = odds_h
                ev_bet = ev_h
            elif best_ev == ev_d:
                prediction = 'D'
                prob_bet = prob_d
                odds_bet = odds_d
                ev_bet = ev_d
            else:
                prediction = 'A'
                prob_bet = prob_a
                odds_bet = odds_a
                ev_bet = ev_a
            
            # Filtri
            if ev_bet < min_ev or prob_bet < min_prob:
                continue
            
            # Kelly sizing
            edge = prob_bet * odds_bet - 1
            if edge <= 0:
                continue
            
            kelly = edge / (odds_bet - 1)
            stake_pct = max(0, min(kelly * kelly_fraction, 0.05))  # Max 5%
            stake = bankroll * stake_pct
            
            # Risultato
            won = (prediction == actual)
            if won:
                profit = stake * (odds_bet - 1)
            else:
                profit = -stake
            
            bankroll += profit
            roi = (profit / stake) * 100
            
            trades.append({
                'date': date.strftime('%Y-%m-%d'),
                'match': f'{casa} vs {ospite}',
                'prediction': prediction,
                'actual': actual,
                'prob': round(prob_bet, 3),
                'odds': round(odds_bet, 2),
                'ev': round(ev_bet, 1),
                'affidabilita': round(conf, 2),
                'stake': stake,
                'profit': profit,
                'roi': roi,
                'bankroll': bankroll,
                'won': won
            })
            
            if len(trades) % 50 == 0:
                print(f'   ✓ {len(trades)} trades processati... (Bankroll: €{bankroll:.0f})')
        
        except Exception as e:
            # Skip partite che non possono essere predette
            continue
    
    # Crea DataFrame
    df_trades = pd.DataFrame(trades)
    
    # Calcola metriche finali
    total_profit = bankroll - initial_bankroll
    roi_turnover = (total_profit / (df_trades['stake'].sum())) * 100 if len(df_trades) > 0 else 0
    roi_bankroll = (total_profit / initial_bankroll) * 100
    win_rate = (df_trades['won'].sum() / len(df_trades)) * 100 if len(df_trades) > 0 else 0
    
    # Calcola max drawdown
    df_trades['cumsum'] = df_trades['profit'].cumsum()
    df_trades['peak'] = df_trades['cumsum'].cummax()
    df_trades['dd'] = ((df_trades['cumsum'] - df_trades['peak']) / initial_bankroll) * 100
    max_dd = df_trades['dd'].min()
    
    print('\n' + '='*80)
    print('📊 RISULTATI BACKTEST')
    print('='*80)
    print(f'\n📅 Periodo: {df_trades["date"].min()} → {df_trades["date"].max()}')
    print(f'🎲 Trades: {len(df_trades)}')
    print(f'✅ Win: {df_trades["won"].sum()} / {len(df_trades)} ({win_rate:.1f}%)')
    print(f'💰 Profitto: €{total_profit:.2f}')
    print(f'📈 ROI su Turnover: {roi_turnover:.2f}%')
    print(f'📈 Return Totale: {roi_bankroll:.2f}%')
    print(f'💼 Bankroll finale: €{bankroll:.2f}')
    print(f'📉 Max Drawdown: {max_dd:.1f}%')
    
    # Salva
    output_file = 'backtest_trades.csv'
    df_trades.to_csv(output_file, index=False)
    print(f'\n✅ Salvato: {output_file}')
    
    # Salva anche metriche JSON per dashboard
    metriche = {
        'periodo': {
            'da': df_trades['date'].min(),
            'a': df_trades['date'].max()
        },
        'trades': len(df_trades),
        'win_rate': round(win_rate, 1),
        'roi_turnover': round(roi_turnover, 2),
        'roi_bankroll': round(roi_bankroll, 2),
        'profitto': round(total_profit, 2),
        'max_drawdown': round(max_dd, 1),
        'bankroll_finale': round(bankroll, 2)
    }
    
    import json
    metrics_file = 'data/backtest/roi_metrics.json'
    os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
    with open(metrics_file, 'w') as f:
        json.dump(metriche, f, indent=2)
    print(f'✅ Salvato: {metrics_file}')
    
    print('\n' + '='*80)
    print('✅ BACKTEST RIGENERATO CON SUCCESSO')
    print('='*80)
    print('\n💡 Le nuove metriche riflettono le fix implementate:')
    print('   - Smoothing bayesiano 20% (era 50-100%)')
    print('   - Confronto diretto team-vs-team')
    print('   - Form weight 10x ultimi 10 match')
    print('   - Logiche corrette Asian/European/Cards/Corners')
    
    return df_trades, metriche

if __name__ == '__main__':
    df_trades, metriche = rigenera_backtest_completo()
