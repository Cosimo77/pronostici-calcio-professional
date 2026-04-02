# 📊 Sistema Tracking FASE 2 - Guida Completa

## 🎯 Cosa Fa Questo Sistema

**Tracking automatico** delle performance reali per le **12+ opportunità FASE 2** validate dal sistema di value betting. Confronta ROI reale vs backtest (+29%) e monitora evoluzione bankroll in tempo reale.

### Componenti Principali

1. **`genera_tracking_fase2.py`**: Estrae opportunità validate dal sistema e crea CSV tracciabile
2. **`aggiorna_tracking_fase2.py`**: Ricalcola P&L e metriche dopo aggiornamento risultati
3. **`aggiorna_risultati_auto.py`**: Scarica risultati partite e aggiorna automaticamente WIN/LOSS
4. **Dashboard Web** (`/tracking`): Interfaccia visuale con grafici equity curve e P&L
5. **API REST** (`/api/tracking/fase2`): Endpoint JSON per dati tracking

---

## 🚀 Quick Start (3 Step)

### Step 1: Genera File Tracking Iniziale

```bash
cd /Users/cosimomassaro/Desktop/pronostici_calcio
python3 genera_tracking_fase2.py
```

**Output**: File `tracking_fase2_febbraio2026.csv` con ~12 opportunità FASE 2 validate

### Step 2: Avvia Dashboard

```bash
# Opzione A: Script automatico
./start_tracking_fase2.sh

# Opzione B: Manuale
python3 -m web.app_professional
```

### Step 3: Apri Dashboard

Visita: **http://localhost:5000/tracking**

Vedrai:
- 📈 **Metriche summary**: ROI, Win Rate, P&L, Bankroll
- 📋 **Tabella trade**: Elenco completo con status colorati (verde=win, rosso=loss)
- 📉 **Equity curve**: Grafico evoluzione bankroll

---

## 📖 Workflow Operativo Completo

### 1️⃣ Generazione Opportunità (Giornaliera)

```bash
# Rigenera tracking con opportunità aggiornate
python3 genera_tracking_fase2.py

# Output:
# ✅ Creato tracking_fase2_febbraio2026.csv
# 📊 Opportunità salvate: 12
# 
# 📈 Riepilogo per Strategia:
#   • FASE2_DOUBLE_CHANCE: 6 opportunità (ROI backtest: +75.21%)
#   • FASE2_OVER_UNDER: 5 opportunità (ROI backtest: +5.86%)
#   • FASE1_PAREGGIO: 1 opportunità (ROI backtest: +7.17%)
```

### 2️⃣ Monitoraggio Partite (Durante la Giornata)

**Opzione A - Manuale**: Apri CSV e aggiorna colonna `Risultato`:
```
Risultato: WIN     # Se scommessa vinta
Risultato: LOSS    # Se scommessa persa
Risultato: VOID    # Se partita annullata
```

**Opzione B - Automatico**:
```bash
# Scarica risultati da API e aggiorna automaticamente
python3 aggiorna_risultati_auto.py
```

### 3️⃣ Calcolo P&L (Dopo Aggiornamenti)

```bash
python3 aggiorna_tracking_fase2.py

# Output:
# ✅ Aggiornato tracking_fase2_febbraio2026.csv
# 
# 📈 PERFORMANCE FASE 2
# Total Trade: 12
#   • Chiusi: 5 (Win: 3, Loss: 2)
#   • Pending: 7
# 
# Win Rate: 60.0% (atteso 50.6%)
# ROI: +45.2% (backtest +29.0%)
# 
# P&L Totale: €+22.60
# Bankroll Finale: €522.60 (Iniziale: €500.00)
# Variazione: +4.5%
```

### 4️⃣ Analisi Dashboard (Continua)

Dashboard aggiorna automaticamente quando ricarichi la pagina:
- **Equity Curve**: Vedi andamento bankroll su timeline
- **Metriche Realtime**: Confronto ROI reale vs backtest
- **Filtri**: Analizza per strategia (DC, Over/Under, Pareggi)

---

## 🤖 Automazione Completa

### Setup Cron Job (Esecuzione Giornaliera)

```bash
# Apri crontab
crontab -e

# Aggiungi queste righe:

# 1. Genera tracking ogni mattina ore 9:00
0 9 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && python3 genera_tracking_fase2.py >> logs/tracking_cron.log 2>&1

# 2. Aggiorna risultati ogni sera ore 23:00  
0 23 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && python3 aggiorna_risultati_auto.py >> logs/tracking_cron.log 2>&1

# 3. Ricalcola P&L ogni sera ore 23:05
5 23 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && python3 aggiorna_tracking_fase2.py >> logs/tracking_cron.log 2>&1
```

### Script Notifiche Email (Opzionale)

```bash
# Invia report giornaliero via email
0 9 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && python3 genera_tracking_fase2.py | mail -s "🎯 Opportunità FASE 2 Oggi" tua@email.com
```

---

## 📊 Struttura File CSV

```csv
Data,Casa,Ospite,Mercato,Esito,Quota,EV_%,Prob_Modello_%,Strategia,ROI_Backtest,Stake_Suggerito,Risultato,Profit_Loss,Bankroll,Note
2026-02-09,Roma,Cagliari,Over/Under 2.5,Over 2.5,2.1,17.7,55.9,FASE2_OVER_UNDER,5.86,10.0,WIN,11.0,511.0,Auto-aggiornato 2026-02-09
2026-02-14,Lazio,Atalanta,Over/Under 2.5,Over 2.5,2.13,48.8,70.0,FASE2_OVER_UNDER,5.86,10.0,PENDING,0.0,500.0,Auto-generato 2026-02-09 20:32
```

### Campi Chiave

- **EV_%**: Expected Value percentuale (quanto il modello pensa sia sottoquotata)
- **Prob_Modello_%**: Probabilità calcolata dal modello (es. 55.9% = 55.9% chance Over 2.5)
- **ROI_Backtest**: Performance storica strategia su 420 test matches
- **Stake_Suggerito**: 2% bankroll (conservativo, backtest validato)
- **Profit_Loss**: Calcolato automaticamente da `aggiorna_tracking_fase2.py`

---

## 🔧 Troubleshooting

### File tracking non trovato
```bash
# Genera nuovo file
python3 genera_tracking_fase2.py
```

### Dashboard mostra 0 trade
- Verifica file CSV esista: `ls -lh tracking_fase2_febbraio2026.csv`
- Check permessi lettura: `chmod 644 tracking_fase2_febbraio2026.csv`
- Riavvia server Flask

### API risultati non funziona
```bash
# Fallback: Aggiornamento manuale CSV
# Apri file con editor e modifica colonna Risultato
nano tracking_fase2_febbraio2026.csv

# Poi ricalcola P&L
python3 aggiorna_tracking_fase2.py
```

### Quote API esaurite (The Odds API)
```bash
# Check quota rimanente
curl https://pronostici-calcio-pro.onrender.com/api/upcoming_matches | jq '.remaining_requests'

# Soluzione temporanea: Usa dati cached (15 min TTL)
# Sistema degrada gracefully
```

---

## 📈 Metriche Attese (Backtest)

### Performance Target FASE 2

| Strategia | ROI Backtest | Win Rate | Sample Size |
|-----------|--------------|----------|-------------|
| **Double Chance** | +75.21% | 75.0% | 96 trade |
| **Over/Under 2.5** | +5.86% | 46.5% | 215 trade |
| **Pareggi (FASE1)** | +7.17% | 31.0% | 158 trade |
| **MEDIA PESATA** | **+29.0%** | **50.6%** | 469 trade |

### Soglie Validazione Realtime

- ✅ **ROI > +15%** dopo 30 trade: Performance eccellente, continua
- ⚠️ **ROI tra 0% e +15%** dopo 30 trade: Normale varianza, monitora
- 🔴 **ROI < -10%** dopo 50 trade: Review filtri, possibile overfitting backtest

---

## 🎓 Best Practices

### 1. Money Management Conservativo
- **Stake fisso**: 2% bankroll (€10 su €500)
- **Max drawdown tollerato**: -20% (-€100)
- **Stop trading** se bankroll < €400 → Rivedi strategia

### 2. Validazione Graduale
- **Primi 10 trade**: Paper trading (non scommettere soldi veri)
- **Trade 11-30**: Stake ridotto (1% bankroll)
- **Trade 31+**: Stake normale (2%) se ROI positivo

### 3. Tracking Disciplinato
- **Mai saltare trade**: Anche se perdi, registra tutto
- **Nessuna selezione cherry-pick**: Se filtro valida, gioca il trade
- **Aggiorna risultati entro 24h**: Evita bias memoria

### 4. Review Settimanale
```bash
# Ogni domenica, analizza performance
python3 aggiorna_tracking_fase2.py

# Domande da farti:
# - Win Rate allineato a backtest?
# - Quale strategia performa meglio?
# - Ci sono pattern nei loss (es. sempre Away teams)?
```

---

## 🚀 Prossime Features (Roadmap)

- [ ] **Alert Telegram/Pushover**: Notifiche quando nuova opportunità >30% EV
- [ ] **Export PDF Report**: Report settimanale automatico con grafici
- [ ] **Filtri avanzati dashboard**: Filtra per strategia, data, EV min
- [ ] **Backtesting integrato**: Simula "what-if" su filtri diversi
- [ ] **Confronto bookmaker**: Mostra migliori quote per stessa bet

---

## 📞 Support

- **File importante**: Se hai problemi, allega `tracking_fase2_febbraio2026.csv`
- **Log errori**: Check `logs/tracking_cron.log` se automazione fallisce
- **API Debug**: Visita `http://localhost:5000/api/debug/odds_api_test`

---

**Creato**: 9 Febbraio 2026  
**Versione**: 1.0.0  
**Sistema**: Pronostici Calcio Pro - FASE 2 Tracking
