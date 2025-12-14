#!/usr/bin/env python3
"""
🎯 BACKTEST ROI SIMULATOR
Simula portafoglio scommesse su dati storici per validare sistema value betting

OBIETTIVO: Dimostrare ROI positivo necessario per acquisizione
TARGET: +15% ROI annuo con max 20% drawdown
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from modelli_predittivi import PronosticiCalculator

class ROIBacktester:
    """Simula scommesse reali su dati storici"""
    
    def __init__(self, initial_bankroll=1000):
        self.initial_bankroll = initial_bankroll
        self.bankroll = initial_bankroll
        self.trades = []
        self.calculator = PronosticiCalculator()
        self.kelly_fraction = 0.125  # 1/8 Kelly (ultra-conservativo per ridurre drawdown)
        
    def kelly_criterion(self, prob, odds, fraction=None):
        """
        Kelly Criterion per sizing ottimale scommesse
        
        Args:
            prob: Probabilità vittoria (modello ML)
            odds: Quote bookmaker
            fraction: Frazione Kelly (None = usa self.kelly_fraction)
        """
        if fraction is None:
            fraction = self.kelly_fraction
            
        edge = prob * odds - 1
        if edge <= 0:
            return 0
        
        kelly = edge / (odds - 1)
        return max(0, min(kelly * fraction, 0.025))  # Max 2.5% bankroll per bet (ridotto da 5%)
    
    def simulate_bet(self, prediction, prob, odds_real, actual_outcome, date, match):
        """
        Simula singola scommessa
        
        Returns:
            profit, roi_percent
        """
        # Calcola EV
        ev = (prob * odds_real) - 1
        
        # Filtri qualità:
        # 1. EV positivo >5% (più selettivo)
        # 2. Probabilità >35% (evita scommesse deboli)
        if ev < 0.05 or prob < 0.35:
            return 0, 0
        
        # Sizing con Kelly
        kelly_size = self.kelly_criterion(prob, odds_real)
        if kelly_size == 0:
            return 0, 0
        
        stake = self.bankroll * kelly_size
        
        # Esito
        won = (prediction == actual_outcome)
        profit = stake * (odds_real - 1) if won else -stake
        roi_percent = (profit / stake * 100) if stake > 0 else 0
        
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
            'ev': ev * 100,
            'stake': stake,
            'profit': profit,
            'roi': roi_percent,
            'bankroll': self.bankroll,
            'won': won
        })
        
        return profit, roi_percent
    
    def run_backtest(self, df, start_date=None, end_date=None, min_partite_training=1000):
        """
        Esegue backtest completo su dataset storico
        
        Args:
            min_partite_training: Minimo partite richieste per training (default 1000)
        
        Args:
            df: Dataset con partite storiche
            start_date: Data inizio (None = usa tutto)
            end_date: Data fine (None = oggi)
        """
        print("🎯 BACKTEST ROI SIMULATOR")
        print("=" * 70)
        
        # Filtra date
        if start_date:
            df = df[df['Date'] >= start_date]
        if end_date:
            df = df[df['Date'] <= end_date]
        
        df = df.sort_values('Date')
        print(f"📅 Periodo: {df['Date'].min()} → {df['Date'].max()}")
        print(f"📊 Partite: {len(df)}")
        print(f"💰 Bankroll iniziale: €{self.initial_bankroll}")
        print()
        
        # Carica squadre disponibili
        squadre_set = set(df['HomeTeam'].unique()) | set(df['AwayTeam'].unique())
        
        # Simula ogni partita
        for idx, row in df.iterrows():
            home = row['HomeTeam']
            away = row['AwayTeam']
            
            # Skip se squadre non hanno dati sufficienti
            if home not in squadre_set or away not in squadre_set:
                continue
            
            # Predici la partita usando tutte le features disponibili fino a questo punto
            df_up_to_now = df.loc[:idx]
            result = self.calculator.predici_partita(home, away, df_up_to_now)
            
            # predici_partita ritorna (predizione, messaggio) o (predizione, probabilities)
            if result is None or (isinstance(result, tuple) and len(result) < 2):
                continue
            
            pred, probs = result[0], result[1]
            
            # Se probs è un dizionario, estraiamo le probabilità
            if not isinstance(probs, dict):
                # Se è una stringa (messaggio errore), skippiamo
                continue
            
            # Quote reali (media delle disponibili)
            odds_home = row.get('B365H', row.get('BWH', 2.0))
            odds_draw = row.get('B365D', row.get('BWD', 3.0))
            odds_away = row.get('B365A', row.get('BWA', 3.5))
            
            # Map predizione a outcome
            outcome_map = {'H': ('H', probs.get('H', 0.33), odds_home),
                          'D': ('D', probs.get('D', 0.33), odds_draw),
                          'A': ('A', probs.get('A', 0.34), odds_away)}
            
            if pred in outcome_map:
                pred_outcome, pred_prob, pred_odds = outcome_map[pred]
                actual = row['FTR']
                
                self.simulate_bet(
                    pred_outcome, 
                    pred_prob, 
                    pred_odds, 
                    actual,
                    row['Date'],
                    f"{home} vs {away}"
                )
        
        # Report finale
        self.print_report()
    
    def print_report(self):
        """Stampa report performance"""
        if not self.trades:
            print("❌ Nessuna scommessa eseguita")
            return
        
        df_trades = pd.DataFrame(self.trades)
        
        total_bets = len(df_trades)
        won_bets = df_trades['won'].sum()
        win_rate = won_bets / total_bets * 100
        
        total_staked = df_trades['stake'].sum()
        total_profit = df_trades['profit'].sum()
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        
        final_bankroll = self.bankroll
        total_return = ((final_bankroll - self.initial_bankroll) / self.initial_bankroll * 100)
        
        # Drawdown
        df_trades['cumulative'] = df_trades['profit'].cumsum()
        running_max = df_trades['cumulative'].expanding().max()
        drawdown = (df_trades['cumulative'] - running_max)
        max_drawdown = (drawdown.min() / self.initial_bankroll * 100) if len(drawdown) > 0 else 0
        
        # Sharpe Ratio (approssimato)
        if len(df_trades) > 1:
            returns = df_trades['roi'] / 100
            sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe = 0
        
        print("\n" + "=" * 70)
        print("📊 RISULTATI BACKTEST")
        print("=" * 70)
        print(f"\n💰 PERFORMANCE FINANZIARIA:")
        print(f"   Bankroll iniziale:  €{self.initial_bankroll:,.2f}")
        print(f"   Bankroll finale:    €{final_bankroll:,.2f}")
        print(f"   Profitto totale:    €{total_profit:,.2f}")
        print(f"   ROI:                {roi:+.2f}%")
        print(f"   Return totale:      {total_return:+.2f}%")
        
        print(f"\n🎯 STATISTICHE SCOMMESSE:")
        print(f"   Totale bets:        {total_bets}")
        print(f"   Bets vinte:         {won_bets} ({win_rate:.1f}%)")
        print(f"   Bets perse:         {total_bets - won_bets}")
        print(f"   Stake totale:       €{total_staked:,.2f}")
        print(f"   Avg stake:          €{total_staked/total_bets:,.2f}")
        
        print(f"\n📈 RISCHIO:")
        print(f"   Max drawdown:       {max_drawdown:.2f}%")
        print(f"   Sharpe Ratio:       {sharpe:.2f}")
        
        # EV medio
        avg_ev = df_trades['ev'].mean()
        print(f"   EV medio:           +{avg_ev:.2f}%")
        
        # Best/Worst
        best = df_trades.nlargest(1, 'profit').iloc[0]
        worst = df_trades.nsmallest(1, 'profit').iloc[0]
        print(f"\n🏆 BEST BET:")
        print(f"   {best['match']} ({best['date']})")
        print(f"   Profit: €{best['profit']:,.2f} (ROI: {best['roi']:+.1f}%)")
        
        print(f"\n💔 WORST BET:")
        print(f"   {worst['match']} ({worst['date']})")
        print(f"   Loss: €{worst['profit']:,.2f} (ROI: {worst['roi']:+.1f}%)")
        
        print("\n" + "=" * 70)
        
        # Valutazione acquisizione
        print("\n🏢 VALUTAZIONE ACQUISIZIONE:")
        if roi >= 15 and max_drawdown > -20:
            print("   ✅ TARGET RAGGIUNTO: ROI >15%, drawdown <20%")
            print("   💰 Valore stimato: $50K-150K")
        elif roi >= 10:
            print("   ⚠️ ROI positivo ma sotto target (+15%)")
            print("   💰 Valore stimato: $15K-50K")
        elif roi > 0:
            print("   ⚠️ ROI marginalmente positivo")
            print("   💰 Valore stimato: $5K-15K")
        else:
            print("   ❌ ROI NEGATIVO - Sistema non profittevole")
            print("   💰 Valore: Solo tecnologia ($5K)")
        
        print("=" * 70)
        
        # Salva report
        df_trades.to_csv('backtest_trades.csv', index=False)
        print("\n💾 Report salvato: backtest_trades.csv")


if __name__ == "__main__":
    print("Caricamento dati...")
    
    # Carica dataset COMPLETO con features + quote storiche
    df = pd.read_csv('data/dataset_completo_con_quote.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Backtest su ultimi 2 anni (più dati storici per validazione robusta)
    two_years_ago = datetime.now() - pd.Timedelta(days=730)
    
    print("\n🔧 Addestramento modelli...")
    
    # Prepara calculator e addestra modelli su TUTTO il dataset disponibile
    # (In produzione usa train/test split, ma per backtest usiamo tutto)
    calculator = PronosticiCalculator()
    
    # Usa solo dati PRIMA del periodo di backtest per train
    df_train = df[df['Date'] < two_years_ago]
    
    if len(df_train) < 100:
        print("⚠️ Dati insufficienti per training, uso tutto il dataset")
        df_train = df
    
    # Prepara dati - esclude automaticamente colonne non numeriche
    # ma assicurati che HTR sia esclusa se presente
    exclude_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HTR', 'Referee', 'Div']
    feature_cols = [col for col in df_train.columns if col not in exclude_cols and df_train[col].dtype in ['int64', 'float64']]
    
    calculator.feature_columns = feature_cols
    X = df_train[feature_cols].fillna(0)
    y = df_train['FTR']
    
    print(f"📊 Features selezionate: {len(feature_cols)}")
    
    calculator.train_models(X, y, test_size=0.2, random_state=42)
    
    print(f"✅ Modelli addestrati su {len(df_train)} partite")
    print(f"   Periodo training: {df_train['Date'].min()} → {df_train['Date'].max()}")
    
    # Crea backtester con calculator addestrato
    backtester = ROIBacktester(initial_bankroll=1000)
    backtester.calculator = calculator
    
    # Esegui backtest
    backtester.run_backtest(df, start_date=two_years_ago.strftime('%Y-%m-%d'))

