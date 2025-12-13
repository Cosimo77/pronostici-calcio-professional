#!/usr/bin/env python3
"""
🎯 BACKTEST FASE 1 - FILTRI MIGLIORATI
Confronto: Approccio ATTUALE vs FASE 1 CONSERVATIVA

FASE 1 - Filtri Conservativi:
  1. Quote: 2.8-3.5 (no >3.5)
  2. EV minimo: 35% (vs 5% attuale)
  3. Affidabilità: >0.75 (vs nessun filtro)
  4. Kelly: × 0.5 (più aggressivo vs 0.125 attuale)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

from app_professional import ProfessionalCalculator  # type: ignore[import-not-found]

class BacktestFase1:
    """Backtest con filtri FASE 1 migliorati"""
    
    def __init__(self, initial_bankroll=1000, mode='fase1'):
        self.initial_bankroll = initial_bankroll
        self.bankroll = initial_bankroll
        self.trades = []
        self.mode = mode  # 'attuale' o 'fase1'
        
        # Configurazione per modalità
        if mode == 'attuale':
            # Filtri ATTUALI (baseline)
            self.kelly_fraction = 0.125  # 1/8 Kelly conservativo
            self.min_ev = 5  # EV minimo 5%
            self.min_prob = 0.35  # Prob minima 35%
            self.min_odds = 2.8  # Quote minime
            self.max_odds = 10.0  # No limite superiore quote
            self.min_affidabilita = 0.0  # No filtro affidabilità
        else:  # fase1
            # Filtri FASE 1 MIGLIORATI
            self.kelly_fraction = 0.5  # Kelly più aggressivo (4x)
            self.min_ev = 35  # EV minimo 35%
            self.min_prob = 0.35  # Prob minima 35%
            self.min_odds = 2.8  # Quote minime 2.8
            self.max_odds = 3.5  # Quote massime 3.5 (KEY!)
            self.min_affidabilita = 0.75  # Affidabilità minima 75%
        
        # Traccia equity curve
        self.equity_history = []
        self.dates_history = []
        
    def kelly_criterion(self, prob, odds):
        """Kelly Criterion per sizing"""
        edge = prob * odds - 1
        if edge <= 0:
            return 0
        
        kelly = edge / (odds - 1)
        return max(0, min(kelly * self.kelly_fraction, 0.05))  # Max 5% bankroll
    
    def simulate_bet(self, prediction, prob, odds_real, actual_outcome, date, match, ev, affidabilita):
        """Simula singola scommessa con filtri configurabili"""
        
        # Applica filtri basati su mode
        if ev < self.min_ev:
            return 0, 0, False, 'ev_basso'
        
        if prob < self.min_prob:
            return 0, 0, False, 'prob_bassa'
        
        if odds_real < self.min_odds or odds_real > self.max_odds:
            return 0, 0, False, 'quote_fuori_range'
        
        if affidabilita < self.min_affidabilita:
            return 0, 0, False, 'affidabilita_bassa'
        
        # Sizing con Kelly
        kelly_size = self.kelly_criterion(prob, odds_real)
        if kelly_size == 0:
            return 0, 0, False, 'kelly_zero'
        
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
        
        return profit, roi_percent, True, 'accepted'
    
    def run_backtest(self, df_full, months_backtest=18):
        """Esegue backtest su ultimi N mesi"""
        
        df_full['Date'] = pd.to_datetime(df_full['Date'])
        df_full = df_full.sort_values('Date')
        
        # Split: training su dati vecchi, backtest su ultimi N mesi
        cutoff = df_full['Date'].max() - timedelta(days=months_backtest * 30)
        df_train = df_full[df_full['Date'] < cutoff]
        df_test = df_full[df_full['Date'] >= cutoff]
        
        # Inizializza calculator
        calculator = ProfessionalCalculator()
        
        # Simula ogni partita nel test set
        bet_placed = 0
        skipped = 0
        skip_reasons = {}
        
        for idx, row in df_test.iterrows():
            home = row['HomeTeam']
            away = row['AwayTeam']
            date = row['Date']
            
            # Skip se squadre non disponibili
            if home not in calculator.squadre_disponibili or away not in calculator.squadre_disponibili:
                continue
            
            # Predizione
            pred, probs, conf = calculator.predici_partita_deterministica(home, away)
            
            # Solo pareggi (come sistema attuale)
            if pred != 'D':
                continue
            
            # Quote reali e outcome
            odds_draw = row.get('B365D', 0) or row.get('BWD', 0) or row.get('IWD', 0)
            if odds_draw <= 0:
                continue
            
            actual = 'H' if row['FTR'] == 'H' else ('A' if row['FTR'] == 'A' else 'D')
            
            # Calcola metrics
            prob_draw = probs['D']
            ev = (prob_draw * odds_draw - 1) * 100
            affidabilita = conf  # Usa confidenza come proxy affidabilità
            
            # Simula scommessa
            profit, roi, placed, reason = self.simulate_bet(
                pred, prob_draw, odds_draw, actual, 
                date, f"{home} vs {away}", ev, affidabilita
            )
            
            if placed:
                bet_placed += 1
            else:
                skipped += 1
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        
        return {
            'trades_placed': bet_placed,
            'trades_skipped': skipped,
            'skip_reasons': skip_reasons,
            'final_bankroll': self.bankroll,
            'trades': self.trades
        }


def compare_strategies():
    """Confronta strategia ATTUALE vs FASE 1"""
    
    print("=" * 80)
    print("🎯 CONFRONTO: APPROCCIO ATTUALE vs FASE 1 CONSERVATIVA")
    print("=" * 80)
    print()
    
    # Carica dataset
    df = pd.read_csv('data/dataset_completo_con_quote.csv')
    
    print(f"📚 Dataset: {len(df)} partite")
    print(f"📅 Periodo: {df['Date'].min()} → {df['Date'].max()}")
    print()
    
    # BACKTEST 1: Strategia ATTUALE
    print("\n" + "─" * 80)
    print("📊 BACKTEST 1: STRATEGIA ATTUALE (Baseline)")
    print("─" * 80)
    print("Filtri:")
    print("  - Quote: 2.8-10.0")
    print("  - EV minimo: 5%")
    print("  - Affidabilità: nessun filtro")
    print("  - Kelly: × 0.125 (1/8)")
    print()
    
    bt_attuale = BacktestFase1(initial_bankroll=1000, mode='attuale')
    results_attuale = bt_attuale.run_backtest(df, months_backtest=18)
    
    # Metriche ATTUALE
    df_trades_att = pd.DataFrame(results_attuale['trades'])
    if len(df_trades_att) > 0:
        win_rate_att = df_trades_att['won'].mean() * 100
        total_profit_att = df_trades_att['profit'].sum()
        roi_att = (total_profit_att / 1000) * 100
        avg_stake_att = df_trades_att['stake'].mean()
        
        # Drawdown
        df_trades_att['cumsum'] = df_trades_att['profit'].cumsum()
        df_trades_att['peak'] = df_trades_att['cumsum'].cummax()
        df_trades_att['dd'] = df_trades_att['cumsum'] - df_trades_att['peak']
        max_dd_att = df_trades_att['dd'].min()
        max_dd_pct_att = (max_dd_att / 1000) * 100
    else:
        win_rate_att = roi_att = avg_stake_att = max_dd_att = max_dd_pct_att = 0
    
    print(f"✅ Risultati:")
    print(f"  Trade piazzati: {results_attuale['trades_placed']}")
    print(f"  Trade skippati: {results_attuale['trades_skipped']}")
    print(f"  Win Rate: {win_rate_att:.1f}%")
    print(f"  Profit totale: €{total_profit_att:.2f}")
    print(f"  ROI: {roi_att:.2f}%")
    print(f"  Stake medio: €{avg_stake_att:.2f}")
    print(f"  Max Drawdown: €{max_dd_att:.2f} ({max_dd_pct_att:.2f}%)")
    print(f"  Bankroll finale: €{results_attuale['final_bankroll']:.2f}")
    
    # BACKTEST 2: FASE 1
    print("\n" + "─" * 80)
    print("📊 BACKTEST 2: FASE 1 CONSERVATIVA")
    print("─" * 80)
    print("Filtri:")
    print("  - Quote: 2.8-3.5 (NO >3.5) ⭐")
    print("  - EV minimo: 35% ⭐")
    print("  - Affidabilità: >0.75 ⭐")
    print("  - Kelly: × 0.5 (4x più aggressivo) ⭐")
    print()
    
    bt_fase1 = BacktestFase1(initial_bankroll=1000, mode='fase1')
    results_fase1 = bt_fase1.run_backtest(df, months_backtest=18)
    
    # Metriche FASE 1
    df_trades_f1 = pd.DataFrame(results_fase1['trades'])
    if len(df_trades_f1) > 0:
        win_rate_f1 = df_trades_f1['won'].mean() * 100
        total_profit_f1 = df_trades_f1['profit'].sum()
        roi_f1 = (total_profit_f1 / 1000) * 100
        avg_stake_f1 = df_trades_f1['stake'].mean()
        
        # Drawdown
        df_trades_f1['cumsum'] = df_trades_f1['profit'].cumsum()
        df_trades_f1['peak'] = df_trades_f1['cumsum'].cummax()
        df_trades_f1['dd'] = df_trades_f1['cumsum'] - df_trades_f1['peak']
        max_dd_f1 = df_trades_f1['dd'].min()
        max_dd_pct_f1 = (max_dd_f1 / 1000) * 100
    else:
        win_rate_f1 = roi_f1 = avg_stake_f1 = max_dd_f1 = max_dd_pct_f1 = 0
    
    print(f"✅ Risultati:")
    print(f"  Trade piazzati: {results_fase1['trades_placed']}")
    print(f"  Trade skippati: {results_fase1['trades_skipped']}")
    print(f"  Skip reasons: {results_fase1['skip_reasons']}")
    print(f"  Win Rate: {win_rate_f1:.1f}%")
    print(f"  Profit totale: €{total_profit_f1:.2f}")
    print(f"  ROI: {roi_f1:.2f}%")
    print(f"  Stake medio: €{avg_stake_f1:.2f}")
    print(f"  Max Drawdown: €{max_dd_f1:.2f} ({max_dd_pct_f1:.2f}%)")
    print(f"  Bankroll finale: €{results_fase1['final_bankroll']:.2f}")
    
    # CONFRONTO FINALE
    print("\n\n" + "=" * 80)
    print("📈 CONFRONTO FINALE")
    print("=" * 80)
    print()
    
    # Tabella comparativa
    print(f"{'Metrica':<25} {'ATTUALE':<20} {'FASE 1':<20} {'Delta':<15}")
    print("-" * 80)
    
    # Trade
    delta_trades = results_fase1['trades_placed'] - results_attuale['trades_placed']
    delta_trades_pct = (delta_trades / results_attuale['trades_placed'] * 100) if results_attuale['trades_placed'] > 0 else 0
    print(f"{'Trade':<25} {results_attuale['trades_placed']:<20} {results_fase1['trades_placed']:<20} {delta_trades:+.0f} ({delta_trades_pct:+.1f}%)")
    
    # Win Rate
    wr_att_val = float(win_rate_att) if win_rate_att is not None else 0.0
    wr_f1_val = float(win_rate_f1) if win_rate_f1 is not None else 0.0
    delta_wr = wr_f1_val - wr_att_val
    print(f"{'Win Rate':<25} {wr_att_val:.1f}%{'':<15} {wr_f1_val:.1f}%{'':<15} {delta_wr:+.1f}%")
    
    # ROI
    roi_att_val = float(roi_att) if roi_att is not None else 0.0
    roi_f1_val = float(roi_f1) if roi_f1 is not None else 0.0
    delta_roi = roi_f1_val - roi_att_val
    print(f"{'ROI':<25} {roi_att_val:.2f}%{'':<15} {roi_f1_val:.2f}%{'':<15} {delta_roi:+.2f}%")
    
    # Profit
    profit_att_val = float(total_profit_att) if total_profit_att is not None else 0.0
    profit_f1_val = float(total_profit_f1) if total_profit_f1 is not None else 0.0
    delta_profit = profit_f1_val - profit_att_val
    print(f"{'Profit':<25} €{profit_att_val:.2f}{'':<14} €{profit_f1_val:.2f}{'':<14} €{delta_profit:+.2f}")
    
    # Drawdown
    dd_att_val = float(max_dd_pct_att) if max_dd_pct_att is not None else 0.0
    dd_f1_val = float(max_dd_pct_f1) if max_dd_pct_f1 is not None else 0.0
    delta_dd = dd_f1_val - dd_att_val
    print(f"{'Max Drawdown':<25} {dd_att_val:.2f}%{'':<15} {dd_f1_val:.2f}%{'':<15} {delta_dd:+.2f}%")
    
    # Stake medio
    stake_att_val = float(avg_stake_att) if avg_stake_att is not None else 0.0
    stake_f1_val = float(avg_stake_f1) if avg_stake_f1 is not None else 0.0
    delta_stake = stake_f1_val - stake_att_val
    delta_stake_pct = (delta_stake / stake_att_val * 100) if stake_att_val > 0 else 0
    print(f"{'Stake medio':<25} €{stake_att_val:.2f}{'':<14} €{stake_f1_val:.2f}{'':<14} €{delta_stake:+.2f} ({delta_stake_pct:+.1f}%)")
    
    print()
    print("=" * 80)
    
    # VERDETTO
    print("\n🎯 VERDETTO:")
    print("─" * 80)
    
    if roi_f1 > roi_att + 3:  # +3% miglioramento
        print("✅ FASE 1 VINCE! ROI significativamente migliore")
        print(f"   Miglioramento: +{delta_roi:.2f}% ROI")
        print(f"   Raccomandazione: IMPLEMENTA FASE 1 in produzione")
        verdict = "SUCCESSO"
    elif roi_f1 > roi_att:
        print("⚠️  FASE 1 lievemente migliore ma non significativo")
        print(f"   Miglioramento: +{delta_roi:.2f}% ROI")
        print(f"   Raccomandazione: Testa su più dati o ottimizza ulteriormente")
        verdict = "PARZIALE"
    else:
        print("❌ FASE 1 PEGGIORE dell'attuale")
        print(f"   Peggioramento: {delta_roi:.2f}% ROI")
        print(f"   Raccomandazione: Sistema ha problemi più profondi (ricalibra ML)")
        verdict = "FALLITO"
    
    print()
    print("=" * 80)
    
    return {
        'verdict': verdict,
        'attuale': results_attuale,
        'fase1': results_fase1,
        'delta_roi': delta_roi,
        'delta_profit': delta_profit
    }


if __name__ == '__main__':
    compare_strategies()
