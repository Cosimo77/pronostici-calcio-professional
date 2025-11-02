# 🤖 Sistema Automazione

Documentazione completa del sistema di automazione per aggiornamenti e training automatici.

## 📋 Panoramica

Il sistema di automazione gestisce autonomamente:

- Aggiornamento dati quotidiano
- Training modelli settimanale
- Backup automatici
- Health check continui
- Pulizia cache periodica

## 🚀 Avvio Daemon

### Comando Base

```bash
python automation_master.py
```

### Con Nohup (Background)

```bash
nohup python automation_master.py > logs/automation.out 2>&1 &
```

### Verifica Stato

```bash
# Script rapido
./stato_automazione.sh

# Manuale
ps aux | grep automation_master
cat logs/automation_status.json
```

## ⚙️ Configurazione

### File Config

`config/automation_config.json`:

```json
{
  "schedule": {
    "daily_update": "06:00",
    "weekly_retrain": "Sunday 02:00",
    "health_check": "hourly",
    "cache_cleanup": "every 3 days"
  },
  "backup": {
    "enabled": true,
    "rotation": 3,
    "location": "backups/"
  },
  "notifications": {
    "on_error": true,
    "on_success": false
  }
}
```

## 📅 Schedulazione

### Operazioni Automatiche

| Operazione | Frequenza | Orario | Durata |
|-----------|-----------|--------|--------|
| Aggiornamento Dati | Quotidiana | 06:00 | ~3 min |
| Training Modelli | Settimanale | Dom 02:00 | ~6 ore |
| Health Check | Oraria | Ogni ora | ~1 sec |
| Backup | Dopo operazioni | Auto | ~2 sec |
| Pulizia Cache | Ogni 3 giorni | Auto | ~1 sec |

### Dettaglio Task

#### Aggiornamento Dati (Daily)

```python
# Eseguito ogni giorno ore 06:00
1. Scarica nuovi dati da football-data.co.uk
2. Aggiorna dataset_pulito.csv
3. Rigenera features (dataset_features.csv)
4. Valida dati aggiornati
5. Crea backup automatico
6. Aggiorna automation_status.json
```

#### Training Modelli (Weekly)

```python
# Eseguito ogni domenica ore 02:00
1. Backup modelli esistenti
2. Ricarica dataset completo
3. GridSearchCV su 3 modelli
4. Salva nuovi modelli ottimizzati
5. Aggiorna metriche performance
6. Commit e push su GitHub
```

## 📊 Monitoring

### Dashboard Web

Accesso: <http://localhost:5008/automation>

Mostra in tempo reale:

- Stato daemon (RUNNING/STOPPED)
- Timestamp ultimo aggiornamento
- Timestamp ultimo training
- Prossime operazioni schedulate
- Info dataset (partite, ultima data)
- Errori recenti

### Logs

```bash
# Log completo daemon
tail -f logs/automation_daemon.log

# Status JSON
cat logs/automation_status.json | jq

# Solo errori
grep ERROR logs/automation_daemon.log
```

### Status File

`logs/automation_status.json`:

```json
{
  "started_at": "2025-11-01T18:15:55",
  "last_daily_update": "2025-11-02T06:00:00",
  "last_weekly_retrain": "2025-11-03T02:00:00",
  "last_backup": "2025-11-02T06:03:00",
  "last_health_check": "2025-11-02T09:00:00",
  "errors": [],
  "running": true
}
```

## 🔧 Gestione Daemon

### Avvio

```bash
# Avvio normale (foreground)
python automation_master.py

# Avvio background
nohup python automation_master.py &

# Con script helper
./start_automation.sh
```

### Stop

```bash
# Trova PID
ps aux | grep automation_master | grep -v grep

# Kill process
kill <PID>

# Force kill se necessario
kill -9 <PID>
```

### Restart

```bash
# Stop
kill $(cat logs/automation_master.pid)

# Start
python automation_master.py
```

## 🐛 Troubleshooting

### Daemon Non Si Avvia

```bash
# Verifica Python path
which python3

# Verifica dipendenze
pip list | grep schedule

# Verifica permessi
ls -la automation_master.py

# Log errori
cat logs/automation_daemon.log | tail -20
```

### Operazioni Non Eseguite

```bash
# Verifica schedule
grep "Job scheduled" logs/automation_daemon.log

# Verifica esecuzioni
grep "INIZIO\|COMPLETATO" logs/automation_daemon.log

# Verifica timestamp
cat logs/automation_status.json
```

### Errori Ricorrenti

```bash
# Lista errori
jq '.errors[]' logs/automation_status.json

# Conta errori per tipo
grep ERROR logs/automation_daemon.log | cut -d: -f4 | sort | uniq -c
```

## 🔄 Backup System

### Posizione Backup

```text
backups/
├── data_backup_YYYYMMDD_HHMMSS/
│   ├── dataset_pulito.csv
│   └── dataset_features.csv
├── backup_YYYYMMDD_HHMMSS.zip
└── (mantiene ultimi 3)
```

### Rotazione Automatica

- Mantiene ultimi **3 backup**
- Elimina automaticamente i più vecchi
- Backup dopo ogni operazione critica

### Ripristino Manuale

```bash
# Lista backup
ls -lt backups/

# Estrai backup
unzip backups/backup_YYYYMMDD_HHMMSS.zip -d restore/

# Copia dati
cp restore/data/dataset_pulito.csv data/
```

## 📈 Performance

### Metriche Sistema

```bash
# CPU usage
ps aux | grep automation_master | awk '{print $3}'

# Memory usage
ps aux | grep automation_master | awk '{print $4}'

# Uptime
ps -p <PID> -o etime=
```

### Ottimizzazioni

- Schedule library: leggero, <1% CPU idle
- Operazioni batch per I/O
- Cache minimizzata (auto-cleanup)
- Logs con rotation automatica

## 🔐 Sicurezza

### Best Practices

- ✅ Daemon con utente non-root
- ✅ Logs protetti (600 permissions)
- ✅ PID file per single-instance
- ✅ Graceful shutdown su SIGTERM

### Health Checks

```python
# Verifica ogni ora
- Dataset esistente e recente
- Modelli caricabili
- Spazio disco sufficiente
- API rispondono
```

## 📝 Manutenzione

### Pulizia Periodica

```bash
# Pulisci logs vecchi (>30 giorni)
find logs/ -name "*.log" -mtime +30 -delete

# Pulisci backup vecchi (automatico)
# Rotazione: mantiene ultimi 3

# Pulisci cache
rm -rf cache/*.json
```

### Aggiornamento Sistema

```bash
# Stop daemon
kill $(cat logs/automation_master.pid)

# Pull updates
git pull origin main

# Reinstalla dipendenze se necessario
pip install -r requirements.txt

# Restart daemon
python automation_master.py
```

## 🎯 FAQ

### Q: Daemon consuma troppa RAM?

A: No, footprint ~8MB idle. Se più alto, verifica memory leak nei logs.

### Q: Posso cambiare orari schedule?

A: Sì, modifica `config/automation_config.json` e restart daemon.

### Q: Operazioni bloccano il sistema?

A: No, training usa tutti i core ma con nice priority bassa.

### Q: Cosa succede se il Mac va in sleep?

A: Operazioni saltate vengono rieseguite al risveglio (catch-up logic).

---

*Documentazione Automazione v1.0 - Aggiornato il 2 Novembre 2025*
