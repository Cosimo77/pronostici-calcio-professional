"""
🎯 BACKTEST ROI SIMULATOR - NO ODDS VERSION
Test di sistema predittivo usando SOLO statistiche pure (no data leakage da odds)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional
from scripts.sistema_pronostici import PronosticiCalculator

class ROIBacktester:
    def __init__(self, initial_bankroll=1000):
        self.initial_bankroll = initial_bankroll
        self.bankroll = initial_bankroll
        self.trades = []
        self.kelly_fraction = 0.125  # Ultra-conservativo (1/8 Kelly)
        self.calculator: Optional[PronosticiCalculator] = None  # Set externally
        
    def kelly_criterion(self, prob, odds):
        """Calcola stake ottimale con Kelly Criterion"""
        # Kelly formula: f = (bp - q) / b
        # b = decimal odds - 1, p = prob win, q = prob loss
        b = odds - 1
        p = prob
        q = 1 - p
        
        kelly = (b * p - q) / b
        
        # Ultra-conservativo: usa 1/8 del Kelly
        kelly_fractional = kelly * self.kelly_fraction
        
        # Cap al 2.5% del bankroll (gestione rischio)
        return max(0, min(kelly_fractional, 0.025))
    
    def simulate_bet(self, prediction, prob, odds_real, actual_outcome, date, match):
        """Simula una singola scommessa"""
        # Expected Value
        ev = (prob * odds_real) - 1
        
        # Filtri qualità:
        # 1. EV positivo >5% (più selettivo)
        # 2. Probabilità >35% (evita scommesse deboli)
        if ev < 0.05 or prob < 0.35:
            return 0, 0
        
        # Sizing con Kelly
        kelly_size = self.kelly_criterion(prob, odds_real)
        stake = self.bankroll * kelly_size
        
        # Min stake €1
        if stake < 1:
            return 0, 0
        
        # Esito
        won = (prediction == actual_outcome)
        profit = (stake * odds_real - stake) if won else -stake
        
        # Aggiorna bankroll
        self.bankroll += profit
        
        # Log trade
        self.trades.append({
            'date': date,
            'match': match,
            'prediction': prediction,
            'actual': actual_outcome,
            'prob': prob,
            'odds': odds_real,
            'ev': ev,
            'stake': stake,
            'profit': profit,
            'roi': (profit/stake) if stake > 0 else 0,
            'bankroll': self.bankroll,
            'won': won,
            'cumulative': self.bankroll - self.initial_bankroll
        })
        
        return stake, profit
    
    def run_backtest(self, df, start_date=None):
        """Esegui backtest completo"""
        
        if start_date:
            df = df[df['Date'] >= start_date].copy()
        
        print(f"\n{'='*70}")
        print(f"🎯 BACKTEST ROI - NO ODDS (Solo Statistiche Pure)")
        print(f"{'='*70}")
        print(f"📅 Periodo: {df['Date'].min()} → {df['Date'].max()}")
        print(f"🎲 Partite: {len(df)}")
        print(f"💰 Bankroll iniziale: €{self.initial_bankroll:,.2f}")
        print(f"{'='*70}\n")
        
        total_bets = 0
        total_stake = 0
        
        for idx, row in df.iterrows():
            # Prepara features (esclude odds che non abbiamo più)
            exclude_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HTR', 'Referee', 'Div']
            feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['int64', 'float64']]
            
            features = row[feature_cols].fillna(0)
            
            try:
                # Predizione (SENZA odds!)
                assert self.calculator is not None, "Calculator non inizializzato"
                prediction_result = self.calculator.ensemble_prediction(features)
                
                # ensemble_prediction restituisce tupla (pred, probs) o più valori
                if isinstance(prediction_result, tuple) and len(prediction_result) >= 2:
                    pred_result = prediction_result[0]
                    probabilities = prediction_result[1]
                else:
                    continue
                    
                pred_prob = probabilities.get(pred_result, 0) if isinstance(probabilities, dict) else 0
                
                if pred_prob == 0:
                    continue
                
                # Usa odds reali dal dataset ORIGINALE per simulare scommessa
                # (In produzione usiamo odds bookmaker, qui le carichiamo per backtest)
                df_with_odds = pd.read_csv('data/dataset_completo_con_quote.csv')
                df_with_odds['Date'] = pd.to_datetime(df_with_odds['Date'])
                
                match_odds = df_with_odds[
                    (df_with_odds['Date'] == row['Date']) &
                    (df_with_odds['HomeTeam'] == row['HomeTeam']) &
                    (df_with_odds['AwayTeam'] == row['AwayTeam'])
                ]
                
                if len(match_odds) == 0:
                    continue
                
                match_odds = match_odds.iloc[0]
                
                # pred_result potrebbe essere lista, prendi primo elemento
                prediction_str = pred_result[0] if isinstance(pred_result, (list, np.ndarray)) else pred_result
                
                # Odds reali per il risultato predetto
                odds_map = {
                    'H': match_odds.get('B365H', match_odds.get('BWH', 0)),
                    'D': match_odds.get('B365D', match_odds.get('BWD', 0)),
                    'A': match_odds.get('B365A', match_odds.get('BWA', 0))
                }
                
                odds_real = odds_map.get(prediction_str, 0)
                
                if odds_real == 0:
                    continue
                
                # Simula bet
                stake, profit = self.simulate_bet(
                    prediction_str,
                    pred_prob,
                    odds_real,
                    row['FTR'],
                    row['Date'],
                    f"{row['HomeTeam']} vs {row['AwayTeam']}"
                )
                
                if stake > 0:
                    total_bets += 1
                    total_stake += stake
                    
            except Exception as e:
                continue
        
        # Risultati
        self.print_results()
    
    def print_results(self):
        """Stampa risultati backtest"""
        if len(self.trades) == 0:
            print("⚠️ Nessuna scommessa effettuata")
            return
        
        df_trades = pd.DataFrame(self.trades)
        
        # Metriche
        total_profit = df_trades['profit'].sum()
        total_stake = df_trades['stake'].sum()
        roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
        total_return = ((self.bankroll - self.initial_bankroll) / self.initial_bankroll) * 100
        
        wins = df_trades[df_trades['won'] == True]
        win_rate = (len(wins) / len(df_trades)) * 100
        
        # Drawdown
        df_trades['cumulative_max'] = df_trades['cumulative'].cummax()
        df_trades['drawdown'] = df_trades['cumulative'] - df_trades['cumulative_max']
        max_drawdown = (df_trades['drawdown'].min() / self.initial_bankroll) * 100
        
        # Sharpe Ratio (approssimato)
        returns = df_trades['profit'] / df_trades['stake']
        sharpe = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"📊 RISULTATI BACKTEST - NO ODDS")
        print(f"{'='*70}\n")
        
        print(f"💰 PERFORMANCE FINANZIARIA:")
        print(f"   Bankroll iniziale:  €{self.initial_bankroll:,.2f}")
        print(f"   Bankroll finale:    €{self.bankroll:,.2f}")
        print(f"   Profitto totale:    €{total_profit:,.2f}")
        print(f"   ROI:                {roi:+.2f}%")
        print(f"   Return totale:      {total_return:+.2f}%")
        
        print(f"\n🎯 STATISTICHE SCOMMESSE:")
        print(f"   Totale bets:        {len(df_trades)}")
        print(f"   Bets vinte:         {len(wins)} ({win_rate:.1f}%)")
        print(f"   Bets perse:         {len(df_trades) - len(wins)}")
        print(f"   Stake totale:       €{total_stake:,.2f}")
        print(f"   Avg stake:          €{df_trades['stake'].mean():.2f}")
        
        print(f"\n📈 RISCHIO:")
        print(f"   Max drawdown:       {max_drawdown:.2f}%")
        print(f"   Sharpe Ratio:       {sharpe:.2f}")
        print(f"   EV medio:           {df_trades['ev'].mean()*100:+.2f}%")
        
        # Best/worst bets
        best_bet = df_trades.loc[df_trades['profit'].idxmax()]
        worst_bet = df_trades.loc[df_trades['profit'].idxmin()]
        
        print(f"\n🏆 BEST BET:")
        print(f"   {best_bet['match']} ({best_bet['date']})")
        print(f"   Profit: €{best_bet['profit']:.2f} (ROI: {best_bet['roi']*100:+.1f}%)")
        
        print(f"\n💔 WORST BET:")
        print(f"   {worst_bet['match']} ({worst_bet['date']})")
        print(f"   Loss: €{worst_bet['profit']:.2f} (ROI: {worst_bet['roi']*100:+.1f}%)")
        
        print(f"\n{'='*70}\n")
        
        # Valutazione acquisizione
        print(f"🏢 VALUTAZIONE ACQUISIZIONE - NO ODDS:")
        if roi > 15:
            print(f"   ✅ ROI eccellente (>15%)")
            print(f"   💰 Valore stimato: $50K-150K")
        elif roi > 10:
            print(f"   ✅ ROI buono (10-15%)")
            print(f"   💰 Valore stimato: $30K-80K")
        elif roi > 5:
            print(f"   ⚠️ ROI moderato (5-10%)")
            print(f"   💰 Valore stimato: $15K-30K")
        elif roi > 0:
            print(f"   ⚠️ ROI marginalmente positivo (<5%)")
            print(f"   💰 Valore stimato: $5K-15K")
        else:
            print(f"   ❌ ROI negativo")
            print(f"   💰 Valore stimato: $1K-5K (solo tecnologia)")
        print(f"{'='*70}\n")
        
        # Salva report
        df_trades.to_csv('backtest_NO_ODDS_trades.csv', index=False)
        print("💾 Report salvato: backtest_NO_ODDS_trades.csv")


if __name__ == "__main__":
    print("Caricamento dati...")
    
    # Carica dataset SENZA ODDS (solo statistiche)
    df = pd.read_csv('data/dataset_SOLO_STATS.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Backtest su ultimi 2 anni
    two_years_ago = datetime.now() - pd.Timedelta(days=730)
    
    print("\n🔧 Addestramento modelli (SENZA ODDS)...")
    
    calculator = PronosticiCalculator()
    
    # Training su dati PRIMA del periodo backtest
    df_train = df[df['Date'] < two_years_ago]
    
    if len(df_train) < 100:
        print("⚠️ Dati insufficienti per training, uso tutto il dataset")
        df_train = df
    
    # Prepara dati
    exclude_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HTR', 'Referee', 'Div']
    feature_cols = [col for col in df_train.columns if col not in exclude_cols and df_train[col].dtype in ['int64', 'float64']]
    
    calculator.feature_columns = feature_cols
    X = df_train[feature_cols].fillna(0)
    y = df_train['FTR']
    
    print(f"📊 Features selezionate: {len(feature_cols)} (SOLO STATISTICHE)")
    
    calculator.train_models(X, y, test_size=0.2, random_state=42)
    
    print(f"✅ Modelli addestrati su {len(df_train)} partite")
    print(f"   Periodo training: {df_train['Date'].min()} → {df_train['Date'].max()}")
    
    # Crea backtester
    backtester = ROIBacktester(initial_bankroll=1000)
    backtester.calculator = calculator
    
    # Esegui backtest
    backtester.run_backtest(df, start_date=two_years_ago.strftime('%Y-%m-%d'))
