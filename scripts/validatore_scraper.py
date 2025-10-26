#!/usr/bin/env python3
"""
Sistema di Validazione e Verifica Dati Scraper
Verifica correttezza, consistenza e qualità dei dati raccolti
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scraper_dati import ScraperDatiCalcio
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Tuple, Optional, Any
import logging
import time

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidatoreDatiScraper:
    """Sistema completo di validazione dati scraper"""
    
    def __init__(self):
        self.scraper = ScraperDatiCalcio()
        self.errori_validazione = []
        self.warning_validazione = []
        self.metriche_qualita = {}
        
        # Squadre Serie A ufficiali 2025-26 (dal CSV I1_2526.csv)
        self.squadre_serie_a = {
            'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
            'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli',
            'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona'
        }
        
        # Variazioni nomi comuni (Serie A 2025-26)
        self.varianti_nomi = {
            'Milan': ['Milan', 'AC Milan', 'Milano'],
            'Inter': ['Inter', 'Internazionale', 'Inter Milan'],
            'Juventus': ['Juventus', 'Juve', 'Juventus FC'],
            'Napoli': ['Napoli', 'SSC Napoli'],
            'Roma': ['Roma', 'AS Roma'],
            'Lazio': ['Lazio', 'SS Lazio'],
            'Verona': ['Verona', 'Hellas Verona', 'HV'],
            'Como': ['Como', 'Como 1907'],
            'Pisa': ['Pisa', 'Pisa SC']
        }
    
    def _normalizza_nome_squadra(self, nome: str) -> str:
        """Normalizza nome squadra per confronti"""
        nome = nome.strip()
        for ufficiale, varianti in self.varianti_nomi.items():
            if nome in varianti:
                return ufficiale
        return nome
    
    def valida_quote(self, quote_data: Dict) -> Dict[str, Any]:
        """Valida dati quote live"""
        risultato = {'valido': True, 'errori': [], 'warning': [], 'score': 100}
        
        if not quote_data:
            risultato['valido'] = False
            risultato['errori'].append("Nessuna quota trovata")
            risultato['score'] = 0
            return risultato
        
        for partita, dati in quote_data.items():
            # Verifica struttura dati
            campi_richiesti = ['casa', 'trasferta', 'quota_1', 'quota_x', 'quota_2', 'timestamp']
            for campo in campi_richiesti:
                if campo not in dati:
                    risultato['errori'].append(f"Campo mancante '{campo}' in {partita}")
                    risultato['score'] -= 10
            
            # Verifica validità quote
            try:
                q1, qx, q2 = float(dati.get('quota_1', 0)), float(dati.get('quota_x', 0)), float(dati.get('quota_2', 0))
                
                # Range ragionevoli per quote calcio
                if not (1.01 <= q1 <= 50.0):
                    risultato['warning'].append(f"Quota 1 sospetta in {partita}: {q1}")
                    risultato['score'] -= 5
                
                if not (1.8 <= qx <= 10.0):
                    risultato['warning'].append(f"Quota X sospetta in {partita}: {qx}")
                    risultato['score'] -= 5
                
                if not (1.01 <= q2 <= 50.0):
                    risultato['warning'].append(f"Quota 2 sospetta in {partita}: {q2}")
                    risultato['score'] -= 5
                
                # Verifica margine bookmaker (dovrebbe essere ~103-110%)
                prob_implicita = (1/q1 + 1/qx + 1/q2) * 100
                if not (102 <= prob_implicita <= 115):
                    risultato['warning'].append(f"Margine bookmaker anomalo in {partita}: {prob_implicita:.1f}%")
                    risultato['score'] -= 3
                
            except (ValueError, TypeError, ZeroDivisionError) as e:
                risultato['errori'].append(f"Errore quote in {partita}: {e}")
                risultato['score'] -= 15
            
            # Verifica nomi squadre
            casa = self._normalizza_nome_squadra(dati.get('casa', ''))
            trasferta = self._normalizza_nome_squadra(dati.get('trasferta', ''))
            
            if casa not in self.squadre_serie_a and casa:
                risultato['warning'].append(f"Squadra casa non riconosciuta: {casa}")
                risultato['score'] -= 5
            
            if trasferta not in self.squadre_serie_a and trasferta:
                risultato['warning'].append(f"Squadra trasferta non riconosciuta: {trasferta}")
                risultato['score'] -= 5
        
        risultato['score'] = max(0, risultato['score'])
        if risultato['errori']:
            risultato['valido'] = False
        
        return risultato
    
    def valida_classifica(self, classifica_data: Dict) -> Dict[str, Any]:
        """Valida dati classifica"""
        risultato = {'valido': True, 'errori': [], 'warning': [], 'score': 100}
        
        if not classifica_data:
            risultato['valido'] = False
            risultato['errori'].append("Classifica vuota")
            risultato['score'] = 0
            return risultato
        
        posizioni_viste = set()
        
        for squadra, dati in classifica_data.items():
            # Verifica campi
            campi_richiesti = ['posizione', 'partite', 'punti', 'media_punti']
            for campo in campi_richiesti:
                if campo not in dati:
                    risultato['errori'].append(f"Campo mancante '{campo}' per {squadra}")
                    risultato['score'] -= 8
            
            try:
                posizione = int(dati.get('posizione', 0))
                partite = int(dati.get('partite', 0))
                punti = int(dati.get('punti', 0))
                media_punti = float(dati.get('media_punti', 0))
                
                # Verifica range validi
                if not (1 <= posizione <= 20):
                    risultato['errori'].append(f"Posizione non valida per {squadra}: {posizione}")
                    risultato['score'] -= 10
                
                if posizione in posizioni_viste:
                    risultato['errori'].append(f"Posizione duplicata: {posizione}")
                    risultato['score'] -= 15
                posizioni_viste.add(posizione)
                
                if not (0 <= partite <= 38):
                    risultato['warning'].append(f"Numero partite sospetto per {squadra}: {partite}")
                    risultato['score'] -= 5
                
                if not (0 <= punti <= 114):  # Max teorico 38*3
                    risultato['warning'].append(f"Punti sospetti per {squadra}: {punti}")
                    risultato['score'] -= 5
                
                # Verifica coerenza media punti
                if partite > 0:
                    media_calcolata = punti / partite
                    if abs(media_calcolata - media_punti) > 0.1:
                        risultato['warning'].append(f"Media punti incoerente per {squadra}: {media_punti} vs {media_calcolata:.2f}")
                        risultato['score'] -= 3
                
            except (ValueError, TypeError) as e:
                risultato['errori'].append(f"Errore dati numerici per {squadra}: {e}")
                risultato['score'] -= 10
        
        # Verifica che ci siano almeno 18 squadre (Serie A)
        if len(classifica_data) < 18:
            risultato['warning'].append(f"Poche squadre in classifica: {len(classifica_data)}")
            risultato['score'] -= 10
        
        risultato['score'] = max(0, risultato['score'])
        if risultato['errori']:
            risultato['valido'] = False
        
        return risultato
    
    def valida_infortuni(self, infortuni_data: Dict) -> Dict[str, Any]:
        """Valida dati infortuni"""
        risultato = {'valido': True, 'errori': [], 'warning': [], 'score': 100}
        
        if not infortuni_data:
            risultato['warning'].append("Nessun dato infortuni")
            risultato['score'] = 70
            return risultato
        
        ruoli_validi = {'portiere', 'difensore', 'centrocampista', 'attaccante'}
        gravita_valide = {'lieve', 'medio', 'grave'}
        
        for squadra, infortuni in infortuni_data.items():
            if not isinstance(infortuni, list):
                risultato['errori'].append(f"Formato infortuni non valido per {squadra}")
                risultato['score'] -= 15
                continue
            
            # Verifica ragionevolezza numero infortuni (0-8 per squadra)
            if len(infortuni) > 8:
                risultato['warning'].append(f"Troppi infortuni per {squadra}: {len(infortuni)}")
                risultato['score'] -= 5
            
            for i, infortunio in enumerate(infortuni):
                if not isinstance(infortunio, dict):
                    risultato['errori'].append(f"Formato infortunio non valido per {squadra}[{i}]")
                    risultato['score'] -= 10
                    continue
                
                # Verifica campi
                if 'ruolo' in infortunio and infortunio['ruolo'] not in ruoli_validi:
                    risultato['warning'].append(f"Ruolo non valido per {squadra}: {infortunio['ruolo']}")
                    risultato['score'] -= 3
                
                if 'gravita' in infortunio and infortunio['gravita'] not in gravita_valide:
                    risultato['warning'].append(f"Gravità non valida per {squadra}: {infortunio['gravita']}")
                    risultato['score'] -= 3
                
                # Verifica giorni stop
                if 'giorni_stop' in infortunio:
                    giorni = infortunio['giorni_stop']
                    if not isinstance(giorni, (int, float)) or giorni < 0 or giorni > 365:
                        risultato['warning'].append(f"Giorni stop non validi per {squadra}: {giorni}")
                        risultato['score'] -= 3
        
        risultato['score'] = max(0, risultato['score'])
        return risultato
    
    def valida_meteo(self, meteo_data: Dict) -> Dict[str, Any]:
        """Valida dati meteo"""
        risultato = {'valido': True, 'errori': [], 'warning': [], 'score': 100}
        
        if not meteo_data:
            risultato['errori'].append("Dati meteo mancanti")
            risultato['score'] = 0
            risultato['valido'] = False
            return risultato
        
        condizioni_valide = {'sereno', 'nuvoloso', 'pioggia_leggera', 'pioggia', 'neve'}
        
        # Verifica condizione
        condizione = meteo_data.get('condizione')
        if condizione not in condizioni_valide:
            risultato['warning'].append(f"Condizione meteo non standard: {condizione}")
            risultato['score'] -= 10
        
        # Verifica temperatura (range ragionevole per Italia)
        try:
            temp = float(meteo_data.get('temperatura', 0))
            if not (-10 <= temp <= 45):
                risultato['warning'].append(f"Temperatura fuori range: {temp}°C")
                risultato['score'] -= 5
        except (ValueError, TypeError):
            risultato['errori'].append("Temperatura non valida")
            risultato['score'] -= 15
        
        # Verifica vento
        try:
            vento = float(meteo_data.get('vento_kmh', 0))
            if not (0 <= vento <= 200):
                risultato['warning'].append(f"Velocità vento sospetta: {vento} km/h")
                risultato['score'] -= 5
        except (ValueError, TypeError):
            risultato['warning'].append("Velocità vento non valida")
            risultato['score'] -= 10
        
        # Verifica umidità
        try:
            umidita = float(meteo_data.get('umidita', 50))
            if not (0 <= umidita <= 100):
                risultato['warning'].append(f"Umidità fuori range: {umidita}%")
                risultato['score'] -= 5
        except (ValueError, TypeError):
            risultato['warning'].append("Umidità non valida")
            risultato['score'] -= 10
        
        risultato['score'] = max(0, risultato['score'])
        return risultato
    
    def valida_sentiment(self, sentiment_data: Dict) -> Dict[str, Any]:
        """Valida dati sentiment"""
        risultato = {'valido': True, 'errori': [], 'warning': [], 'score': 100}
        
        mood_validi = {'positivo', 'negativo', 'neutro'}
        
        for squadra, dati in sentiment_data.items():
            if not isinstance(dati, dict):
                risultato['errori'].append(f"Formato sentiment non valido per {squadra}")
                risultato['score'] -= 15
                continue
            
            # Verifica sentiment score
            try:
                score = float(dati.get('sentiment_score', 0))
                if not (-1.0 <= score <= 1.0):
                    risultato['warning'].append(f"Sentiment score fuori range per {squadra}: {score}")
                    risultato['score'] -= 5
            except (ValueError, TypeError):
                risultato['errori'].append(f"Sentiment score non valido per {squadra}")
                risultato['score'] -= 10
            
            # Verifica mood
            mood = dati.get('mood')
            if mood and mood not in mood_validi:
                risultato['warning'].append(f"Mood non valido per {squadra}: {mood}")
                risultato['score'] -= 5
            
            # Verifica confidence
            try:
                confidence = float(dati.get('confidence', 0))
                if not (0.0 <= confidence <= 1.0):
                    risultato['warning'].append(f"Confidence fuori range per {squadra}: {confidence}")
                    risultato['score'] -= 5
            except (ValueError, TypeError):
                risultato['warning'].append(f"Confidence non valida per {squadra}")
                risultato['score'] -= 5
        
        risultato['score'] = max(0, risultato['score'])
        return risultato
    
    def test_consistenza_temporale(self, casa: str, trasferta: str, num_test: int = 3) -> Dict:
        """Testa consistenza dati nel tempo"""
        risultato = {'valido': True, 'errori': [], 'warning': [], 'score': 100}
        
        dati_raccolti = []
        
        for i in range(num_test):
            logger.info(f"Test consistenza {i+1}/{num_test}")
            dati = self.scraper.get_dati_completi(casa, trasferta)
            dati_raccolti.append(dati)
            
            if i < num_test - 1:
                time.sleep(2)  # Pausa tra richieste
        
        # Confronta dati meteo (dovrebbero essere simili)
        temperature = [d['meteo'].get('temperatura') for d in dati_raccolti if d['meteo'].get('temperatura')]
        if len(temperature) > 1:
            temp_var = np.std(temperature)
            if temp_var > 5:  # Variazione > 5°C sospetta
                risultato['warning'].append(f"Variazione temperatura eccessiva: {temp_var:.1f}°C")
                risultato['score'] -= 10
        
        # Confronta numero infortuni (dovrebbe essere stabile)
        for squadra in ['casa', 'trasferta']:
            infortuni_counts = [len(d['infortuni'].get(squadra, [])) for d in dati_raccolti]
            if len(set(infortuni_counts)) > 1:
                risultato['warning'].append(f"Numero infortuni {squadra} inconsistente: {infortuni_counts}")
                risultato['score'] -= 5
        
        return risultato
    
    def verifica_fonti_esterne(self) -> Dict:
        """Verifica con fonti esterne quando possibile"""
        risultato = {'valido': True, 'errori': [], 'warning': [], 'score': 100}
        
        try:
            # Test connettività a fonti note
            fonti_test = [
                'https://www.google.com',
                'https://www.espn.com',
                'https://httpbin.org/status/200'
            ]
            
            for fonte in fonti_test:
                try:
                    response = requests.get(fonte, timeout=5)
                    if response.status_code != 200:
                        risultato['warning'].append(f"Fonte {fonte} non raggiungibile: {response.status_code}")
                        risultato['score'] -= 5
                except Exception as e:
                    risultato['warning'].append(f"Errore connessione {fonte}: {str(e)[:50]}")
                    risultato['score'] -= 5
        
        except Exception as e:
            risultato['errori'].append(f"Errore verifica fonti: {e}")
            risultato['score'] -= 20
        
        return risultato
    
    def valida_dati_completi(self, casa: str, trasferta: str) -> Dict:
        """Validazione completa di tutti i dati per una partita"""
        logger.info(f"Validazione completa dati per {casa} vs {trasferta}")
        
        # Raccogli dati
        dati = self.scraper.get_dati_completi(casa, trasferta)
        
        # Valida ogni componente
        risultati_componenti = {
            'quote': self.valida_quote(dati['quote_live']),
            'classifica': self.valida_classifica(dati['classifica']),
            'infortuni': self.valida_infortuni(dati['infortuni']),
            'meteo': self.valida_meteo(dati['meteo']),
            'sentiment': self.valida_sentiment(dati['sentiment'])
        }
        
        # Test aggiuntivi
        risultati_componenti['consistenza'] = self.test_consistenza_temporale(casa, trasferta, 2)
        risultati_componenti['fonti_esterne'] = self.verifica_fonti_esterne()
        
        # Calcola score globale
        score_medio = np.mean([r['score'] for r in risultati_componenti.values()])
        
        # Raccogliere errori e warning
        tutti_errori = []
        tutti_warning = []
        
        for componente, risultato in risultati_componenti.items():
            tutti_errori.extend([f"[{componente}] {e}" for e in risultato['errori']])
            tutti_warning.extend([f"[{componente}] {w}" for w in risultato['warning']])
        
        return {
            'partita': f"{casa} vs {trasferta}",
            'score_globale': round(score_medio, 1),
            'valido': score_medio >= 70,  # Soglia accettabilità
            'qualita': self._classifica_qualita(float(score_medio)),
            'componenti': risultati_componenti,
            'errori_totali': len(tutti_errori),
            'warning_totali': len(tutti_warning),
            'errori': tutti_errori,
            'warning': tutti_warning,
            'timestamp': datetime.now().isoformat(),
            'dati_originali': dati
        }
    
    def _classifica_qualita(self, score: float) -> str:
        """Classifica qualità dati basata su score"""
        if score >= 90:
            return "Eccellente"
        elif score >= 80:
            return "Buona"
        elif score >= 70:
            return "Accettabile"
        elif score >= 50:
            return "Scarsa"
        else:
            return "Inaccettabile"

def main():
    """Test del sistema di validazione"""
    print("🔍 SISTEMA DI VALIDAZIONE DATI SCRAPER")
    print("=" * 50)
    
    validator = ValidatoreDatiScraper()
    
    # Test con diverse partite
    partite_test = [
        ("Inter", "Juventus"),
        ("Milan", "Napoli"),
        ("Roma", "Lazio")
    ]
    
    risultati_validazione = []
    
    for casa, trasferta in partite_test:
        print(f"\n📊 Validazione {casa} vs {trasferta}")
        print("-" * 30)
        
        risultato = validator.valida_dati_completi(casa, trasferta)
        risultati_validazione.append(risultato)
        
        # Mostra risultati
        print(f"Score Globale: {risultato['score_globale']}/100")
        print(f"Qualità: {risultato['qualita']}")
        print(f"Valido: {'✅' if risultato['valido'] else '❌'}")
        print(f"Errori: {risultato['errori_totali']}")
        print(f"Warning: {risultato['warning_totali']}")
        
        # Mostra dettagli componenti
        print("\nDettagli componenti:")
        for comp, res in risultato['componenti'].items():
            status = "✅" if res['valido'] else "❌"
            print(f"  {comp}: {status} ({res['score']}/100)")
        
        # Mostra primi errori/warning
        if risultato['errori']:
            print(f"\nPrimi errori:")
            for err in risultato['errori'][:3]:
                print(f"  ❌ {err}")
        
        if risultato['warning']:
            print(f"\nPrimi warning:")
            for warn in risultato['warning'][:3]:
                print(f"  ⚠️ {warn}")
    
    # Statistiche finali
    print("\n" + "=" * 50)
    print("📈 STATISTICHE VALIDAZIONE")
    print("=" * 50)
    
    scores = [r['score_globale'] for r in risultati_validazione]
    validi = sum(1 for r in risultati_validazione if r['valido'])
    
    print(f"Partite testate: {len(risultati_validazione)}")
    print(f"Partite valide: {validi}/{len(risultati_validazione)}")
    print(f"Score medio: {np.mean(scores):.1f}/100")
    print(f"Score minimo: {min(scores):.1f}/100")
    print(f"Score massimo: {max(scores):.1f}/100")
    
    # Salva risultati
    output_file = 'cache/validazione_scraper.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'statistiche': {
                    'partite_testate': len(risultati_validazione),
                    'partite_valide': validi,
                    'score_medio': float(np.mean(scores)),
                    'score_min': float(min(scores)),
                    'score_max': float(max(scores))
                },
                'risultati': risultati_validazione
            }, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Risultati salvati in: {output_file}")
    except Exception as e:
        print(f"\n❌ Errore salvataggio: {e}")

if __name__ == "__main__":
    main()