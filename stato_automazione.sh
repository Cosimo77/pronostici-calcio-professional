#!/bin/bash
# 📊 STATO AUTOMAZIONE SISTEMA
# Visualizza lo stato corrente del sistema di automazione

echo "🤖 STATO SISTEMA AUTOMAZIONE"
echo "============================================"
echo ""

# Controlla se l'automazione è attiva
if ps aux | grep -q "[a]utomation_master.py"; then
    echo "✅ Sistema di automazione: ATTIVO"
    PID=$(ps aux | grep "[a]utomation_master.py" | awk '{print $2}')
    echo "   PID: $PID"
else
    echo "❌ Sistema di automazione: NON ATTIVO"
    echo "   Per avviare: ./start_automation.sh"
fi

echo ""
echo "============================================"
echo "📅 TIMESTAMP OPERAZIONI"
echo "============================================"

if [ -f "logs/automation_status.json" ]; then
    # Legge e formatta il file JSON
    STARTED=$(cat logs/automation_status.json | grep "started_at" | cut -d'"' -f4)
    LAST_UPDATE=$(cat logs/automation_status.json | grep "last_daily_update" | cut -d'"' -f4)
    LAST_TRAIN=$(cat logs/automation_status.json | grep "last_weekly_retrain" | cut -d'"' -f4)
    
    echo ""
    echo "🚀 Sistema avviato:"
    if [ "$STARTED" != "null" ] && [ -n "$STARTED" ]; then
        echo "   $STARTED"
    else
        echo "   Mai avviato"
    fi
    
    echo ""
    echo "📡 Ultimo aggiornamento dati:"
    if [ "$LAST_UPDATE" != "null" ] && [ -n "$LAST_UPDATE" ]; then
        echo "   $LAST_UPDATE"
    else
        echo "   Mai eseguito"
    fi
    
    echo ""
    echo "🎯 Ultimo allenamento modelli:"
    if [ "$LAST_TRAIN" != "null" ] && [ -n "$LAST_TRAIN" ]; then
        echo "   $LAST_TRAIN"
    else
        echo "   Mai eseguito"
    fi
else
    echo ""
    echo "⚠️  File stato non trovato"
fi

echo ""
echo "============================================"
echo "📊 DATASET E MODELLI"
echo "============================================"

if [ -f "data/dataset_pulito.csv" ]; then
    LINES=$(wc -l < data/dataset_pulito.csv)
    MATCHES=$((LINES - 1))
    LAST_MATCH=$(tail -1 data/dataset_pulito.csv | cut -d',' -f1)
    DATASET_DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" data/dataset_pulito.csv)
    
    echo ""
    echo "📈 Dataset:"
    echo "   Partite: $MATCHES"
    echo "   Ultima partita: $LAST_MATCH"
    echo "   Aggiornato: $DATASET_DATE"
else
    echo ""
    echo "⚠️  Dataset non trovato"
fi

if [ -d "models/enterprise" ]; then
    MODEL_COUNT=$(ls -1 models/enterprise/*.pkl 2>/dev/null | wc -l)
    if [ $MODEL_COUNT -gt 0 ]; then
        LATEST_MODEL=$(ls -t models/enterprise/*.pkl | head -1)
        MODEL_DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$LATEST_MODEL")
        
        echo ""
        echo "🤖 Modelli:"
        echo "   Numero modelli: $MODEL_COUNT"
        echo "   Ultimo aggiornamento: $MODEL_DATE"
    else
        echo ""
        echo "⚠️  Nessun modello trovato"
    fi
else
    echo ""
    echo "⚠️  Directory modelli non trovata"
fi

echo ""
echo "============================================"
echo "📋 PIANIFICAZIONE AUTOMATICA"
echo "============================================"
echo ""
echo "🔄 Aggiornamento dati:  Ogni giorno alle 06:00"
echo "🎯 Allenamento modelli: Ogni domenica alle 02:00"
echo "💚 Health check:        Ogni ora"
echo "🧹 Pulizia cache:       Ogni 3 giorni"
echo ""
echo "============================================"
echo "🌐 MONITORING WEB"
echo "============================================"
echo ""
echo "📊 Dashboard locale:  http://localhost:5001/automation"
echo "🌍 Dashboard online:  https://pronostici-calcio-professional.onrender.com/automation"
echo ""
echo "============================================"

# Comandi utili
echo ""
echo "💡 COMANDI UTILI:"
echo "   Avvia automazione:  ./start_automation.sh"
echo "   Ferma automazione:  kill \$(cat logs/automation_master.pid)"
echo "   Stato completo:     ./stato_automazione.sh"
echo "   Visualizza log:     tail -f logs/automation_daemon.log"
echo ""
