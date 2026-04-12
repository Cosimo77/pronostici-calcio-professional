# 📊 Sistema Auto-Tracking Professionale

Sistema completamente automatizzato per tracking predizioni e monitoring accuracy in real-time.

## 🎯 Funzionalità

### 1️⃣ **Auto-Tracking Predizioni**
- ✅ Ogni chiamata `/api/predict_enterprise` salva automaticamente:
  - Squadre, data, mercato
  - Predizione e probabilità
  - Quote bookmaker
  - Expected Value (EV%)
  - Strategia (FASE1_VALIDATED / FILTERED_OUT)

### 2️⃣ **Aggiornamento Risultati Automatico**
- ✅ Cron job 3x giorno (09:00, 15:00, 21:00)
- ✅ Scarica risultati reali da football-data.co.uk
- ✅ Aggiorna tracking con esiti partite
- ✅ Calcola profit automaticamente

### 3️⃣ **Dashboard Live Metrics**
- ✅ Accuracy real-time ultimi 30 giorni
- ✅ ROI % e profit totale
- ✅ Breakdown per mercato (1X2, OU2.5, GGNG)
- ✅ Confronto vs backtest baseline

---

## 📁 File Sistema

```
utils/
└── auto_tracking.py          # Modulo tracking (get_tracker singleton)

integrations/
└── football_data_results.py  # Client risultati reali Serie A

scripts/
└── auto_update_tracking.py   # Cron job aggiornamento

tracking_predictions_live.csv # Database tracking (CSV)
logs/
└── auto_tracking.log         # Log automazione
```

---

## 🚀 Utilizzo

### Tracciamento Automatico (già attivo)
Ogni predizione API viene tracciata automaticamente:

```bash
curl -X POST http://localhost:5008/api/predict_enterprise \
  -H "Content-Type: application/json" \
  -d '{"squadra_casa":"Inter","squadra_ospite":"Milan"}'

# ✅ Salvata automaticamente in tracking_predictions_live.csv
```

### Aggiornamento Manuale Risultati
```bash
python3 scripts/auto_update_tracking.py
```

### Configurazione Cron
Il cron job è già configurato in `crontab.txt`:
```
# 3x al giorno: mattina, pomeriggio, sera
0 9,15,21 * * * python3 scripts/auto_update_tracking.py
```

Per installare:
```bash
crontab crontab.txt
# Verifica
crontab -l | grep auto_update_tracking
```

---

## 📊 API Dashboard

### Endpoint Monitoring Accuracy
```bash
curl http://localhost:5008/api/monitoring/accuracy
```

**Response:**
```json
{
  "status": "ok",
  "status_icon": "🟢",
  "accuracy_7d_pct": 84.62,
  "predictions_7d": 13,
  "correct_7d": 11,
  "roi_7d_pct": 69.15,
  "total_profit_7d": 8.99,
  "market_breakdown": {
    "1X2": {"accuracy": 0.8462, "correct": 11, "total": 13},
    "OU25": {"accuracy": 1.0, "correct": 4, "total": 4}
  },
  "vs_backtest": {
    "baseline": 0.395,
    "difference_pct": 44.7,
    "better": true
  }
}
```

---

## 🔧 Architettura

### 1. Tracking Layer (`utils/auto_tracking.py`)
```python
from utils.auto_tracking import get_tracker

tracker = get_tracker()

# Salva predizione
tracker.track_prediction(
    casa='Inter',
    ospite='Milan',
    mercato='1X2',
    predizione='Casa',
    probabilita=0.65,
    quota=1.80,
    ev_pct=17.0
)

# Aggiorna risultato
tracker.update_result(
    casa='Inter',
    ospite='Milan',
    data='2026-04-12',
    risultato_reale='H'  # H=Casa, D=Pareggio, A=Away
)

# Stats
stats = tracker.get_stats(days=30)
# → accuracy, ROI, profit
```

### 2. Results Client (`integrations/football_data_results.py`)
```python
from integrations.football_data_results import get_results_client

client = get_results_client()

# Scarica risultati ultimi 7 giorni
results = client.get_results_for_tracking(days_back=7)

# Output:
# [
#   {
#     'data': '2026-04-12',
#     'casa': 'Inter',
#     'ospite': 'Milan',
#     'home_goals': 2,
#     'away_goals': 1,
#     '1X2': 'H',
#     'OU25': 'Over',
#     'GGNG': 'GG'
#   }
# ]
```

### 3. Auto Integration (`web/app_professional.py`)
Auto-tracking integrato direttamente in `/api/predict_enterprise`:

```python
# AUTO_TRACKING_ENABLED = True  # Import automatico

@app.route("/api/predict_enterprise", methods=["POST"])
def api_predict_enterprise():
    # ... logica predizione ...
    
    # 📊 Auto-tracking
    if AUTO_TRACKING_ENABLED:
        tracker.track_prediction(...)
        logger.info("📊 Predizione tracciata")
    
    return jsonify(response)
```

---

## ✅ Testing

### Test Completo End-to-End
```bash
python3 << 'EOF'
from utils.auto_tracking import get_tracker
import requests

# 1. Predizione (auto-tracked)
r = requests.post('http://localhost:5008/api/predict_enterprise',
                  json={'squadra_casa': 'Inter', 'squadra_ospite': 'Milan'})
print(f"✅ Predizione: {r.json()['predizione_enterprise']}")

# 2. Aggiorna risultato
tracker = get_tracker()
tracker.update_result('Inter', 'Milan', '2026-04-12', 'H')
print("✅ Risultato aggiornato")

# 3. Statistiche
stats = tracker.get_stats(days=30)
print(f"✅ Accuracy: {stats['accuracy_pct']:.1f}%")
print(f"✅ ROI: {stats['roi_pct']:+.2f}%")
EOF
```

### Test Cron Job
```bash
# Dry run
python3 scripts/auto_update_tracking.py

# Output atteso:
# 📥 Scarico risultati ultimi 3 giorni...
# ✅ Trovate X partite completate
# ✅ Aggiornate Y predizioni
# 📊 STATISTICHE: Accuracy X%, ROI X%
```

---

## 🔄 Workflow Automatico

```
┌─────────────────────────────────────────────────┐
│  1. UTENTE CHIAMA API PREDIZIONE                │
│     /api/predict_enterprise                      │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  2. AUTO-TRACKING SALVA IN CSV                   │
│     → tracking_predictions_live.csv              │
│     Data, Casa, Ospite, Predizione, Quota, EV    │
│     Risultato_Reale: VUOTO                       │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  3. PARTITA GIOCATA                              │
│     (ore/giorni dopo)                            │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  4. CRON JOB (3x giorno)                         │
│     scripts/auto_update_tracking.py              │
│     → Scarica risultati football-data.co.uk      │
│     → Trova predizioni da aggiornare             │
│     → Calcola correttezza: predizione == reale   │
│     → Calcola profit: (quota-1) se win, -1 loss  │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  5. CSV AGGIORNATO CON RISULTATI                 │
│     Risultato_Reale: H/D/A, Over/Under, GG/NG    │
│     Corretto: True/False                         │
│     Profit: +X.XX o -X.XX                        │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  6. DASHBOARD MOSTRA METRICHE LIVE               │
│     /api/monitoring/accuracy                     │
│     → Accuracy %                                 │
│     → ROI %                                      │
│     → Profit totale                              │
│     → Breakdown mercati                          │
└─────────────────────────────────────────────────┘
```

---

## 📋 Formato CSV Tracking

```csv
Data,Giornata,Casa,Ospite,Mercato,Predizione,Probabilita_Sistema,Quota,EV_%,Risultato_Reale,Corretto,Profit,Note
2026-04-12,0,Inter,Milan,1X2,Casa,0.65,1.80,17.0,H,True,0.80,FILTERED_OUT | EV 17.0%
2026-04-12,0,Inter,Milan,OU25,Over,0.58,1.95,13.1,Over,True,0.95,Auto-tracked
```

**Colonne:**
- `Data`: YYYY-MM-DD
- `Casa`/`Ospite`: Nomi squadre
- `Mercato`: 1X2, OU25, GGNG, ecc.
- `Predizione`: Casa/Pareggio/Away, Over/Under, GG/NG
- `Probabilita_Sistema`: 0.0-1.0 (confidenza modello)
- `Quota`: Decimal odds bookmaker
- `EV_%`: Expected Value percentuale
- `Risultato_Reale`: H/D/A, Over/Under, GG/NG (compilato dopo)
- `Corretto`: True/False (calcolato automaticamente)
- `Profit`: ±X.XX unità (calcolato automaticamente)
- `Note`: Strategia, annotazioni

---

## 🎛️ Configurazione Avanzata

### Modifica Frequenza Cron
```bash
# Aumenta a 4x giorno
0 6,12,18,23 * * * python3 scripts/auto_update_tracking.py

# Solo sera (per partite del pomeriggio)
0 21 * * * python3 scripts/auto_update_tracking.py
```

### Lookback Days Personalizzato
```python
# scripts/auto_update_tracking.py
# Cerca risultati ultimi 7 giorni invece di 3
update_tracking_results(days_back=7)
```

### Disable Auto-Tracking Temporaneo
```python
# web/app_professional.py
AUTO_TRACKING_ENABLED = False  # Disabilita tracking
```

---

## 🐛 Troubleshooting

### Tracking non salva predizioni
```bash
# 1. Verifica import
python3 -c "from utils.auto_tracking import get_tracker; print('✅ OK')"

# 2. Controlla log server
tail -f logs/server.log | grep "Auto-tracking"

# 3. Test manuale
python3 << 'EOF'
from utils.auto_tracking import get_tracker
tracker = get_tracker()
tracker.track_prediction('Inter', 'Milan', '1X2', 'Casa', 0.65, 1.80, 17.0)
print("✅ Salvato")
EOF

# 4. Verifica file
tail -1 tracking_predictions_live.csv
```

### Cron non esegue aggiornamenti
```bash
# 1. Test manuale
python3 scripts/auto_update_tracking.py

# 2. Verifica crontab installato
crontab -l | grep auto_update_tracking

# 3. Controlla log
tail -f logs/auto_tracking.log

# 4. Permessi file
chmod +x scripts/auto_update_tracking.py
```

### Risultati non scaricati
```bash
# Test client
python3 integrations/football_data_results.py

# Output atteso:
# 📥 Scarico risultati da: https://www.football-data.co.uk/mmz4281/2526/I1.csv
# ✅ Trovate X partite completate

# Se 0 risultati:
# → football-data.co.uk non ancora aggiornato (aspetta 24h dopo partite)
# → Verifica manualmente: https://www.football-data.co.uk/italym.php
```

---

## 📈 Metriche Performance

### Expected Accuracy
- **Baseline Backtest**: 39.5% (1X2)  
- **Target Live**: >45%  
- **Current**: 84.6% (13 partite)  

⚠️ **Nota**: Piccolo campione, convergenza verso baseline su 100+ partite.

### Expected ROI
- **FASE 1 Backtest**: +7.17% (158 trade)  
- **Current Live**: +69.15% (13 trade)  

⚠️ **Variance**: Sample size troppo piccolo, ROI si stabilizzerà su +5-10% a lungo termine.

---

## 🔐 Security & Privacy

- ✅ Nessun dato personale utente salvato
- ✅ Solo predizioni anonime (squadre, esiti, quote)
- ✅ File CSV locale, non esposto pubblicamente
- ✅ Logs rotation automatica (gzip dopo 30 giorni)

---

## 📝 Changelog

### v1.0.0 (12 Aprile 2026)
- ✨ **Sistema auto-tracking completo**
- ✨ Integrazione API `/api/predict_enterprise`
- ✨ Client football-data.co.uk risultati reali
- ✨ Cron job aggiornamento 3x giorno
- ✨ Dashboard metrics `/api/monitoring/accuracy`
- ✨ Calcolo automatico profit/ROI
- ✅ Test end-to-end passed

---

## 🚀 Roadmap

### Fase 2 (Q2 2026)
- [ ] Notifiche email risultati giornalieri
- [ ] Export grafici accuracy PNG
- [ ] Integrazione Telegram bot per alert
- [ ] Backup automatico su cloud (S3/Drive)

### Fase 3 (Q3 2026)
- [ ] Machine learning calibration dinamica
- [ ] A/B testing framework tracking
- [ ] Dashboard web interattiva (React)
- [ ] Multi-league support (Premier, Liga)

---

## 📞 Support

- 📖 Docs: `/docs/AUTO_TRACKING.md` (questo file)
- 🐛 Issues: Crea issue su GitHub
- 💬 Logs: `logs/auto_tracking.log`
- 📧 Email: (inserisci se pubblico)

---

**Sistema Professional Auto-Tracking v1.0.0**  
*Accuracy Monitoring Live - Zero Manual Intervention*
