# 📊 Guida Tracking Accuracy Live

## 🎯 Obiettivo

Monitorare l'**accuracy reale** del sistema deployato confrontando predizioni vs risultati effettivi delle prossime **15-20 partite Serie A** (14-30 marzo 2026).

Questo permette di validare se l'accuracy è più vicina a:
- **51.38%** (test locale 14 marzo) → Sistema affidabile ✅
- **39.5%** (backtest 6 febbraio) → Sistema problematico ⚠️

---

## 📋 Sistema di Tracking

### File Creati

1. **`tracking_accuracy_live_mar2026.csv`**
   - CSV con predizioni generate dal sistema
   - Colonne: Data, Casa, Ospite, Mercato, Predizione, Probabilità, Quota, EV%, Risultato_Reale, Corretto, Profit
   - Aggiorna manualmente risultati dopo ogni partita

2. **`scripts/track_live_accuracy.py`**
   - Script Python per automazione tracking
   - Comandi: `add` (aggiungi risultato), `stats` (statistiche), `pending` (predizioni da validare)

---

## 🚀 Come Usare il Sistema

### STEP 1: Genera Predizioni (Prima delle Partite)

**Opzione A: Via Web Dashboard**
```bash
# Apri browser
https://pronostici-calcio-pro.onrender.com

# Vai su "Giornata" o "Upcoming Matches"
# Copia predizioni per prossime partite in CSV
```

**Opzione B: Via API**
```bash
# Upcoming matches con quote reali
curl https://pronostici-calcio-pro.onrender.com/api/upcoming_matches > predizioni.json

# Singola partita
curl -X POST https://pronostici-calcio-pro.onrender.com/api/predict_enterprise \
  -H "Content-Type: application/json" \
  -d '{"squadra_casa":"Inter","squadra_ospite":"Napoli"}'
```

**Opzione C: Manuale CSV**

Apri `tracking_accuracy_live_mar2026.csv` e aggiungi righe:
```csv
Data,Giornata,Casa,Ospite,Mercato,Predizione,Probabilita_Sistema,Quota,EV_%,Risultato_Reale,Corretto,Profit,Note
2026-03-15,28,Inter,Napoli,1X2,Casa,0.58,1.75,1.5,,,0,
2026-03-15,28,Inter,Napoli,OU25,Over,0.62,1.85,14.7,,,0,
2026-03-15,28,Inter,Napoli,GGNG,GG,0.55,1.90,4.5,,,0,
```

---

### STEP 2: Aggiorna Risultati (Dopo le Partite)

**Opzione A: Script Python (RACCOMANDATO)** 🐍

```bash
# Aggiungi risultato partita
python3 scripts/track_live_accuracy.py add \
  --casa Inter \
  --ospite Napoli \
  --risultato H \
  --gol-casa 2 \
  --gol-ospite 1

# Output:
# ✅ Trovata partita: Inter vs Napoli (3 mercati)
# ✅ Risultato salvato per Inter vs Napoli
#    Risultato: H
#    Score: 2-1
```

**Parametri**:
- `--risultato`: `H` (casa vince), `D` (pareggio), `A` (trasferta vince)
- `--gol-casa` / `--gol-ospite`: Per calcolare O/U 2.5 e GG/NG

**Opzione B: Manuale CSV** ✏️

Apri CSV e compila colonne:
- **Risultato_Reale**: `H`, `D`, `A` (per 1X2), `Over`/`Under` (per OU25), `GG`/`NG` (per GG/NG)
- **Corretto**: `TRUE` o `FALSE`
- **Profit**: `(quota-1)` se WIN, `-1` se LOSS

---

### STEP 3: Visualizza Statistiche

```bash
# Mostra statistiche complete
python3 scripts/track_live_accuracy.py stats
```

**Output Esempio**:
```
======================================================================
  📊 LIVE ACCURACY TRACKING - STATISTICHE
======================================================================

📈 PERFORMANCE COMPLESSIVA:
   Predizioni Totali:     15
   Predizioni Corrette:   7 (46.7%)
   Profit Totale:         -1.20€ (stake 1€)
   ROI:                   -8.0%

📊 ACCURACY PER MERCATO:
   Mercato         Total    Correct    Accuracy     Profit       ROI       
   --------------- -------- ---------- ------------ ------------ ----------
   1X2             5        2          40.0%        -1.50€       -30.0%    
   OU25            5        3          60.0%        +1.10€       +22.0%    
   GGNG            5        2          40.0%        -0.80€       -16.0%    

🎯 CONFRONTO CON BACKTEST (6 Feb 2026):
   Mercato         Backtest     Live         Diff      
   --------------- ------------ ------------ ----------
   1X2              39.5%        40.0%        +0.5pp    
   OU25             51.6%        60.0%        +8.4pp    
   GGNG             50.3%        40.0%        -10.3pp   

🟡 WARNING: Accuracy 42-48% → Monitorare strettamente, ridurre stake
```

---

### STEP 4: Check Predizioni Pending

```bash
# Mostra partite ancora da validare
python3 scripts/track_live_accuracy.py pending
```

**Output Esempio**:
```
⏳ PREDIZIONI PENDING:

📅 2026-03-16: Milan vs Roma (3 mercati)
   1X2    → Casa         (Prob 52%, EV +1.4%)
   OU25   → Over         (Prob 58%, EV +10.2%)
   GGNG   → GG           (Prob 53%, EV -1.9%)

📅 2026-03-16: Juventus vs Atalanta (3 mercati)
   1X2    → Pareggio     (Prob 31%, EV -0.8%)
   OU25   → Over         (Prob 65%, EV +17.0%)
   GGNG   → GG           (Prob 58%, EV +1.5%)
```

---

## 📈 Metriche da Monitorare

### 1. Accuracy Complessiva

| Range | Status | Azione |
|-------|--------|--------|
| **≥48%** | 🟢 OK | Sistema validato, continua operativo |
| **42-48%** | 🟡 WARNING | Ridurre stake 50%, monitor stretto |
| **<42%** | 🔴 ALERT | STOP betting, considerare rollback |

### 2. Accuracy per Mercato

**Target Minimi**:
- **Over/Under 2.5**: ≥48% (aspettativa: 51.6%)
- **GG/NG**: ≥45% (aspettativa: 50.3%)
- **1X2**: ≥40% (aspettativa: 39.5% - 51.38%)

### 3. ROI per Mercato

**Target**:
- ROI complessivo: **≥0%** (positivo)
- ROI Over/Under 2.5: **≥+5%** (mercato forte)
- ROI 1X2: **≥-10%** (mercato difficile, tolleranza)

---

## 🎯 Decision Tree (Dopo 15-20 Partite)

### Scenario A: Accuracy ≥48% ✅

**Azione**: Sistema VALIDATO
- ✅ Continua operativo normale
- ✅ Update dashboard con accuracy live
- ✅ Backtest 39.5% era pessimistico
- ✅ Modelli affidabili

### Scenario B: Accuracy 42-48% ⚠️

**Azione**: CAUTELA
- ⚠️ Riduci stake 50% (Kelly 0.10 invece 0.25)
- ⚠️ Focus solo su Over/Under 2.5 (se ≥48%)
- ⚠️ Skip 1X2 (se <40%)
- ⚠️ Monitor altri 10-15 match

### Scenario C: Accuracy <42% 🔴

**Azione**: ROLLBACK + RE-TRAINING
- 🔴 STOP betting immediato
- 🔴 Rollback a modelli pre-14 marzo
- 🔴 Re-training con:
  - Regularizzazione (Ridge/Lasso)
  - Feature selection (top 20)
  - Cross-validation più rigorosa
  - Ensemble più conservativo

---

## 📊 Esempio Workflow Completo

### Venerdì 15 Marzo (Pre-Partite)

**9:00 AM** - Genera predizioni weekend:
```bash
# Apri dashboard
open https://pronostici-calcio-pro.onrender.com

# Copia predizioni Inter-Napoli, Milan-Roma, Juve-Atalanta
# Incolla in tracking_accuracy_live_mar2026.csv
```

### Domenica 16 Marzo (Post-Partite)

**10:00 PM** - Aggiorna risultati:
```bash
# Inter batte Napoli 2-1
python3 scripts/track_live_accuracy.py add --casa Inter --ospite Napoli --risultato H --gol-casa 2 --gol-ospite 1

# Milan pareggia con Roma 1-1
python3 scripts/track_live_accuracy.py add --casa Milan --ospite Roma --risultato D --gol-casa 1 --gol-ospite 1

# Juventus-Atalanta 2-2
python3 scripts/track_live_accuracy.py add --casa Juventus --ospite Atalanta --risultato D --gol-casa 2 --gol-ospite 2
```

### Lunedì 17 Marzo (Review)

**10:00 AM** - Analizza performance:
```bash
# Statistiche complete
python3 scripts/track_live_accuracy.py stats

# Check predizioni pending
python3 scripts/track_live_accuracy.py pending
```

---

## 🔄 Automazione (Opzionale)

### Script Auto-Update da API Risultati

```python
# scripts/auto_update_results.py (TODO)
import requests
from track_live_accuracy import add_result

# Fetch risultati da API esterna (es. football-data.org)
matches = get_completed_matches()

for match in matches:
    add_result(
        casa=match['home_team'],
        ospite=match['away_team'],
        risultato=match['result'],  # H/D/A
        gol_casa=match['score_home'],
        gol_ospite=match['score_away']
    )
```

---

## 📞 Troubleshooting

### Problema: "Partita non trovata"

```bash
python3 scripts/track_live_accuracy.py add --casa Inter --ospite Napoli --risultato H
# ⚠️  Partita Inter vs Napoli non trovata o già aggiornata
```

**Soluzione**:
1. Verifica spelling squadre (case-sensitive!)
2. Check se già aggiornata: `python3 scripts/track_live_accuracy.py pending`
3. Aggiungi manualmente al CSV se mancante

### Problema: CSV Corrotto

```bash
# Backup prima di modifiche manuali
cp tracking_accuracy_live_mar2026.csv tracking_accuracy_live_mar2026.csv.backup

# Se corrotto, ripristina
mv tracking_accuracy_live_mar2026.csv.backup tracking_accuracy_live_mar2026.csv
```

---

## 📚 Riferimenti

- **Backtest Originale**: 39.5% accuracy (6 feb 2026, 537 partite)
- **Test Locale**: 51.38% Random Forest (14 mar 2026, 545 partite)
- **Gap Analysis**: [ACCURACY_GAP_ANALYSIS.md](ACCURACY_GAP_ANALYSIS.md)
- **Deploy Status**: [DEPLOY_STATUS_14MAR2026.md](DEPLOY_STATUS_14MAR2026.md)

---

**Ultima modifica**: 14 marzo 2026, 17:15  
**Status**: 📊 Sistema tracking attivo, 0/15 partite validate  
**Next Review**: 21 marzo 2026 (dopo ~15 partite)
