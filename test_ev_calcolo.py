#!/usr/bin/env python3
"""Verifica calcolo EV per Milan vs Torino"""

# Dati reali dal test
prob_H = 0.558  # Milan 55.8%
prob_D = 0.300  # Pareggio 30.0%
prob_A = 0.142  # Torino 14.2%

# Quote mercato reali
odds_home = 1.36  # Milan
odds_draw = 4.93  # Pareggio
odds_away = 9.27  # Torino

# Calcolo probabilità implicite mercato
total_prob_market = (1/odds_home + 1/odds_draw + 1/odds_away)
margin = (total_prob_market - 1) * 100

prob_market_h = (1/odds_home) / total_prob_market
prob_market_d = (1/odds_draw) / total_prob_market
prob_market_a = (1/odds_away) / total_prob_market

# Expected Value
def calc_ev(prob, odds):
    return prob * odds - 1

ev_h = calc_ev(prob_H, odds_home)
ev_d = calc_ev(prob_D, odds_draw)
ev_a = calc_ev(prob_A, odds_away)

# Discrepanze
diff_h = prob_H - prob_market_h
diff_d = prob_D - prob_market_d
diff_a = prob_A - prob_market_a

print("=" * 70)
print("🔍 ANALISI EV MILAN vs TORINO")
print("=" * 70)

print("\n📊 PROBABILITÀ MODELLO:")
print(f"  Milan casa: {prob_H:.1%}")
print(f"  Pareggio: {prob_D:.1%}")
print(f"  Torino trasferta: {prob_A:.1%}")

print("\n💰 QUOTE MERCATO:")
print(f"  Milan: {odds_home:.2f}")
print(f"  Pareggio: {odds_draw:.2f}")
print(f"  Torino: {odds_away:.2f}")
print(f"  Margine bookmaker: {margin:.1f}%")

print("\n📈 PROBABILITÀ IMPLICITE MERCATO:")
print(f"  Milan: {prob_market_h:.1%} (quota {odds_home:.2f})")
print(f"  Pareggio: {prob_market_d:.1%} (quota {odds_draw:.2f})")
print(f"  Torino: {prob_market_a:.1%} (quota {odds_away:.2f})")

print("\n💎 EXPECTED VALUE:")
print(f"  EV Casa (Milan): {ev_h:+.1%} {'❌ NEGATIVO' if ev_h < 0 else '✅ POSITIVO'}")
print(f"  EV Pareggio: {ev_d:+.1%} {'❌ NEGATIVO' if ev_d < 0 else '✅ POSITIVO'}")
print(f"  EV Trasferta (Torino): {ev_a:+.1%} {'❌ NEGATIVO' if ev_a < 0 else '✅ POSITIVO'}")

print("\n📐 DISCREPANZE MODELLO vs MERCATO:")
print(f"  Diff Casa: {diff_h:+.1%} (modello sottovaluta Milan)")
print(f"  Diff Pareggio: {diff_d:+.1%}")
print(f"  Diff Trasferta: {diff_a:+.1%}")

print("\n" + "=" * 70)
print("🐛 BUG IDENTIFICATO:")
print("=" * 70)

# Logica ATTUALE (ERRATA)
all_diffs = {
    '1X2 Casa': abs(diff_h),
    '1X2 Pareggio': abs(diff_d),
    '1X2 Trasferta': abs(diff_a)
}
best_market_key_wrong = max(all_diffs.keys(), key=lambda k: all_diffs[k])
best_outcome_wrong = best_market_key_wrong.split(' ')[1]

if best_outcome_wrong == 'Casa':
    best_ev_wrong = ev_h
    best_odds_wrong = odds_home
elif best_outcome_wrong == 'Pareggio':
    best_ev_wrong = ev_d
    best_odds_wrong = odds_draw
else:
    best_ev_wrong = ev_a
    best_odds_wrong = odds_away

print("\n❌ LOGICA ATTUALE (ERRATA):")
print(f"  Sceglie: {best_outcome_wrong} @ {best_odds_wrong:.2f}")
print(f"  EV: {best_ev_wrong:+.1%}")
print(f"  Ragione: Discrepanza assoluta più grande ({all_diffs[best_market_key_wrong]:.1%})")
print(f"  PROBLEMA: Ignora che l'EV è NEGATIVO!")

# Logica CORRETTA
all_evs = {
    'Casa': ev_h,
    'Pareggio': ev_d,
    'Trasferta': ev_a
}
positive_evs = {k: v for k, v in all_evs.items() if v > 0}

if positive_evs:
    best_outcome_correct = max(positive_evs.keys(), key=lambda k: positive_evs[k])
    best_ev_correct = positive_evs[best_outcome_correct]
    
    if best_outcome_correct == 'Casa':
        best_odds_correct = odds_home
    elif best_outcome_correct == 'Pareggio':
        best_odds_correct = odds_draw
    else:
        best_odds_correct = odds_away
    
    print("\n✅ LOGICA CORRETTA:")
    print(f"  Sceglie: {best_outcome_correct} @ {best_odds_correct:.2f}")
    print(f"  EV: {best_ev_correct:+.1%}")
    print(f"  Ragione: EV positivo più alto")
else:
    print("\n✅ LOGICA CORRETTA:")
    print(f"  Nessuna opportunità (tutti EV negativi)")

print("\n" + "=" * 70)
