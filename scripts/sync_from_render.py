#!/usr/bin/env python3
"""
Sincronizza dati diario da Render database a CSV locale
"""
import os
import requests
import json
import pandas as pd
from datetime import datetime

RENDER_URL = "https://pronostici-calcio-professional.onrender.com"

def sync_betting_data():
    """Scarica tutti i bet da Render e salva in CSV locale"""
    
    print("🔄 Sincronizzazione dati diario da Render...")
    print(f"   Source: {RENDER_URL}/api/diario/completed + /api/diario/pending")
    print()
    
    try:
        # Fetch pending
        response_pending = requests.get(f"{RENDER_URL}/api/diario/pending", timeout=30)
        
        if response_pending.status_code != 200:
            print(f"❌ Errore HTTP {response_pending.status_code} su /pending")
            return False
        
        pending_data = response_pending.json()
        pending_bets = pending_data.get('bets', [])
        
        # Fetch completed
        response_completed = requests.get(f"{RENDER_URL}/api/diario/completed", timeout=30)
        
        if response_completed.status_code != 200:
            print(f"❌ Errore HTTP {response_completed.status_code} su /completed")
            return False
        
        completed_data = response_completed.json()
        completed_bets = completed_data.get('bets', [])
        
        # Merge
        all_bets = pending_bets + completed_bets
        
        if not all_bets:
            print("⚠️  Nessun bet trovato su Render database")
            return False
        
        print(f"✅ Trovati {len(all_bets)} bet sul database Render")
        print(f"   - Pending: {len(pending_bets)}")
        print(f"   - Completed: {len(completed_bets)}")
        print()
        
        # Converti in formato CSV locale
        rows = []
        for event in all_bets:
            rows.append({
                'Data': event.get('data', ''),
                'Partita': event.get('partita', ''),
                'Mercato': event.get('mercato', ''),
                'Quota_Sistema': event.get('quota_sistema', event.get('quota', '')),
                'Quota_Sisal': event.get('quota', ''),
                'EV_Modello': event.get('ev_modello', ''),
                'EV_Realistico': event.get('ev_reale', event.get('ev_realistico', '')),
                'Stake': event.get('stake', ''),
                'Risultato': event.get('risultato', 'PENDING'),
                'Profit': event.get('profit', 0.0),
                'Note': event.get('note', '')
            })
        
        # Salva backup del file esistente
        if os.path.exists('tracking_giocate.csv'):
            backup_file = f'tracking_giocate_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            os.rename('tracking_giocate.csv', backup_file)
            print(f"💾 Backup creato: {backup_file}")
        
        # Salva nuovo CSV
        df = pd.DataFrame(rows)
        df.to_csv('tracking_giocate.csv', index=False, encoding='utf-8')
        
        print(f"✅ Salvati {len(rows)} bet in tracking_giocate.csv")
        print()
        
        # Mostra statistiche
        pending = sum(1 for r in rows if r['Risultato'] == 'PENDING')
        win = sum(1 for r in rows if r['Risultato'] == 'WIN')
        loss = sum(1 for r in rows if r['Risultato'] == 'LOSS')
        
        print("📊 Statistiche:")
        print(f"   - Pending: {pending}")
        print(f"   - Win: {win}")
        print(f"   - Loss: {loss}")
        print(f"   - Total: {len(rows)}")
        
        return True
        
    except requests.Timeout:
        print("❌ Timeout connessione a Render (server spento?)")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == '__main__':
    success = sync_betting_data()
    
    if success:
        print()
        print("🎉 Sincronizzazione completata!")
        print("   I dati sono ora disponibili localmente in tracking_giocate.csv")
    else:
        print()
        print("💡 Suggerimento: Verifica che il server Render sia online")
        print(f"   URL: {RENDER_URL}")
