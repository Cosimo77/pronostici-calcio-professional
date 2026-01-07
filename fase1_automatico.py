#!/usr/bin/env python3
"""
🤖 SISTEMA FASE1 COMPLETAMENTE AUTOMATICO
- Fetcha partite live da The Odds API
- Identifica opportunità FASE1 automaticamente
- Traccia risultati automaticamente
- Genera report su comando

NO configurazione manuale necessaria!
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import csv

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'web'))
sys.path.insert(0, os.path.join(script_dir, 'integrations'))

try:
    from app_professional import ProfessionalCalculator  # type: ignore
    from odds_api import OddsAPIClient  # type: ignore
except ImportError as e:
    print(f"❌ Errore import: {e}")
    sys.exit(1)

# ============================================================================
# CONFIGURAZIONE FASE1
# ============================================================================

FASE1_CONFIG = {
    'quota_min': 2.8,
    'quota_max': 3.5,
    'ev_min': 0.25,      # 25%
    'ev_max': 0.50,      # 50%
    'confidenza_min': 0.35,
    'kelly_multiplier': 0.25,
    'kelly_fraction': 0.387
}

TRACKING_FILE = 'tracking_fase1_gennaio2026.csv'
BANKROLL_INIZIALE = 500

# ============================================================================
# FUNZIONI CORE
# ============================================================================

def calcola_ev(prob_modello, quota):
    """Calcola Expected Value percentuale"""
    return ((prob_modello * quota) - 1) * 100

def calcola_stake(bankroll, kelly_fraction=0.387, multiplier=0.25):
    """Calcola stake con Kelly conservativo"""
    return round(bankroll * kelly_fraction * multiplier, 2)

def get_bankroll_attuale():
    """Legge bankroll attuale da tracking CSV"""
    try:
        df = pd.read_csv(TRACKING_FILE)
        if len(df) > 0 and 'Bankroll' in df.columns:
            # Filtra righe con bankroll valido
            df_valid = df[df['Bankroll'].notna()]
            if len(df_valid) > 0:
                return float(df_valid['Bankroll'].iloc[-1])
    except:
        pass
    return BANKROLL_INIZIALE

def salva_opportunita(opportunita):
    """Salva opportunità nel tracking CSV"""
    bankroll = get_bankroll_attuale()
    stake = calcola_stake(bankroll)
    
    with open(TRACKING_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Data', 'Giornata', 'Casa', 'Ospite', 'Quota_X', 'EV_%', 
            'Confidenza', 'Predizione', 'Risultato', 'Stake', 
            'Profit_Loss', 'Bankroll', 'ROI_%', 'Note'
        ])
        
        writer.writerow({
            'Data': opportunita['data'],
            'Giornata': opportunita.get('giornata', ''),
            'Casa': opportunita['casa'],
            'Ospite': opportunita['ospite'],
            'Quota_X': f"{opportunita['quota_x']:.2f}",
            'EV_%': f"{opportunita['ev_percent']:.1f}",
            'Confidenza': f"{opportunita['confidenza']:.2f}",
            'Predizione': 'X',
            'Risultato': 'PENDING',
            'Stake': f"{stake:.2f}",
            'Profit_Loss': '0',
            'Bankroll': f"{bankroll:.2f}",
            'ROI_%': '0',
            'Note': 'Auto-identificato'
        })

# ============================================================================
# IDENTIFICAZIONE AUTOMATICA OPPORTUNITÀ
# ============================================================================

def identifica_opportunita_automatico():
    """
    Fetcha partite live da API e identifica opportunità FASE1 automaticamente
    
    Returns:
        List of opportunities
    """
    print("\n" + "="*80)
    print("🤖 SISTEMA FASE1 AUTOMATICO - SCAN PARTITE PROSSIME")
    print("="*80)
    
    # Inizializza clients
    calculator = ProfessionalCalculator()
    odds_client = OddsAPIClient()
    
    # Fetcha partite prossime (7 giorni)
    print("\n📡 Fetching partite da The Odds API...")
    try:
        partite_api = odds_client.get_upcoming_odds(regions='eu', markets='h2h')
    except Exception as e:
        print(f"❌ Errore API: {e}")
        print("\n💡 Verifica:")
        print("   - ODDS_API_KEY configurata in .env")
        print("   - Quota mensile API non esaurita (500 req/mese)")
        return []
    
    if not partite_api:
        print("⚠️  Nessuna partita trovata nei prossimi 7 giorni")
        return []
    
    print(f"✅ Trovate {len(partite_api)} partite Serie A\n")
    
    # Analizza ogni partita
    opportunita = []
    
    for partita in partite_api:
        casa = partita.get('home_team')
        ospite = partita.get('away_team')
        data_partita = partita.get('commence_time', '')
        
        # Quote già parsate da OddsAPIClient
        quota_h = partita.get('odds_home', 0)
        quota_x = partita.get('odds_draw', 0)
        quota_a = partita.get('odds_away', 0)
        
        if quota_x == 0:
            continue
        
        print(f"📊 {casa} vs {ospite}")
        print(f"   Data: {data_partita[:10]}")
        print(f"   Quota X: {quota_x:.2f}")
        
        # Check range quote FASE1
        if quota_x < FASE1_CONFIG['quota_min'] or quota_x > FASE1_CONFIG['quota_max']:
            print(f"   ❌ Quota fuori range {FASE1_CONFIG['quota_min']}-{FASE1_CONFIG['quota_max']}")
            continue
        
        # Genera predizione
        try:
            predizione, probabilita, confidenza = calculator.predici_partita_deterministica(casa, ospite)
            prob_x = probabilita.get('D', 0)  # 'D' = Draw (pareggio)
        except Exception as e:
            print(f"   ⚠️  Errore predizione: {e}")
            continue
        
        # Calcola EV
        ev_percent = calcola_ev(prob_x, quota_x)
        
        print(f"   Probabilità X: {prob_x:.1%}")
        print(f"   EV: {ev_percent:+.1f}%")
        print(f"   Confidenza: {confidenza:.1%}")
        
        # Valida criteri FASE1
        checks = []
        checks.append(('Quota range', quota_x >= FASE1_CONFIG['quota_min'] and quota_x <= FASE1_CONFIG['quota_max']))
        checks.append(('EV range', ev_percent >= FASE1_CONFIG['ev_min']*100 and ev_percent <= FASE1_CONFIG['ev_max']*100))
        checks.append(('Confidenza', confidenza >= FASE1_CONFIG['confidenza_min']))
        
        if all(check[1] for check in checks):
            print(f"   ✅ OPPORTUNITÀ FASE1 VALIDATA!")
            
            opportunita.append({
                'data': data_partita[:10],
                'casa': casa,
                'ospite': ospite,
                'quota_x': quota_x,
                'prob_x': prob_x,
                'ev_percent': ev_percent,
                'confidenza': confidenza
            })
            
            # Salva automaticamente
            salva_opportunita(opportunita[-1])
            print(f"   💾 Salvata nel tracking automaticamente")
        else:
            failed = [check[0] for check in checks if not check[1]]
            print(f"   ❌ Falliti: {', '.join(failed)}")
        
        print()
    
    return opportunita

# ============================================================================
# AGGIORNAMENTO AUTOMATICO RISULTATI
# ============================================================================

def aggiorna_risultati_automatico():
    """
    Aggiorna automaticamente risultati partite completate
    Fetcha risultati finali da API
    """
    print("\n" + "="*80)
    print("🔄 AGGIORNAMENTO AUTOMATICO RISULTATI")
    print("="*80)
    
    try:
        df = pd.read_csv(TRACKING_FILE)
    except FileNotFoundError:
        print("❌ Nessun tracking trovato")
        return
    
    # Filtra solo trade pending
    df_pending = df[df['Risultato'] == 'PENDING'].copy()
    
    if len(df_pending) == 0:
        print("✅ Tutti i trade hanno risultato aggiornato")
        return
    
    print(f"⏳ {len(df_pending)} trade pending da aggiornare\n")
    
    # Inizializza API client
    odds_client = OddsAPIClient()
    
    aggiornati = 0
    
    for idx, row in df_pending.iterrows():
        casa = row['Casa']
        ospite = row['Ospite']
        data = row['Data']
        
        print(f"🔍 {casa} vs {ospite} ({data})")
        
        # Cerca risultato finale
        # (The Odds API non ha risultati - useremo dataset)
        try:
            calculator = ProfessionalCalculator()
            
            # Cerca nel dataset partite passate
            df_partite = calculator.df_features
            match = df_partite[
                (df_partite['HomeTeam'] == casa) & 
                (df_partite['AwayTeam'] == ospite) &
                (df_partite['Date'].astype(str).str.contains(data))
            ]
            
            if len(match) == 0:
                print(f"   ⏳ Partita non ancora giocata o non nel dataset")
                continue
            
            risultato = match.iloc[0]['FTR']
            
            # Aggiorna tracking (usando .at per singoli valori - più veloce)
            df.at[idx, 'Risultato'] = risultato  # type: ignore
            
            # Calcola P/L
            stake = float(row['Stake'])
            quota_x = float(row['Quota_X'])
            
            if risultato == 'X':
                profit = stake * (quota_x - 1)
                print(f"   ✅ WIN - Pareggio! Profit: €{profit:+.2f}")
            else:
                profit = -stake
                print(f"   ❌ LOSS - {risultato} - Loss: €{profit:.2f}")
            
            # Aggiorna bankroll
            bankroll_precedente = float(row['Bankroll'])
            bankroll_nuovo = bankroll_precedente + profit
            
            df.at[idx, 'Profit_Loss'] = f"{profit:.2f}"  # type: ignore
            df.at[idx, 'Bankroll'] = f"{bankroll_nuovo:.2f}"  # type: ignore
            
            # Calcola ROI
            roi = ((bankroll_nuovo - BANKROLL_INIZIALE) / BANKROLL_INIZIALE) * 100
            df.at[idx, 'ROI_%'] = f"{roi:.2f}"  # type: ignore
            
            aggiornati += 1
            
        except Exception as e:
            print(f"   ⚠️  Errore: {e}")
    
    # Salva CSV aggiornato
    if aggiornati > 0:
        df.to_csv(TRACKING_FILE, index=False)
        print(f"\n✅ {aggiornati} risultati aggiornati")
    else:
        print("\n⏳ Nessun risultato disponibile ancora")

# ============================================================================
# REPORT AUTOMATICO
# ============================================================================

def genera_report_automatico():
    """Genera report performance completo"""
    try:
        df = pd.read_csv(TRACKING_FILE)
    except FileNotFoundError:
        print("❌ Nessun tracking trovato")
        return
    
    # Filtra trade completati
    df_completati = df[df['Risultato'] != 'PENDING'].copy()
    
    print("\n" + "="*80)
    print("📊 REPORT PERFORMANCE FASE1")
    print("="*80)
    
    if len(df_completati) == 0:
        print("\n⏳ Nessun trade completato ancora")
        print(f"📋 Trade pending: {len(df)}")
        return
    
    # Metriche
    n_trade = len(df_completati)
    n_win = len(df_completati[df_completati['Risultato'] == 'X'])
    win_rate = (n_win / n_trade * 100) if n_trade > 0 else 0
    
    profit_total = df_completati['Profit_Loss'].astype(float).sum()
    bankroll_final = float(df_completati['Bankroll'].iloc[-1])
    roi = float(df_completati['ROI_%'].iloc[-1])
    
    print(f"\n📈 METRICHE:")
    print(f"   Trade completati: {n_trade}")
    print(f"   Win: {n_win} | Loss: {n_trade - n_win}")
    print(f"   Win Rate: {win_rate:.1f}% (target: 31.0%)")
    print(f"   Profit/Loss: €{profit_total:+.2f}")
    print(f"   Bankroll: €{BANKROLL_INIZIALE:.2f} → €{bankroll_final:.2f}")
    print(f"   ROI: {roi:+.2f}% (target: +7.17%)")
    
    # Decision
    print("\n🚦 DECISIONE:")
    if n_trade < 20:
        print(f"   ⏳ Continua validazione ({n_trade}/20 minimi)")
    elif roi >= 3.0:
        print("   ✅ SISTEMA VALIDATO - Considera deploy reale!")
    elif roi >= 0:
        print("   ⚠️  Performance incerta - Continua monitoring")
    else:
        print("   ❌ Performance negativa - Rivedi strategia")
    
    # Trade pending
    n_pending = len(df[df['Risultato'] == 'PENDING'])
    if n_pending > 0:
        print(f"\n📋 Trade pending: {n_pending}")
    
    print("\n" + "="*80)

# ============================================================================
# MAIN - INTERFACCIA UTENTE
# ============================================================================

def main():
    """Menu principale"""
    
    print("\n" + "="*80)
    print("🤖 SISTEMA FASE1 AUTOMATICO")
    print("="*80)
    print("\nOpzioni:")
    print("  1. 🔍 SCAN - Identifica opportunità automaticamente")
    print("  2. 🔄 UPDATE - Aggiorna risultati automaticamente")
    print("  3. 📊 REPORT - Mostra performance")
    print("  4. 🚀 AUTO - Scan + Update + Report (tutto automatico)")
    print("  5. ❌ ESCI")
    
    scelta = input("\nScelta: ").strip()
    
    if scelta == '1':
        opportunita = identifica_opportunita_automatico()
        if opportunita:
            print(f"\n✅ {len(opportunita)} opportunità salvate automaticamente")
            print(f"💾 Tracking: {TRACKING_FILE}")
    
    elif scelta == '2':
        aggiorna_risultati_automatico()
    
    elif scelta == '3':
        genera_report_automatico()
    
    elif scelta == '4':
        print("\n🚀 MODALITÀ COMPLETAMENTE AUTOMATICA")
        print("="*80)
        
        # Step 1: Scan opportunità
        opportunita = identifica_opportunita_automatico()
        
        # Step 2: Aggiorna risultati
        if os.path.exists(TRACKING_FILE):
            aggiorna_risultati_automatico()
        
        # Step 3: Report
        if os.path.exists(TRACKING_FILE):
            genera_report_automatico()
    
    elif scelta == '5':
        print("\n👋 Ciao!")
        return
    
    else:
        print("\n❌ Scelta non valida")

if __name__ == "__main__":
    main()
