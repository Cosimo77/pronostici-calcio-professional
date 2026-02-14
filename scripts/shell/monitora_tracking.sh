#!/bin/bash
# Script automazione completa tracking FASE 2

PROGETTO_DIR="/Users/cosimomassaro/Desktop/pronostici_calcio"
LOG_DIR="$PROGETTO_DIR/logs"
TRACKING_LOG="$LOG_DIR/tracking_cron.log"

# Crea directory logs se non esiste
mkdir -p "$LOG_DIR"

# Timestamp
echo "======================================" >> "$TRACKING_LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Inizio automazione" >> "$TRACKING_LOG"

cd "$PROGETTO_DIR"

# 1. Genera tracking giornaliero
echo "📊 Generazione tracking..." >> "$TRACKING_LOG"
python3 genera_tracking_fase2.py >> "$TRACKING_LOG" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Tracking generato con successo" >> "$TRACKING_LOG"
else
    echo "❌ Errore generazione tracking" >> "$TRACKING_LOG"
fi

# 2. Aggiorna risultati
echo "🔄 Aggiornamento risultati..." >> "$TRACKING_LOG"
python3 aggiorna_risultati_auto.py >> "$TRACKING_LOG" 2>&1

# 3. Ricalcola P&L
echo "💰 Calcolo P&L..." >> "$TRACKING_LOG"
python3 aggiorna_tracking_fase2.py >> "$TRACKING_LOG" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Fine automazione" >> "$TRACKING_LOG"
echo "" >> "$TRACKING_LOG"
