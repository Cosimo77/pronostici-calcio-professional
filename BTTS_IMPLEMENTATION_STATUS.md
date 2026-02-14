# ⚠️ BTTS Implementation Status - Analisi Critica

**Data**: 14 Febbraio 2026  
**Issue**: Quote BTTS storiche NON disponibili nei dataset CSV

---

## 🔍 Problema Identificato

### Quote BTTS NON Disponibili

**CSV Analizzati**: `I1_2324.csv`, `I1_2425.csv` (105 colonne totali)

**Quote disponibili**:
- ✅ 1X2 (H/D/A): `B365H`, `AvgH`, `MaxH`, etc.
- ✅ Over/Under 2.5: `B365>2.5`, `Avg>2.5`, etc.
- ✅ Asian Handicap: `B365AHH`, `AvgAHH`, etc.
- ✅ Corner markets: `AvgC>2.5`, etc.

**Quote MANCANTI**:
- ❌ **BTTS (Both Teams To Score)**: Nessuna colonna `BTTS`, `BTS`, o simili
- ❌ Nessun bookmaker fornisce quote BTTS storiche in questi CSV

### Dati Disponibili

**Possiamo calcolare outcome BTTS**:
```csv
Colonne: FTHG, FTAG (Full Time Home/Away Goals)
BTTS_Outcome = YES se (FTHG > 0 AND FTAG > 0)
               NO  altrimenti

Esempio:
Genoa 2-2 Inter → BTTS = YES ✅
Genoa 0-1 Inter → BTTS = NO  ❌
```

**NON possiamo calcolare EV**:
```python
# Servono quote bookmaker BTTS per calcolare Expected Value
EV = (prob_model × odds_bookmaker) - 1

# Senza odds_bookmaker → NO backtest rigoroso possibile
```

---

## ❌ Perché NON Procedere con Quote Simulate

### Critical Issue: Quote Inventate = Bug Como-Fiorentina 2.0

**Lezione appresa**: Bug Double Chance (+317% quota inventata)
- Abbiamo fixato 3 bug derivanti da quote DC simulate
- Commit: 09bc8db, 6763dc6, 397b13b
- **ZERO TOLERANCE** per quote non reali

**Se simulassimo quote BTTS**:
```python
# ❌ ANTI-PATTERN
odds_btts_yes = 1.80  # Hardcoded
odds_btts_no = 2.10   # Inventato

# Conseguenze:
# 1. Backtest ROI falso (non riproducibile trading reale)
# 2. EV calculation matematicamente corretta ma quote sbagliate
# 3. Risk: Trade su quote "value" che non esistono nel mercato
```

**Evidenza empirica**:
- Double Chance aveva ROI +75% backtest (quote simulate)
- Trading reale sarebbe stato disastro (quote diverse da simulate)

---

## ✅ Soluzioni Professionali

### Opzione A: Raccolta Dati Live (CONSIGLIATA) ⭐⭐⭐⭐⭐

**Step 1: Configura The Odds API**
```bash
# Registra account: https://the-odds-api.com
# Free tier: 500 requests/month

export ODDS_API_KEY="your_real_key_here"
```

**Step 2: Verifica mercato BTTS disponibile**
```bash
curl "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/?apiKey=$ODDS_API_KEY&markets=btts"

# Output atteso:
{
  "markets": [
    {
      "key": "btts",
      "outcomes": [
        {"name": "Yes", "price": 1.85},
        {"name": "No", "price": 2.05}
      ]
    }
  ]
}
```

**Step 3: Data Collection (1-2 mesi)**
```python
# Script automatico: salva quote BTTS ogni giorno
# File: scripts/collect_btts_odds.py

import json
from datetime import datetime
from integrations.odds_api import OddsAPIClient

client = OddsAPIClient()
matches = client.get_upcoming_odds(markets='btts,h2h,totals')

# Salva in database/CSV
with open(f'data/btts_odds_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
    json.dump(matches, f)

# Dopo 30-60 giorni → ~100-200 partite con quote BTTS reali
```

**Step 4: Backtest con dati reali** (dopo 1-2 mesi)
```python
# Usa quote BTTS raccolte + outcome BTTS da FTHG/FTAG
df_btts = combine_collected_odds_with_results()

# Backtest rigoroso con quote REALI
roi_btts = run_backtest(df_btts, filters={'ev_min': 0.15, 'odds_range': (1.70, 2.30)})
```

**Timeline**:
- Oggi: Configura API key
- Oggi: Deploy script collezione automatica
- Marzo-Aprile 2026: Raccolta dati (30-60 partite)
- Aprile 2026: Backtest + Certificazione FASE3
- Maggio 2026: Deploy tri-strategy con BTTS

**Pro**:
- ✅ Quote 100% reali (stesso standard Pareggi/Under)
- ✅ Backtest affidabile
- ✅ Zero rischio "quote inventate"

**Contro**:
- ⏰ Richiede 1-2 mesi attesa
- 📊 Sample size inizialmente basso (cresce col tempo)

---

### Opzione B: Solo Analisi (NO Trading) ⭐⭐⭐

**Implementazione immediata**:
```python
# Backend calcola probabilità BTTS (già implementato)
mercati['mgg'] = {
    'nome': 'Goal/No Goal',
    'probabilita': {
        'gg': prob_gg,
        'ng': 1 - prob_gg
    },
    'confidenza': max(prob_gg, 1 - prob_gg)
}

# ⚠️ Ma NO filtri value betting
# ⚠️ NO trading reale (solo informativo)
```

**Use case**:
- Dashboard mostra previsione BTTS
- User vede probabilità modello vs bookmaker (se ha quote)
- **NO automatico alert trading** (quote non validate)

**Pro**:
- ✅ Implementazione immediata
- ✅ Valore aggiunto interfaccia

**Contro**:
- ❌ NO value betting automatico
- ❌ NO certificazione trading

---

### Opzione C: Dual-Strategy Consolidata ⭐⭐⭐⭐

**Mantieni sistema attuale**:
- ✅ Pareggi: ROI +7.17% (certificato)
- ✅ Under 2.5: ROI +5.86% (certificato)
- ✅ 516 trade/anno (dual-strategy professionale)
- ✅ Quote 100% reali

**Focus prossimi mesi**:
1. Trading reale dual-strategy
2. Monitoraggio performance live
3. Raccolta dati BTTS in background
4. FASE3 quando dati sufficienti

**Pro**:
- ✅ Sistema production-ready ORA
- ✅ Zero rischio quote simulate
- ✅ BTTS come bonus futuro (non critico)

**Contro**:
- ⏰ BTTS posticipato a Q2 2026

---

## 🎯 Raccomandazione Finale

### Piano Ibrido: Dual-Strategy ORA + BTTS Q2 2026

**Fase 1: Oggi - Trading Dual-Strategy** (Pronto)
```
Bankroll: 10,000 EUR
- 60% Pareggi (6,000 EUR) → ROI +7.17%
- 40% Under 2.5 (4,000 EUR) → ROI +5.86%

Expected: +664 EUR/anno, 516 trade/anno
Status: ✅ PRODUCTION READY
```

**Fase 2: Oggi - Setup Data Collection** (30 min lavoro)
```bash
# 1. Configura API key
export ODDS_API_KEY="..."

# 2. Deploy script collezione
python scripts/collect_btts_odds.py  # Cron giornaliero

# 3. Logging automatico
# Salva in data/btts_historical/
```

**Fase 3: Aprile 2026 - Certificazione BTTS** (quando 100+ partite)
```python
# Backtest con quote reali raccolte
roi_btts = backtest_btts_value(data='btts_historical/')

# Se ROI >3% → Certificare FASE3
# Se ROI <3% → Mercato non profittevole, no implementazione
```

**Fase 4: Maggio 2026 - Tri-Strategy** (se BTTS validato)
```
Allocazione aggiornata:
- 40% Pareggi
- 30% Under 2.5
- 30% BTTS (nuovo)

Expected: +613 EUR/anno, 800+ trade/anno
```

---

## 📊 Alternative Immediate (Mercati con Quote Disponibili)

### Mercati Implementabili SUBITO (Dati CSV)

**Nessuno** - Situazione critica:
1. ❌ BTTS: Quote non disponibili (analizzato sopra)
2. ❌ O/U 1.5: Quote non disponibili CSV (solo 2.5)
3. ❌ O/U 3.5: Quote non disponibili CSV
4. ✅ **Corner O/U**: Quote disponibili (`AvgC>2.5`) - Ma threshold incerto (9.5 o 10.5?)

**Verifica Corner Markets**:
```bash
# Check se AvgC>2.5 significa "Corner Over 9.5" o altro threshold
python3 -c "
import pandas as pd
df = pd.read_csv('data/I1_2324.csv')
df['total_corners'] = df['HC'] + df['AC']
print(df[['HomeTeam', 'AwayTeam', 'HC', 'AC', 'total_corners', 'AvgC>2.5', 'AvgC<2.5']].head(10))
"
```

Se `AvgC>2.5` corrisponde a soglia specifica (es. 9.5 o 10.5):
- ✅ Possiamo fare backtest Corner O/U
- ✅ Quote CSV reali disponibili
- **Priorità**: Corner come alternativa BTTS?

---

## ⚠️ CRITICAL: NO Shortcuts

### Anti-Pattern da EVITARE

**❌ Simulare quote BTTS "realistiche"**:
```python
# WRONG
if prob_gg > 0.55:
    odds_gg_simulated = 1.80  # "Tipica quota BTTS Yes"
    odds_ng_simulated = 2.10
```
→ Stesso errore Double Chance (+317%)

**❌ Usare solo probabilità modello senza quote**:
```python
# WRONG
if prob_gg > 0.60:
    alert_trading("BTTS YES value bet!")
```
→ No EV calculation = no value betting

**❌ Backtest su outcome senza quote**:
```python
# WRONG
df['btts_outcome'] = (df['FTHG'] > 0) & (df['FTAG'] > 0)
df['model_correct'] = df['prob_gg'] > 0.5 == df['btts_outcome']
accuracy = df['model_correct'].mean()  # 63% accuracy
```
→ Accuracy ≠ ROI (servono quote per calcolare profitto)

---

## 🎯 Conclusione

**Status BTTS Implementation**:
- ❌ **NON implementabile ORA** (quote storiche assenti)
- ✅ **Implementabile Q2 2026** (dopo raccolta dati live)
- ⚠️ **Alternativa**: Verifica Corner markets come FASE3 alternativa

**Next Action Consigliata**:
1. **Confermare dual-strategy production** (Pareggi + Under 2.5)
2. **Configurare API key** per collezione BTTS futura
3. **Valutare Corner O/U** come alternativa immediata (verificare threshold)
4. **BTTS posticipato** a Aprile-Maggio 2026

**User Decision Required**:
- Procedi con dual-strategy + data collection BTTS?
- O esplora Corner markets come alternativa immediata?

