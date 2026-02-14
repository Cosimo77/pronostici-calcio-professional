#!/bin/bash
# Monitoring rapido partite OGGI (7 gennaio 2026)

clear
echo "⚽ FASE1 - PARTITE DI OGGI (7 Gennaio 2026)"
echo "==========================================="
echo ""

# Partite di oggi dal CSV
grep "2026-01-07" tracking_fase1_gennaio2026.csv | while IFS=',' read -r data giornata casa ospite quota ev conf pred result stake pl bank roi note; do
    echo "📊 $casa vs $ospite"
    echo "   Quota X: $quota"
    echo "   EV: +${ev}%"
    echo "   Stake: €$stake"
    echo "   Risultato: $result"
    echo ""
done

echo "==========================================="
echo "💡 REMINDER:"
echo "   - Partite ore 15:00/18:00/20:45"
echo "   - Dopo le partite: python3 fase1_automatico.py → Opzione 2 (UPDATE)"
echo "   - Aggiorna automaticamente risultati dal dataset"
echo ""
echo "📊 Stake totale oggi: €145.14 (3 partite)"
echo "🎯 ROI target: +7.17% (FASE1 validato)"
echo ""
