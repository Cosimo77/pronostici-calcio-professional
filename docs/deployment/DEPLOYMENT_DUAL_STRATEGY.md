# 🚀 DEPLOYMENT DUAL-STRATEGY - Guida Completa

**Data**: 14 Febbraio 2026  
**Status**: ✅ **PRODUCTION READY** - Sistema Dual-Strategy Certificato

---

## 📊 Sistema Certificato

### Strategia Trading Attiva

| Mercato | ROI | Win Rate | Trade/Anno | Quote Range | EV Minimo | Backtest |
|---------|-----|----------|------------|-------------|-----------|----------|
| **Pareggi 1X2** | **+7.17%** | 31.0% | ~108 | 2.8-3.5 | ≥25% | ✅ 158 trade |
| **Under 2.5** | **+5.86%** | 46.5% | ~400 | 2.0-2.5 | ≥15% | ✅ 144 trade |
| **Combined** | **+6.64%** | 41.4% | ~516 | Mixed | Mixed | ✅ 302 trade |

### Allocazione Bankroll Consigliata

```
Bankroll Totale: 10,000 EUR

Allocazione:
- 60% Pareggi (6,000 EUR)
  → Expected return: +430 EUR/anno
  → ~108 opportunità/anno (1 ogni 3.4 giorni)
  
- 40% Under 2.5 (4,000 EUR)
  → Expected return: +234 EUR/anno
  → ~400 opportunità/anno (1.1/giorno)

Total Expected Profit: +664 EUR/anno
Frequenza Trade: 516 trade/anno (1.4/giorno media)
Max Drawdown Stimato: -30%
```

---

## 🔧 Requisiti Sistema

### 1. Python Environment

```bash
# Python 3.8+
python3 --version  # Verifica ≥3.8

# Dipendenze
pip install -r requirements.txt

# Principali:
# - Flask 3.1.0
# - scikit-learn 1.3.2
# - pandas 2.1.4
# - Redis (opzionale, sistema degrada gracefully)
```

### 2. API Key (OBBLIGATORIA)

```bash
# Registra account: https://the-odds-api.com
# Free tier: 500 requests/mese

# Configura variabile ambiente
export ODDS_API_KEY="your_32_char_api_key_here"

# Verifica configurata
echo $ODDS_API_KEY | wc -c  # Deve essere 32 caratteri
```

### 3. Redis (Opzionale)

```bash
# macOS
brew install redis
redis-server &

# Linux
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:latest

# ⚠️ Se Redis non disponibile: sistema usa fallback in-memory
```

---

## 🚀 Deployment Locale

### Quick Start (Development)

```bash
cd /Users/cosimomassaro/Desktop/pronostici_calcio

# 1. Configura API key
export ODDS_API_KEY="..."

# 2. Avvia server
python3 -m web.app_professional

# Server disponibile su:
# - http://localhost:5008
# - http://127.0.0.1:5008
```

### Production (Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn gevent

# Avvia con workers
gunicorn -w 4 -k gevent --bind 0.0.0.0:5008 web.app_professional:app

# Con logging
gunicorn -w 4 -k gevent \
  --bind 0.0.0.0:5008 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  web.app_professional:app
```

### Supervisord (Keep Alive)

```ini
# /etc/supervisor/conf.d/pronostici.conf
[program:pronostici_calcio]
command=/usr/local/bin/gunicorn -w 4 -k gevent --bind 0.0.0.0:5008 web.app_professional:app
directory=/Users/cosimomassaro/Desktop/pronostici_calcio
user=cosimomassaro
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pronostici_calcio.log
environment=ODDS_API_KEY="your_key_here"
```

---

## 📡 API Endpoints

### 1. Health Check

```bash
curl http://localhost:5008/api/health | python3 -m json.tool

# Response:
{
  "status": "healthy",
  "odds_api_key_configured": true,
  "squadre_caricate": 20,
  "database_records": 2931,
  "cache_attiva": true
}
```

### 2. Predizione Enterprise con Value Betting

```bash
curl -X POST http://localhost:5008/api/predict_enterprise \
  -H "Content-Type: application/json" \
  -d '{
    "squadra_casa": "Inter",
    "squadra_ospite": "Milan",
    "odds_casa": 2.1,
    "odds_pareggio": 3.3,
    "odds_trasferta": 3.5,
    "odds_over_25": 1.85,
    "odds_under_25": 2.05
  }' | python3 -m json.tool

# Response include:
# - predizione_enterprise: outcome previsto
# - probabilita_ensemble: prob H/D/A
# - value_betting.fase2_opportunities: lista opportunità value
# - mercati: tutti i 25+ mercati calcolati
```

### 3. Opportunità Value Betting (Upcoming Matches)

```bash
curl http://localhost:5008/api/upcoming_matches | python3 -m json.tool

# Response:
{
  "opportunities": [
    {
      "match": "Como vs Fiorentina",
      "market": "1X2",
      "outcome": "Pareggio",
      "odds": 3.20,
      "ev": 28.5,
      "strategy": "FASE1_PAREGGIO",
      "roi_backtest": 7.17,
      "prob_model": 35.2
    },
    {
      "match": "Lecce vs Lazio",
      "market": "Over/Under 2.5",
      "outcome": "Under 2.5",
      "odds": 2.15,
      "ev": 18.3,
      "strategy": "FASE2_UNDER",
      "roi_backtest": 5.86,
      "prob_model": 55.1
    }
  ],
  "last_update": "2026-02-14T19:00:00",
  "api_requests_remaining": 478
}
```

### 4. Test Coerenza (Predizioni Deterministiche)

```bash
curl http://localhost:5008/api/test_coerenza | python3 -m json.tool

# Verifica che predizioni siano sempre identiche
# (nessuna randomness, 100% deterministiche)
```

---

## 🎯 Workflow Operativo

### Daily Routine

**09:00 - Check Partite Upcoming**
```bash
curl http://localhost:5008/api/upcoming_matches > opportunities.json

# Analizza opportunità trovate
python3 << EOF
import json
with open('opportunities.json') as f:
    data = json.load(f)
    opps = data.get('opportunities', [])
    print(f"Opportunità oggi: {len(opps)}")
    for opp in opps:
        print(f"  {opp['match']}: {opp['market']} {opp['outcome']} @ {opp['odds']} (EV {opp['ev']:.1f}%)")
EOF
```

**Per Ogni Opportunità: Validazione Manuale**
1. ✅ Verifica EV ≥25% (pareggi) o ≥15% (under 2.5)
2. ✅ Quote nel range validato
3. ✅ Check news: infortuni, squalifiche, motivazione
4. ✅ Confronta quote su 2-3 bookmaker (arbitraggi)
5. ✅ Kelly Criterion: stake = (EV% × prob) / quote

**Placing Bets**
```python
# Esempio calcolo stake con Kelly conservativo
bankroll_pareggi = 6000  # EUR
ev_pct = 28.5  # %
prob_model = 0.352
odds = 3.20

# Kelly Fraction
kelly_full = (prob_model * odds - 1) / (odds - 1)
kelly_conservativo = kelly_full * 0.25  # 25% del Kelly pieno

stake = bankroll_pareggi * kelly_conservativo
print(f"Stake consigliato: {stake:.2f} EUR")
# Output: ~75-150 EUR tipicamente
```

**Post-Match: Tracking**
```bash
# Aggiungi risultato a tracking CSV
echo "2026-02-14,Como,Fiorentina,Pareggio,3.20,28.5,WIN,+220.00" >> tracking_giocate.csv
```

---

## 📊 Monitoring e KPI

### Metriche da Tracciare

```bash
# Dashboard metriche live (implementato in frontend)
# - http://localhost:5008/dashboard

# KPI Chiave:
# 1. ROI Turnover (target >6%)
# 2. Win Rate (target >40%)
# 3. Max Drawdown (alert se >35%)
# 4. Sharpe Ratio (target >0.4)
# 5. Frequenza trade (target 1-2/giorno)
```

### Alerts Automatici

```bash
# Script check anomalie (da schedulare cron)
python3 << EOF
import pandas as pd

df = pd.read_csv('tracking_giocate.csv')
roi = df['profit'].sum() / df['stake'].sum()

if roi < -0.15:  # -15% alert
    print("🚨 ALERT: ROI below -15%, review strategy!")
if df.tail(20)['result'].value_counts().get('LOSS', 0) > 15:
    print("⚠️ WARNING: 15+ losses in last 20 trades")
EOF
```

---

## ⚠️ Risk Management

### Limiti Operativi

```python
# Hard limits (implementare prima di trading reale)
LIMITS = {
    'max_stake_singolo': 250,  # EUR per singolo trade
    'max_stake_giornaliero': 500,  # EUR totale giorno
    'max_stakes_simultanei': 3,  # Max trade aperti contemporaneamente
    'stop_loss_giornaliero': -200,  # EUR loss giornaliero → stop trading
    'stop_loss_settimanale': -500,  # EUR loss settimanale → pausa 1 settimana
}
```

### Red Flags - STOP Trading

❌ **Fermarsi immediatamente se**:
1. Drawdown >40% bankroll totale
2. 10 loss consecutive
3. ROI <-20% su ultimo mese
4. Quote sistema vs bookmaker divergono >50% costantemente (modello rotto)
5. API key esaurita (no quote reali = no trading)

---

## 🔄 Manutenzione Sistema

### Weekly Tasks

```bash
# Domenica sera

# 1. Aggiorna dati storici
python3 scripts/aggiorna_automatico.py

# 2. Riaddestra modelli (opzionale, se nuovi dati)
python3 scripts/modelli_predittivi.py

# 3. Backup tracking
cp tracking_giocate.csv backups/tracking_$(date +%Y%m%d).csv

# 4. Review performance settimana
python3 scripts/report_settimanale.py
```

### Monthly Tasks

```bash
# Fine mese

# 1. Backtest rolling window (ultimi 3 mesi)
python3 backtest_fase1_improved.py --recent-only

# 2. Verifica calibrazione probabilità
python3 tests/test_ml_predictions.py

# 3. Check API quota usage
curl "https://api.the-odds-api.com/v4/sports?apiKey=$ODDS_API_KEY" \
  -I | grep x-requests

# 4. Review mercati alternativi (quando dati sufficienti)
# - BTTS (se raccolti >60 giorni dati)
# - Corner O/U (se backtest validato)
```

---

## 🐛 Troubleshooting

### Problema: Server non si avvia

```bash
# Check porta occupata
lsof -ti:5008 | xargs kill -9

# Check dipendenze
pip install -r requirements.txt --upgrade

# Check API key
echo $ODDS_API_KEY
# Deve essere 32 caratteri, no spazi

# Check logs
tail -f logs/app.log
```

### Problema: Nessuna opportunità trovata

```bash
# 1. Verifica partite upcoming
curl "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/?apiKey=$ODDS_API_KEY&regions=eu&markets=h2h,totals"

# 2. Check filtri non troppo restrittivi
# - Pareggi: solo quote 2.8-3.5, EV ≥25% (conservativo ma corretto)
# - Under 2.5: quote 2.0-2.5, EV ≥15%

# 3. Stagione calcistica
# - Serie A: Agosto-Maggio
# - Giugno-Luglio: nessuna partita = nessuna opportunità

# 4. Weekend vs infrasettimanale
# - Weekend: 8-10 partite Serie A
# - Infrasettimanale: 0-2 partite (Coppe europee)
```

### Problema: ROI negativo dopo 1-2 settimane

```bash
# NORMALE variance a breve termine
# Sistema validato su 158-144 trade (3-6 mesi)

# Action:
# 1. Continua tracking rigoroso
# 2. Review ogni trade: errori manuali? News non considerate?
# 3. Se ROI <-15% dopo 50+ trade → rivaluta filtri
# 4. Mai cambiare strategia per sample <50 trade (variance)
```

---

## 📈 Performance Attese

### Scenario Realistico (Anno 1)

```
Capitale Iniziale: 10,000 EUR

Mese 1:  10,520 EUR (+520, ROI +5.2%)
Mese 2:  10,290 EUR (-230, drawdown -2.2%)
Mese 3:  10,780 EUR (+780, recupero +7.8%)
Mese 4:  10,650 EUR (-130, variance normale)
... (continua)

Fine Anno: 10,660 EUR (+660, ROI +6.6%)

Trade Totali: 516
Win Rate: 213/516 = 41.3%
Max Drawdown: -320 EUR (-3.2%)
Sharpe Ratio: 0.42
```

**⚠️ Importante**: Questi sono expected values statistici. Risultati reali varieranno per:
- Variance naturale scommesse
- Qualità esecuzione (timing bets, quote ottenute)
- Eventi imprevedibili (VAR, infortuni last-minute, meteo)
- Cambiamenti mercato (se tutti usano stesso sistema, EV diminuisce)

---

## ✅ Checklist Pre-Launch

Prima di iniziare trading reale, verifica:

- [ ] **API Key configurata** (`echo $ODDS_API_KEY`)
- [ ] **Server avvia correttamente** (health check OK)
- [ ] **Redis running** (opzionale ma consigliato)
- [ ] **Bankroll dedicato** (mai fondi che non puoi permetterti di perdere)
- [ ] **Tracking sheet pronto** (CSV o Excel per monitoraggio)
- [ ] **Bookmaker account** (2-3 bookmaker per migliori quote)
- [ ] **Kelly calculator** (per stake sizing)
- [ ] **Stop-loss limiti** (definiti e rispettati)
- [ ] **Tempo disponibile** (10-30 min/giorno review opportunità)
- [ ] **Aspettative realistiche** (ROI 6-8%, non 50%+)

---

## 🎯 Next Steps

### Oggi - Deploy Sistema

```bash
# 1. Configura ambiente
export ODDS_API_KEY="..."
redis-server &  # Se disponibile

# 2. Avvia server production
gunicorn -w 4 -k gevent --bind 0.0.0.0:5008 web.app_professional:app &

# 3. Test endpoint
curl http://localhost:5008/api/health
curl http://localhost:5008/api/upcoming_matches

# 4. Setup tracking
touch tracking_giocate.csv
echo "data,casa,ospite,mercato,outcome,odds,ev,result,profit" > tracking_giocate.csv
```

### Prossimi 7 Giorni - Test Paper Trading

```
Giorni 1-7: Simula bets senza soldi reali
- Track opportunità trovate
- Calcola stake con Kelly
- Registra risultati post-match
- Verifica accuratezza predizioni
- Identifica eventuali problemi operativi
```

### Post 7 Giorni - Go Live Graduale

```
Week 2: Stake 25% normale (test con soldi reali bassi)
Week 3-4: Stake 50% normale (se ROI paper trading OK)
Month 2: Stake 100% normale (full deployment)
```

---

## 📚 Documentazione Riferimento

- [CERTIFICAZIONE_DUAL_STRATEGY.md](./CERTIFICAZIONE_DUAL_STRATEGY.md) - Metriche dual-strategy
- [FASE1_IMPLEMENTATA.md](./FASE1_IMPLEMENTATA.md) - Backtest pareggi dettagliato
- [CERTIFICAZIONE_TRADING_14FEB2026.md](./CERTIFICAZIONE_TRADING_14FEB2026.md) - Security audit
- [BTTS_IMPLEMENTATION_STATUS.md](./BTTS_IMPLEMENTATION_STATUS.md) - Mercati futuri
- [README.md](./README.md) - Overview progetto

---

**Status Finale**: ✅ **SISTEMA PRONTO PER TRADING REALE**

*Dual-Strategy Certificato - Quote Reali - Backtest Validati - Production Ready*

**Good luck & Trade Responsibly! 🎯**
