#!/bin/bash
# 🤖 SISTEMA FASE1 - AUTOMAZIONE COMPLETA
# Esegue scan + update + report automaticamente

cd /Users/cosimomassaro/Desktop/pronostici_calcio

echo "🤖 FASE1 Automatico - $(date)"
echo "================================"

# Esegui modalità auto (opzione 4)
echo "4" | python3 fase1_automatico.py

echo ""
echo "✅ Completato - $(date)"
