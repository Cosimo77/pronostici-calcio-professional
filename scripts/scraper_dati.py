#!/usr/bin/env python3
"""
Scraper modulare per raccolta dati calcistici in tempo reale
Supporta multiple fonti e tipi di dati per migliorare le predizioni
"""

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configurazione logging
import os
cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
os.makedirs(cache_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(cache_dir, 'scraper.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScraperDatiCalcio:
    """Scraper modulare per dati calcistici da multiple fonti"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache_timeout = 300  # 5 minuti
        self.dati_cache = {}
        
    def _cache_key(self, fonte: str, tipo: str) -> str:
        """Genera chiave cache"""
        return f"{fonte}_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Recupera dati dalla cache se validi"""
        if key in self.dati_cache:
            timestamp, data = self.dati_cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_timeout:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Salva dati in cache"""
        self.dati_cache[key] = (datetime.now(), data)
    
    def scrape_quote_live(self) -> Dict[str, Dict]:
        """Scrapa quote live da FlashScore"""
        cache_key = self._cache_key('flashscore', 'quote')
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            url = 'https://www.flashscore.it/calcio/italia/serie-a/'
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            partite_quote = {}
            
            # Cerca elementi partite
            partite = soup.find_all('div', class_=re.compile('event__match'))
            
            for partita in partite[:10]:  # Limita a 10 partite
                try:
                    # Estrai nomi squadre
                    squadre = partita.find_all('div', class_=re.compile('event__participant'))
                    if len(squadre) >= 2:
                        casa = squadre[0].get_text(strip=True)
                        trasferta = squadre[1].get_text(strip=True)
                        
                        # Cerca quote se disponibili
                        quote_elem = partita.find_all('span', class_=re.compile('odd'))
                        quote = []
                        for q in quote_elem:
                            try:
                                quote.append(float(q.get_text(strip=True)))
                            except:
                                continue
                        
                        if len(quote) >= 3:
                            partite_quote[f"{casa} vs {trasferta}"] = {
                                'casa': casa,
                                'trasferta': trasferta,
                                'quota_1': quote[0],
                                'quota_x': quote[1],
                                'quota_2': quote[2],
                                'timestamp': datetime.now().isoformat()
                            }
                
                except Exception as e:
                    logger.debug(f"Errore parsing partita: {e}")
                    continue
            
            self._set_cache(cache_key, partite_quote)
            logger.info(f"Quote scraped: {len(partite_quote)} partite")
            return partite_quote
            
        except Exception as e:
            logger.error(f"Errore scraping quote: {e}")
            return {}
    
    def scrape_classifica_live(self) -> Dict[str, Dict]:
        """Scrapa classifica aggiornata da ESPN"""
        cache_key = self._cache_key('espn', 'classifica')
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            url = 'https://www.espn.com/soccer/table/_/league/ita.1'
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            classifica = {}
            
            # Cerca tabella classifica
            tabella = soup.find('table', class_=re.compile('Table'))
            if tabella:
                righe = tabella.find_all('tr')[1:]  # Salta header
                
                for i, riga in enumerate(righe):
                    celle = riga.find_all('td')
                    if len(celle) >= 8:
                        try:
                            squadra = celle[1].get_text(strip=True)
                            partite = int(celle[2].get_text(strip=True))
                            punti = int(celle[8].get_text(strip=True))
                            
                            classifica[squadra] = {
                                'posizione': i + 1,
                                'partite': partite,
                                'punti': punti,
                                'media_punti': round(punti / max(partite, 1), 2),
                                'timestamp': datetime.now().isoformat()
                            }
                        except:
                            continue
            
            self._set_cache(cache_key, classifica)
            logger.info(f"Classifica scraped: {len(classifica)} squadre")
            return classifica
            
        except Exception as e:
            logger.error(f"Errore scraping classifica: {e}")
            return {}
    
    def scrape_infortuni(self) -> Dict[str, List]:
        """Scrapa informazioni infortuni (simulato per ora)"""
        cache_key = self._cache_key('infortuni', 'status')
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        # Squadre Serie A 2025-26 (dal CSV ufficiale I1_2526.csv)
        squadre_serie_a = [
            'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
            'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli',
            'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona'
        ]
        
        infortuni = {}
        for squadra in squadre_serie_a:
            # Simula 0-3 infortuni per squadra
            num_infortuni = np.random.poisson(1.2)
            infortuni_squadra = []
            
            for i in range(num_infortuni):
                gravita = np.random.choice(['lieve', 'medio', 'grave'], p=[0.5, 0.3, 0.2])
                infortuni_squadra.append({
                    'giocatore': f'Giocatore_{i+1}',
                    'ruolo': np.random.choice(['portiere', 'difensore', 'centrocampista', 'attaccante']),
                    'gravita': gravita,
                    'giorni_stop': np.random.randint(1, 30 if gravita != 'grave' else 90)
                })
            
            infortuni[squadra] = infortuni_squadra
        
        self._set_cache(cache_key, infortuni)
        logger.info(f"Infortuni simulati per {len(squadre_serie_a)} squadre")
        return infortuni
    
    def scrape_meteo(self, citta: str) -> Dict:
        """Scrapa condizioni meteo per una città"""
        cache_key = self._cache_key(f'meteo_{citta}', 'condizioni')
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            # Simula dati meteo realistici per ora
            condizioni = ['sereno', 'nuvoloso', 'pioggia_leggera', 'pioggia', 'neve']
            meteo = {
                'citta': citta,
                'condizione': np.random.choice(condizioni, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
                'temperatura': np.random.randint(5, 25),
                'vento_kmh': np.random.randint(0, 30),
                'umidita': np.random.randint(40, 90),
                'timestamp': datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, meteo)
            return meteo
            
        except Exception as e:
            logger.error(f"Errore scraping meteo: {e}")
            return {}
    
    def scrape_statistiche_live(self, partita_id: str) -> Dict:
        """Scrapa statistiche live di una partita"""
        # Per ora simula statistiche realistiche
        stats = {
            'possesso_casa': np.random.randint(35, 65),
            'tiri_casa': np.random.randint(8, 20),
            'tiri_porta_casa': np.random.randint(2, 8),
            'corner_casa': np.random.randint(2, 10),
            'falli_casa': np.random.randint(8, 18),
            'cartellini_gialli_casa': np.random.randint(0, 4),
            'possesso_trasferta': 0,  # Calcolato dopo
            'tiri_trasferta': np.random.randint(8, 20),
            'tiri_porta_trasferta': np.random.randint(2, 8),
            'corner_trasferta': np.random.randint(2, 10),
            'falli_trasferta': np.random.randint(8, 18),
            'cartellini_gialli_trasferta': np.random.randint(0, 4),
            'timestamp': datetime.now().isoformat()
        }
        
        stats['possesso_trasferta'] = 100 - stats['possesso_casa']
        return stats
    
    def analizza_sentiment_media(self, squadra: str) -> Dict:
        """Analizza sentiment dai media (simulato)"""
        sentiment_score = np.random.uniform(-1, 1)  # -1 negativo, +1 positivo
        
        return {
            'squadra': squadra,
            'sentiment_score': round(sentiment_score, 2),
            'mood': 'positivo' if sentiment_score > 0.2 else 'negativo' if sentiment_score < -0.2 else 'neutro',
            'confidence': round(abs(sentiment_score), 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_dati_completi(self, casa: str, trasferta: str) -> Dict:
        """Raccoglie tutti i dati disponibili per una partita"""
        logger.info(f"Raccolta dati completi per {casa} vs {trasferta}")
        
        dati = {
            'partita': f"{casa} vs {trasferta}",
            'timestamp': datetime.now().isoformat(),
            'quote_live': {},
            'classifica': {},
            'infortuni': {},
            'meteo': {},
            'sentiment': {},
            'statistiche_pre': {}
        }
        
        try:
            # Quote live
            quote = self.scrape_quote_live()
            chiave_partita = f"{casa} vs {trasferta}"
            if chiave_partita in quote:
                dati['quote_live'] = quote[chiave_partita]
            
            # Classifica
            classifica = self.scrape_classifica_live()
            if casa in classifica:
                dati['classifica']['casa'] = classifica[casa]
            if trasferta in classifica:
                dati['classifica']['trasferta'] = classifica[trasferta]
            
            # Infortuni
            infortuni = self.scrape_infortuni()
            if casa in infortuni:
                dati['infortuni']['casa'] = infortuni[casa]
            if trasferta in infortuni:
                dati['infortuni']['trasferta'] = infortuni[trasferta]
            
            # Meteo (assume Milano per default)
            dati['meteo'] = self.scrape_meteo('Milano')
            
            # Sentiment
            dati['sentiment']['casa'] = self.analizza_sentiment_media(casa)
            dati['sentiment']['trasferta'] = self.analizza_sentiment_media(trasferta)
            
            logger.info("Raccolta dati completata con successo")
            return dati
            
        except Exception as e:
            logger.error(f"Errore raccolta dati: {e}")
            return dati
    
    def salva_dati_cache(self, filepath: str = 'cache/dati_scraped.json'):
        """Salva tutti i dati in cache su file"""
        try:
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            dati_serializzabili = {}
            for key, (timestamp, data) in self.dati_cache.items():
                dati_serializzabili[key] = {
                    'timestamp': timestamp.isoformat(),
                    'data': data
                }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dati_serializzabili, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Cache salvata in {filepath}")
            
        except Exception as e:
            logger.error(f"Errore salvataggio cache: {e}")

def main():
    """Test delle funzionalità dello scraper"""
    scraper = ScraperDatiCalcio()
    
    print("=== TEST SCRAPER DATI CALCIO ===")
    print()
    
    # Test quote live
    print("1. Test Quote Live:")
    quote = scraper.scrape_quote_live()
    for partita, dati in list(quote.items())[:3]:
        print(f"   {partita}: 1={dati.get('quota_1', 'N/A')} X={dati.get('quota_x', 'N/A')} 2={dati.get('quota_2', 'N/A')}")
    print()
    
    # Test classifica
    print("2. Test Classifica:")
    classifica = scraper.scrape_classifica_live()
    for squadra, dati in list(classifica.items())[:5]:
        print(f"   {dati['posizione']}. {squadra}: {dati['punti']} pt ({dati['media_punti']}/partita)")
    print()
    
    # Test dati completi
    print("3. Test Dati Completi Inter vs Juventus:")
    dati_completi = scraper.get_dati_completi('Inter', 'Juventus')
    print(f"   Quote: {dati_completi['quote_live']}")
    print(f"   Classifica Casa: {dati_completi['classifica'].get('casa', 'N/A')}")
    print(f"   Infortuni Casa: {len(dati_completi['infortuni'].get('casa', []))} giocatori")
    print(f"   Meteo: {dati_completi['meteo'].get('condizione', 'N/A')}")
    print()
    
    # Salva cache
    scraper.salva_dati_cache()
    print("4. Cache salvata in cache/dati_scraped.json")

if __name__ == "__main__":
    main()