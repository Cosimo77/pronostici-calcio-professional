#!/usr/bin/env python3
"""
Test Predizioni Match Oggi - 6 Aprile 2026
Con validazione bookmaker automatica
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
from datetime import datetime

# URL Flask app (locale o produzione)
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

def test_match(home, away):
    """Testa predizione con validazione bookmaker"""

    print(f"\n{'='*60}")
    print(f"🎯 TEST PREDIZIONE: {home} vs {away}")
    print(f"{'='*60}")

    try:
        # Chiamata API validata
        response = requests.post(
            f"{BASE_URL}/api/predict_validated",
            json={
                "squadra_casa": home,
                "squadra_ospite": away
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Errore HTTP {response.status_code}: {response.text}")
            return None

        data = response.json()

        # Display risultati
        print(f"\n📊 PREDIZIONE MODELLO:")
        print(f"  Casa ({home}):      {data['probabilita']['Casa']}%")
        print(f"  Pareggio:           {data['probabilita']['Pareggio']}%")
        print(f"  Trasferta ({away}): {data['probabilita']['Trasferta']}%")
        print(f"  Confidenza:         {data['confidenza']:.3f}")

        # Match info
        match_info = data['match_info']
        print(f"\n🏷️  MATCH TYPE:")
        print(f"  {home}: {match_info['home_tier']}")
        print(f"  {away}: {match_info['away_tier']}")
        print(f"  Classification: {match_info['match_type']}")

        # Bookmaker validation
        validation = data['bookmaker_validation']
        if validation['available']:
            print(f"\n💰 QUOTE BOOKMAKER:")
            print(f"  Casa:      {validation['odds']['H']:.2f} (implied {validation['implied_probabilities']['Casa']}%)")
            print(f"  Pareggio:  {validation['odds']['D']:.2f} (implied {validation['implied_probabilities']['Pareggio']}%)")
            print(f"  Trasferta: {validation['odds']['A']:.2f} (implied {validation['implied_probabilities']['Trasferta']}%)")

            print(f"\n📏 DISCREPANCY (Model - Market):")
            print(f"  Casa:      {validation['discrepancies_pp']['Casa']:+.1f}pp")
            print(f"  Pareggio:  {validation['discrepancies_pp']['Pareggio']:+.1f}pp")
            print(f"  Trasferta: {validation['discrepancies_pp']['Trasferta']:+.1f}pp")
        else:
            print(f"\n⚠️  Quote bookmaker non disponibili")

        # Validation warnings
        if data.get('validation_warning'):
            warning = data['validation_warning']
            print(f"\n{'⚠️ '*20}")
            print(f"🚨 VALIDATION WARNING:")
            print(f"  Type: {warning.get('type', 'N/A')}")
            print(f"  Severity: {warning.get('severity', 'N/A')}")
            print(f"  Message: {warning.get('message', 'N/A')}")
            print(f"  Recommendation: {warning.get('recommendation', 'N/A')}")

            if warning.get('asymmetric_warning'):
                asym = warning['asymmetric_warning']
                print(f"\n  ⚡ Asymmetric Match Alert:")
                print(f"     {asym['message']}")
                print(f"     {asym['recommendation']}")

            print(f"{'⚠️ '*20}")
        else:
            print(f"\n✅ No validation warnings - Model aligned with market")

        print(f"\n{'='*60}\n")

        return data

    except requests.exceptions.Timeout:
        print(f"❌ Timeout - Server potrebbe essere offline")
        return None
    except Exception as e:
        print(f"❌ Errore: {e}")
        return None


def run_today_tests():
    """Testa tutti i match di oggi"""

    print(f"\n🚀 TEST SUITE - Match 6 Aprile 2026\n")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}\n")

    # Match oggi (dalla API odds verificata prima)
    today_matches = [
        ('Juventus', 'Genoa'),      # 16:00 - Top vs Mid
        ('Napoli', 'AC Milan'),     # 18:45 - Top vs Top
    ]

    results = []

    for home, away in today_matches:
        result = test_match(home, away)
        if result:
            results.append({
                'match': f"{home} vs {away}",
                'warning': result.get('validation_warning') is not None,
                'bookmaker_available': result['bookmaker_validation']['available']
            })

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Total matches tested: {len(results)}")
    print(f"With warnings: {sum(1 for r in results if r['warning'])}")
    print(f"Bookmaker data available: {sum(1 for r in results if r['bookmaker_available'])}")

    if any(r['warning'] for r in results):
        print(f"\n⚠️  Review recommended before betting on flagged matches!")

    print(f"\n✅ Test suite completato")
    print(f"📂 Predizioni registrate in: tracking_predictions_live.csv")


if __name__ == '__main__':
    # Check se server è online
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server online: {BASE_URL}")
        else:
            print(f"⚠️  Server risponde ma con status {response.status_code}")
    except:
        print(f"❌ Server non raggiungibile: {BASE_URL}")
        print(f"   Assicurati che Flask app sia in esecuzione:")
        print(f"   $ python web/app_professional.py")
        sys.exit(1)

    run_today_tests()
