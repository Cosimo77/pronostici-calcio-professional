#!/usr/bin/env python3
"""Analisi professionale fallimenti Double Chance - Non nascondersi, capire e migliorare"""
import numpy as np
import pandas as pd

df = pd.read_csv("tracking_predictions_live.csv")
df_dc = df[df["Mercato"].isin(["Double Chance", "1X", "X2"])].copy()
df_dc_done = df_dc[df_dc["Risultato_Reale"].notna()]

print("=" * 80)
print("🔍 ANALISI APPROFONDITA FALLIMENTI DOUBLE CHANCE")
print("=" * 80)

print("\n📊 BREAKDOWN DETTAGLIATO 8 TRADE:\n")
print(f'{"Data":<12} {"Match":<30} {"Pred":<5} {"Prob%":<7} {"Quota":<6} {"EV%":<6} {"Risultato":<10} {"Profit":<8}')
print("-" * 80)

for idx, row in df_dc_done.iterrows():
    match = f"{row['Casa']}-{row['Ospite']}"[:28]
    pred = str(row["Predizione"])[:4]
    prob = f"{float(row['Probabilita_Sistema']):.1f}"
    quota = f"{float(row['Quota']):.2f}"
    ev = f"{float(row['EV_%']):.1f}"
    result = "✅ WIN" if row["Corretto"] else "❌ LOSS"
    profit = f"€{float(row['Profit']):.2f}"

    print(f'{row["Data"]:<12} {match:<30} {pred:<5} {prob:<7} {quota:<6} {ev:<6} {result:<10} {profit:<8}')

print("\n🎯 PATTERN DEI FALLIMENTI:\n")

# Analizza pattern
df_dc_loss = df_dc_done[df_dc_done["Corretto"] == False]
df_dc_win = df_dc_done[df_dc_done["Corretto"] == True]

df_dc_loss["Probabilita_Sistema"] = pd.to_numeric(df_dc_loss["Probabilita_Sistema"])
df_dc_loss["Quota"] = pd.to_numeric(df_dc_loss["Quota"])
df_dc_loss["EV_%"] = pd.to_numeric(df_dc_loss["EV_%"])

df_dc_win["Probabilita_Sistema"] = pd.to_numeric(df_dc_win["Probabilita_Sistema"])
df_dc_win["Quota"] = pd.to_numeric(df_dc_win["Quota"])
df_dc_win["EV_%"] = pd.to_numeric(df_dc_win["EV_%"])

print("TRADE PERDENTI (5):")
print(f'   Probabilità media sistema: {df_dc_loss["Probabilita_Sistema"].mean():.1f}%')
print(f'   Quota media: {df_dc_loss["Quota"].mean():.2f}')
print(f'   EV medio: {df_dc_loss["EV_%"].mean():.1f}%')
print(f'   Break-even richiesto: {(1/df_dc_loss["Quota"].mean()*100):.1f}%')

print("\nTRADE VINCENTI (3):")
print(f'   Probabilità media sistema: {df_dc_win["Probabilita_Sistema"].mean():.1f}%')
print(f'   Quota media: {df_dc_win["Quota"].mean():.2f}')
print(f'   EV medio: {df_dc_win["EV_%"].mean():.1f}%')

print("\n💡 DIAGNOSI PROBLEMI:\n")

# Problema 1: Overconfidence
avg_prob_loss = df_dc_loss["Probabilita_Sistema"].mean()
avg_quota_loss = df_dc_loss["Quota"].mean()
implied_prob = 1 / avg_quota_loss * 100

print(f"1. CALIBRAZIONE PROBABILITÀ:")
print(f"   Sistema stima: {avg_prob_loss:.1f}%")
print(f"   Mercato implica: {implied_prob:.1f}%")
print(f"   Gap: {avg_prob_loss - implied_prob:+.1f}pp")
if avg_prob_loss > implied_prob + 10:
    print(f"   ⚠️  OVERCONFIDENCE: Il sistema è troppo ottimista su Double Chance")
else:
    print(f"   ✅ Calibrazione ragionevole")

# Problema 2: Selettività
print(f"\n2. QUALITÀ SELEZIONE:")
print(f'   EV medio perdenti: {df_dc_loss["EV_%"].mean():.1f}%')
print(f'   EV medio vincenti: {df_dc_win["EV_%"].mean():.1f}%')
if df_dc_loss["EV_%"].mean() < df_dc_win["EV_%"].mean():
    print(f"   ✅ EV più alti performano meglio (filtro EV funziona)")
else:
    print(f"   ⚠️  EV non predice successo (problema calibrazione)")

# Problema 3: Range quote
print(f"\n3. RANGE QUOTE:")
print(
    f'   Perdenti: {df_dc_loss["Quota"].min():.2f}-{df_dc_loss["Quota"].max():.2f} (avg {df_dc_loss["Quota"].mean():.2f})'
)
print(
    f'   Vincenti: {df_dc_win["Quota"].min():.2f}-{df_dc_win["Quota"].max():.2f} (avg {df_dc_win["Quota"].mean():.2f})'
)

# Problema 4: Sample size
print(f"\n4. STATISTICAL SIGNIFICANCE:")
n = len(df_dc_done)
wr_observed = len(df_dc_win) / n
wr_needed = 1 / df_dc_done["Quota"].astype(float).mean()
std_error = np.sqrt(wr_needed * (1 - wr_needed) / n)
z_score = (wr_observed - wr_needed) / std_error if std_error > 0 else 0

print(f"   Sample size: {n} trade (⚠️ PICCOLO - serve 30+ per confidenza)")
print(f"   WR osservato: {wr_observed*100:.1f}%")
print(f"   WR atteso (quote): {wr_needed*100:.1f}%")
print(f"   Z-score: {z_score:.2f} (|z|<1.96 = non significativo)")

if abs(z_score) < 1.96:
    print(f"   ⚠️  Performance NON statisticamente significativa")
    print(f"      Potrebbe essere SOLO varianza, non problema strutturale!")

print("\n" + "=" * 80)
print("🛠️ SOLUZIONI PROFESSIONALI (NON NASCONDERSI):")
print("=" * 80)

print("\n🎯 PRIORITÀ 1: RACCOGLIERE PIÙ DATI (CRITICO)\n")
print("   Problema: 8 trade sono INSUFFICIENTI per giudicare")
print("   Azione: Continua trading Double Chance per altri 20-30 trade")
print("   Rationale: Z-score -1.03 indica potrebbe essere solo sfortuna")
print("   Timeline: 4-6 settimane di dati prima di conclusioni definitive")

print("\n🔬 PRIORITÀ 2: FILTRI PIÙ STRINGENTI (IMPLEMENTABILE ORA)\n")
print("   Double Chance richiede quote basse (1.30-1.60) per essere profittevole")
print("   Implementazione in app_professional.py:")
print(
    '''
   def _valida_opportunita_fase1_dc(self, market, odds, ev, prob_sistema):
       """Filtri specifici per Double Chance"""
       if market != 'Double Chance':
           return True, 'ok'

       # Filtri più stringenti per DC
       if odds > 1.60:
           return False, 'dc_quota_troppo_alta'
       if ev < 35:  # Non 25%
           return False, 'dc_ev_insufficiente'
       if prob_sistema < 75:  # Non 65%
           return False, 'dc_confidenza_bassa'

       return True, 'ok'
'''
)

print("\n🧪 PRIORITÀ 3: CALIBRAZIONE MODELLO (MEDIO TERMINE)\n")
print("   Script da eseguire: scripts/calibra_double_chance.py")
print("   Azioni:")
print("   1. Train modello separato SOLO per Double Chance")
print("   2. CalibratedClassifierCV con isotonic regression (più flessibile)")
print("   3. Cross-validation 10-fold su ultimi 3 anni Serie A")
print("   4. Threshold EV ottimale via backtest (25%, 30%, 35%, 40%)")

print("\n📊 PRIORITÀ 4: FEATURE ENGINEERING (LUNGO TERMINE)\n")
print("   Feature specifiche Double Chance:")
print("   - Forma ultimi 5 (casa + ospite) = indicatore forza combinata")
print("   - Gap classifica assoluto = distanza posizioni in Serie A")
print("   - Motivation index = bonus salvezza/Champions/scontro diretto")
print("   - Head-to-head ultimi 3 anni = pattern storici")

print("\n💰 PRIORITÀ 5: STAKE SIZING DINAMICO (RISK MANAGEMENT)\n")
print("   Implementazione Kelly fractional:")
print(
    """
   def calcola_stake_dinamico(self, ev, market):
       base_stake = 10.0

       if market == 'Double Chance':
           # Più conservativo su DC finché non migliora
           if ev < 35:
               return 0  # Skip
           elif ev < 45:
               return base_stake * 0.5  # 5€
           else:
               return base_stake  # 10€

       # Altri mercati: stake standard
       return base_stake
"""
)

print("\n" + "=" * 80)
print("📈 TIMELINE PROFESSIONALE:")
print("=" * 80)
print(
    """
SETTIMANA 1-2 (IMMEDIATO):
✓ Implementa filtri stringenti per DC (odds <1.60, EV >35%, prob >75%)
✓ Stake ridotto 5€ su DC finché non migliora
✓ Continua raccolta dati (target: 30 trade DC totali)

SETTIMANA 3-4 (BREVE TERMINE):
✓ Analizza 20+ trade DC, verifica se pattern migliora
✓ Se ROI ancora <-20%, considera calibrazione modello
✓ Backtest filtri stringenti su storico

MESE 2 (MEDIO TERMINE):
✓ Se serve: riaddestra modello con calibrazione isotonica
✓ Feature engineering specifico per DC
✓ Walk-forward validation su 3 stagioni

MESE 3+ (OTTIMIZZAZIONE):
✓ Kelly fractional per sizing ottimale
✓ Portfolio optimization cross-market
✓ Monitoring automatico early warning

CRITERIO STOP-LOSS:
Se dopo 30 trade totali DC mantiene ROI < -15%:
→ Riduci esposizione a 0-2 trade/mese (non esclusione totale)
→ Focus su 1X2 e Over/Under che funzionano
→ Revisione modello completa
"""
)

print("\n" + "=" * 80)
print("✅ QUESTO È APPROCCIO PROFESSIONALE:")
print("=" * 80)
print(
    """
❌ Nascondersi = Escludere DC perché 8 trade vanno male
✅ Professionale = Capire, migliorare, adattare, decidere con dati

Il value betting È esattamente questo:
- Testare mercati con rischio controllato
- Raccogliere dati sufficienti (30+ trade)
- Decidere basandosi su statistical significance
- Migliorare modello continuamente
- Non aver paura dei risultati negativi temporanei
"""
)

print("\n" + "=" * 80)
