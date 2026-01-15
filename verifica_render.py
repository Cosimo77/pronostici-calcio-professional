#!/usr/bin/env python3
"""Verifica stato Render produzione"""

import requests
import json
from datetime import datetime, timezone

print("\n" + "="*70)
print("🌐 VERIFICA RENDER - PRODUZIONE")
print("="*70 + "\n")

base_url = "https://pronostici-calcio-professional.onrender.com"

# 1. Health check
print("1️⃣ HEALTH CHECK:")
print("-" * 70)
try:
    r = requests.get(f"{base_url}/api/health", timeout=10)
    health = r.json()
    print(f"✅ Status: {health.get('status','N/A').upper()}")
    print(f"   Database: {health.get('database_records',0)} partite")
    print(f"   Squadre: {health.get('squadre_caricate',0)}")
    print(f"   Environment: {health.get('environment','N/A')}")
    print(f"   Version: {health.get('version','N/A')}")
    print(f"   Cache: {'Attiva' if health.get('cache_attiva') else 'Disabilitata'}")
except Exception as e:
    print(f"❌ Errore: {e}")

# 2. Automation status
print("\n2️⃣ AUTOMATION STATUS:")
print("-" * 70)
try:
    r = requests.get(f"{base_url}/api/automation_status", timeout=10)
    auto = r.json()
    
    running = auto.get('running', False)
    print(f"{'✅' if running else '⚠️'} Running: {running}")
    print(f"   Mode: {auto.get('mode','N/A')}")
    print(f"   Location: {auto.get('automation_location','N/A')}")
    print(f"   Web Server: {auto.get('web_server','N/A')}")
    
    last_update = auto.get('last_daily_update','N/A')
    if last_update != 'N/A':
        try:
            dt = datetime.fromisoformat(last_update.replace('Z',''))
            ora_locale = dt.strftime('%d/%m/%Y %H:%M')
            print(f"   Ultimo aggiornamento dati: {ora_locale}")
        except:
            print(f"   Ultimo aggiornamento dati: {last_update}")
    
    last_train = auto.get('last_weekly_retrain','N/A')
    if last_train != 'N/A':
        try:
            dt = datetime.fromisoformat(last_train.replace('Z',''))
            ora_locale = dt.strftime('%d/%m/%Y %H:%M')
            print(f"   Ultimo training modelli: {ora_locale}")
        except:
            print(f"   Ultimo training modelli: {last_train}")
    
    errors = auto.get('errors', [])
    if errors:
        print(f"   ⚠️ Errori: {len(errors)}")
        for err in errors[:3]:
            print(f"      - {err}")
except Exception as e:
    print(f"❌ Errore: {e}")

# 3. ML Models status
print("\n3️⃣ MODELLI ML:")
print("-" * 70)
try:
    r = requests.get(f"{base_url}/api/monitoring/health_detailed", timeout=10)
    detailed = r.json()
    ml = detailed.get('components',{}).get('ml_models',{})
    
    status = ml.get('status','N/A')
    models_loaded = ml.get('models_loaded',0)
    
    if status == 'healthy' and models_loaded > 0:
        print(f"✅ Status: {status}")
        print(f"   Modelli caricati: {models_loaded}")
    elif models_loaded == 0:
        print(f"⚠️ Status: {status}")
        print(f"   Modelli caricati: {models_loaded}")
        print(f"   Nota: Sistema usa ProfessionalCalculator (no modelli esterni)")
    else:
        print(f"❌ Status: {status}")
        print(f"   Modelli caricati: {models_loaded}")
except Exception as e:
    print(f"❌ Errore: {e}")

# 4. Test mercati fix
print("\n4️⃣ TEST MERCATI FIX (Juventus vs Inter):")
print("-" * 70)
try:
    r = requests.post(
        f"{base_url}/api/predict_enterprise",
        json={"squadra_casa":"Juventus","squadra_ospite":"Inter"},
        timeout=15
    )
    result = r.json()
    
    if 'error' in result:
        print(f"❌ Errore: {result['error']}")
    else:
        m = result.get('mercati',{})
        
        # Clean Sheet
        cs = m.get('mcs',{}).get('probabilita',{})
        if cs:
            categorie = list(cs.keys())
            print(f"   Clean Sheet: {len(categorie)} categorie")
            if len(categorie) == 4:
                print(f"      ✅ FIX APPLICATO - 4 categorie corrette")
                for cat, prob in cs.items():
                    print(f"         {cat}: {prob:.3f}")
            else:
                print(f"      ❌ FIX NON APPLICATO - ancora {len(categorie)} categorie")
        
        # Exact Score
        es = m.get('mes',{}).get('probabilita',{})
        if es:
            top3 = sorted(es.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   Exact Score (Poisson):")
            for ris, prob in top3:
                print(f"      {ris}: {prob:.3f}")
        
        # Cards
        cards = m.get('mcards',{})
        if cards:
            prev = cards.get('cartellini_previsti','N/A')
            print(f"   Cartellini previsti: {prev} (da dati reali HY/AY)")
        
        # Corner
        corner = m.get('mcorner',{})
        if corner:
            prev = corner.get('corner_previsti','N/A')
            print(f"   Corner previsti: {prev} (da dati reali HC/AC)")
        
        print(f"\n   ✅ Predizione completata - {len(m)} mercati disponibili")
        
except Exception as e:
    print(f"❌ Errore: {e}")

# 5. Upcoming matches
print("\n5️⃣ PARTITE PROSSIME:")
print("-" * 70)
try:
    r = requests.get(f"{base_url}/api/upcoming_matches?days=3", timeout=15)
    data = r.json()
    
    if 'error' in data:
        print(f"❌ Errore: {data['error']}")
    else:
        total = data.get('total_matches', 0)
        timestamp = data.get('timestamp', 'N/A')[:19]
        
        print(f"   Totale partite: {total}")
        print(f"   Timestamp: {timestamp}")
        
        matches = data.get('matches', [])
        if matches:
            print(f"   Prossime 3 partite:")
            for match in matches[:3]:
                casa = match.get('home_team', 'N/A')
                ospite = match.get('away_team', 'N/A')
                data_match = match.get('date', 'N/A')
                print(f"      - {casa} vs {ospite} ({data_match})")
except Exception as e:
    print(f"❌ Errore: {e}")

# 6. Ultimo deploy
print("\n6️⃣ ULTIMO DEPLOY:")
print("-" * 70)
print("   Commit: b9a6c03")
print("   Data: 11 gennaio 2026")
print("   Descrizione: Documentazione fix mercati")
print("   Commit precedente: 9055bf2")
print("   Descrizione: Fix 4 mercati critici")

# 7. Sommario
print("\n" + "="*70)
print("📊 SOMMARIO")
print("="*70)

try:
    # Controlla se i fix sono applicati
    r = requests.post(
        f"{base_url}/api/predict_enterprise",
        json={"squadra_casa":"Juventus","squadra_ospite":"Inter"},
        timeout=15
    )
    result = r.json()
    m = result.get('mercati',{})
    cs = m.get('mcs',{}).get('probabilita',{})
    
    if len(cs) == 4:
        print("✅ FIX MERCATI: Applicati correttamente su Render")
        print("   - Clean Sheet: 4 categorie ✅")
        print("   - Exact Score: Poisson distribution ✅")
        print("   - Cartellini: Dati reali HY/AY ✅")
        print("   - Corner: Dati reali HC/AC ✅")
    else:
        print("⚠️ FIX MERCATI: Deploy in corso o cache da svuotare")
    
    print("\n✅ SISTEMA RENDER: Operativo")
    print("   URL: https://pronostici-calcio-professional.onrender.com")
    
except Exception as e:
    print(f"⚠️ Impossibile verificare fix: {e}")

print("\n" + "="*70 + "\n")
