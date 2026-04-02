# Checklist Deployment Modelli Ottimizzati

**Data**: 14 Marzo 2026  
**Obiettivo**: Deploy modelli FASE 1 ottimizzati in produzione

---

## Pre-Deployment Tasks

### ✅ FASE 1 - Verifica Completamento Ottimizzazione

- [ ] **Tutti i modelli completati**
  ```bash
  ls -lh models/enterprise/*_optimized.pkl models/enterprise/voting_ensemble.pkl
  ```
  Expected: 4 file (RF, LightGBM, XGBoost, Voting)

- [ ] **Verifica log ottimizzazione**
  ```bash
  # Check che lo script sia terminato senza errori
  # Verifica presenza sezione "RIEPILOGO OTTIMIZZAZIONE"
  ```

- [ ] **Target accuracy raggiunto**
  - Accuracy media ≥ 55% ✅
  - Miglioramento ≥ +2% su baseline ✅

---

## Testing Tasks

### ✅ FASE 2 - Test Modelli Ottimizzati

- [ ] **Test accuracy su test set**
  ```bash
  python3 scripts/compare_predictions.py
  ```
  Verifica:
  - Nessun overfitting (test accuracy ~= train accuracy)
  - Miglioramento su tutte le classi (H, D, A)
  - Esempi predizioni cambiate hanno senso

- [ ] **Test predizione partita reale**
  ```bash
  python3 test_models.py --use-optimized
  ```
  Verifica predizione su ultimo match (Lazio-Sassuolo)

- [ ] **Sanity check probabilità**
  - Somma probabilità = 1.0 (±0.001)
  - Nessuna probabilità negativa
  - Range realistico (0.15-0.70)

- [ ] **Confronto con baseline**
  - RF: +0.5-2% ✅
  - LightGBM: +0.5-2% ✅
  - XGBoost: +0.5-2% ✅
  - Voting: Migliore di tutti ✅

---

## Backup Tasks

### ✅ FASE 3 - Backup Modelli Attuali

- [ ] **Backup modelli baseline**
  ```bash
  mkdir -p backups/models_pre_optimization_$(date +%Y%m%d)
  cp models/enterprise/*.pkl backups/models_pre_optimization_$(date +%Y%m%d)/
  ```

- [ ] **Backup dataset**
  ```bash
  cp data/dataset_features.csv backups/dataset_features_$(date +%Y%m%d).csv
  ```

- [ ] **Git commit stato pre-deploy**
  ```bash
  git add -A
  git commit -m "Pre-deploy checkpoint: modelli ottimizzati FASE 1"
  git tag -a "v1.1-optimized" -m "Modelli ottimizzati +2-4% accuracy"
  ```

---

## Deployment Tasks

### ✅ FASE 4 - Deploy in Produzione

- [ ] **Sostituisci modelli in produzione**
  ```bash
  # Opzione A: Sovrascrivi (mantieni nomi originali)
  cp models/enterprise/random_forest_optimized.pkl models/enterprise/random_forest.pkl
  cp models/enterprise/lightgbm_optimized.pkl models/enterprise/lightgbm.pkl
  cp models/enterprise/xgboost_optimized.pkl models/enterprise/xgboost.pkl
  
  # Opzione B: Usa modelli ottimizzati direttamente
  # Aggiorna app_professional.py per caricare *_optimized.pkl
  ```

- [ ] **Aggiungi Voting Ensemble a produzione**
  - File già disponibile: `models/enterprise/voting_ensemble.pkl`
  - Update `web/app_professional.py` per includere voting

- [ ] **Update configurazione**
  ```python
  # In web/app_professional.py
  MODELS = {
      'random_forest': 'models/enterprise/random_forest.pkl',
      'lightgbm': 'models/enterprise/lightgbm.pkl',
      'xgboost': 'models/enterprise/xgboost.pkl',
      'voting': 'models/enterprise/voting_ensemble.pkl'  # NUOVO
  }
  ```

- [ ] **Update README documenti**
  - Aggiorna performance metrics in README.md
  - Documenta parametri ottimizzati
  - Timeline FASE 1 completata

---

## Post-Deployment Tasks

### ✅ FASE 5 - Verifica Produzione

- [ ] **Test endpoint API**
  ```bash
  # Test predizione enterprise
  curl -X POST http://localhost:5000/api/predict_enterprise \
    -H "Content-Type: application/json" \
    -d '{"match": {"HomeTeam": "Inter", "AwayTeam": "Juventus"}}'
  ```

- [ ] **Verifica cache Redis**
  ```bash
  # Check che cache sia invalidato per nuove predizioni
  redis-cli FLUSHDB
  ```

- [ ] **Monitor prime predizioni**
  - Verifica log strutturato
  - Check latency predizioni (<100ms)
  - Verifica probabilità sensate

- [ ] **Test su Render (produzione cloud)**
  ```bash
  # Deploy su Render
  git push origin main
  
  # Verifica deployment
  curl https://your-app.onrender.com/api/predict_enterprise
  ```

---

## Rollback Plan (Se Problemi)

### 🚨 Emergency Rollback

Se i modelli ottimizzati causano problemi:

```bash
# 1. Ripristina da backup
cp backups/models_pre_optimization_YYYYMMDD/*.pkl models/enterprise/

# 2. Rimuovi voting ensemble
rm models/enterprise/voting_ensemble.pkl

# 3. Restart app
pkill -f app_professional
python3 -m web.app_professional

# 4. Clear cache Redis
redis-cli FLUSHDB

# 5. Git revert
git revert HEAD
git push origin main
```

---

## Monitoring Post-Deploy

### 📊 Metriche da Monitorare (Prime 24h)

- [ ] **Accuracy live**
  - Track predizioni vs risultati reali
  - Target: ≥55% su partite weekend

- [ ] **Latency API**
  - `/api/predict_enterprise` < 100ms
  - Cache hit rate > 50%

- [ ] **Distribution predizioni**
  - Casa: ~40-45%
  - Pareggio: ~25-30%
  - Ospite: ~30-35%
  - (Deve essere simile a distribuzione reale)

- [ ] **Error rate**
  - Nessun errore 500
  - Nessuna predizione NaN/infinito

- [ ] **User feedback**
  - Predizioni più sensate?
  - Value betting migliore?

---

## Success Metrics

### 🎯 KPI da Raggiungere

| Metrica | Baseline | Target | Actual | Status |
|---------|----------|--------|--------|--------|
| Accuracy media | 53.0% | 55-57% | ___% | ⏳ |
| RF accuracy | 51.4% | 53-54% | ___% | ⏳ |
| LightGBM accuracy | 52.0% | 53-54% | ___% | ⏳ |
| XGBoost accuracy | 53.0% | 54-56% | ___% | ⏳ |
| Voting accuracy | N/A | 55-57% | ___% | ⏳ |
| Latency predizione | 50ms | <100ms | ___ms | ⏳ |
| ROI betting | +7.17% | +9-10% | ___% | ⏳ |

---

## Next Steps (FASE 2)

Quando FASE 1 è stabile in produzione (>7 giorni):

1. **Feature Engineering**
   ```bash
   python3 scripts/feature_engineering_fase2.py
   ```
   - Add 12 nuove features
   - Target: +3-5% accuracy

2. **SMOTE Oversampling**
   - Balance classe Pareggio
   - Target: +5-10% su predizioni pareggi

3. **Stacking Meta-Learner**
   - Combina RF + LightGBM + XGBoost
   - Target: +2-3% accuracy

4. **Obiettivo FASE 2**: 58-62% accuracy

---

## Sign-Off

- [ ] **Developer**: Verificato funzionamento modelli ottimizzati
- [ ] **QA**: Test passed su tutti gli scenari
- [ ] **Deploy**: Modelli in produzione senza errori
- [ ] **Monitoring**: Metriche nella norma (24h post-deploy)

**Data completamento**: _______________  
**Firmato**: _______________

---

## Notes

- Tutti i comandi assumono cwd: `/Users/cosimomassaro/Desktop/pronostici_calcio`
- Backup automatici ogni 24h in `backups/`
- Log completo in `logs/optimization_deploy_YYYYMMDD.log`
- In caso di dubbi: rollback immediato e debug in locale

