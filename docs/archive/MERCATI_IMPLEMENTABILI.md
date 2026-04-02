# 📊 Mercati Implementabili - Roadmap Espansione Sistema

**Data**: 14 Febbraio 2026  
**Status Sistema**: Dual-Strategy Certificato (Pareggi + Under 2.5)

---

## 🎯 Mercati Attualmente Certificati per Trading

| Mercato | ROI | Win Rate | Quote Reali | Backtest | Status |
|---------|-----|----------|-------------|----------|--------|
| **Pareggi 1X2** | +7.17% | 31.0% | ✅ The Odds API | ✅ 158 trade | **CERTIFICATO** |
| **Under 2.5** | +5.86% | 46.5% | ✅ The Odds API | ✅ 144 trade | **CERTIFICATO** |

---

## 🚀 Mercati Candidati per Espansione

### Tier 1: Alta Priorità (Quote Reali Disponibili)

#### 1. **BTTS - Both Teams To Score (Goal/No Goal)** ⭐⭐⭐⭐⭐

**Disponibilità Quote**:
- ✅ The Odds API fornisce mercato `btts` (Yes/No)
- ✅ CSV storici hanno gol casa/trasferta per backtest

**Dati per Backtest**:
```csv
Colonne CSV: FTHG, FTAG (Full Time Home/Away Goals)
Calcolo: BTTS = YES se (FTHG > 0 AND FTAG > 0)
Sample: ~2931 partite Serie A (2020-2025)
```

**Implementazione Codice**:
```python
# Già calcolato in app_professional.py (linee ~2513-2535)
prob_gg = (1 - stats_casa.get('clean_sheet_rate', 0.3)) * \
          (1 - stats_ospite.get('clean_sheet_rate', 0.3))

mercati['mgg'] = {
    'nome': 'Goal/No Goal',
    'probabilita': {
        'gg': prob_gg,
        'ng': 1 - prob_gg
    }
}
```

**Potenziale Trading**:
- **Volume**: Alta frequenza (GG ~55% partite Serie A)
- **Variance**: Media (outcome binario)
- **Quote tipiche**: 1.60-2.20 (GG), 1.65-2.30 (NG)
- **Correlazione**: Bassa con Pareggi/Under (diversifica portfolio)

**Prossimi Step**:
1. Verificare endpoint The Odds API per `btts` market
2. Backtest con quote reali CSV (colonne tipo `B365BTTS_Yes`, `Avg_BTTS_Yes`)
3. Testare 3 filtri: Conservativo (EV ≥20%), Moderato (EV ≥15%), Aggressivo (EV ≥10%)
4. Se ROI >3% → Certificare come FASE3

**Difficoltà**: ⭐ Bassa (dati + API disponibili)  
**ROI Stimato**: +4-8% (mercato molto tradato, margini moderati)

---

#### 2. **Over/Under 1.5 Goals** ⭐⭐⭐⭐

**Disponibilità Quote**:
- ⚠️ The Odds API potrebbe fornire (da verificare)
- ✅ CSV storici hanno dati gol per calcolo

**Dati per Backtest**:
```csv
Calcolo: Over 1.5 = (FTHG + FTAG) >= 2
Threshold più basso di O/U 2.5 = più conservativo
```

**Potenziale Trading**:
- **Volume**: Altissima frequenza (~75% partite Serie A Over 1.5)
- **Quote tipiche**: 1.20-1.45 (Over), 2.60-3.50 (Under)
- **Strategia**: Probabile focus su Under 1.5 (quote più alte, eventi rari)

**Prossimi Step**:
1. Verificare se The Odds API fornisce O/U 1.5
2. Backtest con filtri conservativi (Under 1.5 solo se prob >60%)
3. Se quote reali non disponibili → Solo analisi, NO trading

**Difficoltà**: ⭐⭐ Media (dipende da disponibilità quote API)  
**ROI Stimato**: +2-5% (mercato liquid, margini bassi)

---

#### 3. **Over/Under 3.5 Goals** ⭐⭐⭐

**Disponibilità Quote**:
- ⚠️ The Odds API potrebbe fornire (da verificare)
- ✅ CSV storici hanno dati gol

**Dati per Backtest**:
```csv
Calcolo: Over 3.5 = (FTHG + FTAG) >= 4
Evento raro (~25% partite Serie A)
```

**Potenziale Trading**:
- **Volume**: Bassa frequenza
- **Quote tipiche**: 2.20-3.50 (Over), 1.30-1.60 (Under)
- **Strategia**: Focus su Over 3.5 partite offensive (Atalanta, Napoli, Inter)

**Difficoltà**: ⭐⭐ Media  
**ROI Stimato**: +3-7% (nicchia, meno competizione)

---

### Tier 2: Priorità Media (Dati CSV, Quote Simulate)

#### 4. **Corner Over/Under 9.5** ⭐⭐⭐

**Disponibilità Quote**:
- ❌ The Odds API NON fornisce corner (mercato raro API gratuite)
- ✅ CSV storici hanno colonne `HC, AC` (Home/Away Corners)
- ✅ Quote corner storiche: `B365C>2.5`, `AvgC>2.5`, `MaxC>2.5`

**Dati per Backtest**:
```csv
Colonne: HC, AC (corner reali)
Quote: B365C>2.5, B365C<2.5, AvgC>2.5, AvgC<2.5
Sample: ~2931 partite con dati corner
```

**Implementazione Codice**:
```python
# Già calcolato (linee ~2748-2795)
corner_previsti = (media_corner_casa + media_corner_ospite) / 2

mercati['mcorner'] = {
    'nome': 'Totale Corner O/U 9.5',
    'probabilita': {
        'over': prob_over_corner,
        'under': prob_under_corner
    },
    'corner_previsti': corner_previsti
}
```

**Potenziale Trading**:
- **Volume**: Media frequenza
- **Quote tipiche**: 1.80-2.20 (Over/Under equilibrati)
- **Rischio**: ⚠️ Quote CSV potrebbero essere per "Corner Totali O/U 10.5" non 9.5

**Prossimi Step**:
1. Verificare threshold esatto colonne CSV (9.5, 10.5 o altro?)
2. Backtest con quote REALI da CSV
3. **WARNING**: NO trading se quote simulate (solo analisi)
4. Se quote storiche OK → Certificare come mercato secondario

**Difficoltà**: ⭐⭐⭐ Media-Alta (verificare dati CSV)  
**ROI Stimato**: +3-6% (mercato meno tradato, margini migliori)

---

#### 5. **Cards Over/Under 4.5** ⭐⭐

**Disponibilità Quote**:
- ❌ The Odds API NON fornisce cards
- ✅ CSV storici: `HY, AY, HR, AR` (cartellini gialli/rossi)
- ⚠️ Nessuna colonna quote cards nei CSV (solo dati evento)

**Dati per Backtest**:
```csv
Colonne: HY, AY (Yellow Cards), HR, AR (Red Cards)
Calcolo: Total_Cards = HY + AY + (HR + AR) * 2  # Rosso vale doppio?
NO quote storiche → Solo calcolo probabilità modello
```

**Implementazione Codice**:
```python
# Già calcolato (linee ~2690-2747)
cartellini_previsti = (media_y_casa + media_y_ospite) / 2

mercati['mcards'] = {
    'nome': 'Totale Cartellini O/U 4.5',
    'probabilita': {
        'over': prob_over_cards,
        'under': prob_under_cards
    }
}
```

**Potenziale Trading**:
- ❌ **NO TRADING POSSIBILE** (quote reali non disponibili)
- ✅ Solo per analisi e valore aggiunto interfaccia

**Difficoltà**: ⭐⭐⭐⭐ Alta (no quote reali)  
**ROI Stimato**: N/A (non tradabile)

---

#### 6. **Primo Tempo Over/Under 0.5** ⭐⭐

**Disponibilità Quote**:
- ❌ The Odds API probabilmente NON fornisce
- ✅ CSV storici: `HTHG, HTAG` (gol primo tempo)
- ⚠️ Nessuna colonna quote HT nei CSV

**Dati per Backtest**:
```csv
Colonne: HTHG, HTAG (Half Time Home/Away Goals)
Calcolo: HT_Over_05 = (HTHG + HTAG) >= 1
```

**Potenziale Trading**:
- ❌ **NO TRADING** (quote non disponibili)
- ✅ Solo analisi

**Difficoltà**: ⭐⭐⭐⭐ Alta  
**ROI Stimato**: N/A

---

### Tier 3: Bassa Priorità (Mercati Esotici/Complessi)

#### 7. **Exact Score** ⭐

**Disponibilità Quote**:
- ❌ The Odds API non fornisce (mercato complesso)
- ✅ Codice calcola distribuzione Poisson (già implementato)

**Potenziale Trading**:
- ❌ NO TRADING (quote non disponibili + variance altissima)
- Quote tipiche 8.0-25.0 per risultati specifici
- Mercato per bookmaker, non value betting

---

#### 8. **Primo Marcatore** ⭐

**Disponibilità Quote**:
- ❌ The Odds API non fornisce
- Richiede quote individuali giocatori (dati non disponibili)

**Potenziale Trading**:
- ❌ NO TRADING (fuori scope sistema)

---

#### 9. **Handicap Asiatico Reale** ⭐⭐

**Disponibilità Quote**:
- ❌ The Odds API non fornisce AH
- ✅ CSV storici hanno colonne: `B365AHH, B365AHA` (quote handicap)

**Dati per Backtest**:
```csv
Colonne: B365AHH, B365AHA, PAHH, PAHA, MaxAHH, MaxAHA, AvgAHH, AvgAHA
Anche: AHh (valore handicap, es. -0.5, -1.0, +0.5)
```

**Potenziale Trading**:
- ✅ Quote storiche REALI disponibili nei CSV!
- ⚠️ Problema: The Odds API NON fornisce AH live (solo storico)
- **Soluzione**: Usare solo per backtest/analisi, non live trading

**Prossimi Step**:
1. Backtest con quote AH REALI da CSV storico
2. Verificare se pattern AH correlano con 1X2
3. **NO live trading** (API non fornisce quote)

**Difficoltà**: ⭐⭐⭐ Media-Alta  
**ROI Stimato**: +4-9% (mercato professionale, margini buoni)

---

## 🎯 Raccomandazioni Priorità

### Implementare SUBITO (Q1 2026)

1. **BTTS (Goal/No Goal)** - ⭐⭐⭐⭐⭐
   - Quote reali API disponibili
   - Alta frequenza trade
   - Diversifica portfolio (bassa correlazione pareggi/under)
   - **Target**: FASE3 certificata entro Marzo 2026

2. **Over/Under 1.5 Goals** - ⭐⭐⭐⭐
   - Se The Odds API fornisce quote
   - Conservativo (Under 1.5 solo partite difensive)

### Valutare (Q2 2026)

3. **Corner O/U 9.5** - ⭐⭐⭐
   - Backtest con quote CSV storiche
   - Solo se verificato threshold corretto (9.5 vs 10.5)

4. **Over/Under 3.5 Goals** - ⭐⭐⭐
   - Nicchia partite offensive
   - Quote alte, bassa frequenza

### Analisi Only (No Trading)

5. **Cards, Exact Score, Primo Marcatore**
   - Valore aggiunto interfaccia
   - NO trading (quote non disponibili)

---

## 🔍 Workflow Certificazione Mercato

### Step 1: Verifica Quote Reali
```bash
# Test The Odds API per mercato specifico
curl "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/?apiKey=XXX&regions=eu&markets=btts"

# Verifica risposta JSON contiene quote bookmaker reali
```

### Step 2: Backtest con Quote Storiche
```python
# Script backtest template
import pandas as pd

df = pd.read_csv('data/dataset_features.csv')

# Filtra partite con quote disponibili
df_valid = df[df['Avg_BTTS_Yes'].notna()]  # Esempio BTTS

# Calcola EV
df_valid['ev'] = (prob_model * odds) - 1

# Applica filtri
trades = df_valid[
    (df_valid['ev'] >= 0.15) &  # EV minimo 15%
    (df_valid['odds'] >= 1.70) &
    (df_valid['odds'] <= 2.30)
]

# Metriche
roi = (trades['profit'].sum() / len(trades)) * 100
win_rate = (trades['result'] == 'WIN').sum() / len(trades)
```

### Step 3: Validazione Performance
**Criteri Certificazione**:
- ✅ ROI >3% su test set
- ✅ Sample size ≥100 trade
- ✅ Win Rate >42%
- ✅ Max Drawdown <40%
- ✅ Quote 100% reali (no simulate)

### Step 4: Integrazione Sistema
```python
# Aggiungi filtro in web/app_professional.py

def _valida_opportunita_btts(self, odds_yes, odds_no, ev_pct, prob_yes):
    """Filtri BTTS validati backtest"""
    # Focus su Goal/Goal (più frequente)
    if odds_yes < 1.70 or odds_yes > 2.30:
        return False
    if ev_pct < 15:
        return False
    if prob_yes < 0.48:  # Almeno 48% confidenza
        return False
    return True
```

---

## 📊 Impatto Sistema Multi-Mercato

### Scenario: 3 Mercati Certificati (Pareggi + Under + BTTS)

**Allocazione Bankroll**:
```
Totale: 10,000 EUR

40% Pareggi (4,000 EUR)     → ROI +7.17%, ~108 trade/anno
30% Under 2.5 (3,000 EUR)   → ROI +5.86%, ~400 trade/anno
30% BTTS (3,000 EUR)        → ROI +5.00%* (~300 trade/anno stimati)

* Stima conservativa BTTS basata su similarità O/U

Expected ROI Combinato:
= (0.40 × 7.17%) + (0.30 × 5.86%) + (0.30 × 5.00%)
= 2.87% + 1.76% + 1.50%
= +6.13%

Trade Totali: ~808/anno (2.2 trade/giorno)
Profitto Annuale: 613 EUR
```

**Diversificazione**:
- 3 mercati indipendenti
- Correlazione bassa (pareggi vs gol vs BTTS)
- Max Drawdown stimato: -25% (vs -30% dual-strategy)

---

## ⚠️ Rischi e Limitazioni

### 1. Quote API Non Disponibili
**Problema**: The Odds API free tier limita mercati disponibili  
**Soluzione**: Verificare PRIMA di backtest quali mercati API fornisce

### 2. Sample Size Insufficiente
**Problema**: Mercati rari (es. O/U 3.5 Under) = pochi trade  
**Soluzione**: Soglia minima 100 trade per certificazione

### 3. Quote Simulate vs Reali
**Problema**: Backtest con quote simulate = risultati non affidabili  
**Soluzione**: **ZERO TOLERANCE** - Solo quote reali per trading

### 4. Overfitting Filtri
**Problema**: Ottimizzare filtri su test set = bias  
**Soluzione**: Split train/test rigoroso (80/20), walk-forward validation

---

## 🎯 Conclusioni

**Mercati Priorità Massima**:
1. ✅ **BTTS (Goal/No Goal)** - Quote reali + alta frequenza + diversificazione
2. ✅ **Over/Under 1.5** - Se API fornisce quote

**Mercati NO Trading**:
- ❌ Cards, Exact Score, Primo Marcatore (quote non disponibili)
- ❌ Primo Tempo mercati (API non fornisce)

**Target Q1 2026**:
- Sistema **Tri-Strategy**: Pareggi + Under 2.5 + BTTS
- Trade: ~800/anno (vs 516 dual-strategy)
- ROI combinato: +6.13%
- Professional-grade diversificazione

---

**Next Steps**:
1. Verificare endpoint The Odds API per `btts` market
2. Eseguire backtest BTTS con quote REALI
3. Se ROI >3% → Certificare FASE3
4. Deploy tri-strategy production

