#!/usr/bin/env python3
"""Verifica finale ROI calibrati - Script standalone"""

import json
import sys

# Leggi response API salvata
try:
    with open('/tmp/api_roi_test.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("❌ File /tmp/api_roi_test.json non trovato")
    print("Esegui prima: curl -s 'http://localhost:5008/api/upcoming_matches?force_refresh=1' -o /tmp/api_roi_test.json")
    sys.exit(1)

if 'error' in data:
    print(f"\n❌ ERRORE API: {data['error']}")
    sys.exit(1)

partite = data.get('partite', [])
print(f"\n{'='*70}")
print(f"📊 VERIFICA FINALE ROI CALIBRATI - {len(partite)} partite")
print(f"{'='*70}\n")

if not partite:
    print("⚠️ Nessuna partita disponibile")
    sys.exit(0)

# Cerca opportunità FASE2 (Double Chance + Under)
found_dc = False
found_under = False
total_opps = 0

for i, match in enumerate(partite, 1):
    opps = match.get('opportunita', [])
    total_opps += len(opps)
    
    if not opps:
        continue
    
    casa = match.get('squadra_casa', 'N/A')
    ospite = match.get('squadra_ospite', 'N/A')
    
    for opp in opps:
        mercato = opp.get('mercato', '')
        roi = opp.get('roi_backtest', 0)
        ev = opp.get('ev', 0)
        odds = opp.get('odds', 0)
        note = opp.get('roi_note', '')
        
        # Double Chance verification
        if 'Double' in mercato and not found_dc:
            print(f"🎯 DOUBLE CHANCE TROVATO")
            print(f"   Partita: {casa} vs {ospite}")
            print(f"   Mercato: {mercato}")
            print(f"   Quota: {odds:.2f}")
            print(f"   EV: {ev:+.1f}%")
            print(f"   ROI Backtest: {roi:+.2f}%")
            
            if roi == 21.78:
                print(f"   ✅ CALIBRATO CORRETTAMENTE (+21.78%)\n")
            else:
                print(f"   ⚠️ ERRORE: Atteso +21.78%, trovato {roi:+.2f}%\n")
            
            found_dc = True
        
        # Under 2.5 verification
        if 'Under' in mercato and not found_under:
            print(f"🎯 UNDER 2.5 TROVATO")
            print(f"   Partita: {casa} vs {ospite}")
            print(f"   Mercato: {mercato}")
            print(f"   Quota: {odds:.2f}")
            print(f"   EV: {ev:+.1f}%")
            print(f"   ROI Backtest: {roi:+.2f}%")
            
            if roi == 91.00:
                print(f"   ✅ CALIBRATO CORRETTAMENTE (+91.00%)\n")
            else:
                print(f"   ⚠️ ERRORE: Atteso +91.00%, trovato {roi:+.2f}%\n")
            
            found_under = True
        
        if found_dc and found_under:
            break
    
    if found_dc and found_under:
        break

# Riepilogo
print(f"{'='*70}")
print(f"📈 RIEPILOGO")
print(f"{'='*70}")
print(f"Partite totali analizzate: {len(partite)}")
print(f"Opportunità totali: {total_opps}")
print(f"Double Chance trovato: {'✅' if found_dc else '❌'}")
print(f"Under 2.5 trovato: {'✅' if found_under else '❌'}")

if not found_dc and not found_under:
    print(f"\n⚠️ NOTA: Filtri FASE2 calibrati sono MOLTO SELETTIVI")
    print(f"   - Solo EV 20-25% (sweet spot professionale)")
    print(f"   - OVER 2.5 completamente disabilitato")
    print(f"   - Riduzione trade -95% rispetto a soglia EV 10%")
    print(f"\n💡 Questo è normale: qualità > quantità")
    print(f"   Backtest: 25 trade, ROI +24.55%, WR 64%")

print()
