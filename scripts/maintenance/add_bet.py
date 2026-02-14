#!/usr/bin/env python3
"""
Aggiungi puntata al diario betting professionale
Uso rapido: python3 add_bet.py
"""

import pandas as pd
from datetime import datetime
import os

# Colori per terminale
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
BOLD = '\033[1m'
END = '\033[0m'

def aggiungi_puntata():
    """Aggiunge nuova puntata interattivamente"""
    
    print(f"\n{BOLD}{BLUE}{'='*60}{END}")
    print(f"{BOLD}{BLUE}📝 DIARIO BETTING - Nuova Puntata{END}")
    print(f"{BOLD}{BLUE}{'='*60}{END}\n")
    
    # Input user
    print(f"{YELLOW}Partita (es. 'Parma-Verona'):{END} ", end='')
    partita = input().strip()
    
    print(f"{YELLOW}Mercato (es. '1X', 'X2', '1', 'X', 'Over 2.5', 'Under 2.5'):{END} ", end='')
    mercato = input().strip()
    
    print(f"{YELLOW}Quota Sisal (es. '1.45'):{END} ", end='')
    quota_sisal = float(input().strip())
    
    print(f"{YELLOW}Stake € (es. '2.00'):{END} ", end='')
    stake = float(input().strip())
    
    # Opzionali
    print(f"{YELLOW}Data partita (Invio = oggi, formato DD/MM/YYYY):{END} ", end='')
    data_input = input().strip()
    if data_input:
        data = data_input
    else:
        data = datetime.now().strftime('%d/%m/%Y')
    
    print(f"{YELLOW}Quote sistema (Invio = uguale Sisal):{END} ", end='')
    quota_sistema_input = input().strip()
    quota_sistema = float(quota_sistema_input) if quota_sistema_input else quota_sisal
    
    print(f"{YELLOW}EV Modello % (Invio = skip, es. '23.3'):{END} ", end='')
    ev_modello_input = input().strip()
    ev_modello = f"{ev_modello_input}%" if ev_modello_input else "N/A"
    
    print(f"{YELLOW}EV Realistico % (consigliato, es. '3'):{END} ", end='')
    ev_real_input = input().strip()
    ev_realistico = f"{ev_real_input}%" if ev_real_input else "N/A"
    
    print(f"{YELLOW}Note (opzionale, es. 'Parma casa solida'):{END} ", end='')
    note = input().strip()
    
    # Conferma
    print(f"\n{BOLD}📋 RIEPILOGO PUNTATA:{END}")
    print(f"  Data: {data}")
    print(f"  Partita: {partita}")
    print(f"  Mercato: {mercato}")
    print(f"  Quota Sisal: {quota_sisal}")
    print(f"  Stake: €{stake:.2f}")
    print(f"  EV Modello: {ev_modello}")
    print(f"  EV Realistico: {ev_realistico}")
    if note:
        print(f"  Note: {note}")
    
    print(f"\n{YELLOW}Confermi? (s/n):{END} ", end='')
    conferma = input().strip().lower()
    
    if conferma != 's':
        print(f"{RED}❌ Puntata annullata{END}\n")
        return
    
    # Carica CSV esistente o crea nuovo
    csv_file = 'tracking_giocate.csv'
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        df = pd.DataFrame(columns=[
            'Data', 'Partita', 'Mercato', 'Quota_Sistema', 'Quota_Sisal',
            'EV_Modello', 'EV_Realistico', 'Stake', 'Risultato', 'Profit', 'Note'
        ])
    
    # Aggiungi nuova riga
    nuova_riga = {
        'Data': data,
        'Partita': partita,
        'Mercato': mercato,
        'Quota_Sistema': quota_sistema,
        'Quota_Sisal': quota_sisal,
        'EV_Modello': ev_modello,
        'EV_Realistico': ev_realistico,
        'Stake': f"{stake:.2f}",
        'Risultato': 'PENDING',
        'Profit': '0.00',
        'Note': note
    }
    
    df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
    
    # Salva
    df.to_csv(csv_file, index=False)
    
    print(f"\n{GREEN}✅ Puntata salvata in {csv_file}{END}")
    print(f"{BLUE}💡 Per vedere il diario: python3 betting_journal.py{END}\n")

if __name__ == '__main__':
    try:
        aggiungi_puntata()
    except KeyboardInterrupt:
        print(f"\n{RED}❌ Operazione annullata{END}\n")
    except Exception as e:
        print(f"\n{RED}❌ Errore: {e}{END}\n")
