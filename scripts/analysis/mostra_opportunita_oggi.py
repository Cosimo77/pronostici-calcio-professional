#!/usr/bin/env python3
"""
Mostra opportunità di scommessa FASE 2 validate per oggi
"""

import requests
import json
from datetime import datetime

def mostra_opportunita():
    """Estrae e mostra opportunità validate"""
    
    url = "https://pronostici-calcio-pro.onrender.com/api/upcoming_matches"
    
    print("📡 Connessione API...")
    response = requests.get(url)
    data = response.json()
    
    matches = data.get('matches', [])
    
    print("\n" + "="*70)
    print("🎯 OPPORTUNITÀ FASE 2 VALIDATE (Backtest ROI Positivo)")
    print("="*70)
    
    opportunita_trovate = 0
    
    for match in matches:
        vb = match.get('value_betting', {})
        
        # Verifica se ha opportunità FASE 2 validate
        if vb.get('fase2_validated') and vb.get('fase2_total_opportunities', 0) > 0:
            opportunita_trovate += 1
            
            home = match.get('home_team_display', match.get('home_team'))
            away = match.get('away_team_display', match.get('away_team'))
            time = match.get('commence_time', 'N/A')
            
            print(f"\n{'='*70}")
            print(f"📊 PARTITA #{opportunita_trovate}: {home} vs {away}")
            print(f"📅 Orario: {time}")
            print(f"{'='*70}")
            
            # Mostra ogni opportunità validata
            opps = vb.get('fase2_opportunities', [])
            for i, opp in enumerate(opps, 1):
                market = opp.get('market', 'N/A')
                outcome = opp.get('outcome', 'N/A')
                odds = opp.get('odds', 0)
                ev = opp.get('ev', 0)
                prob_model = opp.get('prob_model', 0)
                roi_backtest = opp.get('roi_backtest', 0)
                strategy = opp.get('strategy', 'N/A')
                
                print(f"\n   ✅ OPPORTUNITÀ #{i}:")
                print(f"      Mercato: {market}")
                print(f"      Esito: {outcome}")
                print(f"      Quota Bookmaker: {odds:.2f}")
                print(f"      Probabilità Modello: {prob_model:.1f}%")
                print(f"      Expected Value: {ev:+.1f}%")
                print(f"      📈 ROI Backtest: {roi_backtest:+.2f}%")
                print(f"      Strategia: {strategy}")
                print(f"      {'─'*60}")
    
    if opportunita_trovate == 0:
        print("\n⚠️  NESSUNA OPPORTUNITÀ VALIDATA AL MOMENTO")
        print("\n📋 Motivi possibili:")
        print("   • Filtri FASE 2 molto conservativi (ROI backtest +7% a +75%)")
        print("   • Quote fuori range ottimale")
        print("   • Expected Value sotto soglia minima")
        print("   • Nessuna discrepanza significativa modello vs mercato")
        print("\n💡 Suggerimento:")
        print("   Attendi nuove partite o quote più favorevoli")
    else:
        print(f"\n{'='*70}")
        print(f"📊 RIEPILOGO: {opportunita_trovate} partita/e con opportunità validate")
        print(f"{'='*70}")
        
        # Legenda strategie
        print("\n📖 LEGENDA STRATEGIE:")
        print("   • FASE1_PAREGGIO: Solo pareggi, quote 2.8-3.5, EV ≥25%")
        print("                      ROI Backtest: +7.17%, Win Rate: 31%")
        print("   • FASE2_DOUBLE_CHANCE: Quote 1.2-1.8, EV ≥10%")
        print("                           ROI Backtest: +75.21%, Win Rate: 75%")
        print("   • FASE2_OVER_UNDER: Quote 2.0-2.5, EV ≥15%")
        print("                        ROI Backtest: +5.86%, Win Rate: 46.5%")
        
        print("\n⚠️  DISCLAIMER:")
        print("   Performance passate non garantiscono risultati futuri")
        print("   Gestisci sempre il rischio (max 2% bankroll per trade)")
    
    # Info API quota
    api_quota = data.get('api_quota', {})
    quota_used = api_quota.get('used', '?')
    quota_remaining = api_quota.get('remaining', '?')
    print(f"\n📊 API Quota: {quota_used}/500 usate, {quota_remaining} rimanenti")
    print("="*70 + "\n")

if __name__ == "__main__":
    mostra_opportunita()
