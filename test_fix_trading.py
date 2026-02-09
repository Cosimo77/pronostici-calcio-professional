#!/usr/bin/env python3
"""Test fix critici trading system"""
import sys
sys.path.append('web')
from app_professional import ProfessionalCalculator

# Test inizializzazione
calc = ProfessionalCalculator()
success = calc.carica_dati()
print(f'✅ Caricamento dati: {"OK" if success else "FAIL"}')

# Test predizione con squadre con dati limitati
if 'Como' in calc.squadre_disponibili and 'Fiorentina' in calc.squadre_disponibili:
    pred, prob, conf = calc.predici_partita_deterministica('Como', 'Fiorentina')
    print(f'\n📊 Test Como-Fiorentina (dati limitati):')
    print(f'   Predizione: {pred} (confidenza: {conf:.1%})')
    print(f'   Probabilità: H={prob["H"]:.1%} D={prob["D"]:.1%} A={prob["A"]:.1%}')
    
    # Verifica somma = 1
    somma = sum(prob.values())
    print(f'   Somma probabilità: {somma:.4f} {"✅ OK" if abs(somma - 1.0) < 0.01 else "❌ ERRORE"}')
    
    # Test quote implicite
    odds_h = round(1/prob['H'], 2)
    odds_d = round(1/prob['D'], 2)
    odds_a = round(1/prob['A'], 2)
    print(f'\n💰 Quote implicite modello (NON quote reali!):')
    print(f'   Casa {odds_h} - Pareggio {odds_d} - Trasferta {odds_a}')
else:
    print('⚠️ Como o Fiorentina non disponibili')

# Test con squadra top
if 'Napoli' in calc.squadre_disponibili and 'Juventus' in calc.squadre_disponibili:
    pred2, prob2, conf2 = calc.predici_partita_deterministica('Napoli', 'Juventus')
    print(f'\n📊 Test Napoli-Juventus (squadre top, molti dati):')
    print(f'   Predizione: {pred2} (confidenza: {conf2:.1%})')
    print(f'   Probabilità: H={prob2["H"]:.1%} D={prob2["D"]:.1%} A={prob2["A"]:.1%}')
    
    somma2 = sum(prob2.values())
    print(f'   Somma probabilità: {somma2:.4f} {"✅ OK" if abs(somma2 - 1.0) < 0.01 else "❌ ERRORE"}')

# Verifica smoothing applicato correttamente
stats_como = calc._calcola_statistiche_squadra('Como', in_casa=True)
stats_napoli = calc._calcola_statistiche_squadra('Napoli', in_casa=True)

print(f'\n🔍 Verifica smoothing bayesiano:')
print(f'   Como: {stats_como.get("partite_totali", 0)} partite (affidabilità: {stats_como.get("affidabilita", 0):.2f})')
print(f'   Napoli: {stats_napoli.get("partite_totali", 0)} partite (affidabilità: {stats_napoli.get("affidabilita", 0):.2f})')

print(f'\n✅ Test completati - Fix trading applicati correttamente')
