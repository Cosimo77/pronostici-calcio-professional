# 🤖 Sistema di Automazione Autonomo

## 📋 Panoramica

Il sistema è configurato per funzionare in modo **completamente autonomo**, senza necessità di intervento manuale. Tutti gli aggiornamenti dati e allenamenti modelli vengono eseguiti automaticamente secondo una pianificazione predefinita.

## 🚀 Stato Attuale

✅ **Sistema ATTIVO e funzionante**
- Avviato il: **01/11/2025 18:15**
- PID processo: **97698**
- Ultimo aggiornamento: **01/11/2025 18:20**
- Ultimo allenamento: **18/10/2025 10:20**

## 📅 Pianificazione Automatica

Il sistema esegue automaticamente:

| Operazione | Frequenza | Orario | Descrizione |
|------------|-----------|--------|-------------|
| 📡 **Aggiornamento Dati** | Quotidiano | 06:00 | Download nuove partite da football-data.co.uk |
| 🎯 **Allenamento Modelli** | Settimanale | Domenica 02:00 | Ritraining completo di tutti i modelli ML |
| 💚 **Health Check** | Orario | Ogni ora | Verifica stato sistema e servizi |
| 🧹 **Pulizia Cache** | Ogni 3 giorni | Automatico | Rimozione file temporanei obsoleti |

## 🌐 Monitoraggio

### Dashboard Web

Puoi monitorare lo stato del sistema in tempo reale:

- **Locale**: http://localhost:5001/automation
- **Online**: https://pronostici-calcio-professional.onrender.com/automation

La dashboard mostra:
- ✅ Stato sistema (running/stopped)
- 📅 Data e ora ultimo aggiornamento dati
- 🎯 Data e ora ultimo allenamento modelli
- 📊 Statistiche dataset (partite totali, ultima partita)
- 📋 Pianificazione automatica
- 🔄 Auto-refresh ogni 30 secondi

### Terminale

```bash
# Visualizza stato completo
./stato_automazione.sh

# Visualizza log in tempo reale
tail -f logs/automation_daemon.log

# Controlla processo attivo
ps aux | grep automation_master
```

## 🎮 Comandi Principali

### Avvio Sistema

```bash
# Il sistema è GIÀ ATTIVO! Non serve riavviare
# Se dovessi fermarlo e riavviarlo:
./start_automation.sh
```

### Fermare Sistema

```bash
# Solo se necessario (sconsigliato, sistema deve rimanere attivo)
kill $(cat logs/automation_master.pid)
```

### Verifica Stato

```bash
# Stato rapido
./stato_automazione.sh

# Stato JSON
cat logs/automation_status.json
```

## 📊 Informazioni Dataset e Modelli

### Dataset Attuale
- **File**: `data/dataset_pulito.csv`
- **Partite**: 1845
- **Ultima partita**: 2025-10-22
- **Ultimo aggiornamento**: 01/11/2025 18:20

### Modelli Attivi
- **Numero modelli**: 8
- **Tipo**: RandomForest, LightGBM, XGBoost
- **Ultimo training**: 18/10/2025 10:20
- **Prossimo training**: Domenica 03/11/2025 02:00

## 🔄 Come Funziona l'Automazione

1. **Processo Daemon**: `automation_master.py` viene eseguito come processo background
2. **Scheduler**: Utilizza la libreria `schedule` per pianificare i task
3. **Esecuzione Tasks**: Ogni task viene eseguito automaticamente all'orario stabilito
4. **Logging**: Tutte le operazioni vengono registrate in `logs/automation_daemon.log`
5. **Status Tracking**: Lo stato viene salvato in `logs/automation_status.json`

## 🛡️ Persistenza

Il sistema è configurato per:
- ✅ Sopravvivere ai riavvii del terminale (processo daemon)
- ✅ Continuare a funzionare in background
- ✅ Salvare lo stato dopo ogni operazione
- ✅ Riprendere automaticamente in caso di errori minori

**IMPORTANTE**: Il sistema deve rimanere in esecuzione sul server. Su Render, usa i worker/background jobs per la persistenza completa.

## 📈 Prossimi Aggiornamenti Automatici

- **Prossimo aggiornamento dati**: Domani 02/11/2025 alle 06:00
- **Prossimo allenamento**: Domenica 03/11/2025 alle 02:00
- **Prossimo health check**: Ogni ora

## 🔍 Troubleshooting

### Sistema non attivo?

```bash
# Verifica se è in esecuzione
ps aux | grep automation_master

# Se non attivo, riavvia
./start_automation.sh
```

### Timestamp non aggiornati?

```bash
# Verifica log per errori
tail -50 logs/automation_daemon.log

# Forza aggiornamento manuale
python3 aggiornamento_veloce.py
```

### Dashboard non accessibile?

```bash
# Verifica server locale
curl http://localhost:5001/api/automation_status

# Verifica server online
curl https://pronostici-calcio-professional.onrender.com/api/automation_status
```

## 📝 Note Importanti

1. **Non fermare il processo** a meno che non sia strettamente necessario
2. Il sistema si aggiorna **automaticamente** - non serve intervento manuale
3. Tutti i timestamp sono visibili nella dashboard web
4. I log sono salvati in `logs/automation_daemon.log`
5. Lo stato è sempre consultabile in `logs/automation_status.json`

## 🎯 Obiettivo Raggiunto

✅ Sistema completamente autonomo
✅ Aggiornamenti automatici quotidiani
✅ Allenamento automatico settimanale
✅ Monitoraggio in tempo reale
✅ Timestamp visibili ovunque
✅ Zero intervento manuale richiesto

---

**Il sistema è operativo e si occupa di tutto autonomamente!** 🚀
