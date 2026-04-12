#!/usr/bin/env python3
"""
Test verifica deploy modello calibrato in produzione
"""
import requests
import json

PROD_URL = "https://pronostici-calcio-pro.onrender.com"

def test_health():
    """Verifica health endpoint"""
    print("🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{PROD_URL}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data}")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return False

def test_prediction_calibrated():
    """Test predizione con modello calibrato - match equilibrato"""
    print("\n🔍 Test 2: Predizione Match Equilibrato (Fiorentina vs Inter)")
    try:
        # Match test: dovrebbe dare pareggio ~35-40% (vs <3% pre-calibrazione)
        response = requests.post(
            f"{PROD_URL}/api/predict_enterprise",
            json={
                "home_team": "Fiorentina",
                "away_team": "Inter"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            prob = data.get('probabilita', {})
            
            print(f"   Probabilità:")
            print(f"     Casa:      {prob.get('H', 0)*100:.1f}%")
            print(f"     Pareggio:  {prob.get('D', 0)*100:.1f}%")
            print(f"     Trasferta: {prob.get('A', 0)*100:.1f}%")
            
            # Verifica somma = 1.0
            somma = sum(prob.values())
            print(f"   Somma: {somma:.4f}")
            
            # Check calibrazione: pareggio match equilibrati dovrebbe essere ~35-40%
            pareggio_pct = prob.get('D', 0) * 100
            if pareggio_pct > 30:
                print(f"   ✅ CALIBRAZIONE OK! Pareggio {pareggio_pct:.1f}% (atteso ~35-40%)")
                return True
            else:
                print(f"   ⚠️ Pareggio {pareggio_pct:.1f}% (atteso >30%, probabile modello vecchio)")
                return False
        else:
            print(f"   ❌ Status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return False

def test_probability_sum():
    """Test somma probabilità = 1.0 (calibrazione corretta)"""
    print("\n🔍 Test 3: Validazione Matematica Probabilità")
    try:
        response = requests.post(
            f"{PROD_URL}/api/predict_enterprise",
            json={
                "home_team": "Juventus",
                "away_team": "Napoli"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            prob = data.get('probabilita', {})
            somma = sum(prob.values())
            
            print(f"   Somma probabilità: {somma:.6f}")
            if abs(somma - 1.0) < 0.001:
                print(f"   ✅ Matematicamente corretta!")
                return True
            else:
                print(f"   ❌ Somma non corretta (dovrebbe essere 1.0)")
                return False
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return False

def main():
    print("=" * 60)
    print("🚀 TEST DEPLOY MODELLO CALIBRATO - PRODUCTION")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health
    results.append(("Health API", test_health()))
    
    # Test 2: Calibrazione pareggi
    results.append(("Calibrazione Pareggi", test_prediction_calibrated()))
    
    # Test 3: Somma prob
    results.append(("Validazione Matematica", test_probability_sum()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Score: {passed}/{total}")
    
    if passed == total:
        print("\n✅ DEPLOY SUCCESSO! Modello calibrato in produzione!")
    else:
        print("\n⚠️ Alcuni test falliti - verifica deploy logs su Render")

if __name__ == "__main__":
    main()
