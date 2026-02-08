#!/usr/bin/env python3
"""Verifica partite Serie A disponibili oggi"""
import os
import sys
from dotenv import load_dotenv
import requests

# Carica API key (file .env in root progetto)
load_dotenv('.env')
api_key = os.getenv('ODDS_API_KEY')

if not api_key:
    print('❌ API Key non configurata in web/.env')
    sys.exit(1)

# Chiama The Odds API per Serie A
url = f'https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/'
params = {
    'apiKey': api_key,
    'regions': 'eu',
    'markets': 'h2h,spreads,totals',
    'oddsFormat': 'decimal'
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    print('📅 Data: 8 febbraio 2026')
    print(f'🔍 Partite disponibili (prossime 48h): {len(data)}')
    print('=' * 80)
    
    if len(data) == 0:
        print('\n❌ Nessuna partita Serie A nelle prossime 48 ore')
        print('   (Possibile pausa campionato, coppa, o infrasettimanale già giocato)')
    else:
        print('\n🏟️  PARTITE CON QUOTE DISPONIBILI:\n')
        for i, match in enumerate(data, 1):
            print(f'{i}. {match["home_team"]} vs {match["away_team"]}')
            print(f'   📅 Inizio: {match["commence_time"]}')
            if match.get('bookmakers'):
                print(f'   💰 Bookmaker: {len(match["bookmakers"])}')
            print()
    
    print(f'⚠️  Quota API rimanente: {response.headers.get("x-requests-remaining", "N/A")}/500')
    
except Exception as e:
    print(f'❌ Errore chiamata API: {e}')
    sys.exit(1)
