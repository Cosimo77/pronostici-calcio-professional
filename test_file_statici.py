#!/usr/bin/env python3
"""
Test Specifico File Statici
Verifica che CSS e JS siano accessibili
"""

import requests
import sys

def test_static_file(url, nome_file, tipo_content):
    """Testa un singolo file statico"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            size = len(response.content)
            print(f"✅ {nome_file}: OK ({size} bytes, {content_type})")
            if tipo_content in content_type:
                return True
            else:
                print(f"   ⚠️ Content-Type inaspettato: {content_type}")
                return False
        else:
            print(f"❌ {nome_file}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {nome_file}: Errore - {e}")
        return False

def main():
    """Test principale per file statici"""
    print("🎨 Test File Statici Sistema Pronostici")
    print("=" * 50)
    
    base_url = "http://localhost:5003"
    successi = 0
    test_totali = 0
    
    # Test file CSS
    print("\n🎨 Test File CSS:")
    test_totali += 1
    if test_static_file(f"{base_url}/static/css/style.css", "style.css", "text/css"):
        successi += 1
    
    # Test file JS
    print("\n📜 Test File JavaScript:")
    
    test_totali += 1
    if test_static_file(f"{base_url}/static/js/main.js", "main.js", "javascript"):
        successi += 1
    
    test_totali += 1
    if test_static_file(f"{base_url}/static/js/autotest.js", "autotest.js", "javascript"):
        successi += 1
    
    test_totali += 1
    if test_static_file(f"{base_url}/static/js/test.js", "test.js", "javascript"):
        successi += 1
    
    # Test path alternativi
    print("\n🔄 Test Path Alternativi:")
    
    test_totali += 1
    if test_static_file(f"{base_url}/css/style.css", "style.css (alt)", "text/css"):
        successi += 1
    
    test_totali += 1
    if test_static_file(f"{base_url}/js/main.js", "main.js (alt)", "javascript"):
        successi += 1
    
    # Risultati
    print("\n" + "=" * 50)
    print(f"📊 RISULTATI: {successi}/{test_totali} file statici accessibili")
    
    if successi == test_totali:
        print("🎉 TUTTI I FILE STATICI FUNZIONANTI!")
        print("\n✨ I CSS e JavaScript sono ora caricati correttamente")
        return 0
    else:
        print(f"⚠️ {test_totali - successi} file non accessibili")
        return 1

if __name__ == "__main__":
    sys.exit(main())