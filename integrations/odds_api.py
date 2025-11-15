#!/usr/bin/env python3
"""
Integrazione con The Odds API per quote bookmaker
https://the-odds-api.com/

Free tier: 500 requests/month
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class OddsAPIClient:
    """Client per The Odds API"""
    
    BASE_URL = 'https://api.the-odds-api.com/v4'
    SPORT = 'soccer_italy_serie_a'
    
    # Mapping nomi squadre API → Dataset
    TEAM_NAME_MAPPING = {
        'Inter Milan': 'Inter',
        'AC Milan': 'Milan',
        'Atalanta BC': 'Atalanta',
        'AS Roma': 'Roma',
        'Hellas Verona': 'Verona',
        'Udinese': 'Udinese',
        'Bologna': 'Bologna',
        'Cagliari': 'Cagliari',
        'Genoa': 'Genoa',
        'Fiorentina': 'Fiorentina',
        'Juventus': 'Juventus',
        'Lazio': 'Lazio',
        'Lecce': 'Lecce',
        'Napoli': 'Napoli',
        'Torino': 'Torino',
        'Como': 'Como',
        'Sassuolo': 'Sassuolo',
        'Pisa': 'Pisa',
        'Parma': 'Parma',
        'Cremonese': 'Cremonese'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inizializza client
        
        Args:
            api_key: API key (se None, usa variabile ambiente ODDS_API_KEY)
        """
        self.api_key = api_key or os.getenv('ODDS_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ ODDS_API_KEY non configurata - modalità demo attiva")
            self.demo_mode = True
        else:
            self.demo_mode = False
        
        self.session = requests.Session()
        self.cache = {}
        
    def get_quota_usage(self) -> Dict:
        """Verifica quante richieste rimangono"""
        if self.demo_mode:
            return {'used': 0, 'remaining': 0, 'demo_mode': True}
        
        try:
            response = self.session.get(
                f'{self.BASE_URL}/sports',
                params={'apiKey': self.api_key},
                timeout=10
            )
            
            return {
                'used': response.headers.get('x-requests-used', 0),
                'remaining': response.headers.get('x-requests-remaining', 500),
                'demo_mode': False
            }
        except Exception as e:
            logger.error(f"Errore verifica quota: {e}")
            return {'error': str(e)}
    
    def get_upcoming_odds(self, regions: str = 'eu', markets: str = 'h2h,totals') -> List[Dict]:
        """
        Ottieni quote per partite future Serie A
        
        Args:
            regions: 'eu' (Europa), 'us', 'uk', 'au'
            markets: 'h2h' (1X2), 'totals' (Over/Under) - default entrambi
            
        Returns:
            Lista di match con quote (h2h + totals quando disponibili)
        """
        if self.demo_mode:
            return self._get_demo_odds()
        
        try:
            response = self.session.get(
                f'{self.BASE_URL}/sports/{self.SPORT}/odds',
                params={
                    'apiKey': self.api_key,
                    'regions': regions,
                    'markets': markets,
                    'oddsFormat': 'decimal'
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Scaricate quote per {len(data)} partite")
            logger.info(f"📊 Request rimaste: {response.headers.get('x-requests-remaining', 'N/A')}")
            
            return self._parse_odds_response(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Errore API: {e}")
            return []
    
    def _parse_odds_response(self, data: List[Dict]) -> List[Dict]:
        """Parse risposta API in formato uniforme"""
        parsed = []
        
        for match in data:
            try:
                home_team_raw = match['home_team']
                away_team_raw = match['away_team']
                
                # Normalizza nomi squadre
                home_team = self.TEAM_NAME_MAPPING.get(home_team_raw, home_team_raw)
                away_team = self.TEAM_NAME_MAPPING.get(away_team_raw, away_team_raw)
                
                commence_time = match['commence_time']
                
                # Estrai quote medie tra i bookmaker per h2h
                odds_home = []
                odds_draw = []
                odds_away = []
                
                # Estrai quote Over/Under 2.5 (totals)
                odds_over_25 = []
                odds_under_25 = []
                
                for bookmaker in match.get('bookmakers', []):
                    for market in bookmaker.get('markets', []):
                        # h2h (1X2)
                        if market['key'] == 'h2h':
                            outcomes = market['outcomes']
                            for outcome in outcomes:
                                # Usa home_team_raw per confronto API
                                if outcome['name'] == home_team_raw:
                                    odds_home.append(outcome['price'])
                                elif outcome['name'] == away_team_raw:
                                    odds_away.append(outcome['price'])
                                elif outcome['name'] == 'Draw':
                                    odds_draw.append(outcome['price'])
                        
                        # totals (Over/Under) - SOLO 2.5 esatto
                        elif market['key'] == 'totals':
                            for outcome in market['outcomes']:
                                point = outcome.get('point', 0)
                                # Accetta SOLO 2.5 (non 2.25 o 2.75)
                                if point == 2.5:
                                    if outcome['name'] == 'Over':
                                        odds_over_25.append(outcome['price'])
                                    elif outcome['name'] == 'Under':
                                        odds_under_25.append(outcome['price'])
                
                if odds_home and odds_draw and odds_away:
                    match_data = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'commence_time': commence_time,
                        'odds_home': sum(odds_home) / len(odds_home),
                        'odds_draw': sum(odds_draw) / len(odds_draw),
                        'odds_away': sum(odds_away) / len(odds_away),
                        'num_bookmakers': len(match.get('bookmakers', [])),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Aggiungi Over/Under 2.5 se disponibili
                    if odds_over_25 and odds_under_25:
                        match_data['odds_over_25'] = sum(odds_over_25) / len(odds_over_25)
                        match_data['odds_under_25'] = sum(odds_under_25) / len(odds_under_25)
                        match_data['num_bookmakers_totals'] = len(odds_over_25)
                        print(f"✅ {home_team}: Over 2.5 @ {match_data['odds_over_25']:.2f} ({len(odds_over_25)} books)")
                    else:
                        print(f"⚠️ {home_team}: NO Over/Under 2.5 (over={len(odds_over_25)}, under={len(odds_under_25)})")
                    
                    parsed.append(match_data)
                    
            except Exception as e:
                logger.error(f"Errore parsing match: {e}")
                continue
        
        return parsed
    
    def get_odds_for_match(self, home: str, away: str) -> Optional[Dict]:
        """
        Ottieni quote per una specifica partita
        
        Args:
            home: Squadra casa
            away: Squadra ospite
            
        Returns:
            Dict con quote o None se non trovata
        """
        odds_list = self.get_upcoming_odds()
        
        # Normalizza nomi squadre
        home_norm = home.lower().strip()
        away_norm = away.lower().strip()
        
        for match in odds_list:
            match_home = match['home_team'].lower()
            match_away = match['away_team'].lower()
            
            if home_norm in match_home and away_norm in match_away:
                return match
        
        logger.warning(f"⚠️ Quote non trovate per {home} vs {away}")
        return None
    
    def calculate_implied_probabilities(self, odds: Dict) -> Dict:
        """
        Calcola probabilità implicite dalle quote
        
        Args:
            odds: Dict con odds_home, odds_draw, odds_away
            
        Returns:
            Dict con probabilità percentuali
        """
        prob_home = 1 / odds['odds_home']
        prob_draw = 1 / odds['odds_draw']
        prob_away = 1 / odds['odds_away']
        
        # Margine bookmaker (overround)
        total = prob_home + prob_draw + prob_away
        margin = (total - 1) * 100
        
        # Probabilità normalizzate (rimuovi margine)
        prob_home_norm = prob_home / total
        prob_draw_norm = prob_draw / total
        prob_away_norm = prob_away / total
        
        return {
            'prob_home': prob_home_norm * 100,
            'prob_draw': prob_draw_norm * 100,
            'prob_away': prob_away_norm * 100,
            'bookmaker_margin': margin,
            'total_prob': prob_home_norm + prob_draw_norm + prob_away_norm
        }
    
    def _get_demo_odds(self) -> List[Dict]:
        """Quote demo per testing senza API key"""
        logger.info("🎭 Modalità DEMO - quote simulate")
        
        # Quote realistiche Serie A
        return [
            {
                'home_team': 'Inter',
                'away_team': 'Milan',
                'commence_time': (datetime.now() + timedelta(days=2)).isoformat(),
                'odds_home': 1.85,
                'odds_draw': 3.60,
                'odds_away': 4.20,
                'num_bookmakers': 15,
                'timestamp': datetime.now().isoformat(),
                'demo': True
            },
            {
                'home_team': 'Juventus',
                'away_team': 'Napoli',
                'commence_time': (datetime.now() + timedelta(days=3)).isoformat(),
                'odds_home': 2.10,
                'odds_draw': 3.40,
                'odds_away': 3.50,
                'num_bookmakers': 15,
                'timestamp': datetime.now().isoformat(),
                'demo': True
            }
        ]
    
    def save_odds_to_file(self, odds: List[Dict], filepath: str = 'cache/odds_cache.json'):
        """Salva quote in cache locale"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'odds': odds
                }, f, indent=2)
            logger.info(f"✅ Quote salvate in {filepath}")
        except Exception as e:
            logger.error(f"❌ Errore salvataggio: {e}")
    
    def load_odds_from_file(self, filepath: str = 'cache/odds_cache.json', max_age_hours: int = 6) -> List[Dict]:
        """Carica quote da cache se recenti"""
        try:
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Controlla età cache
            cached_time = datetime.fromisoformat(data['timestamp'])
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                logger.warning(f"⚠️ Cache troppo vecchia ({age_hours:.1f}h)")
                return []
            
            logger.info(f"✅ Caricate {len(data['odds'])} quote da cache ({age_hours:.1f}h fa)")
            return data['odds']
            
        except Exception as e:
            logger.error(f"❌ Errore caricamento cache: {e}")
            return []


# Utility functions
def get_odds_client() -> OddsAPIClient:
    """Factory per creare client odds API"""
    return OddsAPIClient()


def test_odds_api():
    """Test funzionamento API"""
    print("🧪 TEST ODDS API")
    print("=" * 60)
    
    client = OddsAPIClient()
    
    # 1. Verifica quota
    print("\n📊 Quota utilizzo:")
    quota = client.get_quota_usage()
    print(json.dumps(quota, indent=2))
    
    # 2. Scarica quote
    print("\n⚽ Quote partite future:")
    odds = client.get_upcoming_odds()
    
    for match in odds[:3]:  # Mostra prime 3
        print(f"\n{match['home_team']} vs {match['away_team']}")
        print(f"  Quote: {match['odds_home']:.2f} - {match['odds_draw']:.2f} - {match['odds_away']:.2f}")
        print(f"  Bookmaker: {match['num_bookmakers']}")
        
        # Calcola probabilità implicite
        probs = client.calculate_implied_probabilities(match)
        print(f"  Prob: {probs['prob_home']:.1f}% - {probs['prob_draw']:.1f}% - {probs['prob_away']:.1f}%")
        print(f"  Margine bookmaker: {probs['bookmaker_margin']:.2f}%")
    
    # 3. Salva in cache
    if odds:
        client.save_odds_to_file(odds)
        print(f"\n✅ {len(odds)} quote salvate in cache")


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_odds_api()
