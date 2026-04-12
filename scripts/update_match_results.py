#!/usr/bin/env python3
"""
Update Match Results - Post-Game
Aggiorna tracking con risultati reali
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.setup_validation_tracking import update_result, generate_performance_report


def main():
    """Update risultati match giocati"""
    
    print("\n🎯 UPDATE MATCH RESULTS\n")
    
    # Match da aggiornare (modifica questo quando hai risultati)
    # Formato: (home, away, risultato)
    # risultato: 'H' = Casa vince, 'D' = Pareggio, 'A' = Trasferta vince
    
    matches_to_update = [
        # Esempio già fatto:
        ('Lecce', 'Atalanta', 'A'),  # 6 Apr - Atalanta vince
        
        # Aggiungi match oggi quando giocati:
        # ('Juventus', 'Genoa', 'H'),     # Se Juve vince
        # ('Napoli', 'AC Milan', 'D'),    # Se pareggio
    ]
    
    for home, away, result in matches_to_update:
        print(f"Aggiornamento: {home} vs {away} → {result}")
        update_result(home, away, result)
    
    print(f"\n{'='*60}")
    print(f"✅ Aggiornamenti completati!")
    
    # Genera report performance
    print(f"\n{'='*60}")
    generate_performance_report()


if __name__ == '__main__':
    main()
