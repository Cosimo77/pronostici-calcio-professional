#!/usr/bin/env python3
"""
🔍 VERIFICA COMPLETA METODI PREDITTIVI - TUTTI I 16 MERCATI
Analizza ogni mercato per verificare funzionamento e qualità delle predizioni
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from scripts.mercati_multipli import MercatiMultipli
import json
import traceback
from datetime import datetime
import numpy as np

def print_header():
    print("🔍 VERIFICA COMPLETA METODI PREDITTIVI")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🎯 Obiettivo: Verificare tutti i 16 mercati")
    print()

def test_mercato_singolo(nome_mercato, squadra_casa, squadra_ospite):
    """Testa un singolo mercato usando il sistema completo"""
    try:
        # Usa il sistema completo per ottenere tutti i mercati
        mercati_obj = MercatiMultipli()
        tutti_risultati = mercati_obj.predici_tutti_mercati(squadra_casa, squadra_ospite)
        
        # Mappa dei nomi ai campi nel risultato
        mappa_mercati = {
            "1X2": "1X2",
            "Over/Under 2.5": "over_under", 
            "Over/Under 1.5": "over_under_15",
            "Over/Under 3.5": "over_under_35",
            "BTTS": "btts",
            "Double Chance": "double_chance",
            "Prima Squadra Gol": "prima_squadra_gol",
            "Clean Sheet": "clean_sheet", 
            "Primo Tempo 1X2": "primo_tempo_1x2",
            "Exact Score": "exact_score",
            "Primo Tempo O/U": "primo_tempo_over_under",
            "Handicap": "handicap",
            "Cartellini Totali": "cartellini_totali",
            "Cartellini Over/Under": "cartellini_over_under",
            "Corner Totali": "calci_angolo_totali", 
            "Corner Over/Under": "calci_angolo_over_under"
        }
        
        campo_risultato = mappa_mercati.get(nome_mercato)
        if not campo_risultato or campo_risultato not in tutti_risultati:
            return None, {
                'funziona': False,
                'errore': f"Mercato {nome_mercato} non trovato nel risultato",
                'campi_disponibili': list(tutti_risultati.keys())
            }
        
        risultato = tutti_risultati[campo_risultato]
        
        # Analisi qualità risultato
        analisi = {
            'funziona': True,
            'tipo_output': type(risultato).__name__,
            'campi_presenti': list(risultato.keys()) if isinstance(risultato, dict) else [],
            'ha_predizione': 'predizione' in risultato if isinstance(risultato, dict) else False,
            'ha_probabilita': any(k for k in (risultato.keys() if isinstance(risultato, dict) else []) if 'probabilit' in k.lower() or 'over' in k.lower() or 'under' in k.lower()),
            'ha_confidenza': 'confidenza' in risultato if isinstance(risultato, dict) else False,
            'valori_numerici_validi': True,
            'errori': []
        }
        
        # Verifica valori numerici
        if isinstance(risultato, dict):
            for key, value in risultato.items():
                if isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        analisi['valori_numerici_validi'] = False
                        analisi['errori'].append(f"Valore non valido in {key}: {value}")
                    elif 'probabilit' in key.lower() and (value < 0 or value > 1):
                        analisi['valori_numerici_validi'] = False
                        analisi['errori'].append(f"Probabilità fuori range [0,1] in {key}: {value}")
        
        return risultato, analisi
        
    except Exception as e:
        return None, {
            'funziona': False,
            'errore': str(e),
            'traceback': traceback.format_exc()
        }

def valuta_qualita_mercato(nome, risultato, analisi):
    """Valuta la qualità di un mercato"""
    score = 0
    issues = []
    
    if not analisi['funziona']:
        return 0, ['ERRORE CRITICO: Mercato non funziona'], 'CRITICO'
    
    # Criteri di valutazione
    if analisi['ha_predizione']:
        score += 20
    else:
        issues.append("Manca campo 'predizione'")
    
    if analisi['ha_probabilita']:
        score += 25
    else:
        issues.append("Mancano probabilità")
    
    if analisi['ha_confidenza']:
        score += 15
    else:
        issues.append("Manca confidenza")
    
    if analisi['valori_numerici_validi']:
        score += 25
    else:
        issues.append("Valori numerici non validi")
        
    # Verifica campi specifici per tipo mercato
    if isinstance(risultato, dict):
        # Mercati over/under dovrebbero avere soglie multiple
        if 'over_' in str(risultato) or any('over' in k for k in risultato.keys()):
            if len([k for k in risultato.keys() if 'over_' in k]) >= 3:
                score += 10
            else:
                issues.append("Poche soglie over/under")
        
        # Mercati con quote
        if any('quota' in k for k in risultato.keys()):
            score += 5
    
    # Determinazione livello
    if score >= 85:
        livello = 'ECCELLENTE'
    elif score >= 70:
        livello = 'BUONO'
    elif score >= 50:
        livello = 'SUFFICIENTE'
    elif score >= 30:
        livello = 'MIGLIORABILE'
    else:
        livello = 'CRITICO'
    
    return score, issues, livello

def main():
    print_header()
    
    try:
        # Inizializza sistema
        print("🚀 Inizializzazione sistema...")
        mercati = MercatiMultipli()
        print("✅ Sistema MercatiMultipli inizializzato\n")
        
        # Squadre di test
        test_cases = [
            ("Juventus", "Inter"),
            ("Atalanta", "Napoli"), 
            ("Milan", "Roma"),
            ("Cagliari", "Genoa")  # Squadre con meno dati
        ]
        
        # Lista di tutti i mercati da testare (nomi semplici)
        mercati_da_testare = [
            "1X2",
            "Over/Under 2.5", 
            "Over/Under 1.5",
            "Over/Under 3.5",
            "BTTS",
            "Double Chance",
            "Prima Squadra Gol",
            "Clean Sheet", 
            "Primo Tempo 1X2",
            "Exact Score",
            "Primo Tempo O/U",
            "Handicap",
            "Cartellini Totali",
            "Cartellini Over/Under",
            "Corner Totali", 
            "Corner Over/Under"
        ]
        
        risultati_complessivi = {}
        
        print("🧪 INIZIO TEST MERCATI")
        print("=" * 60)
        
        for nome_mercato in mercati_da_testare:
            print(f"\n📊 Test {nome_mercato}:")
            print("-" * 40)
            
            risultati_mercato = {}
            
            for i, (casa, ospite) in enumerate(test_cases):
                print(f"  🏠 {casa} vs {ospite}: ", end="")
                
                risultato, analisi = test_mercato_singolo(nome_mercato, casa, ospite)
                
                if analisi['funziona']:
                    print("✅")
                else:
                    print("❌")
                    if i == 0:  # Mostra errore solo per il primo caso
                        print(f"    Errore: {analisi.get('errore', 'Sconosciuto')}")
                
                risultati_mercato[f"{casa}_vs_{ospite}"] = {
                    'risultato': risultato,
                    'analisi': analisi
                }
            
            # Valutazione qualità mercato (usa primo test case valido)
            primo_risultato = None
            prima_analisi = None
            for key, value in risultati_mercato.items():
                if value['analisi']['funziona']:
                    primo_risultato = value['risultato']
                    prima_analisi = value['analisi']
                    break
            
            if primo_risultato and prima_analisi:
                score, issues, livello = valuta_qualita_mercato(nome_mercato, primo_risultato, prima_analisi)
                print(f"  🎯 Qualità: {livello} ({score}/100)")
                if issues:
                    print(f"  ⚠️  Issues: {', '.join(issues[:2])}")  # Mostra solo primi 2
            else:
                score, issues, livello = 0, ["Mercato non funziona"], "CRITICO"
                print(f"  💥 Qualità: {livello} - Mercato non funzionante")
            
            risultati_complessivi[nome_mercato] = {
                'score': score,
                'livello': livello,
                'issues': issues,
                'test_results': risultati_mercato
            }
        
        # ANALISI FINALE
        print(f"\n{'='*60}")
        print("📊 ANALISI FINALE QUALITÀ MERCATI")
        print(f"{'='*60}")
        
        # Statistiche generali
        scores = [r['score'] for r in risultati_complessivi.values()]
        livelli = [r['livello'] for r in risultati_complessivi.values()]
        
        print(f"📈 Score medio: {np.mean(scores):.1f}/100")
        print(f"📊 Score mediano: {np.median(scores):.1f}/100")
        print(f"📉 Score minimo: {min(scores)}/100")
        print(f"📈 Score massimo: {max(scores)}/100")
        
        # Conteggio per livello
        livelli_count = {}
        for livello in livelli:
            livelli_count[livello] = livelli_count.get(livello, 0) + 1
        
        print(f"\n🏆 DISTRIBUZIONE QUALITÀ:")
        for livello, count in sorted(livelli_count.items(), key=lambda x: ['CRITICO', 'MIGLIORABILE', 'SUFFICIENTE', 'BUONO', 'ECCELLENTE'].index(x[0])):
            emoji = {'ECCELLENTE': '🟢', 'BUONO': '🔵', 'SUFFICIENTE': '🟡', 'MIGLIORABILE': '🟠', 'CRITICO': '🔴'}
            print(f"  {emoji.get(livello, '⚪')} {livello}: {count} mercati")
        
        # TOP e FLOP mercati
        mercati_ordinati = sorted(risultati_complessivi.items(), key=lambda x: x[1]['score'], reverse=True)
        
        print(f"\n🥇 TOP 5 MERCATI:")
        for nome, dati in mercati_ordinati[:5]:
            print(f"  {dati['score']:3d}/100 - {nome} ({dati['livello']})")
        
        print(f"\n🔴 MERCATI DA MIGLIORARE:")
        mercati_da_migliorare = [item for item in mercati_ordinati if item[1]['score'] < 70]
        for nome, dati in mercati_da_migliorare:
            print(f"  {dati['score']:3d}/100 - {nome}")
            for issue in dati['issues'][:2]:  # Solo primi 2 issues
                print(f"    • {issue}")
        
        # RACCOMANDAZIONI
        print(f"\n💡 RACCOMANDAZIONI PER MIGLIORAMENTI:")
        print("-" * 50)
        
        issues_globali = {}
        for nome, dati in risultati_complessivi.items():
            for issue in dati['issues']:
                issues_globali[issue] = issues_globali.get(issue, 0) + 1
        
        issues_comuni = sorted(issues_globali.items(), key=lambda x: x[1], reverse=True)
        for issue, count in issues_comuni[:5]:
            print(f"  🔧 {issue}: {count} mercati")
        
        # Salva risultati dettagliati
        with open('verifica_mercati_completa.json', 'w') as f:
            json.dump(risultati_complessivi, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Risultati dettagliati salvati in: verifica_mercati_completa.json")
        print(f"✅ Verifica completata!")
        
        # Verdict finale
        avg_score = np.mean(scores)
        if avg_score >= 80:
            print(f"\n🎉 VERDICT: Sistema mercati in OTTIMO stato ({avg_score:.1f}/100)")
        elif avg_score >= 65:
            print(f"\n👍 VERDICT: Sistema mercati in BUONO stato ({avg_score:.1f}/100)")
        elif avg_score >= 50:
            print(f"\n⚠️  VERDICT: Sistema mercati SUFFICIENTE ({avg_score:.1f}/100)")
        else:
            print(f"\n🚨 VERDICT: Sistema mercati necessita MIGLIORAMENTI ({avg_score:.1f}/100)")
        
    except Exception as e:
        print(f"💥 Errore critico durante la verifica: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()