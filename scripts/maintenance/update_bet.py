#!/usr/bin/env python3
"""
✅ AGGIORNAMENTO RISULTATI PUNTATE
Aggiorna stato puntate (PENDING → WIN/LOSS) e calcola profit
"""

import pandas as pd
import os

# Colori
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD = '\033[1m'
END = '\033[0m'

def mostra_pending():
    """Mostra puntate in attesa"""
    csv_file = 'tracking_giocate.csv'
    
    if not os.path.exists(csv_file):
        print(f"{RED}❌ File {csv_file} non trovato{END}\n")
        return None
    
    df = pd.read_csv(csv_file)
    pending = df[df['Risultato'] == 'PENDING'].copy()
    
    if len(pending) == 0:
        print(f"{GREEN}✅ Nessuna puntata in attesa!{END}\n")
        return None
    
    print(f"{BOLD}{BLUE}{'='*80}{END}")
    print(f"{BOLD}{BLUE}🎯 PUNTATE DA AGGIORNARE{END}")
    print(f"{BOLD}{BLUE}{'='*80}{END}\n")
    
    for idx, row in pending.iterrows():
        print(f"{YELLOW}[{idx}]{END} {row['Data']} - {row['Partita']}")
        print(f"    Mercato: {BOLD}{row['Mercato']}{END} @ {row['Quota_Sisal']} | Stake: €{row['Stake']}")
        print()
    
    return df

def aggiorna_risultato(df, idx):
    """Aggiorna risultato singola puntata"""
    row = df.loc[idx]
    
    print(f"\n{BOLD}{'='*60}{END}")
    print(f"{BOLD}📝 Aggiornamento: {row['Partita']}{END}")
    print(f"{BOLD}{'='*60}{END}\n")
    print(f"Mercato: {row['Mercato']} @ {row['Quota_Sisal']}")
    print(f"Stake: €{row['Stake']}")
    print()
    
    # Input risultato
    print(f"{BOLD}Risultato:{END}")
    print(f"  1. {GREEN}WIN{END} 🏆")
    print(f"  2. {RED}LOSS{END} ❌")
    print(f"  3. {YELLOW}VOID{END} (puntata annullata)")
    print()
    
    scelta = input(f"{YELLOW}Seleziona (1/2/3):{END} ").strip()
    
    if scelta == '1':
        risultato = 'WIN'
        quota = float(row['Quota_Sisal'])
        stake = float(row['Stake'])
        profit = stake * (quota - 1)
        
        print(f"\n{GREEN}✅ VITTORIA!{END}")
        print(f"   Profit: {GREEN}€{profit:+.2f}{END}")
        
    elif scelta == '2':
        risultato = 'LOSS'
        stake = float(row['Stake'])
        profit = -stake
        
        print(f"\n{RED}❌ Puntata persa{END}")
        print(f"   Profit: {RED}€{profit:+.2f}{END}")
        
    elif scelta == '3':
        risultato = 'VOID'
        profit = 0.0
        
        print(f"\n{YELLOW}⚪ Puntata annullata (stake restituito){END}")
        
    else:
        print(f"{RED}Scelta non valida{END}")
        return df, False
    
    # Conferma
    print(f"\n{BOLD}Riepilogo aggiornamento:{END}")
    print(f"  Risultato: {risultato}")
    print(f"  Profit: €{profit:+.2f}")
    
    conferma = input(f"\n{YELLOW}Confermi aggiornamento? (s/n):{END} ").strip().lower()
    
    if conferma != 's':
        print(f"{YELLOW}❌ Annullato{END}\n")
        return df, False
    
    # Aggiorna DataFrame
    df.at[idx, 'Risultato'] = risultato
    df.at[idx, 'Profit'] = round(profit, 2)
    
    return df, True

def main():
    """Main aggiornamento"""
    print(f"\n{BOLD}{GREEN}{'='*80}{END}")
    print(f"{BOLD}{GREEN}✅ AGGIORNAMENTO RISULTATI PUNTATE{END}")
    print(f"{BOLD}{GREEN}{'='*80}{END}\n")
    
    df = mostra_pending()
    
    if df is None:
        return
    
    while True:
        print(f"{YELLOW}Inserisci numero puntata da aggiornare (o 'q' per uscire):{END} ", end='')
        scelta = input().strip()
        
        if scelta.lower() == 'q':
            break
        
        try:
            idx = int(scelta)
            
            if idx not in df.index:
                print(f"{RED}❌ Indice non valido{END}\n")
                continue
            
            if df.loc[idx, 'Risultato'] != 'PENDING':
                print(f"{RED}❌ Puntata già aggiornata!{END}\n")
                continue
            
            df, success = aggiorna_risultato(df, idx)
            
            if success:
                # Salva
                df.to_csv('tracking_giocate.csv', index=False)
                print(f"\n{GREEN}💾 Risultato salvato!{END}\n")
                
                # Mostra pending aggiornate
                pending_rimaste = df[df['Risultato'] == 'PENDING']
                if len(pending_rimaste) == 0:
                    print(f"{GREEN}🎉 Tutte le puntate aggiornate!{END}")
                    print(f"{CYAN}💡 Visualizza diario: python3 betting_journal.py{END}\n")
                    break
                else:
                    print(f"{YELLOW}➡️  Rimangono {len(pending_rimaste)} puntate da aggiornare{END}\n")
        
        except ValueError:
            print(f"{RED}❌ Input non valido{END}\n")
        except Exception as e:
            print(f"{RED}❌ Errore: {e}{END}\n")
    
    print(f"{BOLD}👋 Ciao!{END}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}👋 Ciao!{END}\n")
