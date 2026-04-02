# 🎯 Guida Trading Professionale - Sistema Pronostici Calcio

## Sistema Enterprise per Betting Serio

Questo sistema è progettato per **trading professionistico** con gestione matematica del rischio, stake sizing ottimale e tracking avanzato delle performance.

---

## 🚀 Quick Start

### 1. Avvia Sistema
```bash
cd /Users/cosimomassaro/Desktop/pronostici_calcio
python3 -m web.app_professional
```

**Dashboard principale**: http://localhost:5008/diario

---

## 💰 Bankroll Management

### Configurazione Iniziale

1. **Apri Dashboard** → Tab "Trading Dashboard"
2. **Configura Bankroll**:
   - **Capitale Iniziale**: Es. €1000 (minimo €100)
   - **Kelly Fraction**: `0.25` (1/4 Kelly - Conservativo, raccomandato)
   - **Stop Loss**: `30%` (ferma trading a -30% capitale)

### Metriche Bankroll

Il sistema traccia automaticamente:

- **Bankroll Corrente**: Capitale attuale (iniziale + profit/loss)
- **Unità Betting**: 1% del bankroll corrente (es. €10 su €1000)
- **ROI Bankroll**: Rendimento % sul capitale totale

**Update automatico**: Il bankroll si aggiorna ad ogni bet completata (WIN/LOSS).

---

## 🎲 Kelly Criterion - Stake Sizing Matematico

### Formula Kelly

Il sistema calcola lo **stake ottimale** basato sulla **probabilità di vincita** e **quota bookmaker**:

```
Kelly Fraction (f) = (bp - q) / b

Dove:
- b = quota - 1 (net odds)
- p = probabilità vincita
- q = 1 - p
```

**Conservativo**: Usa 1/4 Kelly per ridurre varianza (evita rovina).

### Come Usare Kelly Calculator

#### Tab "Trading Dashboard" → Kelly Criterion Calculator

**Input**:
- **Probabilità Vincita**: Es. `45%` (dalla dashboard opportunità)
- **Quota**: Es. `3.20` (da Sisal/bookmaker)

**Click**: "Calcola Stake Ottimale"

**Output**:
```
Kelly Stake: €50.00
Unità: 5.0 U
% Bankroll: 5.0%
Expected Value: +44.0%
```

**Interpretazione**:
- **Stake Suggerito**: €50 (ma sistema cap max 5% bankroll)
- **5 Unità**: Puntata aggressiva (normale: 1-3 U)
- **EV +44%**: Valore atteso ottimo (>20% target FASE2)

### Esempio Reale

**Scenario**: Opportunità Parma 1X

1. Dashboard: EV Modello +23.3%, prob modello ~35%
2. Kelly Calculator:
   - Probabilità: `35%`
   - Quota: `1.30`
   - **Output**: Kelly Stake €8.50 (~0.85 U)

3. **Decision**: Stake €10 (1 unità) → Kelly suggerisce puntata leggera su quote basse.

---

## 📊 Risk Metrics Professionali

### Metriche Calcolate

Il sistema calcola automaticamente:

#### 1. **Sharpe Ratio** (annualizzato)
- **Formula**: `(Mean Profit / Std Profit) * √252`
- **Target**: >1.0 (buono), >2.0 (eccellente)
- **Interpretazione**: Rendimento aggiustato per rischio
  - 0.5 = Mediocre
  - 1.0 = Buono
  - 2.0 = Ottimo (hedge fund level)

#### 2. **Max Drawdown**
- **Max perdita consecutiva** da picco equity
- **Target**: <20% bankroll iniziale
- **Stop Loss**: Se drawdown >30% → ferma trading, rianalizza strategia

#### 3. **Win/Loss Ratio**
- **Media vincita / Media perdita**
- **Target**: >1.2 (win medie superiori a loss medie)
- **Esempio**: Avg Win €15 / Avg Loss €10 = 1.5 ratio

#### 4. **Profit Factor**
- **Total Wins / Total Losses**
- **Target**: >1.5 (sostenibile long-term)
- **Esempio**: €500 vinte / €300 perse = 1.67 PF

---

## 📈 Equity Curve - Analisi Visuale

### Grafico Bankroll

**Tab "Trading Dashboard"** → Visualizza grafico equity curve automatico:

- **Linea Blu**: Bankroll corrente (equity curve)
- **Linea Gialla Tratteggiata**: Capitale iniziale (baseline)
- **Hover**: Mostra dettagli bet (partita, risultato, profit)

### Segnali Equity Curve

✅ **Trend Rialzista**: Bankroll sopra capitale iniziale → sistema profittevole

⚠️ **Flat**: Bankroll oscillante → variance alta, sample size basso

❌ **Trend Ribassista**: Bankroll sotto capitale → stop loss, riconsidera filtri

---

## 🎓 Workflow Trading Professionale

### 1. **Setup Iniziale** (una tantum)

```bash
# Configura bankroll
1. Dashboard → Trading Dashboard
2. Capitale Iniziale: €1000
3. Kelly Fraction: 0.25 (1/4)
4. Stop Loss: 30%
5. Salva Configurazione
```

### 2. **Trova Opportunità** (giornaliero)

```bash
# Dashboard opportunità
http://localhost:5008/upcoming_matches

Filtri FASE2:
- Double Chance (1X, X2)
- EV 20-25% (sweet spot validato)
- Quote 1.3-2.5 (range profittevole)
```

### 3. **Calcola Stake** (per ogni opportunità)

```bash
# Metodo 1: Kelly Criterion (matematico)
1. Trading Dashboard → Kelly Calculator
2. Input: Prob 45%, Quota 3.20
3. Output: Stake €50 (5 U)
4. Usa stake suggerito

# Metodo 2: Flat Betting (semplice)
- Sempre 1-2 Unità (€10-20 su €1000)
- Meno varianza, più conservativo
```

### 4. **Aggiungi al Diario**

```bash
# Dashboard opportunità
1. Click "Aggiungi al Diario"
2. Verifica quota su Sisal (prompt)
3. Salva come PENDING
4. Stake: MONITOR (decidi pre-partita)
```

### 5. **Pre-Partita: Edit Stake**

```bash
# Diario → In Attesa
1. Click matita (edit)
2. Stake: Kelly suggerisce €50 → Inserisci 50
3. Quota: Verifica quota finale Sisal
4. Salva
```

### 6. **Post-Partita: Risultato**

```bash
# Diario → In Attesa
1. Click WIN / LOSS / SKIP
2. Sistema calcola profit automatico
3. Bankroll aggiornato real-time
4. Equity curve aggiornata
```

### 7. **Analisi Performance** (settimanale/mensile)

```bash
# Diario → Trading Dashboard
1. Verifica equity curve trend
2. Check Sharpe Ratio >1.0
3. Max Drawdown <20%
4. ROI Bankroll >5% (mensile target)

# Decision Rules
- ROI <-10% → STOP, rianalizza filtri
- Drawdown >30% → STOP, wait recovery
- Sharpe <0.5 → Sistema non profittevole
- ROI >10% mensile → Aumenta bankroll gradualmente
```

---

## ⚠️ Rules Betting Professionale

### 1. **Disciplina**
- ❌ **MAI superare** stake Kelly suggerito
- ❌ **MAI puntare** >5% bankroll su singola bet
- ✅ **SEMPRE tracciare** tutte le puntate (anche SKIP)

### 2. **Stop Loss Obbligatorio**
- **Soglia**: -30% bankroll iniziale
- **Action**: Ferma trading, rianalizza sistema
- **Recovery**: Riparti con stake ridotti (50% unità)

### 3. **Variance Management**
- **Min Sample Size**: 50+ bet per validare sistema
- **Expected Variance**: Win rate 30-35% normale (double chance)
- **Losing Streaks**: 5-7 loss consecutive normali (non panic)

### 4. **Bankroll Growth**
- **ROI >20% annuo**: Incrementa bankroll +50%
- **Stake Adjustment**: Ricalcola unità betting (1% nuovo bankroll)
- **Gradual Scale**: No jump improvvisi (max +20% stake/mese)

---

## 📊 Metriche Target Professionali

| Metrica | Target Minimo | Target Ottimale | Action se sotto |
|---------|---------------|-----------------|-----------------|
| **ROI Turnover** | 0% | +7%+ | Rivedi filtri EV |
| **ROI Bankroll** | +5% mensile | +10%+ mensile | Aumenta sample |
| **Win Rate** | 28% | 32%+ | Normale per DC |
| **Sharpe Ratio** | 0.5 | 1.5+ | Riduci variance |
| **Max Drawdown** | <30% | <20% | Stop loss |
| **Profit Factor** | 1.2 | 1.5+ | Migliora EV filtri |
| **Avg Bet Size** | 1 U | 1-3 U | Kelly sizing |

---

## 🛠 Troubleshooting

### Problema 1: "ROI Negativo dopo 20 bet"

**Cause**:
- Filtri EV troppo permissivi (>25% EV = alta varianza)
- Quote cambiate da modello a Sisal (shrinkage 70%)
- Sample size basso (variance statistico)

**Fix**:
1. Riduci EV target: 20-25% invece di >30%
2. **SEMPRE verifica quota Sisal** prima di bet
3. Continua a 50+ bet prima di conclusioni

### Problema 2: "Bankroll sotto -20%"

**Cause**:
- Losing streak normale (6-8 loss consecutive possibili)
- Stake sizing troppo aggressivo (>3 U)

**Fix**:
1. **Stop trading** fino a analisi completa
2. Riduci stake a 0.5 U (€5 invece di €10)
3. Focus su EV 22-24% (sweet spot)
4. Recovery graduale

### Problema 3: "Equity curve flat"

**Cause**:
- Win/Loss alternati (variance alta)
- Sample size basso (<30 bet)

**Fix**:
1. Normal per primi 30-50 bet
2. Continua con disciplina
3. Verifica dopo 100 bet

---

## 📁 File Critici Sistema

- **`config_bankroll.json`**: Configurazione capitale/Kelly/stop loss
- **`tracking_giocate.csv`**: Database puntate (WIN/LOSS/SKIP)
- **`web/app_professional.py`**: Backend Flask (4900 righe)
- **`web/templates/diario_betting.html`**: Frontend dashboard

---

## 🎯 Next Steps Post-Validazione

Dopo 100+ bet con ROI positivo:

1. **Automazione Quote**: Integrazione API Sisal per quote real-time
2. **Telegram Bot**: Alert opportunità EV >22% automatici
3. **Multi-Sport**: Espandi a Champions League, Premier League
4. **Machine Learning Adattivo**: Sistema impara da risultati reali
5. **Portfolio Diversification**: Multi-strategie parallele

---

## 📞 Support

**Issues GitHub**: (crea repo se necessario)
**Backtest Results**: `FASE2_IMPLEMENTATA.md`
**System Status**: `PRODUCTION_READY.md`

---

## ⚡ Summary Veloce

**Setup 5 minuti**:
1. `python3 -m web.app_professional`
2. http://localhost:5008/diario → Trading Dashboard
3. Config: €1000, Kelly 0.25, Stop 30%

**Workflow quotidiano**:
1. Dashboard opportunità → Trova EV 20-25%
2. Kelly calculator → Calcola stake
3. Aggiungi diario → Pending con MONITOR
4. Pre-partita → Edit stake (Kelly suggerito)
5. Post-partita → WIN/LOSS/SKIP

**Target mensile**:
- ROI Bankroll: +5-10%
- Sharpe Ratio: >1.0
- Max Drawdown: <20%
- Sample: 50+ bet

**Success**: Sistema profittevole sostenibile long-term 🎯

---

**Good luck trading! 📈💰**
