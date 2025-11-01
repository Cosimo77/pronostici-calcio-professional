#!/bin/bash
# Script per avviare automation_master in background

cd /Users/cosimomassaro/Desktop/pronostici_calcio

# Avvia automation_master in background con log
nohup .venv/bin/python automation_master.py > logs/automation_daemon.log 2>&1 &

# Salva PID
echo $! > logs/automation_master.pid

echo "✅ Automation Master avviato in background"
echo "📋 PID: $(cat logs/automation_master.pid)"
echo "📄 Log: logs/automation_daemon.log"
echo ""
echo "Per fermare: kill $(cat logs/automation_master.pid)"
