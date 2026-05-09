#!/usr/bin/env python3
"""
Piano di Miglioramento Sistema Value Betting
"""
import pandas as pd

df = pd.read_csv("tracking_predictions_live.csv")
df_val = df[~df["Note"].str.contains("FILTERED_OUT", na=False)]
df_done = df_val[df_val["Risultato_Reale"].notna()]

print("=" * 80)
print("🎯 PIANO DI MIGLIORAMENTO SISTEMA VALUE BETTING")
print("=" * 80)

# 1. Performance attuale
print("\n📊 SITUAZIONE ATTUALE:\n")
print(f"Trade completati: {len(df_done)}")
print(f'Win Rate: {(df_done["Corretto"].sum()/len(df_done)*100):.1f}%')
print(f'ROI complessivo: {(df_done["Profit"].sum()/(len(df_done)*10)*100):.1f}%')
print(f'Profit totale: €{df_done["Profit"].sum():.2f}')

# 2. Mercati
print("\n🏆 PERFORMANCE PER MERCATO:\n")
markets = {}
for m in df_done["Mercato"].unique():
    df_m = df_done[df_done["Mercato"] == m]
    trades = len(df_m)
    wr = df_m["Corretto"].sum() / trades * 100
    roi = df_m["Profit"].sum() / (trades * 10) * 100
    markets[m] = {"t": trades, "wr": wr, "roi": roi}

    status = "✅ MANTIENI" if roi > 15 else "⚠️  MONITORA" if roi > 0 else "❌ ELIMINA"
    print(f"{m:20} {trades:2}T  WR:{wr:5.1f}%  ROI:{roi:>6.1f}%  {status}")

# 3. Quote range
print("\n📈 PERFORMANCE PER RANGE QUOTE:\n")
for low, high in [(1.0, 2.0), (2.0, 2.5), (2.5, 3.0), (3.0, 5.0)]:
    df_r = df_done[(df_done["Quota"] >= low) & (df_done["Quota"] < high)]
    if len(df_r) > 0:
        wr = df_r["Corretto"].sum() / len(df_r) * 100
        roi = df_r["Profit"].sum() / (len(df_r) * 10) * 100
        print(f"Quote {low:.1f}-{high:.1f}: {len(df_r):2}T WR:{wr:5.1f}% ROI:{roi:>6.1f}%")

# 4. EV range
print("\n💰 PERFORMANCE PER RANGE EV:\n")
df_done["EV_%"] = pd.to_numeric(df_done["EV_%"], errors="coerce")
for low, high in [(0, 15), (15, 25), (25, 35), (35, 100)]:
    df_ev = df_done[(df_done["EV_%"] >= low) & (df_done["EV_%"] < high)]
    if len(df_ev) > 0:
        wr = df_ev["Corretto"].sum() / len(df_ev) * 100
        roi = df_ev["Profit"].sum() / (len(df_ev) * 10) * 100
        print(f"EV {low:>2}-{high:>3}%: {len(df_ev):2}T WR:{wr:5.1f}% ROI:{roi:>6.1f}%")

print("\n" + "=" * 80)
print("📝 RACCOMANDAZIONI STRATEGICHE:")
print("=" * 80)

# Analizza e genera raccomandazioni
print("\n🎯 AZIONI IMMEDIATE:\n")

# 1. Mercati da escludere
bad_markets = [m for m, d in markets.items() if d["roi"] < -20]
if bad_markets:
    print(f"1. ❌ ESCLUDI mercati con ROI < -20%:")
    for m in bad_markets:
        print(f'   → {m} (ROI {markets[m]["roi"]:.1f}%)')
        print(f'     Motivo: WR {markets[m]["wr"]:.1f}% insufficiente, perdite sistematiche')
else:
    print("1. ✅ Nessun mercato con ROI critico < -20%")

# 2. Mercati da concentrare
good_markets = [m for m, d in markets.items() if d["roi"] > 20 and d["t"] >= 3]
if good_markets:
    print(f"\n2. ✅ CONCENTRA betting su mercati con ROI > 20%:")
    for m in good_markets:
        print(f'   → {m} (ROI {markets[m]["roi"]:.1f}%, WR {markets[m]["wr"]:.1f}%)')
        print(f"     Azione: Aumenta stake, cerca più opportunità simili")
else:
    print("\n2. ⚠️  Nessun mercato con ROI > 20% su sample significativo (≥3T)")

# 3. Range quote ottimale
print("\n3. 🎲 OTTIMIZZA RANGE QUOTE:")
best_quote_range = None
best_roi = -100
for low, high in [(1.0, 2.0), (2.0, 2.5), (2.5, 3.0), (3.0, 5.0)]:
    df_r = df_done[(df_done["Quota"] >= low) & (df_done["Quota"] < high)]
    if len(df_r) >= 3:
        roi = df_r["Profit"].sum() / (len(df_r) * 10) * 100
        if roi > best_roi:
            best_roi = roi
            best_quote_range = (low, high)

if best_quote_range:
    print(f"   → Range migliore: {best_quote_range[0]:.1f}-{best_quote_range[1]:.1f} (ROI {best_roi:.1f}%)")
    print(f"     Azione: Prioritizza quote in questo range")

# 4. EV threshold
print("\n4. 💎 OTTIMIZZA SOGLIA EV:")
best_ev_range = None
best_ev_roi = -100
for low, high in [(0, 15), (15, 25), (25, 35), (35, 100)]:
    df_ev = df_done[(df_done["EV_%"] >= low) & (df_done["EV_%"] < high)]
    if len(df_ev) >= 3:
        roi = df_ev["Profit"].sum() / (len(df_ev) * 10) * 100
        if roi > best_ev_roi:
            best_ev_roi = roi
            best_ev_range = (low, high)

if best_ev_range:
    print(f"   → Range migliore: EV {best_ev_range[0]}-{best_ev_range[1]}% (ROI {best_ev_roi:.1f}%)")
    print(f"     Azione: Filtra solo opportunità in questo range EV")

print("\n" + "=" * 80)
print("🚀 PIANO D'AZIONE PRIORITARIO:")
print("=" * 80)
print(
    """
1. ESCLUSIONE MERCATI (IMMEDIATO):
   ✓ Aggiungi filtro in app_professional.py per escludere Double Chance
   ✓ Codice: if market == 'Double Chance': return False

2. CONCENTRAZIONE (QUESTA SETTIMANA):
   ✓ Focus su 1X2 e Over/Under 2.5 (ROI positivo)
   ✓ Aumenta stake gradualmente su questi mercati (10→15€)
   ✓ Cerca più opportunità in queste categorie

3. FILTRI QUOTE (PROSSIMI 7 GIORNI):
   ✓ Analizza range quote vincenti
   ✓ Rimuovi quote troppo basse (<1.50) o troppo alte (>3.5)
   ✓ Test A/B con diversi range

4. CALIBRAZIONE EV (PROSSIME 2 SETTIMANE):
   ✓ Identifica sweet spot EV (es. 20-35%)
   ✓ EV troppo alti possono indicare errori probabilità
   ✓ Backtest con soglie diverse

5. MIGLIORAMENTO MODELLO ML (PROSSIMO MESE):
   ✓ Riaddestra con feature engineering migliorato
   ✓ Usa solo mercati profittevoli per training
   ✓ Cross-validation più rigorosa
   ✓ Calibrazione probabilità per mercato

6. MONITORING CONTINUO:
   ✓ Rivedi performance settimanalmente
   ✓ Aggiorna filtri basandoti su dati reali
   ✓ Kelly Criterion per sizing ottimale (future)
"""
)

print("=" * 80)
print("💡 ASPETTATIVE REALISTICHE:")
print("=" * 80)
print(
    """
ROI attuale: +5.5% (28 trade)
ROI target 1 mese: +10-15% (50+ trade)
ROI target 3 mesi: +15-20% (150+ trade)
ROI target 6 mesi: +20-25% (300+ trade)

⚠️  Value betting richiede:
   - Disciplina (seguire filtri rigidamente)
   - Pazienza (sample size significativo)
   - Bankroll management (max 2-3% per trade)
   - Tracking accurato (ogni singolo trade)
"""
)

print("=" * 80)
