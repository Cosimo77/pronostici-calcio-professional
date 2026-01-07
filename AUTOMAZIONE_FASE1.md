# 🤖 SISTEMA FASE1 COMPLETAMENTE AUTOMATICO

## ✨ Zero Configurazione Manuale

**Tutto gestito automaticamente:**
- ✅ Fetcha partite prossime da The Odds API
- ✅ Identifica opportunità FASE1 
- ✅ Salva nel tracking CSV
- ✅ Aggiorna risultati quando disponibili
- ✅ Genera report performance

---

## 🚀 USO IMMEDIATO

### Modalità Interattiva (Consigliata)

```bash
python3 fase1_automatico.py
```

**Menu opzioni:**
1. 🔍 **SCAN** - Cerca opportunità prossimi 7 giorni
2. 🔄 **UPDATE** - Aggiorna risultati partite completate
3. 📊 **REPORT** - Mostra performance
4. 🚀 **AUTO** - Esegue tutto in sequenza (SCAN → UPDATE → REPORT)

**Usa opzione 4 per tutto automatico!**

---

### Modalità Completamente Automatica

```bash
./run_fase1_auto.sh
```

Esegue SCAN + UPDATE + REPORT in un comando.

---

## ⏰ AUTOMAZIONE CON CRON (Opzionale)

Per esecuzione automatica giornaliera:

```bash
# Apri crontab
crontab -e

# Aggiungi (esegue ogni giorno ore 10:00)
0 10 * * * /Users/cosimomassaro/Desktop/pronostici_calcio/run_fase1_auto.sh >> /Users/cosimomassaro/Desktop/pronostici_calcio/logs/fase1_auto.log 2>&1
```

**Sistema scansiona automaticamente ogni giorno:**
- Identifica nuove opportunità
- Aggiorna risultati partite giocate
- Traccia tutto nel CSV

---

## 📊 WORKFLOW AUTOMATICO

### Lunedì-Mercoledì
Sistema scansiona API → trova partite weekend → salva opportunità FASE1

### Sabato-Domenica
**Niente da fare!** Partite si giocano automaticamente 😎

### Lunedì Successivo
Sistema aggiorna risultati → calcola P/L → genera report

---

## 🔧 CONFIGURAZIONE (Una Tantum)

### 1. API Key The Odds API

**Già configurata nel tuo `.env`!** Verifica:

```bash
cat .env | grep ODDS_API_KEY
```

Se mancante:
```bash
echo "ODDS_API_KEY=tua_chiave_qui" >> .env
```

Ottieni chiave gratis: https://the-odds-api.com  
(500 requests/mese = ~16 scan/mese)

### 2. Verifica Funzionamento

```bash
# Test scan
python3 fase1_automatico.py
# Scegli: 1 (SCAN)

# Test update
python3 fase1_automatico.py
# Scegli: 2 (UPDATE)

# Test report
python3 fase1_automatico.py  
# Scegli: 3 (REPORT)
```

---

## 📂 FILE GENERATI

### `tracking_fase1_gennaio2026.csv`
Tutte le opportunità identificate + risultati

**Struttura:**
```
Data,Casa,Ospite,Quota_X,EV_%,Confidenza,Risultato,Stake,Profit_Loss,Bankroll,ROI_%
11/01/2026,Juventus,Milan,3.20,42.5,0.41,PENDING,48.00,0,500.00,0
12/01/2026,Inter,Napoli,3.35,38.2,0.39,PENDING,48.00,0,500.00,0
```

Aggiornato automaticamente da sistema!

---

## 🎯 VANTAGGI AUTOMAZIONE

### Prima (Manuale)
1. ❌ Vai su bookmaker
2. ❌ Copia quote manualmente
3. ❌ Modifica script
4. ❌ Esegui analisi
5. ❌ Annota risultati CSV
6. ❌ Calcola P/L manualmente

**Tempo: 30+ minuti/settimana**

### Ora (Automatico)
1. ✅ `python3 fase1_automatico.py`
2. ✅ Scegli opzione 4
3. ✅ FATTO!

**Tempo: 10 secondi/settimana** 🚀

---

## 💡 ESEMPI OUTPUT

### SCAN - Identifica Opportunità

```
🤖 SISTEMA FASE1 AUTOMATICO - SCAN PARTITE PROSSIME
================================================================

📡 Fetching partite da The Odds API...
✅ Trovate 10 partite Serie A

📊 Juventus vs Milan
   Data: 2026-01-11
   Quota X media: 3.20 (8 bookmaker)
   Probabilità X: 35.2%
   EV: +42.5%
   Confidenza: 41.0%
   ✅ OPPORTUNITÀ FASE1 VALIDATA!
   💾 Salvata nel tracking automaticamente

📊 Roma vs Lazio
   Data: 2026-01-12
   Quota X media: 2.65
   ❌ Quota fuori range 2.8-3.5

... (continua per tutte le partite)

✅ 2 opportunità salvate automaticamente
💾 Tracking: tracking_fase1_gennaio2026.csv
```

### UPDATE - Aggiorna Risultati

```
🔄 AGGIORNAMENTO AUTOMATICO RISULTATI
================================================================

⏳ 2 trade pending da aggiornare

🔍 Juventus vs Milan (2026-01-11)
   ✅ WIN - Pareggio! Profit: €+105.60

🔍 Roma vs Lazio (2026-01-12)
   ❌ LOSS - H - Loss: €-48.00

✅ 2 risultati aggiornati
```

### REPORT - Performance

```
📊 REPORT PERFORMANCE FASE1
================================================================

📈 METRICHE:
   Trade completati: 15
   Win: 5 | Loss: 10
   Win Rate: 33.3% (target: 31.0%)
   Profit/Loss: €+28.50
   Bankroll: €500.00 → €528.50
   ROI: +5.70% (target: +7.17%)

🚦 DECISIONE:
   ⏳ Continua validazione (15/20 minimi)

📋 Trade pending: 3
```

---

## ⚙️ PERSONALIZZAZIONE

### Cambia Parametri FASE1

Modifica `fase1_automatico.py` linea 30:

```python
FASE1_CONFIG = {
    'quota_min': 2.8,      # Range quote pareggio
    'quota_max': 3.5,
    'ev_min': 0.25,        # 25% EV minimo
    'ev_max': 0.50,        # 50% EV massimo
    'confidenza_min': 0.35,
    'kelly_multiplier': 0.25
}
```

### Cambia Bankroll Iniziale

Linea 48:

```python
BANKROLL_INIZIALE = 500  # Cambia qui
```

---

## 🔍 TROUBLESHOOTING

### "Errore API: 401 Unauthorized"
→ API key mancante o invalida  
→ Verifica `.env` contiene `ODDS_API_KEY`

### "Errore API: 429 Too Many Requests"
→ Quota mensile esaurita (500 req/mese)  
→ Attendi prossimo mese o upgrade piano

### "Nessuna partita trovata"
→ Periodo senza partite Serie A (es. pausa nazionale)  
→ Normale, riprova giorno successivo

### "Errore predizione squadra"
→ Squadra non nel dataset (neopromossa?)  
→ Sistema skippa automaticamente

---

## 🎓 FILOSOFIA AUTOMATICA

> "Il miglior trading system è quello che NON richiede intervento umano"

**Sistema automatico = Zero emozioni = Disciplina perfetta**

- ✅ Segue SEMPRE criteri FASE1
- ✅ NO deviazioni "questa volta è diverso"
- ✅ Tracking perfetto ogni trade
- ✅ Report oggettivi basati su dati

**Tu concentrati su:**
- Analizzare performance
- Decidere quando scalare
- Gestire bankroll

**Sistema pensa al resto!** 🤖

---

## 📅 PROSSIMI STEP

**OGGI:**
1. Test sistema: `python3 fase1_automatico.py`
2. Scegli opzione 4 (AUTO)
3. Verifica output

**QUESTA SETTIMANA:**
1. Sistema identifica opportunità automaticamente
2. Traccia nel CSV
3. Weekend: partite si giocano

**PROSSIMO LUNEDÌ:**
1. Sistema aggiorna risultati automaticamente
2. Genera report
3. Tu decidi: continua/scala/stop

---

**Zero stress. Zero lavoro manuale. Solo risultati.** 🎯
