#!/bin/bash
# Post-Match Update - Esegui DOPO le partite per aggiornare risultati

clear
echo "🔄 AGGIORNAMENTO RISULTATI POST-PARTITE"
echo "========================================"
echo ""
echo "Aggiorno automaticamente i risultati dal dataset..."
echo ""

# Esegui UPDATE automatico
echo "2" | python3 fase1_automatico.py

echo ""
echo "✅ Risultati aggiornati!"
echo ""
echo "📊 Vuoi vedere il report completo? (y/n)"
read -r risposta

if [ "$risposta" = "y" ] || [ "$risposta" = "Y" ]; then
    echo "3" | python3 fase1_automatico.py
fi

echo ""
echo "💾 Tracking salvato in: tracking_fase1_gennaio2026.csv"
