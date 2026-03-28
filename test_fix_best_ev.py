#!/usr/bin/env python3
"""Test fix selezione best EV positivo"""

import sys
sys.path.append('.')

# Simula dati Milan vs Torino
home = 'Milan'
away = 'Torino'

# Probabilità modello (dal test precedente)
probabilita = {
    'H': 0.558,  # Milan 55.8%
    'D': 0.300,  # Pareggio 30.0%
    'A': 0.142   # Torino 14.2%
}

# Quote mercato reali
odds_home = 1.36
odds_draw = 4.93
odds_away = 9.27

# Calcolo EV e discrepanze (stesso calcolo dell'endpoint)
total_prob_market = (1/odds_home + 1/odds_draw + 1/odds_away)
prob_market_h = (1/odds_home) / total_prob_market
prob_market_d = (1/odds_draw) / total_prob_market
prob_market_a = (1/odds_away) / total_prob_market

def calc_ev(prob, odds):
    return prob * odds - 1

ev_h = calc_ev(probabilita['H'], odds_home)
ev_d = calc_ev(probabilita['D'], odds_draw)
ev_a = calc_ev(probabilita['A'], odds_away)

diff_h = probabilita['H'] - prob_market_h
diff_d = probabilita['D'] - prob_market_d
diff_a = probabilita['A'] - prob_market_a

# Over/Under 2.5 (non disponibili nel test)
diff_over = None
ev_over = None
odds_over_25 = None
diff_under = None
ev_under = None
odds_under_25 = None

print("=" * 70)
print("🧪 TEST FIX: Selezione Best EV Positivo")
print("=" * 70)

# ✅ NUOVA LOGICA (FIXATA)
all_candidates = [
    {'key': '1X2 Casa', 'market': '1X2', 'outcome': 'Casa', 'odds': odds_home, 'ev': ev_h, 'diff': diff_h},
    {'key': '1X2 Pareggio', 'market': '1X2', 'outcome': 'Pareggio', 'odds': odds_draw, 'ev': ev_d, 'diff': diff_d},
    {'key': '1X2 Trasferta', 'market': '1X2', 'outcome': 'Trasferta', 'odds': odds_away, 'ev': ev_a, 'diff': diff_a}
]

if diff_over is not None and ev_over is not None:
    all_candidates.append({
        'key': 'Over 2.5', 'market': 'Over/Under 2.5', 'outcome': 'Over 2.5',
        'odds': odds_over_25, 'ev': ev_over, 'diff': diff_over
    })
if diff_under is not None and ev_under is not None:
    all_candidates.append({
        'key': 'Under 2.5', 'market': 'Over/Under 2.5', 'outcome': 'Under 2.5',
        'odds': odds_under_25, 'ev': ev_under, 'diff': diff_under
    })

print("\n📋 TUTTI I CANDIDATI:")
for c in all_candidates:
    print(f"  {c['outcome']:15s} @ {c['odds']:.2f}  →  EV {c['ev']:+.1%}  |  Diff {c['diff']:+.1%}")

# Filtra solo candidati con EV POSITIVO
positive_ev_candidates = [c for c in all_candidates if c['ev'] > 0]

print(f"\n✅ CANDIDATI CON EV POSITIVO: {len(positive_ev_candidates)}")
for c in positive_ev_candidates:
    print(f"  {c['outcome']:15s} @ {c['odds']:.2f}  →  EV {c['ev']:+.1%}")

# Scegli candidato con EV positivo più alto (se esistono)
if positive_ev_candidates:
    best_candidate = max(positive_ev_candidates, key=lambda x: x['ev'])
    best_market = best_candidate['market']
    best_outcome = best_candidate['outcome']
    best_odds = best_candidate['odds']
    best_ev = best_candidate['ev']
    best_diff = abs(best_candidate['diff'])
    
    print(f"\n🎯 MIGLIORE OPPORTUNITÀ (EV più alto):")
    print(f"  Mercato: {best_market}")
    print(f"  Outcome: {best_outcome}")
    print(f"  Quota: {best_odds:.2f}")
    print(f"  EV: {best_ev:+.1%} ✅")
    print(f"  Discrepanza: {best_diff:.1%}")
else:
    # Nessun EV positivo → Fallback a maggiore discrepanza assoluta
    best_candidate = max(all_candidates, key=lambda x: abs(x['diff']))
    best_market = best_candidate['market']
    best_outcome = best_candidate['outcome']
    best_odds = best_candidate['odds']
    best_ev = best_candidate['ev']
    best_diff = abs(best_candidate['diff'])
    
    print(f"\n⚠️ NESSUN EV POSITIVO - Fallback a discrepanza massima:")
    print(f"  Outcome: {best_outcome}")
    print(f"  Quota: {best_odds:.2f}")
    print(f"  EV: {best_ev:+.1%} ❌ NEGATIVO")
    print(f"  Discrepanza: {best_diff:.1%}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETATO")
print("=" * 70)

# Verifica che il risultato sia corretto
expected_outcome = 'Pareggio'
expected_ev = round(ev_d * 100, 1)

if best_outcome == expected_outcome:
    print(f"✅ PASS: Outcome corretto '{expected_outcome}'")
else:
    print(f"❌ FAIL: Expected '{expected_outcome}', got '{best_outcome}'")

if round(best_ev * 100, 1) == expected_ev:
    print(f"✅ PASS: EV corretto {expected_ev:+.1f}%")
else:
    print(f"❌ FAIL: Expected EV {expected_ev:+.1f}%, got {best_ev*100:+.1f}%")

if best_ev > 0:
    print(f"✅ PASS: EV positivo")
else:
    print(f"❌ FAIL: EV dovrebbe essere positivo!")
