#!/usr/bin/env python3
"""
📊 Live Accuracy Tracker - Confronto Predizioni vs Risultati Reali
Aggiorna tracking_predictions_live.csv con risultati e calcola metriche
"""

import pandas as pd
import sys
from datetime import datetime

TRACKING_FILE = 'tracking_predictions_live.csv'

def load_tracking():
    """Carica file tracking"""
    try:
        df = pd.read_csv(TRACKING_FILE)
        return df
    except FileNotFoundError:
        print(f"❌ File {TRACKING_FILE} non trovato!")
        sys.exit(1)

def add_result(casa: str, ospite: str, risultato: str, gol_casa: int | None = None, gol_ospite: int | None = None):
    """
    Aggiunge risultato reale e calcola correttezza predizioni
    
    Args:
        casa: Nome squadra casa
        ospite: Nome squadra ospite
        risultato: 'H' (casa), 'D' (pareggio), 'A' (trasferta)
        gol_casa: Gol segnati da casa (per O/U e GG/NG)
        gol_ospite: Gol segnati da trasferta (per O/U e GG/NG)
    """
    df = load_tracking()
    
    # Trova partita
    mask = (df['Casa'] == casa) & (df['Ospite'] == ospite) & (df['Risultato_Reale'].isna())
    
    if not mask.any():
        print(f"⚠️  Partita {casa} vs {ospite} non trovata o già aggiornata")
        return
    
    n_rows = mask.sum()
    print(f"✅ Trovata partita: {casa} vs {ospite} ({n_rows} mercati)")
    
    # Aggiorna risultato per ogni mercato
    for idx in df[mask].index:
        mercato = df.loc[idx, 'Mercato']
        predizione = df.loc[idx, 'Predizione']
        quota_val = float(df.loc[idx, 'Quota'])  # type: ignore[arg-type]  # Pandas Scalar to float
        
        risultato_reale = None
        corretto = False
        profit = 0.0
        
        # Mercato 1X2
        if mercato == '1X2':
            risultato_reale = risultato
            if (predizione == 'Casa' and risultato == 'H') or \
               (predizione == 'Pareggio' and risultato == 'D') or \
               (predizione == 'Trasferta' and risultato == 'A'):
                corretto = True
                profit = quota_val - 1  # Profit per 1€ stake
            else:
                profit = -1
        
        # Mercato Over/Under 2.5
        elif mercato == 'OU25' and gol_casa is not None and gol_ospite is not None:
            totale_gol = gol_casa + gol_ospite
            if totale_gol > 2.5:
                risultato_reale = 'Over'
            else:
                risultato_reale = 'Under'
            
            if predizione == risultato_reale:
                corretto = True
                profit = quota_val - 1
            else:
                profit = -1
        
        # Mercato GG/NG
        elif mercato == 'GGNG' and gol_casa is not None and gol_ospite is not None:
            if gol_casa > 0 and gol_ospite > 0:
                risultato_reale = 'GG'
            else:
                risultato_reale = 'NG'
            
            if predizione == risultato_reale:
                corretto = True
                profit = quota_val - 1
            else:
                profit = -1
        
        # Aggiorna DataFrame
        df.loc[idx, 'Risultato_Reale'] = risultato_reale
        df.loc[idx, 'Corretto'] = corretto
        df.loc[idx, 'Profit'] = profit
    
    # Salva
    df.to_csv(TRACKING_FILE, index=False)
    print(f"✅ Risultato salvato per {casa} vs {ospite}")
    print(f"   Risultato: {risultato}")
    if gol_casa is not None:
        print(f"   Score: {gol_casa}-{gol_ospite}")
    print()

def show_stats():
    """Mostra statistiche accuracy live"""
    df = load_tracking()
    
    # Filtra solo predizioni con risultato
    df_completed = df[df['Risultato_Reale'].notna()].copy()
    
    if len(df_completed) == 0:
        print("⚠️  Nessuna predizione completata ancora")
        return
    
    print("=" * 70)
    print("  📊 LIVE ACCURACY TRACKING - STATISTICHE")
    print("=" * 70)
    print()
    
    # Overall
    total = len(df_completed)
    correct = df_completed['Corretto'].sum()
    accuracy = correct / total * 100 if total > 0 else 0
    total_profit = df_completed['Profit'].sum()
    roi = total_profit / total * 100 if total > 0 else 0
    
    print(f"📈 PERFORMANCE COMPLESSIVA:")
    print(f"   Predizioni Totali:     {total}")
    print(f"   Predizioni Corrette:   {correct} ({accuracy:.1f}%)")
    print(f"   Profit Totale:         {total_profit:+.2f}€ (stake 1€)")
    print(f"   ROI:                   {roi:+.1f}%")
    print()
    
    # Per mercato
    print(f"📊 ACCURACY PER MERCATO:")
    print(f"   {'Mercato':<15} {'Total':<8} {'Correct':<10} {'Accuracy':<12} {'Profit':<12} {'ROI':<10}")
    print(f"   {'-'*15} {'-'*8} {'-'*10} {'-'*12} {'-'*12} {'-'*10}")
    
    for mercato in ['1X2', 'OU25', 'GGNG']:
        df_mercato = df_completed[df_completed['Mercato'] == mercato]
        if len(df_mercato) > 0:
            n = len(df_mercato)
            corr = df_mercato['Corretto'].sum()
            acc = corr / n * 100
            prof = df_mercato['Profit'].sum()
            roi_m = prof / n * 100
            
            print(f"   {mercato:<15} {n:<8} {corr:<10} {acc:>6.1f}%      {prof:>+6.2f}€      {roi_m:>+6.1f}%")
    
    print()
    
    # Confronto con backtest
    print(f"🎯 CONFRONTO CON BACKTEST (6 Feb 2026):")
    print(f"   {'Mercato':<15} {'Backtest':<12} {'Live':<12} {'Diff':<10}")
    print(f"   {'-'*15} {'-'*12} {'-'*12} {'-'*10}")
    
    backtest = {
        '1X2': 39.5,
        'OU25': 51.6,
        'GGNG': 50.3
    }
    
    for mercato in ['1X2', 'OU25', 'GGNG']:
        df_mercato = df_completed[df_completed['Mercato'] == mercato]
        if len(df_mercato) > 0:
            live_acc = df_mercato['Corretto'].sum() / len(df_mercato) * 100
            diff = live_acc - backtest[mercato]
            
            print(f"   {mercato:<15} {backtest[mercato]:>6.1f}%      {live_acc:>6.1f}%      {diff:>+6.1f}pp")
    
    print()
    
    # Alert se sotto soglia
    if accuracy < 42:
        print(f"🔴 ALERT: Accuracy complessiva <42% → Considerare rollback modelli")
    elif accuracy < 48:
        print(f"🟡 WARNING: Accuracy 42-48% → Monitorare strettamente, ridurre stake")
    else:
        print(f"🟢 OK: Accuracy ≥48% → Sistema performante")
    
    print()
    print("=" * 70)

def show_pending():
    """Mostra predizioni pending (ancora da validare)"""
    df = load_tracking()
    df_pending = df[df['Risultato_Reale'].isna()]
    
    if len(df_pending) == 0:
        print("✅ Nessuna predizione pending")
        return
    
    print("⏳ PREDIZIONI PENDING:")
    print()
    
    partite = df_pending.groupby(['Data', 'Casa', 'Ospite']).size().reset_index(name='Mercati')
    
    for _, row in partite.iterrows():
        print(f"📅 {row['Data']}: {row['Casa']} vs {row['Ospite']} ({row['Mercati']} mercati)")
        
        df_match = df_pending[(df_pending['Casa'] == row['Casa']) & 
                              (df_pending['Ospite'] == row['Ospite'])]
        
        for _, pred in df_match.iterrows():
            print(f"   {pred['Mercato']:<6} → {pred['Predizione']:<12} (Prob {pred['Probabilita_Sistema']:.0%}, EV {pred['EV_%']:+.1f}%)")
        print()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Track live accuracy delle predizioni')
    parser.add_argument('command', choices=['add', 'stats', 'pending'], 
                       help='Comando: add (aggiungi risultato), stats (mostra statistiche), pending (mostra predizioni da validare)')
    parser.add_argument('--casa', help='Squadra casa')
    parser.add_argument('--ospite', help='Squadra ospite')
    parser.add_argument('--risultato', choices=['H', 'D', 'A'], help='Risultato: H (casa), D (pareggio), A (trasferta)')
    parser.add_argument('--gol-casa', type=int, help='Gol segnati da casa')
    parser.add_argument('--gol-ospite', type=int, help='Gol segnati da trasferta')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        if not args.casa or not args.ospite or not args.risultato:
            print("❌ Per 'add' specificare: --casa, --ospite, --risultato")
            sys.exit(1)
        
        add_result(args.casa, args.ospite, args.risultato, args.gol_casa, args.gol_ospite)
        
    elif args.command == 'stats':
        show_stats()
        
    elif args.command == 'pending':
        show_pending()
