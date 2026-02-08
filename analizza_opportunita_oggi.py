#!/usr/bin/env python3
"""Analizza opportunità value betting FASE 2 su partite reali di oggi"""
import os
import sys
from dotenv import load_dotenv
import requests

sys.path.insert(0, 'web')
from web.app_professional import ProfessionalCalculator, _calcola_mercati_deterministici

# Carica configurazione
load_dotenv('.env')
api_key = os.getenv('ODDS_API_KEY')

if not api_key:
    print('❌ API Key non configurata')
    sys.exit(1)

# Mapping nomi squadre The Odds API → Dataset
TEAM_MAPPING = {
    'Inter Milan': 'Inter',
    'AC Milan': 'Milan',
    'AS Roma': 'Roma',
    'Hellas Verona': 'Verona',
    'Atalanta BC': 'Atalanta'
}

def normalize_team(name: str) -> str:
    """Normalizza nome squadra da The Odds API al formato dataset."""
    return TEAM_MAPPING.get(name, name)

def calc_ev(prob, odds):
    return (prob * odds - 1) * 100

def valida_fase2(mercato, pred, odds, ev_pct):
    """Filtri FASE 2 validati su backtest"""
    # FASE 1: Pareggi (ROI +7.17%)
    if mercato == '1X2' and pred == 'D':
        if 2.8 <= odds <= 3.5 and ev_pct >= 25:
            return True, 'FASE1_Pareggi', '+7.17%'
    
    # FASE 2: Double Chance (ROI +75.21%)
    if mercato == 'DC':
        if 1.2 <= odds <= 1.8 and ev_pct >= 10:
            return True, 'FASE2_DoubleChance', '+75.21%'
    
    # FASE 2: Over/Under 2.5 (ROI +5.86%)
    if mercato == 'OU25':
        if 2.0 <= odds <= 2.5 and ev_pct >= 15:
            return True, 'FASE2_OverUnder', '+5.86%'
    
    return False, None, None

# Carica predittore
calc = ProfessionalCalculator()
calc.carica_dati('data/dataset_features.csv')

# Ottieni partite da The Odds API
print('🔍 Recupero partite da The Odds API...\n')
url = f'https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/'
params = {
    'apiKey': api_key,
    'regions': 'eu',
    'markets': 'h2h,spreads,totals',
    'oddsFormat': 'decimal'
}

try:
    response = requests.get(url, params=params, timeout=10)
    partite = response.json()
except Exception as e:
    print(f'❌ Errore API: {e}')
    sys.exit(1)

print(f'📅 Data: 8 febbraio 2026')
print(f'🏟️  Partite analizzate: {len(partite)}')
print('=' * 100)

opportunita = []

for match in partite:
    # Validazione nomi squadre
    home_team = match.get('home_team')
    away_team = match.get('away_team')
    if not home_team or not away_team:
        continue
    
    casa = normalize_team(home_team)
    ospite = normalize_team(away_team)
    
    # Type narrowing per Pylance
    if not casa or not ospite:
        continue
    
    # Predizione modello
    try:
        pred, prob, conf = calc.predici_partita_deterministica(casa, ospite)
        mercati = _calcola_mercati_deterministici(casa, ospite, prob)
    except Exception as e:
        continue  # Squadra non nel dataset
    
    # Estrai quote migliori dai bookmaker
    if not match.get('bookmakers'):
        continue
    
    best_odds = {'h2h': {}, 'totals': {}}
    
    for bookmaker in match['bookmakers']:
        for market in bookmaker.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    key = outcome['name']
                    odds = outcome['price']
                    if key not in best_odds['h2h'] or odds > best_odds['h2h'][key]:
                        best_odds['h2h'][key] = odds
            
            elif market['key'] == 'totals':
                for outcome in market['outcomes']:
                    key = f"{outcome['name']}_{outcome['point']}"
                    odds = outcome['price']
                    if key not in best_odds['totals'] or odds > best_odds['totals'][key]:
                        best_odds['totals'][key] = odds
    
    # Valida opportunità 1X2 (Pareggi)
    if casa in best_odds['h2h']:
        odds_draw = best_odds['h2h'].get('Draw')
        if odds_draw and pred == 'D':
            ev_pct = calc_ev(prob['D'], odds_draw)
            valido, strategia, roi_bt = valida_fase2('1X2', 'D', odds_draw, ev_pct)
            if valido:
                opportunita.append({
                    'partita': f'{casa} vs {ospite}',
                    'mercato': 'Pareggio (X)',
                    'quota': odds_draw,
                    'prob': prob['D'] * 100,
                    'ev': ev_pct,
                    'strategia': strategia,
                    'roi_backtest': roi_bt,
                    'inizio': match['commence_time']
                })
    
    # Valida Over/Under 2.5
    odds_over25 = best_odds['totals'].get('Over_2.5')
    odds_under25 = best_odds['totals'].get('Under_2.5')
    
    if odds_over25:
        prob_over = mercati.get('over_25', 0.5)
        ev_pct = calc_ev(prob_over, odds_over25)
        valido, strategia, roi_bt = valida_fase2('OU25', 'Over', odds_over25, ev_pct)
        if valido:
            opportunita.append({
                'partita': f'{casa} vs {ospite}',
                'mercato': 'Over 2.5',
                'quota': odds_over25,
                'prob': prob_over * 100,
                'ev': ev_pct,
                'strategia': strategia,
                'roi_backtest': roi_bt,
                'inizio': match['commence_time']
            })
    
    if odds_under25:
        prob_under = 1 - mercati.get('over_25', 0.5)
        ev_pct = calc_ev(prob_under, odds_under25)
        valido, strategia, roi_bt = valida_fase2('OU25', 'Under', odds_under25, ev_pct)
        if valido:
            opportunita.append({
                'partita': f'{casa} vs {ospite}',
                'mercato': 'Under 2.5',
                'quota': odds_under25,
                'prob': prob_under * 100,
                'ev': ev_pct,
                'strategia': strategia,
                'roi_backtest': roi_bt,
                'inizio': match['commence_time']
            })

# Mostra risultati
print(f'\n🎯 OPPORTUNITÀ VALUE BETTING VALIDATE:\n')

if len(opportunita) == 0:
    print('❌ Nessuna opportunità trovata che soddisfi i filtri FASE 2')
    print('   Filtri applicati:')
    print('   - Pareggi: quote 2.8-3.5, EV ≥25%')
    print('   - Over/Under 2.5: quote 2.0-2.5, EV ≥15%')
    print('   - Double Chance: quote 1.2-1.8, EV ≥10%')
else:
    for i, opp in enumerate(opportunita, 1):
        print(f'{"="*100}')
        print(f'✅ OPPORTUNITÀ #{i}')
        print(f'{"="*100}')
        print(f'🏟️  Partita: {opp["partita"]}')
        print(f'📅 Inizio: {opp["inizio"]}')
        print(f'🎯 Mercato: {opp["mercato"]}')
        print(f'💰 Quota: {opp["quota"]:.2f}')
        print(f'📊 Probabilità Modello: {opp["prob"]:.1f}%')
        print(f'💎 Expected Value: {opp["ev"]:+.1f}%')
        print(f'🏆 Strategia: {opp["strategia"]}')
        print(f'📈 ROI Backtest: {opp["roi_backtest"]}')
        print()

print(f'\n📊 RIEPILOGO:')
print(f'   Partite analizzate: {len(partite)}')
print(f'   Opportunità validate: {len(opportunita)}')
print(f'   Quota API rimanente: {response.headers.get("x-requests-remaining", "N/A")}/500')
