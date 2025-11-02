# 🤖 Sistema di Aggiornamento Automatico

Questo sistema garantisce che i dati del sistema di pronostici siano sempre aggiornati senza perdere passaggi fondamentali.

## 📋 Script Disponibili

### 1. `aggiorna_tutto.py` - Aggiornamento Completo

```bash
python3 scripts/aggiorna_tutto.py
```

**Cosa fa:**

- ✅ Scarica dati aggiornati stagione corrente
- ✅ Ricrea dataset pulito unificato  
- ✅ Rigenera tutte le features ML
- ✅ Riqualifica tutti i modelli
- ✅ Verifica consistenza finale

**Quando usarlo:** Quando vuoi un aggiornamento completo del sistema.

---

### 2. `aggiorna_quotidiano.py` - Aggiornamento Intelligente

```bash
python3 scripts/aggiorna_quotidiano.py
```

**Cosa fa:**

- 🔍 Controlla se ci sono nuovi dati online
- 📅 Verifica l'età dei dati locali
- 🤔 Propone aggiornamento solo se necessario
- ⚡ Opzione aggiornamento rapido (senza riqualifica modelli)

**Quando usarlo:** Controllo quotidiano manuale.

---

### 3. `aggiorna_automatico.py` - Automazione Completa

```bash
python3 scripts/aggiorna_automatico.py
```

**Cosa fa:**

- 🤖 Esegue automaticamente senza input utente
- 📊 Aggiorna dati e features quando necessario
- 🗓️ Riqualifica modelli solo la domenica sera
- 📝 Salva log dettagliati in `logs/aggiornamento_auto.log`

**Quando usarlo:** Come cron job per automazione completa.

---

## ⚙️ Setup Automazione Completa

### Opzione 1: Cron Job (Raccomandato)

Aggiungi questa riga al crontab per eseguire ogni giorno alle 08:00:

```bash
# Modifica crontab
crontab -e

# Aggiungi questa riga:
0 8 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && /usr/bin/python3 scripts/aggiorna_automatico.py

# Verifica crontab
crontab -l
```

### Opzione 2: Esecuzione Manuale Settimanale

Ogni lunedì mattina:

```bash
python3 scripts/aggiorna_quotidiano.py
```

### Opzione 3: Aggiornamento Prima di Fare Pronostici

Prima di usare l'app web:

```bash
python3 scripts/aggiorna_quotidiano.py
```

---

## 📊 Monitoraggio

### Controllare i Log

```bash
# Ultimi aggiornamenti automatici
tail -f logs/aggiornamento_auto.log

# Log di oggi
grep "$(date '+%Y-%m-%d')" logs/aggiornamento_auto.log
```

### Verificare Stato Dati

```bash
python3 -c "
import pandas as pd
from datetime import datetime

# Controlla features
df = pd.read_csv('data/dataset_features.csv', parse_dates=['Date'])
ultima = df['Date'].max()
giorni = (datetime.now() - ultima).days

print(f'📊 Features: {len(df)} partite')
print(f'🗓️  Ultima partita: {ultima.strftime(\"%d/%m/%Y\")}')
print(f'⏰ {giorni} giorni fa')
"
```

---

## 🛠️ Troubleshooting

### Se l'aggiornamento fallisce

1. **Controlla connessione internet** per download dati
2. **Verifica log** in `logs/aggiornamento_auto.log`
3. **Esegui manualmente** il singolo script che fallisce:

   ```bash
   python3 scripts/aggiorna_stagione_corrente.py
   python3 scripts/analizza_dati.py
   python3 scripts/feature_engineering.py
   python3 scripts/modelli_predittivi.py
   ```

### Se i modelli non si aggiornano

- I modelli vengono riqualificati solo:
  - Con `aggiorna_tutto.py` (sempre)
  - Con `aggiorna_automatico.py` (solo domenica sera)
  - Con `aggiorna_quotidiano.py` (opzione completa)

### Se mancano partite nelle features

- È normale! Le features richiedono almeno 5 partite storiche
- Le partite più recenti appariranno nelle prossime elaborazioni

---

## 📋 Checklist Settimanale

**Lunedì mattina:**

- [ ] Esegui `python3 scripts/aggiorna_quotidiano.py`
- [ ] Verifica che le partite del weekend siano incluse
- [ ] Controlla log per eventuali errori

**Prima di fare pronostici:**

- [ ] Controlla età ultima partita nelle features
- [ ] Se > 3 giorni, esegui aggiornamento
- [ ] Verifica che i modelli siano aggiornati

**Setup iniziale:**

- [ ] Configura cron job per automazione
- [ ] Testa tutti gli script manualmente
- [ ] Controlla che la directory logs/ esista

---

## 🎯 Vantaggi del Sistema

✅ **Nessun dato perso** - Processo sequenziale garantito  
✅ **Aggiornamento intelligente** - Solo quando necessario  
✅ **Logging completo** - Tracciabilità di ogni operazione  
✅ **Automazione completa** - Zero intervento manuale  
✅ **Verifica consistenza** - Controlli automatici  
✅ **Opzioni flessibili** - Rapido vs completo  

Il sistema è ora a prova di errore! 🚀
