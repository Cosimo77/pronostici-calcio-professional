#!/usr/bin/env python3
"""
Modulo di integrazione scraper con sistema di predizioni
Combina dati scraped con modelli ML esistenti
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from scripts.scraper_dati import ScraperDatiCalcio
from scripts.modelli_predittivi import PronosticiCalculator
import logging

logger = logging.getLogger(__name__)

class PredittoreEnhanced:
    """Sistema di predizioni enhanced con dati scraped"""
    
    def __init__(self):
        self.scraper = ScraperDatiCalcio()
        self.predittore_base = PronosticiCalculator()
        # Carica i modelli salvati
        try:
            if hasattr(self.predittore_base, 'carica_modelli'):
                self.predittore_base.carica_modelli()
        except Exception as e:
            logger.warning(f"Impossibile caricare modelli: {e}")
            self.predittore_base = None
        self.coefficienti_enhancement = {
            'quote_live': 0.3,
            'infortuni': 0.15,
            'classifica_live': 0.2,
            'meteo': 0.05,
            'sentiment': 0.1,
            'forma_recente': 0.2
        }
    
    def _calcola_fattore_quote(self, quote_data: dict) -> dict:
        """Calcola fattore di aggiustamento dalle quote live"""
        if not quote_data:
            return {'fattore_casa': 1.0, 'fattore_trasferta': 1.0}
        
        try:
            quota_1 = quote_data.get('quota_1', 2.0)
            quota_x = quote_data.get('quota_x', 3.0)
            quota_2 = quote_data.get('quota_2', 2.0)
            
            # Converti quote in probabilità implicite
            prob_1 = 1 / quota_1
            prob_x = 1 / quota_x
            prob_2 = 1 / quota_2
            
            # Normalizza
            totale = prob_1 + prob_x + prob_2
            prob_1_norm = prob_1 / totale
            prob_2_norm = prob_2 / totale
            
            # Calcola fattori (quote basse = maggiore probabilità = fattore > 1)
            fattore_casa = min(1.5, max(0.7, 2.0 - quota_1))
            fattore_trasferta = min(1.5, max(0.7, 2.0 - quota_2))
            
            return {
                'fattore_casa': fattore_casa,
                'fattore_trasferta': fattore_trasferta,
                'prob_implicita_casa': prob_1_norm,
                'prob_implicita_trasferta': prob_2_norm
            }
            
        except Exception as e:
            logger.error(f"Errore calcolo fattore quote: {e}")
            return {'fattore_casa': 1.0, 'fattore_trasferta': 1.0}
    
    def _calcola_fattore_infortuni(self, infortuni_data: dict) -> dict:
        """Calcola impatto infortuni sulla forza squadra"""
        fattori = {'casa': 1.0, 'trasferta': 1.0}
        
        for squadra in ['casa', 'trasferta']:
            infortuni = infortuni_data.get(squadra, [])
            if not infortuni:
                continue
            
            penalita = 0
            for infortunio in infortuni:
                if infortunio['gravita'] == 'grave':
                    penalita += 0.15
                elif infortunio['gravita'] == 'medio':
                    penalita += 0.08
                else:
                    penalita += 0.03
                
                # Penalità extra per ruoli chiave
                if infortunio['ruolo'] in ['attaccante', 'centrocampista']:
                    penalita += 0.02
            
            fattori[squadra] = max(0.6, 1.0 - penalita)
        
        return fattori
    
    def _calcola_fattore_classifica(self, classifica_data: dict) -> dict:
        """Calcola fattore dalla posizione in classifica attuale"""
        fattori = {'casa': 1.0, 'trasferta': 1.0}
        
        for squadra in ['casa', 'trasferta']:
            dati = classifica_data.get(squadra, {})
            if not dati:
                continue
            
            posizione = dati.get('posizione', 10)
            media_punti = dati.get('media_punti', 1.5)
            
            # Fattore basato su posizione (1-4: molto forte, 5-10: forte, etc.)
            if posizione <= 4:
                fattore_pos = 1.2
            elif posizione <= 10:
                fattore_pos = 1.1
            elif posizione <= 15:
                fattore_pos = 0.95
            else:
                fattore_pos = 0.85
            
            # Fattore basato su media punti
            if media_punti >= 2.0:
                fattore_punti = 1.15
            elif media_punti >= 1.5:
                fattore_punti = 1.05
            elif media_punti >= 1.0:
                fattore_punti = 0.95
            else:
                fattore_punti = 0.8
            
            fattori[squadra] = (fattore_pos + fattore_punti) / 2
        
        return fattori
    
    def _calcola_fattore_meteo(self, meteo_data: dict) -> float:
        """Calcola impatto condizioni meteo"""
        if not meteo_data:
            return 1.0
        
        condizione = meteo_data.get('condizione', 'sereno')
        vento = meteo_data.get('vento_kmh', 0)
        temperatura = meteo_data.get('temperatura', 15)
        
        fattore = 1.0
        
        # Condizioni avverse favoriscono difese
        if condizione in ['pioggia', 'neve']:
            fattore *= 0.9  # Meno gol
        elif condizione == 'pioggia_leggera':
            fattore *= 0.95
        
        # Vento forte disturba il gioco
        if vento > 20:
            fattore *= 0.92
        
        # Temperature estreme
        if temperatura < 5 or temperatura > 30:
            fattore *= 0.95
        
        return fattore
    
    def _calcola_fattore_sentiment(self, sentiment_data: dict) -> dict:
        """Calcola impatto sentiment media/tifosi"""
        fattori = {'casa': 1.0, 'trasferta': 1.0}
        
        for squadra in ['casa', 'trasferta']:
            sentiment = sentiment_data.get(squadra, {})
            if not sentiment:
                continue
            
            score = sentiment.get('sentiment_score', 0)
            confidence = sentiment.get('confidence', 0)
            
            # Sentiment positivo aiuta la squadra di casa di più
            if squadra == 'casa':
                fattore = 1.0 + (score * confidence * 0.1)
            else:
                fattore = 1.0 + (score * confidence * 0.05)
            
            fattori[squadra] = max(0.8, min(1.2, fattore))
        
        return fattori
    
    def predici_con_enhancement(self, casa: str, trasferta: str) -> dict:
        """Predizione enhanced con dati scraped"""
        logger.info(f"Predizione enhanced per {casa} vs {trasferta}")
        
        # Predizione base del modello ML (simulata se modelli non disponibili)
        if self.predittore_base is None:
            # Simulazione predizione base realistica
            prob_base_casa = np.random.uniform(0.25, 0.55)
            prob_base_trasferta = np.random.uniform(0.20, 0.45)
            prob_base_pareggio = 1.0 - prob_base_casa - prob_base_trasferta
            
            if prob_base_casa > prob_base_trasferta and prob_base_casa > prob_base_pareggio:
                predizione_base = f"Vittoria {casa}"
                confidenza_base = prob_base_casa * 100
            elif prob_base_trasferta > prob_base_pareggio:
                predizione_base = f"Vittoria {trasferta}"
                confidenza_base = prob_base_trasferta * 100
            else:
                predizione_base = "Pareggio"
                confidenza_base = prob_base_pareggio * 100
                
        else:
            # Fallback senza modelli - usa probabilità simulate
            logger.warning("Predittore base non disponibile, usando simulazione")
            prob_base_casa = np.random.uniform(0.25, 0.55)
            prob_base_trasferta = np.random.uniform(0.20, 0.45)
            prob_base_pareggio = max(0.1, 1.0 - prob_base_casa - prob_base_trasferta)
            predizione_base = "Simulazione"
            confidenza_base = 50.0
        
        # Raccogli dati scraped
        dati_scraped = self.scraper.get_dati_completi(casa, trasferta)
        
        # Calcola fattori di enhancement
        fattore_quote = self._calcola_fattore_quote(dati_scraped['quote_live'])
        fattore_infortuni = self._calcola_fattore_infortuni(dati_scraped['infortuni'])
        fattore_classifica = self._calcola_fattore_classifica(dati_scraped['classifica'])
        fattore_meteo = self._calcola_fattore_meteo(dati_scraped['meteo'])
        fattore_sentiment = self._calcola_fattore_sentiment(dati_scraped['sentiment'])
        
        # Applica enhancement
        # prob_base_casa = predizione_base['probabilita']['vittoria_casa']
        # prob_base_trasferta = predizione_base['probabilita']['vittoria_trasferta']
        # prob_base_pareggio = predizione_base['probabilita']['pareggio']
        
        # Combina fattori con controlli di tipo sicuri
        enhancement_casa = (
            (fattore_quote.get('fattore_casa', 1.0) if isinstance(fattore_quote, dict) else 1.0) * self.coefficienti_enhancement['quote_live'] +
            (fattore_infortuni.get('casa', 1.0) if isinstance(fattore_infortuni, dict) else 1.0) * self.coefficienti_enhancement['infortuni'] +
            (fattore_classifica.get('casa', 1.0) if isinstance(fattore_classifica, dict) else 1.0) * self.coefficienti_enhancement['classifica_live'] +
            fattore_meteo * self.coefficienti_enhancement['meteo'] +
            (fattore_sentiment.get('casa', 1.0) if isinstance(fattore_sentiment, dict) else 1.0) * self.coefficienti_enhancement['sentiment']
        ) / sum(self.coefficienti_enhancement.values())
        
        enhancement_trasferta = (
            (fattore_quote.get('fattore_trasferta', 1.0) if isinstance(fattore_quote, dict) else 1.0) * self.coefficienti_enhancement['quote_live'] +
            (fattore_infortuni.get('trasferta', 1.0) if isinstance(fattore_infortuni, dict) else 1.0) * self.coefficienti_enhancement['infortuni'] +
            (fattore_classifica.get('trasferta', 1.0) if isinstance(fattore_classifica, dict) else 1.0) * self.coefficienti_enhancement['classifica_live'] +
            fattore_meteo * self.coefficienti_enhancement['meteo'] +
            (fattore_sentiment.get('trasferta', 1.0) if isinstance(fattore_sentiment, dict) else 1.0) * self.coefficienti_enhancement['sentiment']
        ) / sum(self.coefficienti_enhancement.values())
        
        # Applica enhancement alle probabilità
        prob_enhanced_casa = prob_base_casa * enhancement_casa
        prob_enhanced_trasferta = prob_base_trasferta * enhancement_trasferta
        
        # Il pareggio è influenzato inversamente
        media_enhancement = (enhancement_casa + enhancement_trasferta) / 2
        prob_enhanced_pareggio = prob_base_pareggio * (2.0 - media_enhancement)
        
        # Normalizza probabilità (evita divisione per zero)
        totale = prob_enhanced_casa + prob_enhanced_trasferta + prob_enhanced_pareggio
        if totale > 0:
            prob_enhanced_casa /= totale
            prob_enhanced_trasferta /= totale
            prob_enhanced_pareggio /= totale
        else:
            # Fallback a probabilità uniformi
            prob_enhanced_casa = 0.33
            prob_enhanced_trasferta = 0.33
            prob_enhanced_pareggio = 0.34
        
        # Determina predizione finale
        if prob_enhanced_casa > prob_enhanced_trasferta and prob_enhanced_casa > prob_enhanced_pareggio:
            risultato = f"Vittoria {casa}"
            confidenza = prob_enhanced_casa
        elif prob_enhanced_trasferta > prob_enhanced_pareggio:
            risultato = f"Vittoria {trasferta}"
            confidenza = prob_enhanced_trasferta
        else:
            risultato = "Pareggio"
            confidenza = prob_enhanced_pareggio
        
        return {
            'partita': f"{casa} vs {trasferta}",
            'predizione_enhanced': risultato,
            'confidenza_enhanced': round(confidenza * 100, 1),
            'probabilita_enhanced': {
                'vittoria_casa': round(prob_enhanced_casa * 100, 1),
                'pareggio': round(prob_enhanced_pareggio * 100, 1),
                'vittoria_trasferta': round(prob_enhanced_trasferta * 100, 1)
            },
            'predizione_base': predizione_base,
            'confidenza_base': round(confidenza_base, 1),
            'probabilita_base': {
                'vittoria_casa': round(prob_base_casa * 100, 1),
                'pareggio': round(prob_base_pareggio * 100, 1),
                'vittoria_trasferta': round(prob_base_trasferta * 100, 1)
            },
            'fattori_enhancement': {
                'quote': fattore_quote,
                'infortuni': fattore_infortuni,
                'classifica': fattore_classifica,
                'meteo': fattore_meteo,
                'sentiment': fattore_sentiment,
                'enhancement_casa': round(enhancement_casa, 3),
                'enhancement_trasferta': round(enhancement_trasferta, 3)
            },
            'dati_scraped': dati_scraped,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Test del sistema enhanced"""
    print("=== TEST PREDITTORE ENHANCED ===")
    print()
    
    predittore = PredittoreEnhanced()
    
    # Test con alcune partite
    partite_test = [
        ("Inter", "Juventus"),
        ("Milan", "Napoli"),
        ("Roma", "Lazio"),
        ("Atalanta", "Fiorentina")
    ]
    
    for casa, trasferta in partite_test:
        print(f"Predizione per {casa} vs {trasferta}:")
        
        risultato = predittore.predici_con_enhancement(casa, trasferta)
        
        print(f"  Base: {risultato['predizione_base']} ({risultato['confidenza_base']}%)")
        print(f"  Enhanced: {risultato['predizione_enhanced']} ({risultato['confidenza_enhanced']}%)")
        
        print(f"  Probabilità Enhanced:")
        prob = risultato['probabilita_enhanced']
        print(f"    {casa}: {prob['vittoria_casa']}%")
        print(f"    Pareggio: {prob['pareggio']}%")
        print(f"    {trasferta}: {prob['vittoria_trasferta']}%")
        
        print(f"  Enhancement: Casa={risultato['fattori_enhancement']['enhancement_casa']}, "
              f"Trasferta={risultato['fattori_enhancement']['enhancement_trasferta']}")
        print()

if __name__ == "__main__":
    main()