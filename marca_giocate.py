#!/usr/bin/env python3
"""
MARCA GIOCATE - Script interattivo per marcare opportunità scommesse
Uso: python3 marca_giocate.py
"""
import csv
import os

def mostra_opportunita():
    """Mostra tutte le opportunità disponibili"""
    with open('tracking_fase2_febbraio2026.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        trades = list(reader)
    
    print("\n" + "="*70)
    print("📊 OPPORTUNITÀ DISPONIBILI")
    print("="*70)
    
    for i, trade in enumerate(trades, 1):
        giocata = trade.get('Giocata', 'NO')
        status_emoji = "✅" if giocata == 'SI' else "⭕"
        risultato = trade.get('Risultato', 'PENDING')
        
        print(f"\n{status_emoji} {i}. {trade['Casa']} vs {trade['Ospite']}")
        print(f"   Mercato: {trade['Mercato']} - {trade['Esito']}")
        print(f"   Quota: {trade['Quota']} | EV: +{trade['EV_%']}% | Stake: €{trade['Stake_Suggerito']}")
        print(f"   Strategia: {trade['Strategia']}")
        print(f"   Giocata: {giocata} | Risultato: {risultato}")
    
    print("\n" + "="*70)
    return trades

def marca_giocate():
    """Marca opportunità come giocate"""
    
    if not os.path.exists('tracking_fase2_febbraio2026.csv'):
        print("❌ File tracking non trovato!")
        return
    
    # Mostra opportunità
    trades = mostra_opportunita()
    
    print("\n💡 Istruzioni:")
    print("   • Inserisci numeri delle opportunità che hai GIOCATO")
    print("   • Esempi: '1' oppure '1,3,5' oppure '1-4' (range)")
    print("   • Premi INVIO senza nulla per vedere solo status")
    print("   • Scrivi 'reset' per marcare TUTTE come NO")
    print("   • Scrivi 'q' per uscire")
    
    scelta = input("\n👉 Quali hai giocato? ").strip()
    
    if scelta.lower() == 'q':
        print("👋 Uscita senza modifiche")
        return
    
    if scelta.lower() == 'reset':
        confirm = input("⚠️  Sicuro di marcare TUTTE come NO? (si/no): ").strip().lower()
        if confirm == 'si':
            for trade in trades:
                trade['Giocata'] = 'NO'
            print("✅ Tutte le opportunità marcate come NO")
        else:
            print("❌ Reset annullato")
            return
    elif scelta:
        # Parse input
        numeri = set()
        
        for parte in scelta.split(','):
            parte = parte.strip()
            if '-' in parte:
                # Range (es. 1-4)
                try:
                    start, end = map(int, parte.split('-'))
                    numeri.update(range(start, end + 1))
                except:
                    print(f"⚠️  Range non valido: {parte}")
            else:
                # Numero singolo
                try:
                    numeri.add(int(parte))
                except:
                    print(f"⚠️  Numero non valido: {parte}")
        
        # Valida numeri
        numeri_validi = [n for n in numeri if 1 <= n <= len(trades)]
        
        if not numeri_validi:
            print("❌ Nessun numero valido inserito")
            return
        
        # Marca come giocate
        for i, trade in enumerate(trades, 1):
            if i in numeri_validi:
                trade['Giocata'] = 'SI'
                print(f"✅ Marcata #{i}: {trade['Casa']}-{trade['Ospite']}")
            else:
                # Mantieni stato precedente se non selezionata
                pass
    
    # Salva modifiche
    with open('tracking_fase2_febbraio2026.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
        writer.writeheader()
        writer.writerows(trades)
    
    # Riepilogo
    giocate = sum(1 for t in trades if t.get('Giocata') == 'SI')
    print("\n" + "="*70)
    print(f"📊 RIEPILOGO: {giocate} opportunità marcate come GIOCATE")
    print("="*70)
    
    if giocate > 0:
        print("\n✅ Ora puoi:")
        print("   1. Piazzare scommesse su bookmaker")
        print("   2. Dopo partite: aggiorna risultati (WIN/LOSS)")
        print("   3. Esegui: python3 aggiorna_tracking_fase2.py")

if __name__ == '__main__':
    try:
        marca_giocate()
    except KeyboardInterrupt:
        print("\n\n👋 Uscita")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
