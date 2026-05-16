# 🔐 Sistema Backup Database Diario Betting

## Overview

Sistema di backup automatico per proteggere i dati del diario betting da perdite accidentali.

## Componenti

### 1. Backup Manuale Integrato (`web/diario_storage.py`)

**Fix implementato**: La funzione `reset_all()` ora crea un backup JSON reale PRIMA di cancellare i dati.

**Comportamento**:
- Prima del DELETE: Export completo in `backups/backup_db_YYYYMMDD_HHMMSS.json`
- Log dettagliato: numero bet backuppate
- Se fallisce export: ERROR e STOP (non cancella)

**Sicurezza**: Impossibile perdere dati con reset accidentale.

---

### 2. Backup Automatico Giornaliero (`scripts/backup_automatico.py`)

**Funzionalità**:
- Export completo database in JSON
- Salvataggio in `backups/daily_backup_YYYYMMDD.json`
- Cleanup automatico backup >30 giorni
- Commit Git opzionale

**Esecuzione Manuale**:
```bash
# Con DATABASE_URL in environment
export DATABASE_URL="postgresql://user:password@host/database"
python3 scripts/backup_automatico.py
```

**Output**:
```
============================================================
🔄 BACKUP AUTOMATICO DATABASE DIARIO
============================================================
📁 Directory backup: /path/to/backups
📊 Bet trovate: 9
✅ Backup salvato: daily_backup_20260516.json (4.9 KB)
ℹ️ Nessun backup da rimuovere (retention: 30 giorni)
============================================================
✅ BACKUP COMPLETATO
============================================================
```

---

## Setup Backup Automatico

### Opzione A: Crontab (Locale)

Esegui backup ogni giorno alle 3:00 AM:

```bash
# Apri crontab editor
crontab -e

# Aggiungi questa linea (modifica path se necessario)
0 3 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && DATABASE_URL="postgresql://user:password@host/database" /usr/bin/python3 scripts/backup_automatico.py >> logs/backup.log 2>&1
```

**Variabili da configurare**:
- Path progetto: `/Users/cosimomassaro/Desktop/pronostici_calcio`
- DATABASE_URL: Connection string Render completo
- Path python3: Usa `which python3` per trovarlo

---

### Opzione B: .env File

Crea/aggiorna `.env` nel root del progetto:

```bash
# .env
DATABASE_URL=postgresql://pronostici_calcio_production_9s31_user:password@dpg-xxx.frankfurt-postgres.render.com/pronostici_calcio_production_9s31
```

Poi nel crontab:

```bash
0 3 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && /usr/bin/python3 scripts/backup_automatico.py >> logs/backup.log 2>&1
```

Script caricherà automaticamente DATABASE_URL da `.env` (se usi python-dotenv).

---

### Opzione C: GitHub Actions (Cloud)

**NON CONSIGLIATO per backup giornalieri** perché:
- Database Render è privato (serve esporre connection string in secrets)
- Costi minuti GitHub Actions
- Meno affidabile di cron locale

---

## Restore da Backup

### 1. Identifica Backup da Ripristinare

```bash
ls -lh backups/daily_backup_*.json
# o
ls -lh backups/backup_db_*.json
```

### 2. Restore con Script Python

```python
import psycopg2
import json

# Carica backup
with open('backups/daily_backup_20260516.json', 'r') as f:
    backup = json.load(f)

# Connetti a database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Import bet
for bet in backup['bets']:
    cur.execute("""
        INSERT INTO bets
        (data, partita, mercato, quota_sistema, quota_sisal,
         ev_modello, ev_realistico, stake, risultato, profit, note,
         created_at, updated_at, group_id, bet_number, tipo_bet)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        bet['data'], bet['partita'], bet['mercato'],
        bet['quota_sistema'], bet['quota_sisal'],
        bet['ev_modello'], bet['ev_realistico'],
        bet['stake'], bet['risultato'], bet['profit'], bet['note'],
        bet['created_at'], bet['updated_at'],
        bet['group_id'], bet['bet_number'], bet['tipo_bet']
    ))

conn.commit()
print(f"✅ {len(backup['bets'])} bet ripristinate")
```

---

## Monitoring

### Check Backup Recenti

```bash
# Lista backup ultimi 7 giorni
find backups/ -name "daily_backup_*.json" -mtime -7 -ls
```

### Verifica Integrità Backup

```bash
# Check JSON valido
python3 -m json.tool backups/daily_backup_20260516.json > /dev/null && echo "✅ Valid JSON"

# Check numero bet
cat backups/daily_backup_20260516.json | jq '.total_bets'
```

### Log Backup Cron

```bash
# Monitora log backup
tail -f logs/backup.log

# Ultimi backup eseguiti
grep "BACKUP COMPLETATO" logs/backup.log | tail -5
```

---

## Best Practices

1. **Test Periodico Restore**: Ogni mese testa restore da backup per verificare integrità
2. **Backup Off-Site**: Copia periodicamente `backups/` su cloud storage (Dropbox, Google Drive)
3. **Monitoring Cron**: Usa servizio tipo healthchecks.io per alertare se backup fallisce
4. **Git Commit**: Abilita commit automatico per versioning backups
5. **Retention**: 30 giorni è un buon compromesso (modifica `days=30` in script se serve)

---

## Troubleshooting

### Errore: "Database non inizializzato"

**Causa**: DATABASE_URL non configurata

**Fix**:
```bash
export DATABASE_URL="postgresql://..."
# o aggiungi a .env
```

### Errore: "Permission denied" su backups/

**Causa**: Directory non scrivibile

**Fix**:
```bash
chmod 755 backups/
```

### Backup Non Schedulato

**Verifica crontab**:
```bash
crontab -l | grep backup_automatico
```

**Check log cron**:
```bash
# macOS
tail -f /var/log/cron.log

# Linux
tail -f /var/log/syslog | grep CRON
```

---

## Statistiche Backup Attuali

- **Fix reset_all()**: ✅ Implementato (16/05/2026)
- **Script automatico**: ✅ Creato e testato
- **Primo backup**: `daily_backup_20260516.json` (9 bet, 4.9 KB)
- **Retention**: 30 giorni
- **Cron**: ⚠️ DA CONFIGURARE MANUALMENTE

---

## Next Steps

1. ✅ Fix bug reset_all() - COMPLETATO
2. ✅ Script backup automatico - COMPLETATO
3. ⚠️ Configurare crontab - MANUALE UTENTE
4. ⚠️ Test restore completo - RACCOMANDATO
