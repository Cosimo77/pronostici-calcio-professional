#!/usr/bin/env python3
"""Test server Flask e API endpoints"""

import requests
import json
from datetime import datetime
import sys

print("🔍 VERIFICA 8/9: THE ODDS API & SERVER FLASK")
print("=" * 60)
print()

# Test 1: Server Flask online
print("📡 Test connessione server Flask...")
try:
    response = requests.get('http://localhost:5008/api/diario/stats', timeout=5)
    if response.status_code == 200:
        print("✅ Server Flask online")
        stats = response.json()
        print(f"  Endpoint /api/diario/stats: OK")
        print(f"    Puntate totali: {stats.get('total', 0)}")
        print(f"    Bankroll: €{stats.get('bankroll_corrente', 0):.2f}")
    else:
        print(f"❌ Server risponde con status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: Server offline o non raggiungibile: {e}")
    sys.exit(1)

print()

# Test 2: Endpoint opportunità
print("📊 Test endpoint opportunità...")
try:
    response = requests.get('http://localhost:5008/api/upcoming_matches', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print("✅ Endpoint /api/upcoming_matches: OK")
        print(f"  Partite disponibili: {len(data.get('matches', []))}")
        print(f"  Timestamp: {data.get('timestamp', 'N/A')[:19]}")
        print(f"  API calls rimanenti: {data.get('quota_rimanente', 'N/A')}")
        
        if len(data.get('matches', [])) > 0:
            match = data['matches'][0]
            print(f"\n  Esempio partita:")
            print(f"    {match['home_team']} vs {match['away_team']}")
            print(f"    Quote: {match.get('odds_home', 0):.2f} / {match.get('odds_draw', 0):.2f} / {match.get('odds_away', 0):.2f}")
            print(f"    EV Realistico: {match.get('ev_realistico', 0):.1f}%")
            print(f"    Bookmakers: {match.get('num_bookmakers', 0)}")
            print("✅ Quote reali presenti")
        else:
            print("  ⚠️  Nessuna partita disponibile (normale se non ci sono match imminenti)")
    else:
        print(f"❌ Endpoint risponde con status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: Errore endpoint opportunità: {e}")
    sys.exit(1)

print()

# Test 3: Kelly Calculator API
print("🧮 Test endpoint Kelly Calculator...")
try:
    payload = {'prob_win': 0.40, 'quota': 2.50}
    response = requests.post('http://localhost:5008/api/calculate_kelly', 
                            json=payload, timeout=5)
    if response.status_code == 200:
        kelly = response.json()
        print("✅ Endpoint /api/calculate_kelly: OK")
        print(f"  Input: Prob {payload['prob_win']*100:.0f}%, Quota {payload['quota']}")
        print(f"  Kelly stake: €{kelly.get('kelly_stake', 0):.2f}")
        print(f"  Expected Value: {kelly.get('expected_value', 0):.1f}%")
    else:
        print(f"❌ Kelly API risponde con status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: Errore Kelly API: {e}")
    sys.exit(1)

print()

# Test 4: Equity Curve API
print("📈 Test endpoint Equity Curve...")
try:
    response = requests.get('http://localhost:5008/api/equity_curve', timeout=5)
    if response.status_code == 200:
        equity = response.json()
        print("✅ Endpoint /api/equity_curve: OK")
        print(f"  Labels: {len(equity.get('labels', []))}")
        print(f"  Bankroll curve: {len(equity.get('bankroll_curve', []))}")
    else:
        print(f"❌ Equity curve risponde con status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: Errore Equity Curve API: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ TUTTI GLI ENDPOINT FUNZIONANTI")
print("=" * 60)
