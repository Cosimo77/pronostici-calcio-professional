#!/usr/bin/env python3
"""
Football-Data.co.uk Results Client
Scarica risultati reali partite Serie A per aggiornamento automatico tracking
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# URL CSV Serie A stagione corrente
SERIE_A_URL = "https://www.football-data.co.uk/mmz4281/{season}/I1.csv"


class FootballDataClient:
    """Client per scaricare risultati reali da football-data.co.uk"""
    
    def __init__(self):
        self.base_url = SERIE_A_URL
    
    def _get_season_code(self, date: Optional[datetime] = None) -> str:
        """
        Calcola codice stagione (es. '2526' per 2025-26)
        
        Args:
            date: Data riferimento (default: oggi)
        
        Returns:
            Codice stagione formato '2526'
        """
        if date is None:
            date = datetime.now()
        
        # Stagione cambia a luglio
        year = date.year
        if date.month >= 7:
            season_start = year
        else:
            season_start = year - 1
        
        season_end = season_start + 1
        
        # Formato: '2526' per stagione 2025-26
        return f"{str(season_start)[2:]}{str(season_end)[2:]}"
    
    def get_recent_results(self, days_back: int = 7) -> pd.DataFrame:
        """
        Scarica risultati recenti dall'ultima settimana
        
        Args:
            days_back: Giorni indietro da cercare
        
        Returns:
            DataFrame con risultati partite
        """
        try:
            season = self._get_season_code()
            url = self.base_url.format(season=season)
            
            logger.info(f"📥 Scarico risultati da: {url}")
            
            # Download CSV
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse CSV
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            # Converti date (formato DD/MM/YYYY)
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, format='mixed', errors='coerce')
            
            # Filtra ultimi N giorni
            cutoff = datetime.now() - timedelta(days=days_back)
            df_recent = df[df['Date'] >= cutoff].copy()
            
            # Rimuovi partite future (senza risultato)
            df_recent = df_recent[df_recent['FTHG'].notna() & df_recent['FTAG'].notna()]
            
            logger.info(f"✅ Trovate {len(df_recent)} partite completate negli ultimi {days_back} giorni")
            
            return df_recent
            
        except Exception as e:
            logger.error(f"❌ Errore download risultati: {e}")
            return pd.DataFrame()
    
    def parse_match_result(self, row: pd.Series) -> Dict[str, str]:
        """
        Parse risultato partita in formato tracking
        
        Args:
            row: Riga DataFrame con dati partita
        
        Returns:
            Dict con risultati per diversi mercati
        """
        try:
            home_goals = int(row['FTHG'])  # Full Time Home Goals
            away_goals = int(row['FTAG'])  # Full Time Away Goals
            total_goals = home_goals + away_goals
            
            # 1X2
            if home_goals > away_goals:
                result_1x2 = 'H'
            elif home_goals < away_goals:
                result_1x2 = 'A'
            else:
                result_1x2 = 'D'
            
            # Over/Under 2.5
            result_ou25 = 'Over' if total_goals > 2.5 else 'Under'
            
            # Goal/Goal (entrambe segnano)
            result_gg = 'GG' if (home_goals > 0 and away_goals > 0) else 'NG'
            
            return {
                'data': row['Date'].strftime('%Y-%m-%d'),
                'casa': row['HomeTeam'],
                'ospite': row['AwayTeam'],
                'home_goals': home_goals,
                'away_goals': away_goals,
                '1X2': result_1x2,
                'OU25': result_ou25,
                'GGNG': result_gg,
                'total_goals': total_goals
            }
            
        except Exception as e:
            logger.error(f"❌ Errore parse risultato: {e}")
            return {}
    
    def get_results_for_tracking(self, days_back: int = 7) -> List[Dict]:
        """
        Ottieni risultati formattati per aggiornamento tracking
        
        Args:
            days_back: Giorni indietro da cercare
        
        Returns:
            Lista di dict con risultati
        """
        df = self.get_recent_results(days_back)
        
        if df.empty:
            return []
        
        results = []
        for _, row in df.iterrows():
            parsed = self.parse_match_result(row)
            if parsed:
                results.append(parsed)
        
        return results


# Singleton instance
_client_instance = None


def get_results_client() -> FootballDataClient:
    """Ottieni istanza singleton del client"""
    global _client_instance
    if _client_instance is None:
        _client_instance = FootballDataClient()
    return _client_instance


# Utility function per test rapido
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    client = get_results_client()
    results = client.get_results_for_tracking(days_back=7)
    
    print(f"\n📊 Risultati ultimi 7 giorni: {len(results)} partite\n")
    
    for r in results[:5]:  # Prime 5
        print(f"{r['data']}: {r['casa']} {r['home_goals']}-{r['away_goals']} {r['ospite']}")
        print(f"  1X2: {r['1X2']} | OU2.5: {r['OU25']} | GGNG: {r['GGNG']}\n")
