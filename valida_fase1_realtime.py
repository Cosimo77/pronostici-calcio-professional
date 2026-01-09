#!/usr/bin/env python3
"""
🎯 VALIDAZIONE FASE1 - GENNAIO 2026
Sistema professionale per tracking predizioni real-time

Criteri FASE1 (validati su 510 trade, ROI +7.17%):
- Mercato: PAREGGIO (X)
- Quote: 2.8 - 3.5
- Expected Value: 25% - 50%
- Confidenza: >0.35
"""

import sys
import os
import pandas as pd
from datetime import datetime
import csv

# Setup path per import
script_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(script_dir, 'web')
sys.path.insert(0, web_dir)

try:
    from app_professional import ProfessionalCalculator  # type: ignore
except ImportError:
    print("❌ Errore: impossibile importare ProfessionalCalculator")
    print(f"Verifica che web/app_professional.py esista in: {web_dir}")
    sys.exit(1)

# ============================================================================
# CONFIGURAZIONE FASE1
# ============================================================================

FASE1_CONFIG = {
    'mercato': 'Pareggio',
    'quota_min': 2.8,
    'quota_max': 3.5,
    'ev_min': 0.25,      # 25%
    'ev_max': 0.50,      # 50%
    'confidenza_min': 0.35,
    'stake_percent': 0.015,  # 1.5% bankroll (conservativo)
    'kelly_multiplier': 0.387
}

BANKROLL_INIZIALE = 500  # €500 per paper trading

# ============================================================================
# FUNZIONI CORE
# ============================================================================

def calcola_expected_value(prob_modello, quota_mercato):
    """Calcola EV percentuale"""
    ev = (prob_modello * quota_mercato) - 1
    return round(ev * 100, 1)

def valida_opportunita_fase1(predizione, quote_reali):
    """
    Valida se predizione rispetta criteri FASE1
    
    Returns:
        (bool, dict): (is_valid, dettagli)
    """
    prob_x = predizione['probabilita'].get('X', 0)
    quota_x = quote_reali.get('X', 0)
    
    # Check quote range
    if quota_x < FASE1_CONFIG['quota_min'] or quota_x > FASE1_CONFIG['quota_max']:
        return False, {'motivo': f'Quota {quota_x} fuori range 2.8-3.5'}
    
    # Check EV
    ev = calcola_expected_value(prob_x, quota_x)
    ev_decimal = ev / 100
    if ev_decimal < FASE1_CONFIG['ev_min'] or ev_decimal > FASE1_CONFIG['ev_max']:
        return False, {'motivo': f'EV {ev}% fuori range 25-50%'}
    
    # Check confidenza
    confidenza = predizione.get('confidenza', 0)
    if confidenza < FASE1_CONFIG['confidenza_min']:
        return False, {'motivo': f'Confidenza {confidenza:.1%} < 35%'}
    
    return True, {
        'quota_x': quota_x,
        'prob_x': prob_x,
        'ev_percent': ev,
        'confidenza': confidenza
    }

def calcola_stake(bankroll, kelly_fraction=0.387, multiplier=0.25):
    """Calcola stake con Kelly conservativo"""
    return round(bankroll * kelly_fraction * multiplier, 2)

def salva_tracking(tracking_file, trade_data):
    """Salva trade nel CSV tracking"""
    with open(tracking_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Data', 'Giornata', 'Casa', 'Ospite', 'Quota_X', 'EV_%', 
            'Confidenza', 'Predizione', 'Risultato', 'Stake', 
            'Profit_Loss', 'Bankroll', 'ROI_%', 'Note'
        ])
        writer.writerow(trade_data)

# ============================================================================
# ANALISI PARTITE PROSSIME
# ============================================================================

def analizza_prossime_partite(calculator, partite_calendario):
    """
    Analizza partite prossimo weekend e identifica opportunità FASE1
    
    Args:
        calculator: ProfessionalCalculator instance
        partite_calendario: List of (casa, ospite, quote_bookmaker) tuples
    
    Returns:
        List of valid opportunities
    """
    opportunita = []
    
    print("\n" + "="*80)
    print("🔍 ANALISI FASE1 - PROSSIME PARTITE SERIE A")
    print("="*80)
    print(f"Criteri: Pareggio quota {FASE1_CONFIG['quota_min']}-{FASE1_CONFIG['quota_max']}, "
          f"EV {int(FASE1_CONFIG['ev_min']*100)}-{int(FASE1_CONFIG['ev_max']*100)}%\n")
    
    for casa, ospite, quote_book in partite_calendario:
        print(f"\n📊 {casa} vs {ospite}")
        
        # Genera predizione
        try:
            pred = calculator.predici_partita_completa(casa, ospite)
            prob_x = pred['probabilita'].get('X', 0)
            confidenza = pred.get('confidenza', 0)
            
            # Quote bookmaker per pareggio
            quota_x = quote_book.get('X', 0)
            
            if quota_x == 0:
                print("   ⚠️  Quote pareggio non disponibili")
                continue
            
            # Calcola EV
            ev = calcola_expected_value(prob_x, quota_x)
            
            print(f"   Probabilità X: {prob_x:.1%}")
            print(f"   Quota X: {quota_x:.2f}")
            print(f"   EV: {ev:+.1f}%")
            print(f"   Confidenza: {confidenza:.1%}")
            
            # Valida FASE1
            is_valid, dettagli = valida_opportunita_fase1(pred, quote_book)
            
            if is_valid:
                print(f"   ✅ OPPORTUNITÀ FASE1 VALIDATA!")
                opportunita.append({
                    'casa': casa,
                    'ospite': ospite,
                    'quota_x': quota_x,
                    'prob_x': prob_x,
                    'ev_percent': ev,
                    'confidenza': confidenza,
                    'predizione': pred
                })
            else:
                print(f"   ❌ {dettagli['motivo']}")
                
        except Exception as e:
            print(f"   ⚠️  Errore: {e}")
    
    return opportunita

# ============================================================================
# REPORT OPPORTUNITÀ
# ============================================================================

def genera_report_opportunita(opportunita, bankroll=BANKROLL_INIZIALE):
    """Genera report dettagliato opportunità FASE1"""
    
    if not opportunita:
        print("\n" + "="*80)
        print("❌ NESSUNA OPPORTUNITÀ FASE1 IDENTIFICATA")
        print("="*80)
        print("\nConsigli:")
        print("- Attendi prossimo weekend")
        print("- Verifica quote bookmaker aggiornate")
        print("- Criteri FASE1 sono selettivi (qualità > quantità)")
        return
    
    print("\n" + "="*80)
    print(f"✅ {len(opportunita)} OPPORTUNITÀ FASE1 IDENTIFICATE")
    print("="*80)
    
    stake_per_trade = calcola_stake(bankroll)
    roi_potenziale_medio = sum(opp['ev_percent'] for opp in opportunita) / len(opportunita)
    
    print(f"\n💰 Bankroll: €{bankroll:.2f}")
    print(f"💵 Stake per trade: €{stake_per_trade:.2f} ({stake_per_trade/bankroll:.1%} bankroll)")
    print(f"📈 EV medio: {roi_potenziale_medio:+.1f}%")
    print(f"🎯 Win rate atteso: 31.0% (da backtest)")
    
    print("\n" + "-"*80)
    print("📋 LISTA TRADE RACCOMANDATI:")
    print("-"*80)
    
    for i, opp in enumerate(opportunita, 1):
        print(f"\n{i}. {opp['casa']} vs {opp['ospite']}")
        print(f"   Scommessa: PAREGGIO @{opp['quota_x']:.2f}")
        print(f"   Probabilità modello: {opp['prob_x']:.1%}")
        print(f"   Expected Value: {opp['ev_percent']:+.1f}%")
        print(f"   Confidenza: {opp['confidenza']:.1%}")
        print(f"   Stake: €{stake_per_trade:.2f}")
        print(f"   Profitto potenziale: €{stake_per_trade * (opp['quota_x'] - 1):.2f}")
    
    print("\n" + "="*80)
    print("⚠️  REMINDER GESTIONE RISCHIO:")
    print("="*80)
    print("- Max 2 trade stesso giorno")
    print("- Stop dopo 3 loss consecutive (pausa 24h)")
    print("- Drawdown max: -60% → STOP totale")
    print("- Aggiorna tracking CSV dopo ogni trade")
    print("="*80)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n🎯 SISTEMA VALIDAZIONE FASE1 - GENNAIO 2026")
    print("="*80)
    
    # Inizializza calculator
    calculator = ProfessionalCalculator()
    
    # INSERISCI QUI LE PARTITE DEL PROSSIMO WEEKEND
    # Formato: (casa, ospite, {'H': quota_h, 'X': quota_x, 'A': quota_a})
    
    partite_prossime = [
        # ESEMPIO - Sostituisci con partite reali Gennaio 2026
        # ('Juventus', 'Milan', {'H': 2.10, 'X': 3.20, 'A': 3.50}),
        # ('Inter', 'Napoli', {'H': 2.05, 'X': 3.40, 'A': 3.80}),
        # ('Roma', 'Lazio', {'H': 2.30, 'X': 3.10, 'A': 3.20}),
    ]
    
    if not partite_prossime:
        print("\n⚠️  NESSUNA PARTITA CONFIGURATA")
        print("\nPer iniziare:")
        print("1. Vai su Bet365/Snai/Eurobet")
        print("2. Copia quote prossime partite Serie A")
        print("3. Aggiungi a lista 'partite_prossime' in questo script")
        print("4. Riesegui: python3 valida_fase1_realtime.py")
        print("\nEsempio formato:")
        print("  ('Juventus', 'Milan', {'H': 2.10, 'X': 3.20, 'A': 3.50})")
        sys.exit(0)
    
    # Analizza partite
    opportunita = analizza_prossime_partite(calculator, partite_prossime)
    
    # Genera report
    genera_report_opportunita(opportunita)
    
    print("\n💾 Per tracciare trade: aggiorna tracking_fase1_gennaio2026.csv")
    print("📊 Analisi metriche: python3 analizza_tracking_fase1.py\n")
