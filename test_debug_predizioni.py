#!/usr/bin/env python3
"""
Test Debug Predizioni - Analizza step-by-step il processo di predizione
Verifica ogni componente per trovare dove si generano le divergenze anomale
"""

import pandas as pd
import numpy as np
import sys
import os

# Aggiungi path
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

from app_professional import calculator, inizializza_sistema_professionale

def test_statistiche_base():
    """Test 1: Verifica calcolo statistiche base squadre"""
    print("\n" + "="*80)
    print("TEST 1: STATISTICHE BASE SQUADRE")
    print("="*80)
    
    squadre_test = ['Napoli', 'Juventus', 'Lecce', 'Pisa', 'Cagliari', 'Roma']
    
    for squadra in squadre_test:
        print(f"\n🔍 {squadra}:")
        
        # Statistiche in casa
        stats_casa = calculator._calcola_statistiche_squadra(squadra, in_casa=True)
        print(f"   IN CASA:")
        print(f"      Vittorie: {stats_casa['vittorie']:.3f} ({stats_casa['vittorie']*100:.1f}%)")
        print(f"      Pareggi: {stats_casa['pareggi']:.3f} ({stats_casa['pareggi']*100:.1f}%)")
        print(f"      Sconfitte: {stats_casa['sconfitte']:.3f} ({stats_casa['sconfitte']*100:.1f}%)")
        print(f"      Partite totali: {stats_casa.get('partite_totali', 0)}")
        print(f"      Clean sheet: {stats_casa.get('clean_sheet_rate', 0):.3f}")
        
        # Statistiche in trasferta
        stats_trasferta = calculator._calcola_statistiche_squadra(squadra, in_casa=False)
        print(f"   IN TRASFERTA:")
        print(f"      Vittorie: {stats_trasferta['vittorie']:.3f} ({stats_trasferta['vittorie']*100:.1f}%)")
        print(f"      Pareggi: {stats_trasferta['pareggi']:.3f} ({stats_trasferta['pareggi']*100:.1f}%)")
        print(f"      Sconfitte: {stats_trasferta['sconfitte']:.3f} ({stats_trasferta['sconfitte']*100:.1f}%)")
        print(f"      Partite totali: {stats_trasferta.get('partite_totali', 0)}")


def test_probabilita_base():
    """Test 2: Verifica calcolo probabilità base (prima della simmetria)"""
    print("\n" + "="*80)
    print("TEST 2: PROBABILITÀ BASE (PRIMA SIMMETRIA)")
    print("="*80)
    
    partite_test = [
        ('Napoli', 'Juventus'),
        ('Cagliari', 'Roma'),
        ('Lecce', 'Pisa'),
        ('Lazio', 'Bologna'),
        ('Torino', 'Milan')
    ]
    
    for casa, ospite in partite_test:
        print(f"\n🔍 {casa} vs {ospite}:")
        
        # Statistiche
        stats_casa = calculator._calcola_statistiche_squadra(casa, in_casa=True)
        stats_ospite = calculator._calcola_statistiche_squadra(ospite, in_casa=False)
        
        # Calcolo probabilità RAW (come nel codice)
        peso_casa = 0.6
        peso_ospite = 0.4
        
        prob_casa_raw = (stats_casa['vittorie'] * peso_casa + 
                         (1 - stats_ospite['vittorie']) * peso_ospite) / 2
        
        prob_ospite_raw = (stats_ospite['vittorie'] * peso_ospite + 
                          (1 - stats_casa['vittorie']) * peso_casa) / 2
        
        prob_pareggio_raw = (stats_casa['pareggi'] + stats_ospite['pareggi']) / 2
        
        print(f"   PROBABILITÀ RAW (prima normalizzazione):")
        print(f"      Casa: {prob_casa_raw:.3f} ({prob_casa_raw*100:.1f}%)")
        print(f"      Pareggio: {prob_pareggio_raw:.3f} ({prob_pareggio_raw*100:.1f}%)")
        print(f"      Ospite: {prob_ospite_raw:.3f} ({prob_ospite_raw*100:.1f}%)")
        print(f"      SOMMA: {prob_casa_raw + prob_pareggio_raw + prob_ospite_raw:.3f}")


def test_simmetria_matematica():
    """Test 3: Verifica applicazione simmetria matematica"""
    print("\n" + "="*80)
    print("TEST 3: SIMMETRIA MATEMATICA")
    print("="*80)
    
    partite_test = [
        ('Napoli', 'Juventus'),
        ('Cagliari', 'Roma'),
        ('Lecce', 'Pisa')
    ]
    
    for casa, ospite in partite_test:
        print(f"\n🔍 {casa} vs {ospite}:")
        
        stats_casa = calculator._calcola_statistiche_squadra(casa, in_casa=True)
        stats_ospite = calculator._calcola_statistiche_squadra(ospite, in_casa=False)
        
        # Calcolo probabilità RAW
        peso_casa = 0.6
        peso_ospite = 0.4
        
        prob_casa_raw = (stats_casa['vittorie'] * peso_casa + 
                         (1 - stats_ospite['vittorie']) * peso_ospite) / 2
        prob_ospite_raw = (stats_ospite['vittorie'] * peso_ospite + 
                          (1 - stats_casa['vittorie']) * peso_casa) / 2
        prob_pareggio_raw = (stats_casa['pareggi'] + stats_ospite['pareggi']) / 2
        
        # Prima normalizzazione
        totale = prob_casa_raw + prob_ospite_raw + prob_pareggio_raw
        prob_casa_norm = prob_casa_raw / totale
        prob_ospite_norm = prob_ospite_raw / totale
        prob_pareggio_norm = prob_pareggio_raw / totale
        
        print(f"   DOPO PRIMA NORMALIZZAZIONE:")
        print(f"      Casa: {prob_casa_norm:.3f} ({prob_casa_norm*100:.1f}%)")
        print(f"      Pareggio: {prob_pareggio_norm:.3f} ({prob_pareggio_norm*100:.1f}%)")
        print(f"      Ospite: {prob_ospite_norm:.3f} ({prob_ospite_norm*100:.1f}%)")
        
        # Applica simmetria matematica
        prob_casa_final, prob_ospite_final, prob_pareggio_final = calculator._applica_simmetria_matematica(
            prob_casa_raw, prob_ospite_raw, prob_pareggio_raw, stats_casa, stats_ospite
        )
        
        print(f"   DOPO SIMMETRIA MATEMATICA:")
        print(f"      Casa: {prob_casa_final:.3f} ({prob_casa_final*100:.1f}%)")
        print(f"      Pareggio: {prob_pareggio_final:.3f} ({prob_pareggio_final*100:.1f}%)")
        print(f"      Ospite: {prob_ospite_final:.3f} ({prob_ospite_final*100:.1f}%)")
        print(f"      SOMMA: {prob_casa_final + prob_pareggio_final + prob_ospite_final:.3f}")


def test_calcolo_mercati_ou():
    """Test 4: Verifica calcolo Over/Under 2.5"""
    print("\n" + "="*80)
    print("TEST 4: CALCOLO OVER/UNDER 2.5")
    print("="*80)
    
    from app_professional import _calcola_mercati_deterministici
    
    partite_test = [
        ('Napoli', 'Juventus'),
        ('Lecce', 'Pisa'),
        ('Lazio', 'Bologna')
    ]
    
    for casa, ospite in partite_test:
        print(f"\n🔍 {casa} vs {ospite}:")
        
        # Ottieni predizione 1X2
        predizione, probabilita, confidenza = calculator.predici_partita_deterministica(casa, ospite)
        
        # Calcola mercati (include Over/Under)
        mercati = _calcola_mercati_deterministici(casa, ospite, probabilita)
        
        if 'mou25' in mercati:
            ou25 = mercati['mou25']
            print(f"   OVER/UNDER 2.5:")
            print(f"      Gol previsti: {ou25.get('gol_previsti', 'N/A')}")
            print(f"      Prob Over: {ou25['probabilita']['over']:.3f} ({ou25['probabilita']['over']*100:.1f}%)")
            print(f"      Prob Under: {ou25['probabilita']['under']:.3f} ({ou25['probabilita']['under']*100:.1f}%)")
            print(f"      Consiglio: {ou25['consiglio']}")
            print(f"      Confidenza: {ou25['confidenza']:.3f}")
        else:
            print(f"   ⚠️ Over/Under 2.5 non disponibile")


def test_confronto_con_mercato():
    """Test 5: Confronto probabilità modello vs mercato (quote simulate)"""
    print("\n" + "="*80)
    print("TEST 5: CONFRONTO MODELLO VS MERCATO")
    print("="*80)
    
    # Simuliamo quote realistiche
    partite_test = [
        ('Napoli', 'Juventus', 2.53, 2.94, 3.22, 2.53, 1.48),  # Quote equilibrate
        ('Cagliari', 'Roma', 5.92, 3.64, 1.66, 2.20, 1.67),   # Favorita trasferta
        ('Lecce', 'Pisa', 2.23, 2.99, 3.49, 2.50, 1.50)      # Quote equilibrate
    ]
    
    for casa, ospite, q_casa, q_pareggio, q_ospite, q_over, q_under in partite_test:
        print(f"\n🔍 {casa} vs {ospite}:")
        
        # Predizione modello
        predizione, probabilita, confidenza = calculator.predici_partita_deterministica(casa, ospite)
        
        # Probabilità modello
        prob_model_casa = probabilita['H']
        prob_model_pareggio = probabilita['D']
        prob_model_ospite = probabilita['A']
        
        # Probabilità mercato (da quote)
        total_prob_market = (1/q_casa + 1/q_pareggio + 1/q_ospite)
        prob_market_casa = (1/q_casa) / total_prob_market
        prob_market_pareggio = (1/q_pareggio) / total_prob_market
        prob_market_ospite = (1/q_ospite) / total_prob_market
        
        # Discrepanze
        diff_casa = prob_model_casa - prob_market_casa
        diff_pareggio = prob_model_pareggio - prob_market_pareggio
        diff_ospite = prob_model_ospite - prob_market_ospite
        
        print(f"   MODELLO:")
        print(f"      Casa: {prob_model_casa:.3f} ({prob_model_casa*100:.1f}%)")
        print(f"      Pareggio: {prob_model_pareggio:.3f} ({prob_model_pareggio*100:.1f}%)")
        print(f"      Ospite: {prob_model_ospite:.3f} ({prob_model_ospite*100:.1f}%)")
        
        print(f"   MERCATO (da quote):")
        print(f"      Casa: {prob_market_casa:.3f} ({prob_market_casa*100:.1f}%)")
        print(f"      Pareggio: {prob_market_pareggio:.3f} ({prob_market_pareggio*100:.1f}%)")
        print(f"      Ospite: {prob_market_ospite:.3f} ({prob_market_ospite*100:.1f}%)")
        print(f"      Margine: {(total_prob_market - 1)*100:.1f}%")
        
        print(f"   DISCREPANZE:")
        print(f"      Casa: {diff_casa:+.3f} ({diff_casa*100:+.1f}%)")
        print(f"      Pareggio: {diff_pareggio:+.3f} ({diff_pareggio*100:+.1f}%)")
        print(f"      Ospite: {diff_ospite:+.3f} ({diff_ospite*100:+.1f}%)")
        
        # Trova massima discrepanza
        max_diff = max(abs(diff_casa), abs(diff_pareggio), abs(diff_ospite))
        print(f"      MASSIMA: {max_diff*100:.1f}%")
        
        # Calcola EV
        ev_casa = prob_model_casa * q_casa - 1
        ev_pareggio = prob_model_pareggio * q_pareggio - 1
        ev_ospite = prob_model_ospite * q_ospite - 1
        
        print(f"   EXPECTED VALUE:")
        print(f"      Casa: {ev_casa:+.3f} ({ev_casa*100:+.1f}%)")
        print(f"      Pareggio: {ev_pareggio:+.3f} ({ev_pareggio*100:+.1f}%)")
        print(f"      Ospite: {ev_ospite:+.3f} ({ev_ospite*100:+.1f}%)")


def test_dati_squadre():
    """Test 6: Verifica disponibilità dati per squadre problematiche"""
    print("\n" + "="*80)
    print("TEST 6: DISPONIBILITÀ DATI SQUADRE")
    print("="*80)
    
    squadre_test = ['Pisa', 'Como', 'Cremonese', 'Parma', 'Lecce']
    
    for squadra in squadre_test:
        print(f"\n🔍 {squadra}:")
        
        if calculator.df_features is not None:
            partite_casa = calculator.df_features[calculator.df_features['HomeTeam'] == squadra]
            partite_trasferta = calculator.df_features[calculator.df_features['AwayTeam'] == squadra]
            
            print(f"   Partite in casa: {len(partite_casa)}")
            print(f"   Partite in trasferta: {len(partite_trasferta)}")
            print(f"   TOTALE: {len(partite_casa) + len(partite_trasferta)}")
            
            if len(partite_casa) > 0:
                print(f"   Stagioni casa: {sorted(partite_casa['Season'].unique()) if 'Season' in partite_casa.columns else 'N/A'}")
            if len(partite_trasferta) > 0:
                print(f"   Stagioni trasferta: {sorted(partite_trasferta['Season'].unique()) if 'Season' in partite_trasferta.columns else 'N/A'}")
        else:
            print(f"   ⚠️ DataFrame non disponibile")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🔬 TEST DEBUG PREDIZIONI - ANALISI COMPLETA")
    print("="*80)
    
    # Inizializza sistema
    print("\n📦 Inizializzazione sistema...")
    inizializza_sistema_professionale()
    
    if calculator.df_features is None:
        print("❌ Errore: Sistema non inizializzato correttamente")
        sys.exit(1)
    
    print(f"✅ Sistema inizializzato: {len(calculator.df_features)} partite nel dataset")
    print(f"✅ Squadre disponibili: {len(calculator.squadre_disponibili)}")
    
    # Esegui tutti i test
    test_dati_squadre()
    test_statistiche_base()
    test_probabilita_base()
    test_simmetria_matematica()
    test_calcolo_mercati_ou()
    test_confronto_con_mercato()
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETATI")
    print("="*80)
