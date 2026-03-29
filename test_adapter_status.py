#!/usr/bin/env python3
"""
Test diagnostico: verifica perché DiarioStorage usa CSV invece di PostgreSQL
"""

import os
import sys

# Setup environment per simulare Render
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://test')

print("🔍 TEST DIARIO STORAGE ADAPTER\n")
print("="*60)

# Test 1: Verifica DATABASE_URL
database_url = os.getenv('DATABASE_URL')
print(f"\n1️⃣ DATABASE_URL presente: {'✅' if database_url else '❌'}")
if database_url:
    print(f"   Lunghezza: {len(database_url)} caratteri")
    print(f"   Provider: {'Neon' if 'neon.tech' in database_url else 'Unknown'}")

# Test 2: Import database module
print(f"\n2️⃣ Import database module...")
try:
    from database import is_db_available, init_db
    print("   ✅ Import riuscito")
except ImportError as e:
    print(f"   ❌ Import fallito: {e}")
    sys.exit(1)

# Test 3: Stato PRIMA di init_db()
print(f"\n3️⃣ is_db_available() PRIMA di init_db():")
print(f"   Result: {is_db_available()}")

# Test 4: Chiamata init_db()
print(f"\n4️⃣ Chiamata init_db()...")
try:
    success = init_db()
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
except Exception as e:
    print(f"   ❌ Exception: {e}")
    success = False

# Test 5: Stato DOPO init_db()
print(f"\n5️⃣ is_db_available() DOPO init_db():")
print(f"   Result: {is_db_available()}")

# Test 6: DiarioStorage adapter check
print(f"\n6️⃣ DiarioStorage._use_database():")
try:
    from web.diario_storage import DiarioStorage
    use_db = DiarioStorage._use_database()
    print(f"   Result: {use_db}")
    print(f"   ✅ Userà {'PostgreSQL' if use_db else 'CSV fallback'}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 7: Count bet da entrambe le sorgenti
print(f"\n7️⃣ Count bet:")
try:
    if is_db_available():
        from database import BetModel
        db_count = len(BetModel.get_all())
        print(f"   PostgreSQL: {db_count} bet")
    else:
        print(f"   PostgreSQL: Non disponibile")
        
    import pandas as pd
    if os.path.exists('tracking_giocate.csv'):
        df = pd.read_csv('tracking_giocate.csv')
        csv_count = len(df)
        print(f"   CSV: {csv_count} bet")
    else:
        print(f"   CSV: File non trovato")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "="*60)
print("🎯 CONCLUSIONE:")
if is_db_available():
    print("✅ PostgreSQL disponibile e configurato correttamente")
else:
    print("❌ PostgreSQL NON disponibile - usando CSV fallback")
    print("   Possibili cause:")
    print("   - init_db() non chiamato durante app startup")
    print("   - Errore connessione a Neon")
    print("   - DATABASE_URL non esportata correttamente")
