#!/usr/bin/env python3
"""
AGGIORNA RISULTATI AUTOMATICO - Fetch risultati da API e aggiorna tracking
Controlla partite finite e aggiorna automaticamente colonna Risultato nel CSV
"""
import csv
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# API per risultati (football-data.org ha endpoint gratis)
# Alternativa: API-Football o scraping football-data.co.uk
RESULTS_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')  # Opzionale

def fetch_risultati_serie_a():
    """
    Scarica risultati Serie A dalle API o da fallback
    Ritorna dict: {(casa, ospite, data): risultato}
    """
    risultati = {}
    
    # Metodo 1: football-data.org (richiede API key gratuita)
    if RESULTS_API_KEY:
        try:
            url = 'https://api.football-data.org/v4/competitions/SA/matches'
            headers = {'X-Auth-Token': RESULTS_API_KEY}
            params = {
                'status': 'FINISHED',
                'dateFrom': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'dateTo': datetime.now().strftime('%Y-%m-%d')
            }
            
            r = requests.get(url, headers=headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for match in data.get('matches', []):
                    home = match['homeTeam']['name']
                    away = match['awayTeam']['name']
                    date = match['utcDate'][:10]
                    
                    home_score = match['score']['fullTime']['home']
                    away_score = match['score']['fullTime']['away']
                    
                    if home_score is not None and away_score is not None:
                        if home_score > away_score:
                            risultato = 'H'
                        elif away_score > home_score:
                            risultato = 'A'
                        else:
                            risultato = 'D'
                        
                        risultati[(home, away, date)] = {
                            'risultato': risultato,
                            'score': f"{home_score}-{away_score}"
                        }
                
                print(f"✅ Scaricati {len(risultati)} risultati da football-data.org")
                return risultati
        except Exception as e:
            print(f"⚠️  Errore football-data.org: {e}")
    
    # Metodo 2: Fallback - usa dati dal repository
    try:
        import pandas as pd
        csv_path = 'data/I1_2526.csv'
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = df.dropna(subset=['FTR'])  # Solo partite finite
            
            for _, row in df.iterrows():
                if pd.notna(row['FTR']):
                    data = pd.to_datetime(row['Date'], dayfirst=True).strftime('%Y-%m-%d')
                    risultati[(row['HomeTeam'], row['AwayTeam'], data)] = {
                        'risultato': row['FTR'],
                        'score': f"{int(row['FTHG'])}-{int(row['FTAG'])}"
                    }
            
            print(f"✅ Caricati {len(risultati)} risultati dal CSV locale")
            return risultati
    except Exception as e:
        print(f"⚠️  Errore caricamento CSV: {e}")
    
    return risultati

def normalizza_team_name(name):
    """Normalizza nome squadra per matching"""
    mapping = {
        'Inter Milan': 'Inter',
        'AC Milan': 'Milan',
        'AS Roma': 'Roma',
        'Hellas Verona': 'Verona',
        'Atalanta BC': 'Atalanta',
        'FC Como': 'Como',
        'Torino FC': 'Torino'
    }
    return mapping.get(name, name)

def valuta_trade(mercato, esito, risultato_partita, home_score, away_score):
    """
    Determina se trade è WIN/LOSS/VOID basato su mercato e risultato
    
    Args:
        mercato: 1X2, DC, OU25, GG/NG, etc.
        esito: Specifico outcome (es. "1X", "Over 2.5", etc.)
        risultato_partita: H, D, A
        home_score: Gol casa (int o None)
        away_score: Gol ospiti (int o None)
    
    Returns:
        'WIN', 'LOSS', o 'VOID'
    """
    try:
        # 1X2
        if mercato == '1X2':
            mapping = {'1': 'H', 'X': 'D', '2': 'A'}
            if mapping.get(esito) == risultato_partita:
                return 'WIN'
            else:
                return 'LOSS'
        
        # Double Chance
        if mercato == 'DC':
            if esito == '1X':
                return 'WIN' if risultato_partita in ['H', 'D'] else 'LOSS'
            elif esito == 'X2':
                return 'WIN' if risultato_partita in ['D', 'A'] else 'LOSS'
            elif esito == '12':
                return 'WIN' if risultato_partita in ['H', 'A'] else 'LOSS'
        
        # Over/Under 2.5
        if mercato == 'OU25':
            if home_score is not None and away_score is not None:
                total_gol = home_score + away_score
                if esito == 'Over 2.5':
                    return 'WIN' if total_gol > 2 else 'LOSS'
                elif esito == 'Under 2.5':
                    return 'WIN' if total_gol < 3 else 'LOSS'
        
        # GG/NG
        if mercato == 'GG/NG':
            if home_score is not None and away_score is not None:
                gg = home_score > 0 and away_score > 0
                if esito == 'GG':
                    return 'WIN' if gg else 'LOSS'
                elif esito == 'NG':
                    return 'WIN' if not gg else 'LOSS'
        
        # Se non riusciamo a determinare, lascia PENDING
        return 'PENDING'
        
    except Exception as e:
        print(f"⚠️  Errore valutazione trade: {e}")
        return 'PENDING'

def aggiorna_tracking_auto():
    """Aggiorna automaticamente risultati nel tracking CSV"""
    
    tracking_file = 'tracking_fase2_febbraio2026.csv'
    
    if not os.path.exists(tracking_file):
        print(f"❌ File {tracking_file} non trovato!")
        return False
    
    # Scarica risultati
    print("📡 Download risultati Serie A...\n")
    risultati = fetch_risultati_serie_a()
    
    if not risultati:
        print("⚠️  Nessun risultato trovato, aggiornamento manuale richiesto")
        return False
    
    # Leggi tracking
    trades = []
    with open(tracking_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        trades = list(reader)
    
    # Aggiorna risultati
    aggiornati = 0
    for trade in trades:
        if trade.get('Risultato', '').upper() != 'PENDING':
            continue  # Già processato
        
        casa = normalizza_team_name(trade['Casa'])
        ospite = normalizza_team_name(trade['Ospite'])
        data = trade['Data']
        
        # Cerca risultato
        chiave = (casa, ospite, data)
        if chiave in risultati:
            ris = risultati[chiave]
            
            # Estrai score per mercati gol-based
            score_parts = ris['score'].split('-')
            home_score = int(score_parts[0]) if len(score_parts) == 2 else None
            away_score = int(score_parts[1]) if len(score_parts) == 2 else None
            
            # Valuta trade
            mercato = trade['Mercato']
            esito = trade['Esito']
            risultato_trade = valuta_trade(
                mercato, esito, ris['risultato'], 
                home_score, away_score
            )
            
            if risultato_trade in ['WIN', 'LOSS']:
                trade['Risultato'] = risultato_trade
                trade['Note'] = f"Auto-aggiornato {datetime.now().strftime('%Y-%m-%d')} | Score: {ris['score']}"
                aggiornati += 1
                
                print(f"✅ {casa} vs {ospite}: {risultato_trade}")
    
    # Salva CSV aggiornato
    if aggiornati > 0:
        fieldnames = list(trades[0].keys())
        with open(tracking_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(trades)
        
        print(f"\n✅ Aggiornati {aggiornati} trade in {tracking_file}")
        
        # Ricalcola P&L
        print("\n🔄 Ricalcolo P&L...")
        os.system('python aggiorna_tracking_fase2.py')
        
    else:
        print("\n⏳ Nessun trade da aggiornare (tutti pending o già processati)")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 AGGIORNAMENTO AUTOMATICO RISULTATI FASE 2")
    print("=" * 60 + "\n")
    
    aggiorna_tracking_auto()
    
    print("\n" + "=" * 60)
    print("💡 Per automatizzare questo script:")
    print("=" * 60)
    print("# Aggiungi a crontab per esecuzione giornaliera:")
    print("crontab -e")
    print("# Inserisci (esegue ogni giorno alle 23:00):")
    print("0 23 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && python aggiorna_risultati_auto.py")
    print("=" * 60)
