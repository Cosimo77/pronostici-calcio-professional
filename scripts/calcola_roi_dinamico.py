#!/usr/bin/env python3
"""
🔄 CALCOLO ROI DINAMICO
Ricalcola le metriche di backtest sul dataset corrente
Viene eseguito automaticamente quando il dataset viene aggiornato
"""

import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path

def calcola_roi_aggiornato():
    """
    Calcola ROI e metriche su dataset corrente
    
    Returns:
        dict con metriche aggiornate
    """
    
    try:
        # Cerca backtest file in ordine di priorità
        base_path = Path(__file__).parent.parent
        backtest_locations = [
            base_path / 'backtest_trades.csv',
            base_path / 'data' / 'backtest' / 'backtest_trades.csv'
        ]
        
        backtest_file = None
        for location in backtest_locations:
            if location.exists():
                backtest_file = location
                break
        
        if not backtest_file:
            return {
                'error': 'Backtest non disponibile',
                'roi_turnover': 0,
                'return_totale': 0,
                'partite': 0,
                'win_rate': 0,
                'aggiornato': datetime.now().isoformat()
            }
        
        df = pd.read_csv(backtest_file)
        
        # Calcola metriche
        capitale_iniziale = 1000
        profitto_totale = df['profit'].sum()
        stake_totale = df['stake'].sum()
        
        roi_turnover = (profitto_totale / stake_totale * 100) if stake_totale > 0 else 0
        return_totale = (profitto_totale / capitale_iniziale * 100)
        win_rate = (df['won'].sum() / len(df) * 100) if len(df) > 0 else 0
        
        # Evoluzione (ultimi periodi)
        ultimi_100 = df.tail(100)['profit'].sum() / capitale_iniziale * 100 if len(df) >= 100 else 0
        
        metriche = {
            'roi_turnover': round(roi_turnover, 2),
            'return_totale': round(return_totale, 2),
            'partite_totali': len(df),
            'partite_vinte': int(df['won'].sum()),
            'win_rate': round(win_rate, 1),
            'profitto_totale': round(profitto_totale, 2),
            'stake_totale': round(stake_totale, 2),
            'capitale_iniziale': capitale_iniziale,
            'ultimi_100_return': round(ultimi_100, 2),
            'aggiornato': datetime.now().isoformat(),
            'periodo': {
                'da': df['date'].min() if 'date' in df.columns else 'N/A',
                'a': df['date'].max() if 'date' in df.columns else 'N/A'
            }
        }
        
        # Salva metriche in file JSON per accesso rapido
        output_file = Path(__file__).parent.parent / 'cache' / 'roi_metrics.json'
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(metriche, f, indent=2)
        
        print(f"✅ ROI aggiornato: {roi_turnover:.2f}% su {len(df)} partite")
        
        return metriche
        
    except Exception as e:
        print(f"❌ Errore calcolo ROI: {e}")
        return {
            'error': str(e),
            'roi_turnover': 0,
            'return_totale': 0,
            'partite': 0,
            'win_rate': 0,
            'aggiornato': datetime.now().isoformat()
        }

def get_roi_metrics():
    """
    Ottiene metriche ROI dalla cache (se disponibile) o ricalcola
    
    Returns:
        dict con metriche
    """
    base_path = Path(__file__).parent.parent
    
    # Cerca cache in ordine di priorità
    cache_locations = [
        base_path / 'cache' / 'roi_metrics.json',
        base_path / 'data' / 'backtest' / 'roi_metrics.json'
    ]
    
    cache_file = None
    for location in cache_locations:
        if location.exists():
            cache_file = location
            break
    
    # Se cache esiste e ha meno di 1 ora, usa quella
    if cache_file:
        try:
            with open(cache_file, 'r') as f:
                metriche = json.load(f)
                
            # Verifica età cache (max 1 ora)
            aggiornato = datetime.fromisoformat(metriche['aggiornato'])
            eta = (datetime.now() - aggiornato).total_seconds()
            
            if eta < 3600:  # 1 ora
                return metriche
        except:
            pass
    
    # Ricalcola
    return calcola_roi_aggiornato()

if __name__ == '__main__':
    metriche = calcola_roi_aggiornato()
    
    print('\n📊 METRICHE ROI AGGIORNATE\n')
    print('='*60)
    print(f"ROI su turnover:     {metriche['roi_turnover']}%")
    print(f"Return totale:       {metriche['return_totale']}%")
    print(f"Partite totali:      {metriche['partite_totali']}")
    print(f"Win rate:            {metriche['win_rate']}%")
    print(f"Profitto:            €{metriche['profitto_totale']}")
    print(f"Stake totale:        €{metriche['stake_totale']}")
    print('='*60)
