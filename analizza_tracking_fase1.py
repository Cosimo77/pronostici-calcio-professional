#!/usr/bin/env python3
"""
📊 ANALISI TRACKING FASE1
Analizza performance real-time del sistema FASE1
"""

import pandas as pd
import sys
from datetime import datetime

def analizza_tracking(csv_file='tracking_fase1_gennaio2026.csv'):
    """Analizza tracking CSV e genera metriche performance"""
    
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"❌ File {csv_file} non trovato")
        print("Assicurati di aver tracciato almeno 1 trade")
        return
    
    if len(df) == 0:
        print("📭 Nessun trade tracciato ancora")
        print("Usa valida_fase1_realtime.py per identificare opportunità")
        return
    
    # Filtra solo trade completati (con risultato)
    df_completati = df[df['Risultato'].notna()].copy()
    
    if len(df_completati) == 0:
        print(f"⏳ {len(df)} trade identificati, nessuno completato ancora")
        print("\nTrade pending:")
        for _, row in df.iterrows():
            print(f"  - {row['Casa']} vs {row['Ospite']} (Quota X: {row['Quota_X']})")
        return
    
    # Calcola metriche
    n_trade = len(df_completati)
    n_win = len(df_completati[df_completati['Risultato'] == 'X'])
    n_loss = n_trade - n_win
    win_rate = (n_win / n_trade * 100) if n_trade > 0 else 0
    
    profit_total = df_completati['Profit_Loss'].sum()
    bankroll_final = df_completati['Bankroll'].iloc[-1] if len(df_completati) > 0 else 500
    roi = df_completati['ROI_%'].iloc[-1] if len(df_completati) > 0 else 0
    
    # Drawdown
    df_completati['Peak'] = df_completati['Bankroll'].cummax()
    df_completati['Drawdown'] = (df_completati['Bankroll'] - df_completati['Peak']) / df_completati['Peak'] * 100
    max_drawdown = df_completati['Drawdown'].min()
    
    # Streaks
    df_completati['Win'] = (df_completati['Risultato'] == 'X').astype(int)
    current_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    temp_streak = 0
    
    for win in df_completati['Win']:
        if win == 1:
            if temp_streak >= 0:
                temp_streak += 1
            else:
                temp_streak = 1
            max_win_streak = max(max_win_streak, temp_streak)
            current_streak = temp_streak
        else:
            if temp_streak <= 0:
                temp_streak -= 1
            else:
                temp_streak = -1
            max_loss_streak = max(max_loss_streak, abs(temp_streak))
            current_streak = temp_streak
    
    # Report
    print("\n" + "="*80)
    print("📊 ANALISI PERFORMANCE FASE1 - GENNAIO 2026")
    print("="*80)
    
    print(f"\n📈 METRICHE GENERALI:")
    print(f"   Trade completati: {n_trade}")
    print(f"   Win: {n_win} | Loss: {n_loss}")
    print(f"   Win Rate: {win_rate:.1f}% (target FASE1: 31.0%)")
    
    print(f"\n💰 PERFORMANCE FINANZIARIA:")
    print(f"   Profit/Loss: €{profit_total:+.2f}")
    print(f"   Bankroll finale: €{bankroll_final:.2f}")
    print(f"   ROI: {roi:+.2f}% (target FASE1: +7.17%)")
    
    print(f"\n📉 RISK METRICS:")
    print(f"   Max Drawdown: {max_drawdown:.2f}% (limite: -60%)")
    print(f"   Max Win Streak: {max_win_streak}")
    print(f"   Max Loss Streak: {max_loss_streak} (stop @3)")
    print(f"   Current Streak: {current_streak:+d}")
    
    # Valutazione vs target
    print("\n" + "="*80)
    print("🎯 VALUTAZIONE VS TARGET FASE1:")
    print("="*80)
    
    status = []
    
    if win_rate >= 31.0:
        status.append("✅ Win rate ≥31%")
    elif win_rate >= 25.0:
        status.append("⚠️  Win rate OK ma sotto target")
    else:
        status.append("❌ Win rate < 25% - ATTENZIONE")
    
    if roi >= 7.0:
        status.append("✅ ROI ≥+7%")
    elif roi >= 3.0:
        status.append("⚠️  ROI positivo ma sotto target")
    elif roi >= 0:
        status.append("⚠️  ROI break-even")
    else:
        status.append("❌ ROI negativo - REVISIONE")
    
    if max_drawdown > -60:
        status.append("✅ Drawdown sotto limite")
    else:
        status.append("❌ Drawdown >60% - STOP!")
    
    for s in status:
        print(f"   {s}")
    
    # Decision tree
    print("\n" + "="*80)
    print("🚦 DECISIONE OPERATIVA:")
    print("="*80)
    
    if n_trade < 20:
        print(f"   ⏳ CONTINUA VALIDAZIONE (trade: {n_trade}/20 minimi)")
        print("   Raccogli più dati prima di decisione finale")
    elif roi >= 3.0 and max_drawdown > -60:
        print("   ✅ SISTEMA VALIDATO - Procedi FASE 3 (deploy graduale)")
        print("   Considera scaling bankroll a €1,000")
    elif roi >= 0 and roi < 3.0:
        print("   ⚠️  RISULTATI INCERTI - Continua monitoring")
        print("   Attendi 30+ trade per valutazione definitiva")
    else:
        print("   ❌ SISTEMA NON PERFORMANTE - Pausa e revisione")
        print("   Rivedi filtri EV/quote o attendi più dati")
    
    # Ultimi 5 trade
    print("\n" + "="*80)
    print("📋 ULTIMI 5 TRADE:")
    print("="*80)
    
    for _, row in df_completati.tail(5).iterrows():
        result_emoji = "✅" if row['Risultato'] == 'X' else "❌"
        print(f"\n{result_emoji} {row['Data']} - {row['Casa']} vs {row['Ospite']}")
        print(f"   Quota: {row['Quota_X']:.2f} | EV: {row['EV_%']}% | Stake: €{row['Stake']:.2f}")
        print(f"   Risultato: {row['Risultato']} | P/L: €{row['Profit_Loss']:+.2f}")
    
    print("\n" + "="*80)
    print(f"📅 Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*80 + "\n")

if __name__ == "__main__":
    analizza_tracking()
