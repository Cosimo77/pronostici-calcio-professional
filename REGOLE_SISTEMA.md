# 🚨 REGOLE SISTEMA - NON MODIFICARE

## ⚠️ VINCOLI RENDER FREE TIER (IMMUTABILI)

**NON è possibile:**
- ❌ Cron jobs / scheduled tasks
- ❌ Background workers
- ❌ Processi che girano oltre 15 min inattività
- ❌ Download dati automatici su Render

**È possibile:**
- ✅ Web server sempre online (quando richiesto)
- ✅ Ricaricamento dataset in memoria via API
- ✅ GitHub Actions per trigger esterni

---

## 📜 SCRIPT UFFICIALI (1 PER TASK)

### Aggiornamento Dati
**Script**: `aggiornamento_dati_reali.py`
- Scarica da: https://www.football-data.co.uk/mmz4281/2526/I1.csv
- Aggiorna: `data/I1_2526.csv` + `data/dataset_pulito.csv`
- Esecuzione: **LOCALE SU MAC**

```bash
python3 aggiornamento_dati_reali.py
# Scegli opzione 1: DATI REALI
```

### Training Modelli
**Script**: `scripts/modelli_predittivi.py`
- Addestra: RandomForest, LightGBM, XGBoost
- Salva in: `models/enterprise/*.pkl`
- Esecuzione: **LOCALE SU MAC** (dopo aggiornamento dati)

```bash
python3 scripts/modelli_predittivi.py
```

### Sincronizzazione Render
**Workflow**: `.github/workflows/reload_render.yml`
- Trigger: Push di `data/dataset_pulito.csv` su main
- Azione: Chiama `/api/automation/force_update`
- Esecuzione: **AUTOMATICO** (GitHub Actions)

```bash
# Dopo aggiornamento dati:
git add data/*.csv
git commit -m "Update: nuove partite"
git push origin main
# → GitHub Actions ricarica Render automaticamente
```

---

## 🔒 ENDPOINT API (NON MODIFICARE LOGICA)

### `/api/automation/force_update`
**Funzione**: Ricarica dataset dal file deployato
**NON FA**: Download dati (non supportato su Render FREE)
**Codice**: `web/app_professional.py` linee ~3166-3200

```python
# LOGICA CORRETTA (NON MODIFICARE):
calculator.df_features = pd.read_csv('data/dataset_pulito.csv')
# ✅ Ricarica file già deployato da GitHub

# ❌ NON USARE:
# subprocess.run(['python3', 'script.py'])  # Non funziona su Render
# requests.get('football-data.co.uk')       # Timeout/Bloccato
```

### `/api/predict_enterprise`
**Funzione**: Predizioni deterministiche 26 mercati
**Input**: `{"squadra_casa": "Juventus", "squadra_ospite": "Inter"}`
**NON MODIFICARE**: Logica ProfessionalCalculator

### `/api/health`
**Funzione**: Status sistema
**Metriche**: database_records, status, uptime

---

## 📁 FILE CRITICI (NON ELIMINARE MAI)

```
data/
  ├── dataset_pulito.csv      ← Dataset principale (2860 partite)
  ├── I1_2526.csv             ← Stagione corrente Serie A
  └── I1_*.csv                ← Stagioni storiche

models/enterprise/
  ├── randomforest_model.pkl
  ├── lightgbm_model.pkl
  └── xgboost_model.pkl

web/
  ├── app_professional.py     ← Flask app CORE (NON MODIFICARE senza motivo)
  └── cache_manager.py        ← Redis cache

.github/workflows/
  └── reload_render.yml       ← Automation trigger
```

---

## 🔄 WORKFLOW STANDARD

### Lunedì/Giovedì (Post-Partite)

```bash
# 1. LOCALE - Aggiorna dati
python3 aggiornamento_dati_reali.py  # Opzione 1

# 2. LOCALE - Verifica
tail -5 data/I1_2526.csv  # Controlla ultime partite

# 3. LOCALE - Push
git add data/dataset_pulito.csv data/I1_2526.csv
git commit -m "Update: partite fino $(date +%d/%m/%Y)"
git push origin main

# 4. AUTOMATICO - GitHub Actions ricarica Render
# (Attendere 2-5 minuti)

# 5. VERIFICA - Render sincronizzato
curl https://pronostici-calcio-professional.onrender.com/api/health | grep database_records
```

### Mensile (Riaddestramento Modelli)

```bash
# SOLO SE: Dataset ha >100 nuove partite
python3 scripts/modelli_predittivi.py
git add models/enterprise/*.pkl
git commit -m "Retrain: modelli con dataset aggiornato"
git push origin main
```

---

## ❌ COSA NON FARE MAI

1. **NON creare nuovi script aggiornamento**
   - Usa `aggiornamento_dati_reali.py`
   - Se non funziona: FIX quello, non crearne altri

2. **NON modificare endpoint `/api/automation/force_update`**
   - Logica corretta: ricarica file deployato
   - NO subprocess, NO download esterni

3. **NON aggiungere cron/scheduled tasks**
   - Render FREE non li supporta
   - Usa GitHub Actions invece

4. **NON cambiare logica ProfessionalCalculator**
   - Sistema deterministico validato su backtest
   - Modifiche = bug difficili da debuggare

5. **NON eliminare file in data/ o models/**
   - Backup prima se necessario
   - Git permette rollback

---

## 🐛 TROUBLESHOOTING

### "Render non ha nuovi dati"
```bash
# Verifica deploy completato
curl https://pronostici-calcio-professional.onrender.com/api/health

# Se ancora vecchi, trigger manuale
curl -X POST https://pronostici-calcio-professional.onrender.com/api/automation/force_update

# Se persiste: Render dashboard → Manual Deploy
```

### "Script aggiornamento non funziona"
```bash
# Test download diretto
curl -I "https://www.football-data.co.uk/mmz4281/2526/I1.csv"
# Deve rispondere: HTTP/2 200

# Se fallisce: verifica connessione internet
ping www.football-data.co.uk
```

### "GitHub Actions fallisce"
```bash
# Verifica workflow
https://github.com/Cosimo77/pronostici-calcio-professional/actions

# Se rosso: controlla che reload_render.yml esista
# Se verde ma Render vecchio: attendere deploy
```

---

## 📊 METRICHE DI SISTEMA

**Target Performance:**
- Accuracy: ~50% (validato su 2860 partite)
- ROI FASE1: +7.17% (backtest 510 trade)
- Response time: <100ms (con cache)
- Uptime: 99% (Render FREE)

**NON modificare sistema per "migliorare" metriche senza:**
1. Backtest completo (>500 partite)
2. Validazione A/B test
3. Documentazione modifiche

---

## 🎯 REGOLA D'ORO

> **Se il sistema funziona, NON toccarlo.**
> 
> Modifiche vanno fatte SOLO per:
> - Bug critici (crash, errori 500)
> - Feature richieste esplicitamente
> - Aggiornamenti dati (workflow standard)
>
> **NON per:**
> - "Ottimizzazioni" non misurate
> - Refactoring senza motivo
> - Cambio logica "perché sì"

---

**Ultima revisione**: 16 Gennaio 2026
**Versione**: 3.0 (Hybrid Local+Cloud)
**Status**: Production-ready ✅
