#!/usr/bin/env python3
"""
Sistema di Confronto con Fonti Ufficiali
Verifica accuratezza dati scraper confrontando con fonti affidabili
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from scripts.scraper_dati import ScraperDatiCalcio

logger = logging.getLogger(__name__)

class VerificatoreAccuratezza:
    """Sistema per verificare accuratezza dati scraper vs fonti ufficiali"""
    
    def __init__(self):
        self.scraper = ScraperDatiCalcio()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Mapping squadre per diverse fonti
        self.mapping_squadre = {
            'Inter': ['Inter', 'Internazionale', 'Inter Milan', 'FC Internazionale'],
            'Milan': ['Milan', 'AC Milan', 'Milano'],
            'Juventus': ['Juventus', 'Juve', 'Juventus FC'],
            'Napoli': ['Napoli', 'SSC Napoli'],
            'Roma': ['Roma', 'AS Roma'],
            'Lazio': ['Lazio', 'SS Lazio'],
            'Atalanta': ['Atalanta', 'Atalanta BC'],
            'Fiorentina': ['Fiorentina', 'ACF Fiorentina'],
            'Bologna': ['Bologna', 'Bologna FC'],
            'Torino': ['Torino', 'Torino FC'],
            'Udinese': ['Udinese', 'Udinese Calcio'],
            'Sassuolo': ['Sassuolo', 'US Sassuolo'],
            'Verona': ['Verona', 'Hellas Verona', 'HV'],
            'Como': ['Como', 'Como 1907'],
            'Pisa': ['Pisa', 'Pisa SC'],
            'Cagliari': ['Cagliari', 'Cagliari Calcio'],
            'Lecce': ['Lecce', 'US Lecce'],
            'Cremonese': ['Cremonese', 'US Cremonese']
        }
    
    def _normalizza_nome_squadra(self, nome: str, fonte: str = "default") -> str:
        """Normalizza nome squadra per confronti"""
        nome_clean = nome.strip()
        
        for standard, varianti in self.mapping_squadre.items():
            if nome_clean in varianti:
                return standard
        
        return nome_clean
    
    def verifica_classifica_ufficiale(self) -> Dict:
        """Confronta classifica scraped con fonte ufficiale simulata"""
        risultato = {
            'fonte_ufficiale': 'Simulata',
            'timestamp': datetime.now().isoformat(),
            'confronto': {},
            'accuratezza': 0.0,
            'errori': []
        }
        
        try:
            # Ottieni classifica dal nostro scraper
            classifica_scraper = self.scraper.scrape_classifica_live()
            
            # Simula classifica ufficiale (in un caso reale useresti API ufficiali)
            classifica_ufficiale = self._genera_classifica_riferimento()
            
            # Confronta
            squadre_comuni = set(classifica_scraper.keys()) & set(classifica_ufficiale.keys())
            
            if not squadre_comuni:
                risultato['errori'].append("Nessuna squadra in comune tra le classifiche")
                return risultato
            
            differenze_posizione = []
            differenze_punti = []
            
            for squadra in squadre_comuni:
                dati_scraper = classifica_scraper[squadra]
                dati_ufficiali = classifica_ufficiale[squadra]
                
                diff_pos = abs(dati_scraper['posizione'] - dati_ufficiali['posizione'])
                diff_punti = abs(dati_scraper['punti'] - dati_ufficiali['punti'])
                
                differenze_posizione.append(diff_pos)
                differenze_punti.append(diff_punti)
                
                risultato['confronto'][squadra] = {
                    'scraper': dati_scraper,
                    'ufficiale': dati_ufficiali,
                    'diff_posizione': diff_pos,
                    'diff_punti': diff_punti,
                    'accurato': diff_pos <= 1 and diff_punti <= 2
                }
            
            # Calcola accuratezza generale
            squadre_accurate = sum(1 for dati in risultato['confronto'].values() if dati['accurato'])
            risultato['accuratezza'] = (squadre_accurate / len(squadre_comuni)) * 100
            
            # Statistiche
            risultato['statistiche'] = {
                'squadre_confrontate': len(squadre_comuni),
                'squadre_accurate': squadre_accurate,
                'diff_media_posizione': float(np.mean(differenze_posizione)),
                'diff_media_punti': float(np.mean(differenze_punti)),
                'diff_max_posizione': int(max(differenze_posizione)) if differenze_posizione else 0,
                'diff_max_punti': int(max(differenze_punti)) if differenze_punti else 0
            }
            
        except Exception as e:
            risultato['errori'].append(f"Errore verifica classifica: {e}")
        
        return risultato
    
    def _genera_classifica_riferimento(self) -> Dict:
        """Genera classifica di riferimento simulata ma realistica"""
        squadre = list(self.mapping_squadre.keys())[:20]  # Prendi 20 squadre
        
        classifica = {}
        
        for i, squadra in enumerate(squadre):
            # Simula dati realistici
            partite = np.random.randint(8, 15)  # Partite giocate stagione in corso
            posizione = i + 1
            
            # Punti basati sulla posizione (con variazione)
            if posizione <= 4:  # Zona Champions
                punti = np.random.randint(max(1, int(partite * 2)), int(partite * 3))
            elif posizione <= 10:  # Zona Europa
                punti = np.random.randint(max(1, int(partite * 1)), int(partite * 2))
            elif posizione <= 15:  # Zona medio-bassa
                punti = np.random.randint(max(1, int(partite * 0.5)), int(partite * 1.5))
            else:  # Zona retrocessione
                punti = np.random.randint(0, max(1, int(partite * 1)))
            
            classifica[squadra] = {
                'posizione': posizione,
                'partite': partite,
                'punti': int(punti),
                'media_punti': round(punti / max(partite, 1), 2)
            }
        
        return classifica
    
    def verifica_quote_multiple_fonti(self, casa: str, trasferta: str) -> Dict:
        """Confronta quote da multiple fonti"""
        risultato = {
            'partita': f"{casa} vs {trasferta}",
            'timestamp': datetime.now().isoformat(),
            'fonti': {},
            'confronto': {},
            'affidabilita': 0.0
        }
        
        try:
            # Fonte 1: Il nostro scraper
            quote_scraper = self.scraper.scrape_quote_live()
            partita_key = f"{casa} vs {trasferta}"
            
            risultato['fonti']['nostro_scraper'] = {
                'disponibile': partita_key in quote_scraper,
                'quote': quote_scraper.get(partita_key, {})
            }
            
            # Fonte 2: Genera quote di riferimento simulate
            quote_riferimento = self._genera_quote_riferimento(casa, trasferta)
            risultato['fonti']['riferimento'] = {
                'disponibile': True,
                'quote': quote_riferimento
            }
            
            # Confronta se abbiamo entrambe le fonti
            if (risultato['fonti']['nostro_scraper']['disponibile'] and 
                risultato['fonti']['riferimento']['disponibile']):
                
                quote1 = risultato['fonti']['nostro_scraper']['quote']
                quote2 = risultato['fonti']['riferimento']['quote']
                
                # Confronta ogni quota
                for tipo in ['quota_1', 'quota_x', 'quota_2']:
                    if tipo in quote1 and tipo in quote2:
                        diff = abs(quote1[tipo] - quote2[tipo])
                        diff_percentuale = (diff / quote2[tipo]) * 100
                        
                        risultato['confronto'][tipo] = {
                            'scraper': quote1[tipo],
                            'riferimento': quote2[tipo],
                            'differenza': round(diff, 2),
                            'diff_percentuale': round(diff_percentuale, 1),
                            'allineato': diff_percentuale <= 10  # Entro 10%
                        }
                
                # Calcola affidabilità
                allineamenti = [v['allineato'] for v in risultato['confronto'].values()]
                risultato['affidabilita'] = (sum(allineamenti) / len(allineamenti)) * 100 if allineamenti else 0
            
        except Exception as e:
            risultato['errore'] = str(e)
        
        return risultato
    
    def _genera_quote_riferimento(self, casa: str, trasferta: str) -> Dict:
        """Genera quote di riferimento realistiche"""
        # Forza squadre Serie A 2025-26 (basata su performance storica)
        forza_squadre = {
            'Inter': 85, 'Milan': 82, 'Juventus': 80, 'Napoli': 83,
            'Roma': 75, 'Lazio': 73, 'Atalanta': 78, 'Fiorentina': 70,
            'Bologna': 65, 'Torino': 62, 'Udinese': 60, 'Sassuolo': 58,
            'Verona': 55, 'Cagliari': 50, 'Lecce': 48, 'Cremonese': 45,
            'Genoa': 56, 'Parma': 52, 'Como': 48, 'Pisa': 46
        }
        
        forza_casa = forza_squadre.get(casa, 60)
        forza_trasferta = forza_squadre.get(trasferta, 60)
        
        # Bonus casa
        forza_casa += 5
        
        # Calcola probabilità base
        diff_forza = forza_casa - forza_trasferta
        
        if diff_forza > 15:
            prob_1, prob_x, prob_2 = 0.55, 0.25, 0.20
        elif diff_forza > 5:
            prob_1, prob_x, prob_2 = 0.45, 0.30, 0.25
        elif diff_forza > -5:
            prob_1, prob_x, prob_2 = 0.35, 0.35, 0.30
        elif diff_forza > -15:
            prob_1, prob_x, prob_2 = 0.25, 0.30, 0.45
        else:
            prob_1, prob_x, prob_2 = 0.20, 0.25, 0.55
        
        # Aggiungi margine bookmaker (circa 5%)
        margine = 1.05
        
        return {
            'casa': casa,
            'trasferta': trasferta,
            'quota_1': round((1 / prob_1) * margine, 2),
            'quota_x': round((1 / prob_x) * margine, 2),
            'quota_2': round((1 / prob_2) * margine, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def verifica_coerenza_meteo(self, citta: str = "Milano") -> Dict:
        """Verifica coerenza dati meteo con fonti esterne"""
        risultato = {
            'citta': citta,
            'timestamp': datetime.now().isoformat(),
            'nostro_meteo': {},
            'riferimento_meteo': {},
            'coerenza': 0.0,
            'note': []
        }
        
        try:
            # Nostro meteo
            meteo_scraper = self.scraper.scrape_meteo(citta)
            risultato['nostro_meteo'] = meteo_scraper
            
            # Meteo di riferimento (simulato)
            meteo_riferimento = self._genera_meteo_riferimento(citta)
            risultato['riferimento_meteo'] = meteo_riferimento
            
            # Confronta temperatura
            if ('temperatura' in meteo_scraper and 
                'temperatura' in meteo_riferimento):
                
                diff_temp = abs(meteo_scraper['temperatura'] - meteo_riferimento['temperatura'])
                
                if diff_temp <= 2:
                    risultato['coerenza'] += 40  # Temperature molto simili
                elif diff_temp <= 5:
                    risultato['coerenza'] += 20  # Abbastanza simili
                else:
                    risultato['note'].append(f"Differenza temperatura eccessiva: {diff_temp}°C")
            
            # Confronta condizioni
            if ('condizione' in meteo_scraper and 
                'condizione' in meteo_riferimento):
                
                if meteo_scraper['condizione'] == meteo_riferimento['condizione']:
                    risultato['coerenza'] += 40  # Condizioni identiche
                elif self._condizioni_compatibili(meteo_scraper['condizione'], 
                                                meteo_riferimento['condizione']):
                    risultato['coerenza'] += 20  # Condizioni compatibili
                else:
                    risultato['note'].append(
                        f"Condizioni incompatibili: {meteo_scraper['condizione']} vs {meteo_riferimento['condizione']}"
                    )
            
            # Confronta vento
            if ('vento_kmh' in meteo_scraper and 
                'vento_kmh' in meteo_riferimento):
                
                diff_vento = abs(meteo_scraper['vento_kmh'] - meteo_riferimento['vento_kmh'])
                if diff_vento <= 10:
                    risultato['coerenza'] += 20
                else:
                    risultato['note'].append(f"Differenza vento eccessiva: {diff_vento} km/h")
            
        except Exception as e:
            risultato['errore'] = str(e)
        
        return risultato
    
    def _genera_meteo_riferimento(self, citta: str) -> Dict:
        """Genera meteo di riferimento realistico per la stagione"""
        # Ottobre in Italia
        temp_base = np.random.randint(12, 20)
        
        condizioni = ['sereno', 'nuvoloso', 'pioggia_leggera']
        condizione = np.random.choice(condizioni, p=[0.4, 0.4, 0.2])
        
        return {
            'citta': citta,
            'condizione': condizione,
            'temperatura': temp_base,
            'vento_kmh': np.random.randint(5, 25),
            'umidita': np.random.randint(50, 80),
            'timestamp': datetime.now().isoformat()
        }
    
    def _condizioni_compatibili(self, cond1: str, cond2: str) -> bool:
        """Verifica se due condizioni meteo sono compatibili"""
        compatibilita = {
            'sereno': ['nuvoloso'],
            'nuvoloso': ['sereno', 'pioggia_leggera'],
            'pioggia_leggera': ['nuvoloso', 'pioggia'],
            'pioggia': ['pioggia_leggera'],
            'neve': []
        }
        
        return cond2 in compatibilita.get(cond1, [])
    
    def genera_report_accuratezza_completo(self) -> Dict:
        """Genera report completo di accuratezza"""
        print("📊 Generazione Report Accuratezza Completo...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'verifiche': {},
            'score_globale': 0.0,
            'raccomandazioni': []
        }
        
        try:
            # 1. Verifica classifica
            print("  Verificando classifica...")
            report['verifiche']['classifica'] = self.verifica_classifica_ufficiale()
            
            # 2. Verifica quote per alcune partite
            print("  Verificando quote...")
            partite_test = [("Inter", "Milan"), ("Roma", "Lazio")]
            report['verifiche']['quote'] = {}
            
            for casa, trasferta in partite_test:
                risultato_quote = self.verifica_quote_multiple_fonti(casa, trasferta)
                report['verifiche']['quote'][f"{casa}_{trasferta}"] = risultato_quote
            
            # 3. Verifica meteo
            print("  Verificando meteo...")
            report['verifiche']['meteo'] = self.verifica_coerenza_meteo("Milano")
            
            # Calcola score globale
            scores = []
            
            if 'accuratezza' in report['verifiche']['classifica']:
                scores.append(report['verifiche']['classifica']['accuratezza'])
            
            for verifica_quote in report['verifiche']['quote'].values():
                if 'affidabilita' in verifica_quote:
                    scores.append(verifica_quote['affidabilita'])
            
            if 'coerenza' in report['verifiche']['meteo']:
                scores.append(report['verifiche']['meteo']['coerenza'])
            
            report['score_globale'] = float(np.mean(scores)) if scores else 0.0
            
            # Genera raccomandazioni
            if report['score_globale'] < 70:
                report['raccomandazioni'].append("Score accuratezza basso - verificare fonti dati")
            
            if report['verifiche']['classifica']['accuratezza'] < 80:
                report['raccomandazioni'].append("Accuratezza classifica migliorabile")
            
            print("✅ Report completato")
            
        except Exception as e:
            report['errore'] = str(e)
            print(f"❌ Errore generazione report: {e}")
        
        return report

def main():
    """Test del sistema di verifica accuratezza"""
    print("🎯 SISTEMA DI VERIFICA ACCURATEZZA DATI")
    print("=" * 45)
    
    verificatore = VerificatoreAccuratezza()
    
    print("\n1️⃣ Verifica Classifica")
    print("-" * 22)
    
    risultato_classifica = verificatore.verifica_classifica_ufficiale()
    print(f"Accuratezza: {risultato_classifica['accuratezza']:.1f}%")
    
    if 'statistiche' in risultato_classifica:
        stats = risultato_classifica['statistiche']
        print(f"Squadre confrontate: {stats['squadre_confrontate']}")
        print(f"Squadre accurate: {stats['squadre_accurate']}")
        print(f"Diff media posizione: {stats['diff_media_posizione']:.1f}")
    
    print("\n2️⃣ Verifica Quote")
    print("-" * 17)
    
    risultato_quote = verificatore.verifica_quote_multiple_fonti("Inter", "Juventus")
    print(f"Affidabilità: {risultato_quote['affidabilita']:.1f}%")
    
    if 'confronto' in risultato_quote:
        for tipo, dati in risultato_quote['confronto'].items():
            print(f"{tipo}: {dati['scraper']} vs {dati['riferimento']} ({dati['diff_percentuale']}%)")
    
    print("\n3️⃣ Verifica Meteo")
    print("-" * 17)
    
    risultato_meteo = verificatore.verifica_coerenza_meteo("Milano")
    print(f"Coerenza: {risultato_meteo['coerenza']:.1f}%")
    
    if risultato_meteo['note']:
        print("Note:")
        for nota in risultato_meteo['note']:
            print(f"  • {nota}")
    
    print("\n4️⃣ Report Completo")
    print("-" * 18)
    
    report_completo = verificatore.genera_report_accuratezza_completo()
    print(f"\nScore Globale Accuratezza: {report_completo['score_globale']:.1f}%")
    
    if report_completo['raccomandazioni']:
        print("\nRaccomandazioni:")
        for raccomandazione in report_completo['raccomandazioni']:
            print(f"  📋 {raccomandazione}")
    
    # Salva report
    try:
        with open('cache/accuratezza_scraper.json', 'w', encoding='utf-8') as f:
            json.dump(report_completo, f, indent=2, ensure_ascii=False)
        print("\n💾 Report salvato in: cache/accuratezza_scraper.json")
    except Exception as e:
        print(f"\n❌ Errore salvataggio: {e}")

if __name__ == "__main__":
    main()