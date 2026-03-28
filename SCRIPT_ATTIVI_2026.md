# 📦 Script Disponibili (Post-Cleanup 28/03/2026)

## ✅ Script Attivi (25 totali, -62% da 66)

### Core - Automazione Dati (6 script) ⭐

Questi script sono **documentati** e utilizzati in **produzione**:

1. **`update_dataset_and_reload.py`** ⭐ **CRITICO**
   - Auto-update dataset + reload API
   - Eseguito quotidianamente dal daemon
   - **NON rimuovere mai**

2. **`aggiorna_stagione_corrente.py`** ⭐
   - Download I1_2526.csv da football-data.co.uk
   - Aggiornamento stagione Serie A corrente

3. **`aggiorna_automatico.py`** ⭐
   - Consolidamento dataset multipli
   - Generazione features automatica
   - Chiamato dopo ogni download

4. **`auto_setup_render.py`** ⭐
   - Setup automatico deploy Render
   - Referenziato in Procfile
   - Essenziale per CI/CD

5. **`feature_engineering.py`** ⭐
   - Rolling statistics (media mobile 5/10 partite)
   - Home/Away splits
   - Feature baseline documentate

6. **`modelli_predittivi.py`** ⭐
   - Training RF, LightGBM, XGBoost
   - GridSearchCV validato
   - Output: models/*.pkl

---

### Ottimizzazione & ML (2 script)

7. **`optimize_models_v2_fast.py`**
   - Hyperparameter tuning veloce (cv=3)
   - FASE 2 con 53 features
   - Sostituisce optimize_models.py + v2.py (rimossi)

8. **`value_betting_advanced.py`**
   - Calcolo Expected Value (EV)
   - Confronto quote mercato
   - Versione avanzata (sostituisce value_betting_system.py)

---

### Utility & Manutenzione (5 script)

9. **`cleanup_cache.py`**
   - Pulizia cache Redis periodica
   - Log rotation
   - Backup cleanup

10. **`health_check.py`**
    - Verifica stato sistema
    - Check connessioni DB/Redis
    - Validazione modelli

11. **`preflight_check.py`**
    - Pre-deploy validations
    - Environment variables check
    - Dependency verification

12. **`weekly_retrain.py`**
    - Riaddestramento modelli settimanale
   - Trigger: Domenica 02:00
    - Backup modelli old

13. **`mercati_multipli_clean.py`**
    - Calcolo 14 mercati aggiuntivi
    - Over/Under, GG/NG, Asian Handicap
    - Versione clean (sostituisce mercati_multipli.py)

---

### Test (1 script + testing/)

14. **`test_ml_simple.py`**
    - Test predizioni rapido
    - Quick validation pipeline
    - Fixato sessione 28/03/2026

15. **`testing/test_predizioni_endtoend.py`**
    - Test completo pipeline ML
    - Validazione mercati multipli

16. **`testing/test_server_api.py`**
    - Test endpoint Flask API
    - Health check /api/*

---

### Maintenance Folder (7 script)

17-23. **`maintenance/*.py`**
    - `add_bet.py` - Aggiungi scommessa manuale
    - `update_bet.py` - Aggiorna risultato bet
    - `aggiorna_risultati_auto.py` - Auto-update risultati
    - `aggiorna_tracking_fase2.py` - Update tracking FASE2
    - `genera_tracking_fase2.py` - Genera CSV tracking
    - `marca_giocate.py` - Marca bet come giocate
    - `rigenera_backtest_professionale.py` - Rigenera backtest

---

### Monitoring Folder (1 script)

24. **`monitoring/monitor_system.py`**
    - Monitoring unificato sistema
    - Sostituisce 5 script rimossi:
      - ❌ monitor_10min.py (obsoleto)
      - ❌ monitor_live.py (obsoleto)
      - ❌ monitor_optimization.py (obsoleto)
      - ❌ monitor_scraper.py (obsoleto)
      - ❌ monitoring/dashboard_monitoring.py (29K, troppo pesante)

---

### Shell Scripts (testing/shell/)

25. **`shell/*.sh`** + **`testing/*.sh`**
    - Utility bash per automazione
    - Check status, deployment, ecc.

---

## 🔴 Script Eliminati (41 totali)

### Duplicati Rimossi (9 script)

- ❌ **optimize_models.py** - Sostituito da v2_fast
- ❌ **optimize_models_v2.py** - Versione lenta
- ❌ **feature_engineering_fase2.py** - Non documentato
- ❌ **feature_engineering_fast.py** - Non utilizzato
- ❌ **sistema_pronostici.py** - Mai importato da web/
- ❌ **sistema_pronostici_enhanced.py** - Duplicato
- ❌ **predittore_enhanced.py** - Overlap funzionale
- ❌ **mercati_multipli.py** - Sostituito da _clean
- ❌ **value_betting_system.py** - Sostituito da _advanced

### Monitoring Duplicati (5 script)

- ❌ **monitor_10min.py** - Sostituito da monitor_system.py
- ❌ **monitor_live.py** - Sostituito
- ❌ **monitor_optimization.py** - Sostituito
- ❌ **monitor_scraper.py** - Sostituito
- ❌ **monitoring/dashboard_monitoring.py** - Sostituito

### Analysis Folder (11 script one-off)

- ❌ **analysis/analizza_ev_roi.py** - Exploratory completato
- ❌ **analysis/analizza_opportunita_oggi.py** - Sostituito
- ❌ **analysis/analizza_quote_sweet.py** - One-time analysis
- ❌ **analysis/analizza_tracking.py** - Redundant
- ❌ **analysis/analizza_tracking_fase1.py** - FASE 1 obsoleta
- ❌ **analysis/calcola_exact_scores.py** - One-off
- ❌ **analysis/check_partite_oggi.py** - Sostituito
- ❌ **analysis/check_roma.py** - Custom per 1 squadra!
- ❌ **analysis/mostra_opportunita_oggi.py** - Duplicato
- ❌ **analysis/mostra_partite.py** - Redundant
- ❌ **analysis/simula_risultati.py** - Experimental

### Debug/Test Obsoleti (7 script)

- ❌ **debug_accuracy.py** - Debug temporaneo
- ❌ **diagnose_accuracy_gap.py** - Debug temporaneo
- ❌ **test_deploy_fase1.py** - Deploy vecchio
- ❌ **test_modelli_base.py** - Obsoleto
- ❌ **test_validation_ml.py** - Obsoleto
- ❌ **compare_predictions.py** - One-off
- ❌ **analisi_feature_importance.py** - One-off

### Script Obsoleti/Completati (9 script)

- ❌ **analizza_dati.py** - Sostituito da analisi moderne
- ❌ **auto_download_data.py** - Redundant
- ❌ **cache_veloce.py** - Obsoleto
- ❌ **calcola_roi_dinamico.py** - One-off
- ❌ **consolidate_tracking_data.py** - Consolidamento completato
- ❌ **keep_alive_service.py** - Render non richiede
- ❌ **migrate_fase2_to_render.py** - Migrazione completata
- ❌ **scarica_dati_storici.py** - Run-once, dati già scaricati
- ❌ **scraper_dati.py** - Sostituito

### Utility Obsolete (4 script)

- ❌ **sync_from_render.py** - Sync manuale non più necessario
- ❌ **track_live_accuracy.py** - Sostituito da monitor_system
- ❌ **valida_tutto.py** - One-off validation
- ❌ **validatore_scraper.py** - One-off
- ❌ **verify_csv_storage.py** - One-off

---

## 📊 Statistiche Cleanup

| Metrica | Prima | Dopo | Delta |
|---------|-------|------|-------|
| **Script Totali** | 66 | 25 | **-62%** |
| **Script Root** | 49 | 15 | **-69%** |
| **Sottocartelle** | 5 | 4 | -1 (analysis/ rimossa) |
| **Script Documentati** | 8 | 8 | Mantenuti tutti |
| **Script Produzione** | 1 | 1 | Mantenuto (auto_setup_render.py) |
| **Script Importati web/** | 0 | 0 | Tutti standalone |

---

## 🚀 Comandi Utili

### Workflow Completo

```bash
# 1. Download dati stagione corrente
python scripts/aggiorna_stagione_corrente.py

# 2. Consolidamento + features
python scripts/aggiorna_automatico.py

# 3. Training modelli (se necessario)
python scripts/modelli_predittivi.py

# 4. Ottimizzazione hyperparameters (opzionale)
python scripts/optimize_models_v2_fast.py

# 5. Test predizioni
python scripts/test_ml_simple.py
```

### Manutenzione

```bash
# Cleanup cache Redis
python scripts/cleanup_cache.py

# Health check sistema
python scripts/health_check.py

# Monitoring completo
python scripts/monitoring/monitor_system.py
```

### Testing

```bash
# Test predizioni end-to-end
python scripts/testing/test_predizioni_endtoend.py

# Test API server
python scripts/testing/test_server_api.py
```

---

## 📝 Note Importanti

⚠️ **Script Critici (NON eliminare)**:
- `update_dataset_and_reload.py` ⭐ - Sistema automazione dipende
- `auto_setup_render.py` ⭐ - Deploy Render dipende
- `aggiorna_automatico.py` ⭐ - Pipeline dati dipende

✅ **Backup Disponibile**:
Branch `archive/scripts-backup-2026-03-28` contiene tutti gli script pre-cleanup.

🔧 **Script Maintenance Folder**:
7 script in `maintenance/` raramente usati ma mantenuti per operazioni manuali su diario scommesse.

---

**Ultimo aggiornamento**: 28 Marzo 2026
**Cleanup by**: GitHub Copilot (sessione Pylance/linting fix)
