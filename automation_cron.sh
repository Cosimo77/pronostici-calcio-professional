#!/bin/bash
# Cron job per automazione giornaliera
# Aggiungi a crontab con: crontab -e
# 
# Esegui ogni giorno alle 06:00
# 0 6 * * * /Users/cosimomassaro/Desktop/pronostici_calcio/automation_cron.sh

cd /Users/cosimomassaro/Desktop/pronostici_calcio

# Attiva ambiente Python (se usi venv)
# source venv/bin/activate

# Esegui automazione
python3 automation_cron.py

# Log risultato
echo "Automazione eseguita: $(date)" >> logs/cron_execution.log
