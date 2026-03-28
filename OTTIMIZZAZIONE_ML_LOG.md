# Log Ottimizzazione Modelli ML

**Data inizio**: 14 Marzo 2026  
**Obiettivo**: Migliorare accuracy da 53% a 55-57% (FASE 1)

---

## Stato Baseline (Pre-Ottimizzazione)

### Dataset
- **Partite totali**: 2,723
- **Features**: 32
- **Train/Test split**: 2,178 / 545 (80/20)

### Distribuzione Classi
- **Casa (H)**: 1,120 partite (41.1%)
- **Pareggio (D)**: 729 partite (26.8%)
- **Ospite (A)**: 874 partite (32.1%)

### Performance Baseline
| Modello | Test Accuracy | Note |
|---------|--------------|------|
| Random Forest | **89.54%** | Modello attuale |
| LightGBM | 87.52% | Modello attuale |
| XGBoost | 87.89% | Modello attuale |
| **Media** | **88.32%** | Baseline da battere |

---

## FASE 1 - Hyperparameter Tuning

### Step 1: Random Forest ⏳ IN CORSO
- **Parametri testati**: 48 combinazioni
- **Griglia**: 
  - `n_estimators`: [200, 300, 400]
  - `max_depth`: [20, 25, 30, None]
  - `min_samples_split`: [5, 10, 15]
  - `class_weight`: ['balanced', 'balanced_subsample']
- **Status**: GridSearchCV in esecuzione...
- **Tempo stimato**: 15-20 minuti

### Step 2: LightGBM ⏸️ IN ATTESA
- **Parametri da testare**: 36 combinazioni
- **Griglia**:
  - `num_leaves`: [31, 50, 70]
  - `learning_rate`: [0.05, 0.1, 0.15]
  - `n_estimators`: [200, 300, 400]
  - `class_weight`: ['balanced', None]

### Step 3: XGBoost ⏸️ IN ATTESA
- **Parametri da testare**: 36 combinazioni
- **Griglia**:
  - `max_depth`: [6, 8, 10]
  - `learning_rate`: [0.05, 0.1, 0.15]
  - `n_estimators`: [200, 300, 400]
  - `subsample`: [0.8, 0.9]

### Step 4: Voting Ensemble ⏸️ IN ATTESA
- **Strategia**: Soft voting con pesi dinamici
- **Pesi**: Proporzionali alle accuracy individuali
- **Target**: Combinare i punti di forza di tutti e 3 i modelli

---

## Risultati Attesi

### Target FASE 1
- **Random Forest**: 90-91% (+0.5-1.5%)
- **LightGBM**: 88-89% (+0.5-1.5%)
- **XGBoost**: 88-90% (+0.5-2%)
- **Voting Ensemble**: 90-92% (nuovo modello)

### Impatto Predizioni
Con accuracy 90-92%:
- Su 100 partite → 90-92 predizioni corrette
- Miglioramento: +2-4 partite corrette rispetto a baseline
- ROI betting: +3-5% stimato

---

## Prossimi Step (FASE 2)

### 1. Feature Engineering (+3-5%)
- [ ] Expected Goals (xG)
- [ ] Forma portiere
- [ ] Assenze giocatori chiave
- [ ] Pressione zonale
- [ ] Sequenze risultati

### 2. SMOTE Oversampling (+5-10% su pareggi)
- [ ] Bilanciamento classe Pareggio (underrepresented)
- [ ] Oversample strategico

### 3. Stacking Meta-Learner (+2-3%)
- [ ] Meta-learner con Logistic Regression
- [ ] Cross-validation 10-fold

### 4. Calibrazione Probabilità (+1-2%)
- [ ] Platt Scaling
- [ ] Isotonic Regression

---

## Note Tecniche

### Class Imbalance Strategy
- **Problema identificato**: Pareggi solo 26.8% del dataset
- **Soluzione FASE 1**: `class_weight='balanced'` in RF/LightGBM
- **Soluzione FASE 2**: SMOTE oversampling

### Cross-Validation
- **Folds**: 5-fold stratified CV
- **Scoring**: Accuracy (metrica principale)
- **Stratificazione**: Preserva distribuzione classi in ogni fold

### Computational Resources
- **CPU utilizzati**: Tutti disponibili (`n_jobs=-1`)
- **Memoria stimata**: ~2-4 GB RAM
- **Tempo totale FASE 1**: 45-60 minuti

---

## Timeline

- **14:00** - Inizio ottimizzazione
- **14:20** - Random Forest completato (stima)
- **14:35** - LightGBM completato (stima)
- **14:50** - XGBoost completato (stima)
- **14:55** - Voting Ensemble + salvataggio
- **15:00** - Report finale e deployment

---

## Deployment Plan

### File da aggiornare
1. `models/enterprise/random_forest_optimized.pkl`
2. `models/enterprise/lightgbm_optimized.pkl`
3. `models/enterprise/xgboost_optimized.pkl`
4. `models/enterprise/voting_ensemble.pkl` (nuovo)

### File da modificare in produzione
- `web/app_professional.py`: Update model loading
- `train_models_quick.py`: Save optimized params as default
- `README.md`: Update performance metrics

### Testing prima del deploy
```bash
# Test predizione con modelli ottimizzati
python3 test_models.py --optimized

# Confronto predizioni old vs new
python3 scripts/compare_predictions.py
```

---

*Log aggiornato automaticamente durante l'esecuzione*
