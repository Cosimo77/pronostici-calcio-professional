#!/bin/bash
# Aggiornamento automatico Render - Cron Script
# Questo script viene eseguito quotidianamente alle 06:00

LOG_FILE="$HOME/Desktop/pronostici_calcio/logs/cron_update.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "================================" >> "$LOG_FILE"
echo "🕐 $(date '+%Y-%m-%d %H:%M:%S') - Avvio aggiornamento automatico" >> "$LOG_FILE"

# Trigger update su Render
RESPONSE=$(curl -s -m 60 -X POST https://pronostici-calcio-professional.onrender.com/api/automation/force_update)

if echo "$RESPONSE" | grep -q '"success":true'; then
    RECORDS=$(echo "$RESPONSE" | grep -o '"records":[0-9]*' | cut -d':' -f2)
    echo "✅ SUCCESS - Dataset ricaricato: $RECORDS partite" >> "$LOG_FILE"
else
    echo "❌ FAILED - Response: $RESPONSE" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
