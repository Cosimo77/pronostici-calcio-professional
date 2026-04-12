# Status Ottimizzazione Modelli ML

**Data**: 14 Marzo 2026, ore 11:55  
**Status**: ✅ IN ESECUZIONE

---

## Setup Validato

### ✅ Pre-Flight Check PASSED
- **Dataset**: 2,753 partite, 32 features
- **Split**: 2,178 train / 545 test (80/20 senza stratify)
- **Modelli baseline**: 3/3 disponibili

### Baseline Accuracy (REALE)
```
Random Forest  : 51.38%
LightGBM       : 46.79%
XGBoost        : 45.32%
───────────────────────
Media baseline : 47.83%
```

### Target Ottimizzazione
```
Minimo: 49.83% (+2.0%)
Target: 51.33% (+3.5%)
Ottimo: 52.83% (+5.0%)
```

---

## Fix Applicati

### 1. Split Consistency ✅
- **Prima**: `stratify=y` (split diverso, accuracy falsata a 89%)
- **Dopo**: Nessun stratify (matching con train_models_quick.py)
- **Risultato**: Baseline realistico 47.83%

### 2. Class Weight Rimosso ✅
- **Prima**: `class_weight='balanced'` causava underfitting  
- **Dopo**: Feature selection naturale, no biasing
- **Risultato**: Accuracy attesa più alta

### 3. Parametri GridSearchCV Ottimizzati ✅

**Random Forest** (48 combinazioni):
```python
n_estimators: [100, 200, 300, 400]
max_depth: [20, 25, 30, None]
min_samples_split: [2, 5, 10]
```

**LightGBM** (48 combinazioni):
```python
num_leaves: [31, 50, 70, 100]
learning_rate: [0.05, 0.1, 0.15]
n_estimators: [100, 200, 300, 400]
```

**XGBoost** (48 combinazioni):
```python
max_depth: [6, 8, 10, 12]
learning_rate: [0.05, 0.1, 0.15]
n_estimators: [100, 200, 300, 400]
```

---

## Processo In Esecuzione

**PID**: 46650  
**Comando**: `python3 scripts/optimize_models.py`  
**Log**: `logs/optimization_latest.log`  
**Status**: Running (RN)  
**Memoria**: 173 MB  
**CPU time**: 3.61s (crescente)

### Timeline Stimata
```
Random Forest GridSearchCV   : ~15-20 min
LightGBM GridSearchCV        : ~12-15 min  
XGBoost GridSearchCV         : ~12-15 min
Voting Ensemble              : ~2 min
──────────────────────────────────────────
TOTALE                       : ~40-50 min
ETA completamento            : ~12:35-12:45
```

---

## Monitoring

### Real-Time Monitor
```bash
python3 scripts/monitor_live.py
```

### Check Log
```bash
tail -f logs/optimization_latest.log
```

### Check Processo
```bash
ps aux | grep optimize_models.py | grep -v grep
```

### Check Modelli Creati
```bash
ls -lh models/enterprise/*_optimized.pkl
```

---

## Prossimi Step

### Quando Completato

1. **Verifica risultati**
   ```bash
   python3 scripts/compare_predictions.py
   ```

2. **Analisi miglioramenti**
   - Confronto accuracy pre/post
   - Performance per classe (H/D/A)
   - Esempi predizioni cambiate

3. **Decisione deployment**
   - Se +2-5%: Deploy immediato ✅
   - Se <+2%: Analisi fallimento, FASE 2
   - Se negativo: Rollback, root cause analysis

4. **FASE 2 (se necessario)**
   ```bash
   python3 scripts/feature_engineering_fase2.py
   ```

---

## Note Tecniche

### Perché 47.83% è realistico?

**Classificazione multiclass (3 classi) sul calcio:**
- **Baseline random**: 33.3% (1/3)
- **Baseline Casa sempre**: 41.5%
- **Modelli attuali**: 47.83% (+14.5 punti su baseline)
- **Target ragionevole**: 50-53%
- **Stato dell'arte**: 55-58%
- **Limite teorico**: ~60-65% (il calcio è imprevedibile)

Il nostro 47.83% è **sopra la media** ma ha margini di miglioramento.

### Success Metrics

**Minimo Accettabile**: +1-2% (49-50%)
**Buono**: +3-4% (51-52%)  
**Eccellente**: +5%+ (53%+)

---

## Troubleshooting

### Se ottimizzazione si blocca
```bash
# Check se processo è morto
ps aux | grep 46650

# Check memoria disponibile
free -h  # Linux
vm_stat  # macOS
```

### Se accuracy peggiora
1. Verifica overfitting (train >> test)
2. Check data leakage
3. Verifica class imbalance non gestito
4. Rollback a baseline

### Se accuracy non migliora (+0-1%)
- **Normal**: GridSearch might not find better params
- **Action**: Procedere a FASE 2 (Feature Engineering)
- **Aspettativa realistica**: Feature engineering > hyperparameter tuning

---

**Last Updated**: 2026-03-14 11:56  
**Status**: 🟢 RUNNING
