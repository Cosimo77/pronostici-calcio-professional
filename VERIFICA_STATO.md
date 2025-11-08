# 🔍 Verifica Stato Sistema - Guida Rapida

## 📊 Come verificare se il sistema è aggiornato

### **Metodo 1: Script Rapido** ⭐ (Consigliato)
```bash
python3 verifica_stato_rapido.py
```

Output mostra:
- ✅ Età dati (ultima partita)
- 🤖 Accuracy modelli + data ultimo training
- ⚙️ Stato automazione (ultimo update, errori)
- 🏥 Health check sistema

---

### **Metodo 2: Dashboard Web**
```bash
python3 -m web.app_professional
```
Poi apri: `http://localhost:8080/monitoring`

Dashboard mostra:
- 🟢 Status in tempo reale
- 📊 Metriche performance
- 🔮 Test predizioni live
- ⏱️ Auto-refresh ogni 30 secondi

---

### **Metodo 3: File di Log**
```bash
# Health check completo
cat logs/health_check.json | python3 -m json.tool

# Stato automazione
cat logs/automation_status.json | python3 -m json.tool

# Log aggiornamento automatico
tail -20 logs/aggiornamento_auto.log
```

---

### **Metodo 4: Comandi Singoli**
```bash
# Data ultimo aggiornamento dati
ls -lht data/dataset_features.csv

# Data ultimo training modelli
ls -lht models/*.pkl | head -1

# Quante partite nel dataset
wc -l data/dataset_features.csv

# Dimensione file stagione corrente
ls -lh data/I1_2526.csv
```

---

## 🤖 Aggiornamento Automatico

### Script automatico (non-interattivo)
```bash
python3 scripts/aggiorna_quotidiano_auto.py
```

**Cosa fa:**
1. ✅ Controlla se ci sono nuovi dati online
2. ✅ Verifica età dati locali (> 3 giorni = aggiorna)
3. ✅ Previene aggiornamenti troppo frequenti (min 6 ore)
4. ✅ Esegue aggiornamento rapido automatico se necessario
5. ✅ Logging completo in `logs/aggiornamento_auto.log`

**Non richiede input utente** → Perfetto per cron/automation!

---

## 📅 Automazione Master

Il sistema `automation_master.py` esegue automaticamente:
- **Ogni giorno (07:00)**: Aggiornamento dati + features
- **Ogni settimana (Domenica 03:00)**: Re-training modelli
- **Ogni giorno (04:00)**: Backup automatico
- **Ogni 30 minuti**: Health check

Stato automazione:
```bash
cat logs/automation_status.json
```

---

## 🎯 Interpretazione Output

### Dati
- ✅ **FRESH**: < 7 giorni → OK
- ⚠️ **VECCHI**: > 7 giorni → Esegui aggiornamento

### Modelli
- **LogisticRegression**: 56.5% (migliore stabilità)
- **RandomForest**: 51.8% (overfitting rilevato)
- **GradientBoosting**: 45.4% (overfitting rilevato)

### Validazione Reale
- **Accuracy globale**: 47%
- **Vittoria Casa**: 74.4% ⭐⭐⭐
- **Alta confidenza (>50%)**: 71-100% ⭐⭐⭐

---

## 🚨 Se vedi errori

### EOFError in automation_status.json
**Risolto!** ✅ Usa `aggiorna_quotidiano_auto.py` (non-interattivo)

### Dati troppo vecchi
```bash
python3 scripts/aggiorna_quotidiano_auto.py
```

### Modelli non trovati
```bash
python3 riaddestra_modelli_rapido.py
```

### Sistema non risponde
```bash
# Verifica processi
ps aux | grep automation_master

# Restart automazione
pkill -f automation_master
python3 automation_master.py &
```

---

## 📈 Deploy Render

Ogni `git push origin main` triggera automaticamente deploy su Render.

Verifica deploy: https://dashboard.render.com

Log deploy: Vedi "Events" nel dashboard Render

---

## ✅ Checklist Pre-Presentazione

```bash
# 1. Verifica stato
python3 verifica_stato_rapido.py

# 2. Se serve, aggiorna dati
python3 scripts/aggiorna_quotidiano_auto.py

# 3. Test predizione
python3 test_professional_calculator.py

# 4. Start server
python3 -m web.app_professional

# 5. Apri monitoring
open http://localhost:8080/monitoring
```

---

**Tutto OK se:**
- ✅ Dati < 7 giorni
- ✅ Modelli caricati (3/3)
- ✅ Health status: healthy
- ✅ Server risponde su /api/health

**Documenti:** `REPORT_PRESENTAZIONE.md` per metriche complete
