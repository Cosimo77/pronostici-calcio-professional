#!/usr/bin/env python3
"""
🔧 TEST MONITORAGGIO LOCALE
Script per testare il monitoraggio in locale mentre aspettiamo Render
"""

import os
import sys
import time
import requests
from datetime import datetime

def test_local_monitoring():
    """Test della configurazione monitoraggio locale"""
    print("🔍 TEST MONITORAGGIO LOCALE")
    print("=" * 50)
    
    # Test import app
    try:
        sys.path.append('/Users/cosimomassaro/Desktop/pronostici_calcio/web')
        from app_professional import app
        
        print("✅ App importata correttamente")
        print(f"📁 Template folder: {app.template_folder}")
        
        # Test route monitoring
        for rule in app.url_map.iter_rules():
            if 'monitoring' in rule.rule:
                print(f"✅ Route {rule.rule} trovata")
        
        print("\n🚀 Per testare localmente:")
        print("cd /Users/cosimomassaro/Desktop/pronostici_calcio/web")
        print("python -c \"from app_professional import app; app.run(debug=True, host='0.0.0.0', port=5008)\"")
        print("Poi vai su: http://localhost:5008/monitoring")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

def test_render_deployment():
    """Monitora lo stato del deployment Render"""
    print("\n🚀 MONITORAGGIO DEPLOYMENT RENDER")
    print("=" * 50)
    
    print("⏰ Aspettando nuovo deployment...")
    print("🔄 Commit 931f18e: Fix Flask Template Configuration")
    print("📅 Deployment dovrebbe completare in 3-5 minuti")
    
    print("\n📋 COSA ASPETTARSI:")
    print("1. Build in corso (~2 min)")
    print("2. Deploy nuovo codice (~1 min)")  
    print("3. Riavvio servizio (~1 min)")
    print("4. ✅ /monitoring disponibile!")

if __name__ == "__main__":
    test_local_monitoring()
    test_render_deployment()
    
    print(f"\n🕐 Ora: {datetime.now().strftime('%H:%M:%S')}")
    print("⏳ Stima disponibilità: ~5 minuti")
    print("🔗 URL da testare: https://tua-app.onrender.com/monitoring")