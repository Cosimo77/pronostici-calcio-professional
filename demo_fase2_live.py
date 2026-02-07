#!/usr/bin/env python3
"""
Demo FASE 2 - Mostra funzionamento con quote ottimizzate
"""
import sys
sys.path.insert(0, 'web')
from web.app_professional import ProfessionalCalculator, _calcola_mercati_deterministici

print('🎯 DEMO FASE 2 - OPPORTUNITÀ VALUE BETTING')
print('=' * 80)

calc = ProfessionalCalculator()
calc.carica_dati('data/dataset_features.csv')

def calc_ev(prob, odds):
    return prob * odds - 1

def _valida_opportunita_fase2(mercato, pred, odds, ev_pct, mercati_data=None):
    """Filtri FASE 2"""
    if mercato == '1X2' and pred == 'D':
        if odds < 2.8 or odds > 3.5 or ev_pct < 25:
            return False, 'filtrato', '1X2'
        return True, 'fase1_pareggio', '1X2'
    if mercato == 'DC':
        if odds < 1.2 or odds > 1.8 or ev_pct < 10:
            return False, 'filtrato', 'DC'
        return True, 'fase2_double_chance', 'DC'
    if mercato == 'OU25':
        if odds < 2.0 or odds > 2.5 or ev_pct < 15:
            return False, 'filtrato', 'OU25'
        return True, 'fase2_over_under', 'OU25'
    return False, 'non_validato', mercato

# Test con quote ottimizzate per passare filtri
print('\n🏟️  ESEMPIO: Juventus vs Inter')
print('=' * 80)

casa, ospite = 'Juventus', 'Inter'
predizione, probabilita, confidenza = calc.predici_partita_deterministica(casa, ospite)
mercati = _calcola_mercati_deterministici(casa, ospite, probabilita)

esiti = {"H": "Casa", "D": "Pareggio", "A": "Trasferta"}
print(f'\n📊 PREDIZIONE MODELLO:')
print(f'   Esito: {esiti[predizione]} ({confidenza:.1%} confidenza)')
print(f'   Prob: H {probabilita["H"]:.1%} | D {probabilita["D"]:.1%} | A {probabilita["A"]:.1%}')

# Quote ottimizzate per validazione
print(f'\n💰 QUOTE BOOKMAKER (Esempio):')

# 1X2 - Quote normali
odds_h = 2.50
odds_d = 3.20  # Range FASE 1: 2.8-3.5
odds_a = 3.60

print(f'   1X2: Casa {odds_h} | Pareggio {odds_d} | Trasferta {odds_a}')

# Double Chance - Range 1.2-1.8
odds_1x = 1.50  # In range!
odds_x2 = 1.75  # In range!
odds_12 = 1.45  # In range!

print(f'   Double Chance: 1X {odds_1x} | X2 {odds_x2} | 12 {odds_12}')

# Over/Under 2.5 - Range 2.0-2.5
prob_over = mercati['mou25']['probabilita']['over']
prob_under = mercati['mou25']['probabilita']['under']
odds_over = 2.10  # In range!
odds_under = 2.20  # In range!

print(f'   Over/Under 2.5: Over {odds_over} | Under {odds_under}')

# VALIDAZIONE
print(f'\n🎯 VALIDAZIONE FASE 2:')
print('─' * 80)

fase2_opps = []

# 1. Pareggio (se predetto)
if predizione == 'D':
    ev = calc_ev(probabilita['D'], odds_d) * 100
    is_valid, reason, _ = _valida_opportunita_fase2('1X2', 'D', odds_d, ev)
    if is_valid:
        fase2_opps.append({
            'market': '1X2 Pareggio',
            'outcome': 'Pareggio',
            'odds': odds_d,
            'ev': ev,
            'prob': probabilita['D'] * 100,
            'strategy': 'FASE1',
            'roi': 7.17
        })

# 2. Double Chance
prob_1x = mercati['mdc']['probabilita']['1X']
prob_x2 = mercati['mdc']['probabilita']['X2']
prob_12 = mercati['mdc']['probabilita']['12']

for dc_name, dc_odds, dc_prob in [('1X', odds_1x, prob_1x), ('X2', odds_x2, prob_x2), ('12', odds_12, prob_12)]:
    ev = calc_ev(dc_prob, dc_odds) * 100
    is_valid, reason, _ = _valida_opportunita_fase2('DC', dc_name, dc_odds, ev)
    if is_valid:
        fase2_opps.append({
            'market': f'Double Chance {dc_name}',
            'outcome': dc_name,
            'odds': dc_odds,
            'ev': ev,
            'prob': dc_prob * 100,
            'strategy': 'FASE2_DC',
            'roi': 75.21
        })

# 3. Over/Under 2.5
for ou_name, ou_odds, ou_prob in [('Over', odds_over, prob_over), ('Under', odds_under, prob_under)]:
    ev = calc_ev(ou_prob, ou_odds) * 100
    is_valid, reason, _ = _valida_opportunita_fase2('OU25', ou_name, ou_odds, ev)
    if is_valid:
        fase2_opps.append({
            'market': f'Over/Under 2.5',
            'outcome': f'{ou_name} 2.5',
            'odds': ou_odds,
            'ev': ev,
            'prob': ou_prob * 100,
            'strategy': 'FASE2_OU',
            'roi': 5.86
        })

# Risultati
if fase2_opps:
    fase2_opps.sort(key=lambda x: x['ev'], reverse=True)
    
    print(f'✅ {len(fase2_opps)} OPPORTUNITÀ VALIDATE\n')
    
    for i, opp in enumerate(fase2_opps, 1):
        icon = '🟣' if 'FASE1' in opp['strategy'] else ('🔵' if 'DC' in opp['strategy'] else '🟢')
        print(f'{icon} {i}. {opp["market"]} → {opp["outcome"]}')
        print(f'   📊 Quota: {opp["odds"]:.2f}')
        print(f'   💰 Expected Value: {opp["ev"]:+.1f}%')
        print(f'   🎲 Prob. Modello: {opp["prob"]:.1f}%')
        print(f'   🏆 ROI Backtest: +{opp["roi"]:.2f}%')
        print()
else:
    print('❌ Nessuna opportunità validata (filtri non soddisfatti)\n')

print('=' * 80)
print('📝 LEGENDA STRATEGIE:')
print('   🟣 FASE1: Pareggi (ROI +7.17%)')
print('   🔵 FASE2_DC: Double Chance (ROI +75.21%)')
print('   🟢 FASE2_OU: Over/Under 2.5 (ROI +5.86%)')
print('=' * 80)

# Statistiche sistema
print(f'\n📊 STATISTICHE SISTEMA:')
print(f'   Squadre disponibili: {len(calc.squadre_disponibili)}')
print(f'   Cache predizioni: {len(calc.cache_deterministica)}')
print()
