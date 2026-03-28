# 🔬 Analisi Gap Accuracy: 51.38% → 39.5%

## 📊 Executive Summary

**Problema identificato**: Discrepanza -11.88 punti percentuali tra test locale e backtest storico.

**Data**: 14 marzo 2026  
**Status**: ⚠️ **INVESTIGAZIONE RICHIESTA**  
**Priorità**: 🔴 **ALTA** (impatta profittabilità sistema)

---

## 🎯 Il Problema

### Test Locale (14 marzo 2026)
```
Random Forest:  51.38% accuracy (545 partite holdout)
LightGBM:       46.79% accuracy
XGBoost:        45.32% accuracy
Media:          47.83%
Baseline (casa):47.83%
```

### Backtest Dashboard (6 febbraio 2026)
```
Risultato Finale: 39.5% accuracy (212/537 partite)
Over/Under 2.5:   48.5% accuracy ✅
GG/NG:            46.3% accuracy ✅
Media Mercati:    43.2%
```

### Gap
```
51.38% - 39.5% = -11.88 punti percentuali (⚠️ SIGNIFICATIVO)
```

---

## 🔍 Ipotesi Cause

### 1. Overfitting (PROBABILITÀ: 70%) 🔴

**Evidenza**:
- Gap 12pp tra test e backtest troppo ampio
- Modelli complessi (RandomForest n_estimators=200+)
- Feature engineering aggressivo (40+ features)
- GridSearch potrebbe aver ottimizzato noise

**Test Diagnostico**:
```bash
# Cross-validation su training set
python scripts/diagnose_overfitting.py
```

**Soluzione**:
- Ridge/Lasso regularizzazione
- Riduzione complessità (max_depth, n_estimators)
- Pruning features meno importanti (<0.01 importance)
- Ensemble averaging più conservativo

---

### 2. Test Set Contamination (PROBABILITÀ: 20%) 🟡

**Evidenza**:
- 51.38% troppo vicino a baseline 47.83%
- Potrebbe esserci data leakage in holdout set
- Split non stratificato per stagione?

**Test Diagnostico**:
```python
# Verifica distribuzione temporale
df_test['Stagione'].value_counts()
# Se test set ha solo 1-2 stagioni recenti = contamination
```

**Soluzione**:
- Risplit con stratified k-fold (5 fold)
- Time-series split (train su storico, test su recente)
- Walk-forward validation

---

### 3. Metriche Non Confrontabili (PROBABILITÀ: 15%) 🟢

**Evidenza**:
- Test: Solo mercato 1X2 (3 classi)
- Backtest: Media 14 mercati (più difficile)
- 39.5% potrebbe essere media pesata

**Test Diagnostico**:
```bash
# Verificare accuracy SOLO 1X2 nel backtest
curl /api/accuracy_report | jq '.market_performance.risultato_finale'
```

**Soluzione**:
- Ricalcolare backtest solo su 1X2
- Confrontare mele con mele
- Dashboard separata per ogni mercato

---

### 4. Distribution Shift (PROBABILITÀ: 10%) 🟠

**Evidenza**:
- Stagione 2025-26 ha 3 neopromesse (Pisa, Como, Parma)
- Solo 2-5 partite per squadra nuova
- Modelli addestrati su storico 2021-2025

**Test Diagnostico**:
```python
# Accuracy per tipo squadra
accuracy_storiche = df[df['is_neopromossa'] == False]['accuracy']
accuracy_nuove = df[df['is_neopromossa'] == True]['accuracy']
print(f"Gap: {accuracy_storiche - accuracy_nuove}%")
```

**Soluzione**:
- Escludere neopromesse da evaluation (almeno 10 partite)
- Transfer learning da campionati inferiori
- Features più generiche (meno specifiche squadra)

---

## 📋 Piano d'Azione Immediato

### ✅ STEP 1: Diagnosi (Est. 1h)
```bash
# 1. Cross-validation accuracy
python scripts/cross_validate_models.py

# 2. Accuracy per mercato (solo 1X2)
python scripts/backtest_1x2_only.py

# 3. Accuracy per stagione
python scripts/seasonal_breakdown.py

# 4. Feature importance stability
python scripts/feature_stability_analysis.py
```

### ✅ STEP 2: Test su Dati Live (Est. 7-14 giorni)
```
- Raccogliere predizioni prossime 20 partite Serie A
- Confrontare con risultati reali
- Calcolare accuracy live (target ≥45%)
- Se <42% → rollback modelli urgente
```

### ✅ STEP 3: Decisione (Post Live Test)

**Scenario A: Live Accuracy ≥48%** → Backtest 39.5% era pessimistico
- ✅ Keep modelli correnti
- ✅ Update dashboard con nuovi numeri
- ✅ Monitoraggio continuo

**Scenario B: Live Accuracy 42-48%** → In mezzo, accettabile
- ⚠️ Keep modelli ma cautela
- ⚠️ Ridurre stake (Kelly 0.10 invece 0.25)
- ⚠️ Focus su mercati O/U 2.5 (48.5%)

**Scenario C: Live Accuracy <42%** → Problema grave
- 🔴 Rollback immediato a modelli pre-ottimizzazione
- 🔴 Re-training con regularizzazione
- 🔴 Feature selection aggressiva
- 🔴 Considerare ensemble più semplici

---

## 📊 Metriche Monitoraggio Live

### Dashboard Custom (TODO)
```python
# web/templates/accuracy_live_monitor.html
- Accuracy rolling 7 giorni
- Accuracy per mercato (separata)
- Accuracy per squadra (bias detection)
- Confronto test vs backtest vs live
```

### Alert Thresholds
```
🟢 Live Accuracy ≥48%  → Sistema performante
🟡 Live Accuracy 42-48% → Cautela, monitor stretto
🔴 Live Accuracy <42%   → ALERT! Rollback considerato
```

---

## 🎯 Aspettative Realistiche

### Best Case (Ottimistico)
- Live accuracy: **48-52%**
- Backtest 39.5% era dataset sfortunato
- ROI +7.17% confermato

### Base Case (Realistico)
- Live accuracy: **44-48%**
- Gap parziale spiegato da overfitting lieve
- ROI +3-5% (comunque positivo)

### Worst Case (Pessimistico)
- Live accuracy: **39-42%**
- Overfitting severo, test 51.38% falso positivo
- ROI negativo, sistema non profittevole

---

## 📚 Riferimenti

**File Rilevanti**:
- `web/app_professional.py` (linea 3440-3460): Backtest metrics
- `scripts/test_modelli_base.py`: Test locale 51.38%
- `models/enterprise/random_forest.pkl`: Modello primario
- `FASE1_IMPLEMENTATA.md`: ROI +7.17% backtest

**Backtest Originale**:
- Data: 6 febbraio 2026
- Partite: 537 (20% di 2683)
- Metodo: Full prediction su holdout

**Test Locale**:
- Data: 14 marzo 2026
- Partite: 545 (20% split)
- Metodo: Holdout set validation

---

## 🔄 Prossimi Aggiornamenti

- [ ] Cross-validation diagnostics (1h)
- [ ] Accuracy breakdown per mercato (30 min)
- [ ] Live tracking prime 20 partite (7-14 giorni)
- [ ] Decision point post live data
- [ ] Eventuale rollback/re-training

**Ultima modifica**: 14 marzo 2026, 17:10  
**Responsabile**: Sistema Monitoring  
**Priority**: 🔴 HIGH
