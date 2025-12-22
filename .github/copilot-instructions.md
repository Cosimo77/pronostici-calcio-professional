# Pronostici Calcio - Sistema Enterprise di Predizioni Serie A

## Architettura e Componenti Principali

Questo è un sistema professionale di **value betting** per Serie A con ML deterministico, automazione e deployment ibrido (locale + cloud).

### Stack Core
- **Backend**: Flask 3.1.0 + Gunicorn (gevent workers)
- **ML**: scikit-learn (RandomForest, GradientBoosting, LogisticRegression) - **100% dati reali**, zero simulazioni
- **Caching**: Redis (TTL differenziati: 15min-24h) con graceful degradation
- **Deploy**: Render (web server) + Daemon locale (automazione)
- **Security**: Flask-Talisman (CSP headers), Flask-Limiter (rate limiting)

### Architettura Ibrida Critical
Sistema split tra **cloud** (web app) e **locale** (automazione):
- **Web Server**: `web/app_professional.py` su Render (sempre online)
- **Automazione**: Daemon locale gestisce aggiornamenti dati/modelli (cron-like)
- **Sincronizzazione**: Backups giornalieri, dati in repository Git trackable

Quando modifichi codice automation: testa locale PRIMA di assumere funzionerà su Render.

## File Critici e Loro Ruoli

### 1. Entry Point Applicazione
- **`web/app_professional.py`** (3365 righe): Flask app principale
  - Classe `ProfessionalCalculator`: Predizioni deterministiche 100% basate su statistiche reali
  - **NO randomness**: Stessa input → stessa output (usa hashing MD5 per cache key)
  - Metodo `_valida_opportunita_fase1()`: Filtri validati su backtest (ROI +7.17%)
  - Integra cache Redis, monitoring strutturato, value betting

### 2. ML e Predizioni
- **`scripts/modelli_predittivi.py`**: Training modelli scikit-learn
  - `PronosticiCalculator`: Addestra RF, GB, LR con GridSearchCV
  - Calibrazione probabilità: `CalibratedClassifierCV` per output affidabili
  - **NON usare** per predizioni live → usa `ProfessionalCalculator` invece

- **Pattern Predittivo Deterministico**:
  ```python
  # CORRETTO: Statistiche reali + Bayesian smoothing leggero (max 20%)
  stats_casa = _calcola_statistiche_squadra(squadra, in_casa=True)
  # Combina dati storici (80%) + prior informativi (20%) solo se <20 partite
  # EVITA: Shrinkage ultra-aggressivo che appiattisce probabilità
  ```

### 3. Value Betting (Focus Sistema)
- **FASE 1 Implementata** (validata su 510 trade): ROI -4.48% → +7.17%
  - Filtri conservativi: Solo pareggi, quote 2.8-3.5, EV ≥25%
  - File: [FASE1_IMPLEMENTATA.md](../FASE1_IMPLEMENTATA.md) per metriche complete
  - Controintuitivo: EV >50% = ROI negativo (quote troppo alte = imprevedibilità)

- **Endpoint API Value Betting**:
  - `/api/predict_enterprise`: Confronto modello vs mercato con EV
  - `/api/upcoming_matches`: Partite future con quote REALI da The Odds API

### 4. Mercati Multipli
Funzione `_calcola_mercati_deterministici()`: 14 mercati oltre 1X2
- **Over/Under 2.5**: Calcolo dinamico basato su gol previsti (formula sigmoidale)
- **GG/NG**: Clean sheet rate inverso, bonus partite offensive
- **Asian Handicap**: Delta probabilità → handicap (-1.0 a +1.0)
- Corner, cartellini, primo tempo, ecc.

**ANTI-PATTERN**: Non hardcodare probabilità 50% per mercati equilibrati → usa sempre calcoli dinamici da statistiche squadra

## Developer Workflows

### Setup Locale
```bash
# 1. Installa dipendenze
pip install -r requirements.txt

# 2. Configura API Key (OBBLIGATORIA per quote reali)
export ODDS_API_KEY="tua_chiave"  # https://the-odds-api.com (500 richieste/mese gratis)

# 3. Avvia Redis (opzionale, sistema degrada gracefully)
brew install redis && redis-server

# 4. Run web server
python -m web.app_professional
# App: http://localhost:5000
```

### Automazione e Aggiornamenti
```bash
# Aggiorna dati (scraping football-data.co.uk)
python scripts/aggiorna_automatico.py

# Riaddestra modelli (settimanale post nuovi dati)
python scripts/modelli_predittivi.py

# Backtest performance con filtri FASE1
python backtest_fase1_improved.py
```

### Testing
```bash
# Unit tests core
python tests/test_value_betting.py  # 14 tests (EV, thresholds, cache)
python tests/test_ml_predictions.py  # 15 tests (feature engineering, validation)

# Coerenza predizioni deterministiche
curl http://localhost:5000/api/test_coerenza
```

## Convenzioni e Pattern Specifici

### 1. Naming Squadre - Mapping Critical
The Odds API usa nomi diversi da dataset CSV:
```python
TEAM_NAME_MAPPING = {
    'Inter Milan': 'Inter',
    'AC Milan': 'Milan',
    'AS Roma': 'Roma',
    'Hellas Verona': 'Verona'
    # Vedi app_professional.py:552-577
}
```
Sempre normalizza con `normalize_team_name()` prima di query dataset.

### 2. Cache Redis Pattern
```python
# Check cache PRIMA di API call costosa
cached_data = cache.cache_upcoming_matches()
if cached_data:
    return jsonify(cached_data), 200

# ... logica API ...

# Salva risultato con TTL appropriato
cache.set_upcoming_matches(response)
```
TTL strategy: 15min (partite), 1h (predizioni), 24h (dataset info)

### 3. Logging Strutturato
Usa `structlog` per logging professional:
```python
logger.info("Predizione generata",
            squadra_casa=casa,
            squadra_ospite=ospite,
            confidenza=round(confidenza, 3),
            cache_hit=True)
```
**NON** usare `print()` o `logging.debug()` tradizionale in produzione.

### 4. Probabilità - Validazione Matematica
```python
# SEMPRE verifica somma = 1.0 (±0.001)
somma_prob = sum(probabilita.values())
if abs(somma_prob - 1.0) > 0.001:
    logger.warning(f"⚠️ Somma probabilità non corretta: {somma_prob}")
```

### 5. Security Headers - CSP Permissivo per Dashboard
CSP configurato con `unsafe-inline` per Chart.js/Bootstrap:
```python
csp = {
    'script-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
    'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com"
}
```
**NON rimuovere** `unsafe-inline` o dashboard non funziona.

## Integration Points

### External Dependencies
1. **The Odds API** (Quota richieste!)
   - `integrations/odds_api.py`: Client con gestione quota
   - Limite free tier: 500 richieste/mese
   - Ogni `/api/upcoming_matches` = 1-2 richieste

2. **Football-Data.co.uk** (Scraping dati storici)
   - `scripts/scraper_dati.py`: Download CSV stagioni passate
   - URL pattern: `https://www.football-data.co.uk/mmz4281/2425/I1.csv` (Serie A)

### Cross-Component Communication
- **Web ↔ Scripts**: `sys.path.append()` per import moduli scripts in Flask
- **Cache Manager**: Singleton pattern, importato in app_professional.py
- **Monitoring**: Optional import con graceful degradation se non disponibile

## Critical Gotchas

### 1. Quote Pareggi Range Validato
```python
# CORRETTO: Solo 2.8-3.5 per pareggi (backtest validato)
if odds < 2.8 or odds > 3.5:
    return False, 'filtered_out'

# Quote >3.5 = WR 20.8%, ROI -24% (alta varianza)
```

### 2. Smoothing Bayesiano - MAX 20%
```python
# CORRETTO: Leggero smoothing solo se pochi dati
if n_partite < 20:
    peso_prior = min(20 / max(n_partite, 1), 0.20)  # MAX 20%

# ANTI-PATTERN: peso_prior = 0.5 → appiattisce tutto
```

### 3. Over/Under 2.5 - Calcolo Dinamico
```python
# CORRETTO: Pendenza realistica sigmoidale
prob_over25 = 1 / (1 + math.exp(-2.0 * diff_25))
prob_over25 = max(0.35, min(0.70, prob_over25))  # Range realistico

# ANTI-PATTERN: prob_over25 = max(0.48, min(0.52, ...))  # Troppo stretto!
```

### 4. Dataset Loading - Include Stagione Corrente
```python
# Carica storico + stagione 2025-26
df_features = pd.read_csv('data/dataset_features.csv')
df_current = pd.read_csv('data/I1_2526.csv')
df_features = pd.concat([df_features, df_current], ignore_index=True)
```
Squadre neopromesse (es. Pisa) hanno pochi dati: usa soglia minima 2 partite.

### 5. Render Environment Variables
```bash
# OBBLIGATORIO su Render dashboard
ODDS_API_KEY="chiave_reale"
FLASK_ENV="production"
# PORT viene iniettato automaticamente da Render
```

## Performance e Metriche

### Backtest Performance (FASE1)
- **ROI Turnover**: +7.17% (da -4.48%)
- **Win Rate**: 31.0% (da 29.2%)
- **Max Drawdown**: -52.3% (da -78.6%)
- **Trade Reduction**: -69% (510 → 158) = migliore qualità

### Cache Performance
- **Speedup**: 160x (2.32s → 0.01s per upcoming_matches)
- **Hit Rate Target**: >50%
- **Memory Usage**: ~1MB per 100 partite cached

### API Rate Limits
- Default: 60 req/min per endpoint
- Critical endpoints: 30 req/min (`/api/predict_enterprise`)
- Admin: 5 req/min (`/api/cache/clear`)

## Quick Reference Commands

```bash
# Rigenera cache ROI (no API calls)
curl -X POST http://localhost:5000/api/rigenera_cache

# Clear Redis cache completo
curl -X POST http://localhost:5000/api/cache/clear

# Check stato automazione
curl http://localhost:5000/api/automation_status

# Test coerenza predizioni
curl http://localhost:5000/api/test_coerenza

# Backtest con filtri FASE1
python backtest_fase1_improved.py
```

## Docs di Riferimento
- [FASE1_IMPLEMENTATA.md](../FASE1_IMPLEMENTATA.md): Filtri validati e metriche
- [PRODUCTION_READY.md](../PRODUCTION_READY.md): Status deployment e task completati
- [MIGLIORAMENTI_IMPLEMENTATI.md](../MIGLIORAMENTI_IMPLEMENTATI.md): Changelog features
- [README.md](../README.md): Setup e quick start generale
