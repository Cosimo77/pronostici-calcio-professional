#!/usr/bin/env python3
"""
Script di migrazione: Importa bet FASE 2 da CSV locale a database PostgreSQL Render
"""

import pandas as pd
import requests
import time
from datetime import datetime

RENDER_URL = "https://pronostici-calcio-professional.onrender.com"
CSV_FILE = "tracking_fase2_febbraio2026.csv"

def convert_date_format(date_str):
    """Converte data da YYYY-MM-DD a DD/MM/YYYY"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except:
        return date_str

def convert_mercato_esito(mercato, esito):
    """Converte mercato + esito nel formato API"""
    if mercato == "Double Chance":
        return esito  # 1X, X2, 12
    elif mercato == "Over/Under 2.5":
        return esito  # Over 2.5, Under 2.5
    elif mercato == "1X2":
        return esito  # Vittoria Casa, Pareggio, Vittoria Ospite
    else:
        return f"{mercato} - {esito}"

def migrate_bets():
    """Migra tutte le bet dal CSV FASE 2 al database Render"""
    
    print("🔄 Migrazione bet FASE 2 → Database PostgreSQL Render\n")
    print(f"📂 Source: {CSV_FILE}")
    print(f"🌐 Target: {RENDER_URL}/api/diario/add\n")
    
    # Leggi CSV
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"✅ Letti {len(df)} record dal CSV\n")
    except FileNotFoundError:
        print(f"❌ File {CSV_FILE} non trovato!")
        return
    
    # Statistiche
    stats = {
        'totali': len(df),
        'importate': 0,
        'duplicate': 0,
        'errori': 0,
        'skipped': 0
    }
    
    # Processa ogni riga
    for idx, row in df.iterrows():
        partita = f"{row['Casa']} vs {row['Ospite']}"
        mercato = convert_mercato_esito(row['Mercato'], row['Esito'])
        
        print(f"[{idx+1}/{len(df)}] {partita} - {mercato}...", end=" ")
        
        # Skip se Giocata=NO e Risultato=PENDING (bet non giocate)
        giocata = str(row.get('Giocata', 'SI')).upper()
        risultato = str(row['Risultato']).upper()
        
        if giocata == 'NO' and risultato == 'PENDING':
            print("⏭️  SKIP (non giocata)")
            stats['skipped'] += 1
            continue
        
        # Prepara payload API
        payload = {
            'data': convert_date_format(row['Data']),
            'partita': partita,
            'mercato': mercato,
            'quota': float(row['Quota']),
            'stake': float(row.get('Stake_Suggerito', 10.0)),
            'ev_modello': f"+{row['EV_%']}%" if row['EV_%'] > 0 else f"{row['EV_%']}%",
            'ev_reale': 'N/A',
            'note': str(row.get('Note', ''))
        }
        
        # POST a Render
        try:
            response = requests.post(
                f"{RENDER_URL}/api/diario/add",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                # Successo
                result = response.json()
                if result.get('success'):
                    print("✅ OK")
                    stats['importate'] += 1
                    
                    # Se bet completata, aggiorna risultato
                    if risultato in ['WIN', 'LOSS']:
                        time.sleep(0.2)  # Rate limit
                        # TODO: Aggiornare bet con risultato e profit
                        # Per ora importiamo solo come PENDING
                else:
                    print(f"⚠️  {result.get('error', 'Unknown')}")
                    stats['errori'] += 1
            
            elif response.status_code == 409:
                # Duplicato
                print("⚠️  DUPLICATO")
                stats['duplicate'] += 1
            
            else:
                print(f"❌ HTTP {response.status_code}")
                stats['errori'] += 1
                
        except requests.exceptions.Timeout:
            print("⏱️  TIMEOUT (server sleeping?)")
            stats['errori'] += 1
            time.sleep(2)  # Wait e retry
            
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            stats['errori'] += 1
        
        # Rate limiting (30 req/min = 1 ogni 2s)
        time.sleep(2.1)
    
    # Report finale
    print("\n" + "="*60)
    print("📊 REPORT MIGRAZIONE")
    print("="*60)
    print(f"Totali nel CSV:    {stats['totali']}")
    print(f"✅ Importate:      {stats['importate']}")
    print(f"⏭️  Skipped (NO):   {stats['skipped']}")
    print(f"⚠️  Duplicate:      {stats['duplicate']}")
    print(f"❌ Errori:         {stats['errori']}")
    print("="*60)
    
    if stats['importate'] > 0:
        print(f"\n🎉 Migrazione completata!")
        print(f"   Vai su {RENDER_URL}/diario per vedere le bet importate")
    else:
        print("\n⚠️  Nessuna bet importata. Controlla i messaggi di errore sopra.")

if __name__ == '__main__':
    migrate_bets()
