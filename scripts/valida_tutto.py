#!/usr/bin/env python3
"""
Script Principale di Validazione Completa Scraper
Esegue tutti i test di validazione e genera report finale
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.validatore_scraper import ValidatoreDatiScraper
from scripts.monitor_scraper import MonitorScraper
from scripts.verificatore_accuratezza import VerificatoreAccuratezza
import json
import time
from datetime import datetime
import argparse

def validazione_completa():
    """Esegue validazione completa del sistema scraper"""
    
    print("🔍 VALIDAZIONE COMPLETA SISTEMA SCRAPER")
    print("=" * 50)
    print(f"Data/Ora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    risultati_finali = {
        'timestamp': datetime.now().isoformat(),
        'validazione_strutturale': {},
        'monitoraggio_sistema': {},
        'verifica_accuratezza': {},
        'score_finale': 0.0,
        'stato_generale': '',
        'raccomandazioni': [],
        'azioni_richieste': []
    }
    
    # 1. VALIDAZIONE STRUTTURALE
    print("1️⃣ VALIDAZIONE STRUTTURALE")
    print("-" * 30)
    
    try:
        validator = ValidatoreDatiScraper()
        
        # Test su partite campione
        partite_test = [("Inter", "Milan"), ("Roma", "Lazio")]
        scores_strutturali = []
        
        for casa, trasferta in partite_test:
            print(f"   Testing {casa} vs {trasferta}...")
            risultato = validator.valida_dati_completi(casa, trasferta)
            scores_strutturali.append(risultato['score_globale'])
            
        score_strutturale = sum(scores_strutturali) / len(scores_strutturali)
        risultati_finali['validazione_strutturale'] = {
            'score': score_strutturale,
            'partite_testate': len(partite_test),
            'dettagli': f"Score medio: {score_strutturale:.1f}/100"
        }
        
        print(f"   ✅ Score Strutturale: {score_strutturale:.1f}/100")
        
    except Exception as e:
        print(f"   ❌ Errore validazione strutturale: {e}")
        risultati_finali['validazione_strutturale']['errore'] = str(e)
        score_strutturale = 0
    
    # 2. MONITORAGGIO SISTEMA
    print("\n2️⃣ MONITORAGGIO SISTEMA")
    print("-" * 26)
    
    try:
        monitor = MonitorScraper(intervallo_minuti=1)
        
        # Esegui alcuni check rapidi
        print("   Eseguendo check multipli...")
        for i in range(3):
            risultato_check = monitor.check_singolo()
            time.sleep(1)  # Pausa breve
        
        report_salute = monitor.genera_report_salute()
        
        risultati_finali['monitoraggio_sistema'] = {
            'stato': report_salute['stato_sistema'],
            'score_medio': report_salute['qualita']['score_medio'],
            'tempo_medio': report_salute['performance']['tempo_medio'],
            'alert_totali': report_salute['alert']['totali']
        }
        
        print(f"   ✅ Stato Sistema: {report_salute['stato_sistema']}")
        print(f"   📊 Score Medio: {report_salute['qualita']['score_medio']:.1f}/100")
        print(f"   ⏱️ Tempo Medio: {report_salute['performance']['tempo_medio']:.1f}s")
        
    except Exception as e:
        print(f"   ❌ Errore monitoraggio: {e}")
        risultati_finali['monitoraggio_sistema']['errore'] = str(e)
    
    # 3. VERIFICA ACCURATEZZA
    print("\n3️⃣ VERIFICA ACCURATEZZA")
    print("-" * 25)
    
    try:
        verificatore = VerificatoreAccuratezza()
        
        print("   Confrontando con fonti esterne...")
        report_accuratezza = verificatore.genera_report_accuratezza_completo()
        
        risultati_finali['verifica_accuratezza'] = {
            'score_globale': report_accuratezza['score_globale'],
            'verifiche_completate': len(report_accuratezza.get('verifiche', {})),
            'raccomandazioni': report_accuratezza.get('raccomandazioni', [])
        }
        
        print(f"   ✅ Score Accuratezza: {report_accuratezza['score_globale']:.1f}/100")
        
    except Exception as e:
        print(f"   ❌ Errore verifica accuratezza: {e}")
        risultati_finali['verifica_accuratezza']['errore'] = str(e)
    
    # 4. CALCOLO SCORE FINALE
    print("\n4️⃣ CALCOLO SCORE FINALE")
    print("-" * 24)
    
    scores_componenti = []
    pesi = []
    
    # Score strutturale (peso 40%)
    if 'score' in risultati_finali['validazione_strutturale']:
        scores_componenti.append(risultati_finali['validazione_strutturale']['score'])
        pesi.append(0.4)
    
    # Score monitoraggio (peso 30%)
    if 'score_medio' in risultati_finali['monitoraggio_sistema']:
        scores_componenti.append(risultati_finali['monitoraggio_sistema']['score_medio'])
        pesi.append(0.3)
    
    # Score accuratezza (peso 30%)
    if 'score_globale' in risultati_finali['verifica_accuratezza']:
        scores_componenti.append(risultati_finali['verifica_accuratezza']['score_globale'])
        pesi.append(0.3)
    
    if scores_componenti:
        # Media ponderata
        score_finale = sum(s * p for s, p in zip(scores_componenti, pesi)) / sum(pesi)
        risultati_finali['score_finale'] = score_finale
    else:
        risultati_finali['score_finale'] = 0
        score_finale = 0
    
    # 5. VALUTAZIONE FINALE
    print("\n5️⃣ VALUTAZIONE FINALE")
    print("-" * 21)
    
    if score_finale >= 85:
        stato = "ECCELLENTE"
        emoji = "🌟"
    elif score_finale >= 75:
        stato = "BUONO"
        emoji = "✅"
    elif score_finale >= 65:
        stato = "ACCETTABILE"
        emoji = "⚠️"
    elif score_finale >= 50:
        stato = "PROBLEMATICO"
        emoji = "⚠️"
    else:
        stato = "CRITICO"
        emoji = "🚨"
    
    risultati_finali['stato_generale'] = stato
    
    print(f"   {emoji} STATO GENERALE: {stato}")
    print(f"   📊 SCORE FINALE: {score_finale:.1f}/100")
    
    # 6. RACCOMANDAZIONI
    print("\n6️⃣ RACCOMANDAZIONI")
    print("-" * 18)
    
    raccomandazioni = []
    azioni = []
    
    if score_finale < 70:
        raccomandazioni.append("Score generale basso - investigare cause principali")
        azioni.append("URGENTE: Verificare configurazione scraper")
    
    if risultati_finali['validazione_strutturale'].get('score', 0) < 70:
        raccomandazioni.append("Dati strutturalmente inconsistenti")
        azioni.append("Rivedere logica di validazione e pulizia dati")
    
    if risultati_finali['verifica_accuratezza'].get('score_globale', 0) < 50:
        raccomandazioni.append("Accuratezza molto bassa vs fonti esterne")
        azioni.append("Cambiare fonti dati o algoritmi di scraping")
    
    if not raccomandazioni:
        raccomandazioni.append("Sistema in buono stato - continuare monitoraggio")
        azioni.append("Mantenere procedure di validazione quotidiane")
    
    risultati_finali['raccomandazioni'] = raccomandazioni
    risultati_finali['azioni_richieste'] = azioni
    
    for i, racc in enumerate(raccomandazioni, 1):
        print(f"   {i}. {racc}")
    
    if azioni:
        print("\n   🎯 AZIONI RICHIESTE:")
        for i, azione in enumerate(azioni, 1):
            print(f"      {i}. {azione}")
    
    # 7. SALVATAGGIO REPORT
    print("\n7️⃣ SALVATAGGIO REPORT")
    print("-" * 22)
    
    try:
        report_file = 'cache/validazione_completa.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(risultati_finali, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Report salvato: {report_file}")
        
        # Genera anche summary testuale
        summary_file = 'cache/validazione_summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"VALIDAZIONE SCRAPER - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"STATO GENERALE: {stato}\n")
            f.write(f"SCORE FINALE: {score_finale:.1f}/100\n\n")
            f.write("DETTAGLI:\n")
            f.write(f"- Strutturale: {risultati_finali['validazione_strutturale'].get('score', 'N/A')}/100\n")
            f.write(f"- Monitoraggio: {risultati_finali['monitoraggio_sistema'].get('score_medio', 'N/A')}/100\n")
            f.write(f"- Accuratezza: {risultati_finali['verifica_accuratezza'].get('score_globale', 'N/A')}/100\n\n")
            f.write("RACCOMANDAZIONI:\n")
            for i, racc in enumerate(raccomandazioni, 1):
                f.write(f"{i}. {racc}\n")
        
        print(f"   📄 Summary salvato: {summary_file}")
        
    except Exception as e:
        print(f"   ❌ Errore salvataggio: {e}")
    
    print("\n" + "=" * 50)
    print("✅ VALIDAZIONE COMPLETA TERMINATA")
    print("=" * 50)
    
    return risultati_finali

def validazione_rapida():
    """Validazione rapida per check quotidiani"""
    print("⚡ VALIDAZIONE RAPIDA")
    print("-" * 20)
    
    try:
        monitor = MonitorScraper()
        risultato = monitor.check_singolo()
        
        if 'errore' not in risultato:
            val = risultato['risultato_validazione']
            score = val['score_globale']
            tempo = risultato['tempo_check']
            
            print(f"Score: {score}/100")
            print(f"Tempo: {tempo:.1f}s")
            print(f"Qualità: {val['qualita']}")
            print(f"Errori: {val['errori_totali']}")
            
            if score >= 70:
                print("✅ Sistema OK")
                return True
            else:
                print("⚠️ Sistema problematico")
                return False
        else:
            print(f"❌ Errore: {risultato['errore']}")
            return False
            
    except Exception as e:
        print(f"❌ Errore validazione: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Sistema Validazione Scraper')
    parser.add_argument('--rapida', action='store_true', help='Validazione rapida')
    parser.add_argument('--completa', action='store_true', help='Validazione completa')
    parser.add_argument('--cron', action='store_true', help='Modalità cron (solo errori)')
    
    args = parser.parse_args()
    
    if args.rapida:
        success = validazione_rapida()
        sys.exit(0 if success else 1)
    elif args.completa:
        risultati = validazione_completa()
        # Exit code basato su score finale
        score = risultati.get('score_finale', 0)
        sys.exit(0 if score >= 70 else 1)
    elif args.cron:
        # Modalità silenziosa per cron
        try:
            monitor = MonitorScraper()
            risultato = monitor.check_singolo()
            
            if 'errore' in risultato:
                print(f"ERRORE SCRAPER: {risultato['errore']}")
                sys.exit(1)
            
            score = risultato['risultato_validazione']['score_globale']
            if score < 50:
                print(f"SCORE CRITICO: {score}/100")
                sys.exit(1)
            
            sys.exit(0)
            
        except Exception as e:
            print(f"ERRORE VALIDAZIONE: {e}")
            sys.exit(1)
    else:
        # Default: validazione completa
        validazione_completa()

if __name__ == "__main__":
    main()