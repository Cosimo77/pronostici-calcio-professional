#!/usr/bin/env python3
"""
Test FASE 2 - Simula partite per verificare validazione multi-mercato
"""
import sys
sys.path.insert(0, 'web')
from web.app_professional import ProfessionalCalculator, _calcola_mercati_deterministici

print('🎯 TEST FASE 2 - VALIDAZIONE MULTI-MERCATO')
print('=' * 80)

# Inizializza calculator
calc = ProfessionalCalculator()
calc.carica_dati('data/dataset_features.csv')

# Partite di test (squadre con dati sufficienti)
partite_test = [
    ('Juventus', 'Inter'),
    ('Napoli', 'Milan'),
    ('Roma', 'Atalanta'),
    ('Lazio', 'Fiorentina')
]

print(f'\n✅ Testing {len(partite_test)} partite simulate\n')

# Funzione validazione FASE 2 (copia da app_professional.py)
def _valida_opportunita_fase2(mercato, pred, odds, ev_pct, mercati_data=None):
    """Filtri FASE 2 validati - Multi-mercato"""
    # 1. PAREGGI (FASE 1)
    if mercato == '1X2' and pred == 'D':
        if odds < 2.8:
            return False, 'pareggio_quota_bassa', '1X2'
        if odds > 3.5:
            return False, 'pareggio_quota_alta', '1X2'
        if ev_pct < 25:
            return False, 'pareggio_ev_basso', '1X2'
        return True, 'fase1_pareggio', '1X2'
    
    # 2. DOUBLE CHANCE (FASE 2)
    if mercato == 'DC':
        if odds < 1.2:
            return False, 'dc_quota_bassa', 'DC'
        if odds > 1.8:
            return False, 'dc_quota_alta', 'DC'
        if ev_pct < 10:
            return False, 'dc_ev_basso', 'DC'
        return True, 'fase2_double_chance', 'DC'
    
    # 3. OVER/UNDER 2.5 (FASE 2)
    if mercato == 'OU25':
        if odds < 2.0:
            return False, 'ou_quota_bassa', 'OU25'
        if odds > 2.5:
            return False, 'ou_quota_alta', 'OU25'
        if ev_pct < 15:
            return False, 'ou_ev_basso', 'OU25'
        return True, 'fase2_over_under', 'OU25'
    
    return False, 'mercato_non_validato', mercato

def calc_ev(prob, odds):
    """Calcola Expected Value"""
    return prob * odds - 1

# Test ogni partita
for casa, ospite in partite_test:
    print(f'\n{"="*80}')
    print(f'🏟️  {casa} vs {ospite}')
    print('=' * 80)
    
    # Predizione
    try:
        predizione, probabilita, confidenza = calc.predici_partita_deterministica(casa, ospite)
        mercati = _calcola_mercati_deterministici(casa, ospite, probabilita)
        
        # Simula quote bookmaker (esempio realistico)
        # Quote 1X2
        odds_h = round(1 / (probabilita['H'] * 0.95), 2)  # Margine 5%
        odds_d = round(1 / (probabilita['D'] * 0.95), 2)
        odds_a = round(1 / (probabilita['A'] * 0.95), 2)
        
        # Quote Over/Under 2.5
        prob_over = mercati['mou25']['probabilita']['over']
        prob_under = mercati['mou25']['probabilita']['under']
        odds_over = round(1 / (prob_over * 0.95), 2)
        odds_under = round(1 / (prob_under * 0.95), 2)
        
        # Quote Double Chance (calcolate da 1X2)
        prob_h_1x2 = 1 / odds_h
        prob_d_1x2 = 1 / odds_d
        prob_a_1x2 = 1 / odds_a
        total = prob_h_1x2 + prob_d_1x2 + prob_a_1x2
        prob_h_1x2 /= total
        prob_d_1x2 /= total
        prob_a_1x2 /= total
        
        margin = 1.05
        odds_1x = round(margin / (prob_h_1x2 + prob_d_1x2), 2)
        odds_x2 = round(margin / (prob_d_1x2 + prob_a_1x2), 2)
        odds_12 = round(margin / (prob_h_1x2 + prob_a_1x2), 2)
        
        esiti = {"H": "Casa", "D": "Pareggio", "A": "Trasferta"}
        
        print(f'\n📊 PREDIZIONE:')
        print(f'   Esito: {esiti[predizione]}')
        print(f'   Confidenza: {confidenza:.1%}')
        print(f'   Probabilità: H {probabilita["H"]:.1%}, D {probabilita["D"]:.1%}, A {probabilita["A"]:.1%}')
        
        print(f'\n💰 QUOTE SIMULATE:')
        print(f'   1X2: Casa {odds_h}, Pareggio {odds_d}, Trasferta {odds_a}')
        print(f'   O/U 2.5: Over {odds_over}, Under {odds_under}')
        print(f'   Double Chance: 1X {odds_1x}, X2 {odds_x2}, 12 {odds_12}')
        
        # VALIDAZIONE FASE 2
        fase2_opportunities = []
        
        # 1. Pareggio 1X2
        if predizione == 'D':
            ev = calc_ev(probabilita['D'], odds_d) * 100
            is_valid, reason, market = _valida_opportunita_fase2('1X2', 'D', odds_d, ev)
            if is_valid:
                fase2_opportunities.append({
                    'market': '1X2',
                    'outcome': 'Pareggio',
                    'odds': odds_d,
                    'ev': ev,
                    'prob': probabilita['D'] * 100,
                    'strategy': 'FASE1_PAREGGIO',
                    'roi_backtest': 7.17
                })
        
        # 2. Double Chance
        prob_model_1x = mercati['mdc']['probabilita']['1X']
        prob_model_x2 = mercati['mdc']['probabilita']['X2']
        prob_model_12 = mercati['mdc']['probabilita']['12']
        
        dc_options = [
            ('1X', odds_1x, prob_model_1x),
            ('X2', odds_x2, prob_model_x2),
            ('12', odds_12, prob_model_12)
        ]
        
        for dc_name, dc_odds, dc_prob in dc_options:
            ev = calc_ev(dc_prob, dc_odds) * 100
            is_valid, reason, market = _valida_opportunita_fase2('DC', dc_name, dc_odds, ev)
            if is_valid:
                fase2_opportunities.append({
                    'market': 'Double Chance',
                    'outcome': dc_name,
                    'odds': dc_odds,
                    'ev': ev,
                    'prob': dc_prob * 100,
                    'strategy': 'FASE2_DOUBLE_CHANCE',
                    'roi_backtest': 75.21
                })
        
        # 3. Over/Under 2.5
        ou_options = [
            ('Over', odds_over, prob_over),
            ('Under', odds_under, prob_under)
        ]
        
        for ou_name, ou_odds, ou_prob in ou_options:
            ev = calc_ev(ou_prob, ou_odds) * 100
            is_valid, reason, market = _valida_opportunita_fase2('OU25', ou_name, ou_odds, ev)
            if is_valid:
                fase2_opportunities.append({
                    'market': 'Over/Under 2.5',
                    'outcome': ou_name + ' 2.5',
                    'odds': ou_odds,
                    'ev': ev,
                    'prob': ou_prob * 100,
                    'strategy': 'FASE2_OVER_UNDER',
                    'roi_backtest': 5.86
                })
        
        # RISULTATI
        print(f'\n🎯 OPPORTUNITÀ FASE 2: {len(fase2_opportunities)}')
        
        if fase2_opportunities:
            # Ordina per EV
            fase2_opportunities.sort(key=lambda x: x['ev'], reverse=True)
            
            print('\n' + '─' * 80)
            for i, opp in enumerate(fase2_opportunities, 1):
                print(f'\n{i}. {opp["market"]} - {opp["outcome"]}')
                print(f'   📊 Quota: {opp["odds"]:.2f}')
                print(f'   💰 EV: {opp["ev"]:+.1f}%')
                print(f'   🎲 Prob. Modello: {opp["prob"]:.1f}%')
                print(f'   🏆 ROI Backtest: +{opp["roi_backtest"]:.2f}%')
                print(f'   🎯 Strategia: {opp["strategy"]}')
        else:
            print('   ❌ Nessuna opportunità validata con filtri FASE 2')
            print('   💡 Nota: Quote simulate potrebbero non soddisfare criteri stretti')
    
    except Exception as e:
        print(f'   ❌ Errore: {e}')

print('\n' + '=' * 80)
print('✅ TEST COMPLETATO')
print('=' * 80)
print('\n📝 NOTA: Quote simulate con margine 5% bookmaker')
print('   Opportunità reali dipendono da quote mercato effettive\n')
