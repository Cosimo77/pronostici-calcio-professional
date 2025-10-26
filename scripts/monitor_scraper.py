#!/usr/bin/env python3
"""
Sistema di Monitoraggio Continuo Dati Scraper
Monitora qualità dati, rileva anomalie e genera alert
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.validatore_scraper import ValidatoreDatiScraper
from scripts.scraper_dati import ScraperDatiCalcio
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List
import threading
from collections import deque

logger = logging.getLogger(__name__)

class MonitorScraper:
    """Sistema di monitoraggio continuo per lo scraper"""
    
    def __init__(self, intervallo_minuti: int = 10):
        self.validator = ValidatoreDatiScraper()
        self.scraper = ScraperDatiCalcio()
        self.intervallo = intervallo_minuti * 60  # Converti in secondi
        self.running = False
        
        # Storico metriche (ultimi 100 check)
        self.storico_scores = deque(maxlen=100)
        self.storico_errori = deque(maxlen=100)
        self.storico_tempi = deque(maxlen=100)
        
        # Soglie per alert
        self.soglie = {
            'score_critico': 50,
            'score_warning': 70,
            'errori_max': 5,
            'tempo_max_secondi': 30
        }
        
        # Log degli alert
        self.alert_log = []
    
    def _genera_alert(self, tipo: str, messaggio: str, severita: str = "WARNING"):
        """Genera un alert con timestamp"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'tipo': tipo,
            'severita': severita,
            'messaggio': messaggio
        }
        
        self.alert_log.append(alert)
        
        # Log su file
        logger.log(
            logging.ERROR if severita == "CRITICAL" else logging.WARNING,
            f"[{severita}] {tipo}: {messaggio}"
        )
        
        # Mantieni solo ultimi 50 alert
        if len(self.alert_log) > 50:
            self.alert_log.pop(0)
    
    def check_singolo(self, casa: str = "Inter", trasferta: str = "Milan") -> Dict:
        """Esegue un singolo check di qualità"""
        start_time = time.time()
        
        try:
            # Validazione completa
            risultato = self.validator.valida_dati_completi(casa, trasferta)
            
            end_time = time.time()
            tempo_check = end_time - start_time
            
            # Aggiorna storico
            self.storico_scores.append(risultato['score_globale'])
            self.storico_errori.append(risultato['errori_totali'])
            self.storico_tempi.append(tempo_check)
            
            # Verifica soglie e genera alert se necessario
            self._verifica_soglie(risultato, tempo_check)
            
            return {
                'risultato_validazione': risultato,
                'tempo_check': tempo_check,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._genera_alert(
                tipo="ERRORE_CHECK",
                messaggio=f"Errore durante check: {str(e)}",
                severita="CRITICAL"
            )
            return {
                'errore': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _verifica_soglie(self, risultato: Dict, tempo_check: float):
        """Verifica soglie e genera alert appropriati"""
        score = risultato['score_globale']
        errori = risultato['errori_totali']
        
        # Alert per score basso
        if score < self.soglie['score_critico']:
            self._genera_alert(
                tipo="QUALITA_CRITICA",
                messaggio=f"Score qualità critico: {score}/100",
                severita="CRITICAL"
            )
        elif score < self.soglie['score_warning']:
            self._genera_alert(
                tipo="QUALITA_BASSA",
                messaggio=f"Score qualità basso: {score}/100",
                severita="WARNING"
            )
        
        # Alert per troppi errori
        if errori > self.soglie['errori_max']:
            self._genera_alert(
                tipo="TROPPI_ERRORI",
                messaggio=f"Troppi errori rilevati: {errori}",
                severita="CRITICAL"
            )
        
        # Alert per tempo eccessivo
        if tempo_check > self.soglie['tempo_max_secondi']:
            self._genera_alert(
                tipo="TEMPO_ECCESSIVO",
                messaggio=f"Check troppo lento: {tempo_check:.1f}s",
                severita="WARNING"
            )
        
        # Alert per trend negativi
        if len(self.storico_scores) >= 5:
            ultimi_5_scores = list(self.storico_scores)[-5:]
            if all(ultimi_5_scores[i] > ultimi_5_scores[i+1] for i in range(4)):
                self._genera_alert(
                    tipo="TREND_NEGATIVO",
                    messaggio=f"Qualità in calo continuo: {ultimi_5_scores}",
                    severita="WARNING"
                )
    
    def genera_report_salute(self) -> Dict:
        """Genera report completo sulla salute del sistema"""
        if not self.storico_scores:
            return {"errore": "Nessun dato disponibile per il report"}
        
        scores = list(self.storico_scores)
        errori = list(self.storico_errori)
        tempi = list(self.storico_tempi)
        
        # Calcola statistiche
        report = {
            'timestamp': datetime.now().isoformat(),
            'numero_check': len(scores),
            'periodo_ore': (len(scores) * self.intervallo) / 3600,
            
            'qualita': {
                'score_medio': float(np.mean(scores)),
                'score_mediano': float(np.median(scores)),
                'score_min': float(min(scores)),
                'score_max': float(max(scores)),
                'deviazione_standard': float(np.std(scores)),
                'trend': self._calcola_trend(scores)
            },
            
            'errori': {
                'media_errori': float(np.mean(errori)),
                'max_errori': int(max(errori)),
                'percentuale_senza_errori': (errori.count(0) / len(errori)) * 100
            },
            
            'performance': {
                'tempo_medio': float(np.mean(tempi)),
                'tempo_max': float(max(tempi)),
                'tempo_min': float(min(tempi))
            },
            
            'alert': {
                'totali': len(self.alert_log),
                'critici': len([a for a in self.alert_log if a['severita'] == 'CRITICAL']),
                'warning': len([a for a in self.alert_log if a['severita'] == 'WARNING']),
                'ultimi_alert': self.alert_log[-5:] if self.alert_log else []
            },
            
            'stato_sistema': self._valuta_stato_sistema(scores, errori, tempi)
        }
        
        return report
    
    def _calcola_trend(self, scores: List[float]) -> str:
        """Calcola trend generale dei scores"""
        if len(scores) < 3:
            return "insufficienti_dati"
        
        # Regressione lineare semplice
        x = np.arange(len(scores))
        y = np.array(scores)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 1:
            return "miglioramento"
        elif slope < -1:
            return "peggioramento"
        else:
            return "stabile"
    
    def _valuta_stato_sistema(self, scores: List[float], errori: List[int], tempi: List[float]) -> str:
        """Valuta stato generale del sistema"""
        score_medio = np.mean(scores)
        errori_medi = np.mean(errori)
        tempo_medio = np.mean(tempi)
        
        if (score_medio >= 80 and 
            errori_medi <= 2 and 
            tempo_medio <= 15):
            return "OTTIMO"
        elif (score_medio >= 70 and 
              errori_medi <= 3 and 
              tempo_medio <= 20):
            return "BUONO"
        elif (score_medio >= 60 and 
              errori_medi <= 5 and 
              tempo_medio <= 30):
            return "ACCETTABILE"
        elif score_medio >= 50:
            return "PROBLEMATICO"
        else:
            return "CRITICO"
    
    def monitora_continuo(self, durata_ore: int = 1):
        """Avvia monitoraggio continuo per X ore"""
        self.running = True
        end_time = time.time() + (durata_ore * 3600)
        
        logger.info(f"Avvio monitoraggio continuo per {durata_ore} ore")
        
        check_count = 0
        
        while self.running and time.time() < end_time:
            try:
                check_count += 1
                logger.info(f"Check #{check_count}")
                
                risultato_check = self.check_singolo()
                
                if 'errore' not in risultato_check:
                    score = risultato_check['risultato_validazione']['score_globale']
                    tempo = risultato_check['tempo_check']
                    logger.info(f"Check completato: Score={score}/100, Tempo={tempo:.1f}s")
                else:
                    logger.error(f"Check fallito: {risultato_check['errore']}")
                
                # Pausa fino al prossimo check
                time.sleep(self.intervallo)
                
            except KeyboardInterrupt:
                logger.info("Monitoraggio interrotto dall'utente")
                break
            except Exception as e:
                logger.error(f"Errore durante monitoraggio: {e}")
                time.sleep(60)  # Pausa più lunga in caso di errore
        
        self.running = False
        logger.info(f"Monitoraggio terminato dopo {check_count} check")
        
        # Genera report finale
        return self.genera_report_salute()
    
    def stop_monitoraggio(self):
        """Ferma il monitoraggio continuo"""
        self.running = False
    
    def salva_report(self, filepath: str = 'cache/monitor_scraper.json'):
        """Salva report di monitoraggio su file"""
        report = self.genera_report_salute()
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report salvato in: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Errore salvataggio report: {e}")
            return False

def main():
    """Test del sistema di monitoraggio"""
    print("📊 SISTEMA DI MONITORAGGIO SCRAPER")
    print("=" * 45)
    
    monitor = MonitorScraper(intervallo_minuti=1)  # Check ogni minuto per demo
    
    print("\n1️⃣ Test Check Singolo")
    print("-" * 25)
    
    risultato = monitor.check_singolo("Inter", "Juventus")
    
    if 'errore' not in risultato:
        val = risultato['risultato_validazione']
        print(f"✅ Check completato in {risultato['tempo_check']:.1f}s")
        print(f"Score: {val['score_globale']}/100 ({val['qualita']})")
        print(f"Errori: {val['errori_totali']}, Warning: {val['warning_totali']}")
    else:
        print(f"❌ Check fallito: {risultato['errore']}")
    
    print("\n2️⃣ Simulazione Check Multipli")
    print("-" * 30)
    
    # Simula alcuni check per testare le metriche
    partite = [("Inter", "Milan"), ("Roma", "Lazio"), ("Juventus", "Napoli")]
    
    for i, (casa, trasferta) in enumerate(partite, 1):
        print(f"Check {i}/3: {casa} vs {trasferta}")
        risultato = monitor.check_singolo(casa, trasferta)
        
        if 'errore' not in risultato:
            score = risultato['risultato_validazione']['score_globale']
            tempo = risultato['tempo_check']
            print(f"  Score: {score}/100, Tempo: {tempo:.1f}s")
        
        time.sleep(1)  # Pausa breve
    
    print("\n3️⃣ Report Salute Sistema")
    print("-" * 28)
    
    report = monitor.genera_report_salute()
    
    print(f"Stato Sistema: {report['stato_sistema']}")
    print(f"Check Eseguiti: {report['numero_check']}")
    print(f"Score Medio: {report['qualita']['score_medio']:.1f}/100")
    print(f"Trend: {report['qualita']['trend']}")
    print(f"Tempo Medio: {report['performance']['tempo_medio']:.1f}s")
    print(f"Alert Totali: {report['alert']['totali']}")
    
    if report['alert']['ultimi_alert']:
        print("\nUltimi Alert:")
        for alert in report['alert']['ultimi_alert']:
            print(f"  {alert['severita']}: {alert['messaggio']}")
    
    # Salva report
    monitor.salva_report()
    
    print("\n4️⃣ Opzioni Avanzate")
    print("-" * 20)
    print("Per monitoraggio continuo:")
    print("  python3 scripts/monitor_scraper.py --continuo --ore 2")
    print("\nPer check programmato:")
    print("  # Aggiungi a crontab per check ogni 30 min:")
    print("  */30 * * * * cd /path/to/project && python3 scripts/monitor_scraper.py --check")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Scraper Dati')
    parser.add_argument('--continuo', action='store_true', help='Monitoraggio continuo')
    parser.add_argument('--ore', type=int, default=1, help='Durata monitoraggio in ore')
    parser.add_argument('--check', action='store_true', help='Esegui singolo check')
    
    args = parser.parse_args()
    
    if args.continuo:
        monitor = MonitorScraper(intervallo_minuti=5)
        report_finale = monitor.monitora_continuo(durata_ore=args.ore)
        print("\n📊 REPORT FINALE MONITORAGGIO")
        print("=" * 35)
        print(f"Stato: {report_finale['stato_sistema']}")
        print(f"Score Medio: {report_finale['qualita']['score_medio']:.1f}/100")
        print(f"Alert: {report_finale['alert']['totali']}")
    elif args.check:
        monitor = MonitorScraper()
        risultato = monitor.check_singolo()
        if 'errore' not in risultato:
            val = risultato['risultato_validazione']
            print(f"Score: {val['score_globale']}/100")
            print(f"Qualità: {val['qualita']}")
        else:
            print(f"Errore: {risultato['errore']}")
    else:
        main()