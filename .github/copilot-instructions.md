# Pronostici Calcio - Istruzioni per l'assistente

Sistema di value betting per Serie A: Flask + scikit-learn, dati reali, predizioni deterministiche.
Web su Render, automazione dati/modelli in locale. Contesto completo e metriche: `docs/guides/CONTESTO_PROGETTO.md`
(leggilo solo se serve).

## File chiave
- `web/app_professional.py`: app Flask, `ProfessionalCalculator`, mercati (`_calcola_mercati_deterministici`), API.
- `web/diario_storage.py` + `database/`: Diario betting (PostgreSQL, ripiego CSV). Regole multiple in `database/multipla_rules.py`.
- `web/templates/*.html` e `web/static/css/professional-theme.css`: UI (tema scuro/chiaro con `data-bs-theme`).
- `scripts/modelli_predittivi.py`: solo training; per predizioni live usare `ProfessionalCalculator`.

## Comandi
- Avvio locale: `python -m web.app_professional` (porta `PORT`, default 5008).
- Test: `pytest tests/test_multipla_rules.py tests/test_risk_metrics.py tests/test_value_betting.py tests/test_ml_predictions.py`.
- Lint/format: hook pre-commit (black, flake8, isort, riga max 120). Il commit va fatto con `venv/bin` nel PATH
  (`PATH="$PWD/venv/bin:$PATH" git commit ...`); non saltare gli hook.

## Regole da rispettare
- Predizioni deterministiche, nessuna casualita'; probabilita' sempre con somma 1.0 (±0.001).
- Smoothing bayesiano al massimo 20% (`peso_prior = min(20 / max(n, 1), 0.20)`), solo con meno di 20 partite.
- Niente probabilita' fisse al 50% per i mercati: usare calcoli dinamici dalle statistiche delle squadre.
- Over/Under 2.5: sigmoide, probabilita' limitata a 0.35-0.70.
- Value betting FASE 1: solo pareggi, quote 2.8-3.5, EV >= 25% (quote > 3.5 hanno ROI negativo nel backtest).
- Nomi squadra: normalizzare con `normalize_team_name()` prima di interrogare il dataset (The Odds API usa nomi diversi).
- Dataset: storico `data/dataset_features.csv` + stagione corrente; neopromosse con poche partite (soglia minima 2).
- Log con `structlog` (no `print()` in produzione); cache Redis con degradazione graceful.
- CSP: non rimuovere `'unsafe-inline'` (serve a Chart.js/Bootstrap).
- The Odds API: 500 richieste/mese; controllare la cache prima di ogni chiamata.

## Diario betting
- Date in formato `DD/MM/YYYY`: mai usare `pd.to_datetime` senza `dayfirst`. Ordinare con `ordina_cronologico`.
- Una multipla e' PENDING finche' tutti gli eventi non sono validati; la contabilita' usa `get_accounting_bets()`
  (singole + una voce per multipla, mai le gambe).

## Sicurezza
- Mai scrivere chiavi API o credenziali nei file versionati (`render.yaml` incluso): usare variabili d'ambiente.
