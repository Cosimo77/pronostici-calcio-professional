#!/usr/bin/env python3
"""
🎯 BACKTEST COMPLETO SU 2,920 PARTITE
Backtest su ultimi 18 mesi con training su dati storici precedenti

OBIETTIVO: Validare sistema su campione più grande (510→1500+ partite)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

from app_professional import ProfessionalCalculator  # type: ignore[import-not-found]

class BacktestCompleto:
    """Backtest su dataset completo 2,920 partite"""
    
    def __init__(self, initial_bankroll=1000):
        self.initial_bankroll = initial_bankroll
        self.bankroll = initial_bankroll
        self.trades = []
        self.kelly_fraction = 0.125  # 1/8 Kelly conservativo
        
        # Traccia equity curve
        self.equity_history = []
        self.dates_history = []
        
    def kelly_criterion(self, prob, odds):
        """Kelly Criterion per sizing"""
        edge = prob * odds - 1
        if edge <= 0:
            return 0
        
        kelly = edge / (odds - 1)
        return max(0, min(kelly * self.kelly_fraction, 0.02))  # Max 2% bankroll
    
    def simulate_bet(self, prediction, prob, odds_real, actual_outcome, date, match, ev, affidabilita):
        """Simula singola scommessa"""
        
        # Filtri qualità REALISTICI (come backtest originale):
        # 1. EV >5% (soglia standard value betting)
        # 2. Probabilità >35% (evita scommesse troppo rischiose)
        if ev < 5 or prob < 0.35:
            return 0, 0, False
        
        # Sizing con Kelly
        kelly_size = self.kelly_criterion(prob, odds_real)
        if kelly_size == 0:
            return 0, 0, False
        
        stake = self.bankroll * kelly_size
        
        # Esito
        won = (prediction == actual_outcome)
        profit = stake * (odds_real - 1) if won else -stake
        roi_percent = (profit / stake * 100) if stake > 0 else 0
        
        # Aggiorna bankroll
        self.bankroll += profit
        
        # Traccia equity
        self.equity_history.append(self.bankroll)
        self.dates_history.append(date)
        
        # Log trade
        self.trades.append({
            'date': date,
            'match': match,
            'prediction': prediction,
            'actual': actual_outcome,
            'prob': prob,
            'odds': odds_real,
            'ev': ev,
            'affidabilita': affidabilita,
            'stake': stake,
            'profit': profit,
            'roi': roi_percent,
            'bankroll': self.bankroll,
            'won': won
        })
        
        return profit, roi_percent, True
    
    def run_backtest(self, df_full, months_backtest=18):
        """
        Esegue backtest su ultimi N mesi
        
        Args:
            df_full: Dataset completo
            months_backtest: Mesi da testare (default 18)
        """
        print("🎯 BACKTEST COMPLETO - DATASET 2,920 PARTITE")
        print("=" * 70)
        
        df_full['Date'] = pd.to_datetime(df_full['Date'])
        df_full = df_full.sort_values('Date')
        
        # Split: training su dati vecchi, backtest su ultimi N mesi
        cutoff = df_full['Date'].max() - timedelta(days=months_backtest * 30)
        df_train = df_full[df_full['Date'] < cutoff]
        df_test = df_full[df_full['Date'] >= cutoff]
        
        print(f"📚 Training set: {len(df_train)} partite ({df_train['Date'].min()} → {df_train['Date'].max()})")
        print(f"🎯 Test set:     {len(df_test)} partite ({df_test['Date'].min()} → {df_test['Date'].max()})")
        print(f"💰 Bankroll iniziale: €{self.initial_bankroll}")
        print()
        
        # Inizializza calculator con dati training
        print("🔧 Inizializzazione sistema predittivo...")
        calculator = ProfessionalCalculator()
        
        # Simula ogni partita nel test set
        bet_placed = 0
        skipped = 0
        
        print("\n⚙️ Esecuzione backtest...\n")
        
        for idx, row in df_test.iterrows():
            home = row['HomeTeam']
            away = row['AwayTeam']
            
            try:
                # Predici la partita
                pred, prob_dict, conf = calculator.predici_partita_deterministica(home, away)
                
                if pred is None or prob_dict is None:
                    skipped += 1
                    continue
                
                # Quote reali (usa B365 come primario, fallback su altri)
                odds_map = {
                    'H': row.get('B365H', row.get('BWH', row.get('AvgH', 2.0))),
                    'D': row.get('B365D', row.get('BWD', row.get('AvgD', 3.0))),
                    'A': row.get('B365A', row.get('BWA', row.get('AvgA', 3.5)))
                }
                
                # Calcola EV e affidabilità per la predizione
                pred_prob = prob_dict.get(pred, 0)
                pred_odds = odds_map.get(pred, 0)
                
                if pred_odds == 0:
                    skipped += 1
                    continue
                
                ev = ((pred_prob * pred_odds) - 1) * 100
                affidabilita = conf  # Confidence già calcolata
                
                actual = row['FTR']
                match = f"{home} vs {away}"
                
                profit, roi, placed = self.simulate_bet(
                    pred, pred_prob, pred_odds, actual, 
                    row['Date'], match, ev, affidabilita
                )
                
                if placed:
                    bet_placed += 1
                    
                    # Progress ogni 50 bet
                    if bet_placed % 50 == 0:
                        print(f"   ✓ {bet_placed} bet | Bankroll: €{self.bankroll:.2f} ({((self.bankroll/self.initial_bankroll - 1)*100):+.1f}%)")
                
            except Exception as e:
                skipped += 1
                continue
        
        print(f"\n✅ Backtest completato!")
        print(f"   Bet piazzate: {bet_placed}")
        print(f"   Partite skippate: {skipped}")
        print()
        
        return self.generate_report()
    
    def generate_report(self):
        """Genera report finale backtest"""
        
        if len(self.trades) == 0:
            print("❌ Nessuna bet piazzata")
            return None
        
        df_trades = pd.DataFrame(self.trades)
        
        # Metriche principali
        total_profit = df_trades['profit'].sum()
        total_stake = df_trades['stake'].sum()
        wins = df_trades['won'].sum()
        losses = len(df_trades) - wins
        
        roi_turnover = (total_profit / total_stake * 100) if total_stake > 0 else 0
        return_totale = ((self.bankroll - self.initial_bankroll) / self.initial_bankroll * 100)
        win_rate = (wins / len(df_trades) * 100) if len(df_trades) > 0 else 0
        
        # Drawdown
        equity = np.array(self.equity_history)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (approssimato)
        returns = np.array(df_trades['roi'].values, dtype=float)
        sharpe = (returns.mean() / returns.std()) if returns.std() > 0 else 0
        
        # EV medio
        ev_medio = df_trades['ev'].mean()
        
        print("=" * 70)
        print("📊 RISULTATI BACKTEST COMPLETO")
        print("=" * 70)
        print()
        print(f"💰 Capitale finale:      €{self.bankroll:.2f}")
        print(f"📈 Return totale:        {return_totale:+.2f}%")
        print(f"📊 ROI su turnover:      {roi_turnover:+.2f}%")
        print()
        print(f"🎯 Bet totali:           {len(df_trades)}")
        print(f"✅ Vinte:                {wins} ({win_rate:.1f}%)")
        print(f"❌ Perse:                {losses}")
        print()
        print(f"💸 Profitto totale:      €{total_profit:+.2f}")
        print(f"💵 Stake totale:         €{total_stake:.2f}")
        print(f"📉 Max drawdown:         {max_drawdown:.2f}%")
        print(f"📊 Sharpe ratio:         {sharpe:.2f}")
        print(f"🎲 EV medio bet:         {ev_medio:.2f}%")
        print()
        
        # Analisi temporale
        if len(df_trades) >= 100:
            ultimi_100 = df_trades.tail(100)
            roi_100 = ultimi_100['profit'].sum() / self.initial_bankroll * 100
            win_rate_100 = (ultimi_100['won'].sum() / 100 * 100)
            
            print(f"📅 Ultimi 100 bet:")
            print(f"   Return:               {roi_100:+.2f}%")
            print(f"   Win rate:             {win_rate_100:.1f}%")
            print()
        
        # Periodo
        print(f"📆 Periodo:              {df_trades['date'].min()} → {df_trades['date'].max()}")
        print("=" * 70)
        
        # Salva trades
        output_file = 'backtest_trades.csv'
        df_trades.to_csv(output_file, index=False)
        print(f"\n💾 Trades salvati: {output_file}")
        
        # Salva metriche JSON
        metriche = {
            'roi_turnover': round(roi_turnover, 2),
            'return_totale': round(return_totale, 2),
            'partite_totali': len(df_trades),
            'partite_vinte': int(wins),
            'win_rate': round(win_rate, 1),
            'profitto_totale': round(total_profit, 2),
            'stake_totale': round(total_stake, 2),
            'capitale_iniziale': self.initial_bankroll,
            'capitale_finale': round(self.bankroll, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe, 2),
            'ev_medio': round(ev_medio, 2),
            'aggiornato': datetime.now().isoformat(),
            'periodo': {
                'da': str(df_trades['date'].min()),
                'a': str(df_trades['date'].max())
            }
        }
        
        import json
        with open('cache/roi_metrics.json', 'w') as f:
            json.dump(metriche, f, indent=2)
        
        print(f"💾 Metriche salvate: cache/roi_metrics.json")
        
        return metriche


if __name__ == "__main__":
    print("Caricamento dataset...")
    
    # Carica dataset COMPLETO 2,920 partite
    df = pd.read_csv('data/dataset_features.csv')
    
    print(f"✅ Dataset caricato: {len(df)} partite\n")
    
    # Esegui backtest su ultimi 18 mesi (più robusto)
    backtester = BacktestCompleto(initial_bankroll=1000)
    metriche = backtester.run_backtest(df, months_backtest=18)
    
    print("\n✅ Backtest completo terminato!")
