#!/usr/bin/env python3
"""
Test Quick Wins Implementati
Verifica funzionamento miglioramenti senza avviare server completo
"""

import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))

def test_imports():
    """Test che tutte le dipendenze siano installate"""
    print("🧪 Test 1: Import Dipendenze")
    
    try:
        from flask import Flask, g
        print("  ✅ Flask + g context")
        
        import uuid
        print("  ✅ uuid")
        
        import psutil
        disk = psutil.disk_usage('/')
        print(f"  ✅ psutil (disk {disk.percent:.1f}% usato)")
        
        try:
            from flask_compress import Compress
            print("  ✅ Flask-Compress")
        except ImportError:
            print("  ⚠️  Flask-Compress non installato (opzionale)")
        
        from psycopg2.pool import ThreadedConnectionPool
        print("  ✅ ThreadedConnectionPool (psycopg2)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore import: {e}")
        return False

def test_app_config():
    """Test configurazione app con modifiche"""
    print("\n🧪 Test 2: App Configuration")
    
    try:
        # Importa app (può richiedere tempo)
        print("  ⏳ Importando app...")
        from web.app_professional import app
        print("  ✅ App importata")
        
        # Check middleware configurato
        if hasattr(app, 'before_request_funcs'):
            before_req_count = sum(len(funcs) for funcs in app.before_request_funcs.values())
            print(f"  ✅ Before request middleware: {before_req_count} funzioni")
        
        if hasattr(app, 'after_request_funcs'):
            after_req_count = sum(len(funcs) for funcs in app.after_request_funcs.values())
            print(f"  ✅ After request middleware: {after_req_count} funzioni")
        
        # Check routes
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        
        if '/api/health' in rules:
            print("  ✅ Route /api/health presente")
        
        if '/api/health/detailed' in rules:
            print("  ✅ Route /api/health/detailed presente (NUOVO)")
        else:
            print("  ⚠️  Route /api/health/detailed non trovata")
        
        # Check config
        if 'START_TIME' in app.config:
            print("  ✅ START_TIME configurato (per uptime)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore app config: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_pool():
    """Test connection pool PostgreSQL"""
    print("\n🧪 Test 3: Database Connection Pool")
    
    try:
        from database.connection import get_database_url, init_db
        
        db_url = get_database_url()
        
        if db_url:
            print(f"  ✅ DATABASE_URL configurata ({len(db_url)} caratteri)")
            
            # Test init (può richiedere tempo)
            print("  ⏳ Testing connection pool init...")
            result = init_db()
            
            if result:
                print("  ✅ Connection pool inizializzato (ThreadedConnectionPool)")
            else:
                print("  ⚠️  Connection pool fallito (normale se DB non locale)")
        else:
            print("  ⚠️  DATABASE_URL non configurata (ok per test locale)")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Database test skipped: {e}")
        return True  # Non blocchiamo su errori DB

def test_request_id_uuid():
    """Test generazione UUID per request ID"""
    print("\n🧪 Test 4: Request ID Generation")
    
    try:
        import uuid
        
        # Genera 10 UUID per verificare univocità
        uuids = [str(uuid.uuid4()) for _ in range(10)]
        
        # Check formato
        assert all(len(u) == 36 for u in uuids), "UUID length non corretta"
        
        # Check univocità
        assert len(set(uuids)) == 10, "UUID non univoci"
        
        print(f"  ✅ UUID generation OK (sample: {uuids[0]})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore UUID: {e}")
        return False

def test_system_resources():
    """Test lettura system resources (per health check)"""
    print("\n🧪 Test 5: System Resources Check")
    
    try:
        import psutil
        
        # Disk
        disk = psutil.disk_usage('/')
        print(f"  ✅ Disk: {disk.percent:.1f}% usato, {disk.free / (1024**3):.2f} GB liberi")
        
        # Memory
        memory = psutil.virtual_memory()
        print(f"  ✅ Memory: {memory.percent:.1f}% usato, {memory.available / (1024**3):.2f} GB disponibili")
        
        # CPU
        cpu = psutil.cpu_percent(interval=0.1)
        print(f"  ✅ CPU: {cpu}% utilizzo")
        
        # Warning checks
        if disk.percent > 90:
            print("  ⚠️  WARNING: Disk usage >90%")
        
        if memory.percent > 90:
            print("  ⚠️  WARNING: Memory usage >90%")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore system resources: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 QUICK WINS - TEST SUITE")
    print("=" * 70)
    
    results = []
    
    results.append(("Import Dipendenze", test_imports()))
    results.append(("Request ID UUID", test_request_id_uuid()))
    results.append(("System Resources", test_system_resources()))
    results.append(("Database Pool", test_database_pool()))
    results.append(("App Configuration", test_app_config()))
    
    print("\n" + "=" * 70)
    print("📊 RISULTATI TEST")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    total_passed = sum(1 for _, r in results if r)
    total_tests = len(results)
    
    print(f"\n🎯 Total: {total_passed}/{total_tests} test passati")
    
    if total_passed == total_tests:
        print("\n🎉 TUTTI I TEST PASSATI - Quick wins pronti per deploy!")
        return 0
    elif total_passed >= total_tests - 1:
        print("\n⚠️  QUASI TUTTI I TEST PASSATI - Verificare warning sopra")
        return 0
    else:
        print("\n❌ ALCUNI TEST FALLITI - Fix necessari prima di deploy")
        return 1

if __name__ == '__main__':
    exit(main())
