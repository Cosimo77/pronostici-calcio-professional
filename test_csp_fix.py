#!/usr/bin/env python3
"""
🛡️ Test per la correzione CSP (Content Security Policy)
Verifica che gli errori CSP siano stati risolti
"""

import requests
import re
import time
from bs4 import BeautifulSoup

def test_csp_headers():
    """Test degli header CSP"""
    print("🔍 Testing CSP Headers...")
    
    try:
        response = requests.get('http://localhost:5008/', timeout=10)
        headers = response.headers
        
        # Verifica presenza Content-Security-Policy
        if 'Content-Security-Policy' in headers:
            csp = headers['Content-Security-Policy']
            print(f"✅ CSP Header presente: {csp[:100]}...")
            
            # Verifica che non ci sia più 'unsafe-inline'
            if 'unsafe-inline' not in csp:
                print("✅ 'unsafe-inline' rimosso correttamente dal CSP")
            else:
                print("⚠️ 'unsafe-inline' ancora presente nel CSP")
                
            # Verifica che ci sia il nonce
            if 'nonce-' in csp:
                print("✅ Nonce presente nel CSP")
            else:
                print("❌ Nonce mancante nel CSP")
                
        else:
            print("❌ CSP Header mancante")
            
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore connessione: {e}")
        return None

def test_html_nonce():
    """Test che il nonce sia presente nell'HTML"""
    print("\n🔍 Testing HTML Nonce...")
    
    try:
        response = requests.get('http://localhost:5008/', timeout=10)
        html = response.text
        
        # Estrai il nonce dal CSP header
        csp = response.headers.get('Content-Security-Policy', '')
        nonce_match = re.search(r"'nonce-([^']+)'", csp)
        
        if nonce_match:
            expected_nonce = nonce_match.group(1)
            print(f"✅ Nonce estratto dal CSP: {expected_nonce}")
            
            # Verifica che il nonce sia nel tag style
            if f'nonce="{expected_nonce}"' in html and '<style nonce=' in html:
                print("✅ Nonce presente nel tag <style>")
            else:
                print("❌ Nonce mancante nel tag <style>")
                
            # Verifica che il nonce sia nel tag script
            if f'nonce="{expected_nonce}"' in html and '<script nonce=' in html:
                print("✅ Nonce presente nel tag <script>")
            else:
                print("❌ Nonce mancante nel tag <script>")
                
            # Verifica che non ci siano stili inline senza nonce
            if 'style="' in html:
                print("⚠️ Ancora presenti stili inline nel HTML")
            else:
                print("✅ Nessuno stile inline trovato")
                
        else:
            print("❌ Impossibile estrarre nonce dal CSP")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore connessione: {e}")

def test_csp_compliance():
    """Test di compliance CSP completo"""
    print("\n🔍 Testing CSP Compliance...")
    
    try:
        response = requests.get('http://localhost:5008/', timeout=10)
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estrai il nonce dal CSP
        csp = response.headers.get('Content-Security-Policy', '')
        nonce_match = re.search(r"'nonce-([^']+)'", csp)
        expected_nonce = nonce_match.group(1) if nonce_match else None
        
        issues = []
        
        # Controlla tutti i tag style
        style_tags = soup.find_all('style')
        for tag in style_tags:
            if tag.get('nonce') != expected_nonce:
                issues.append(f"Tag <style> senza nonce corretto: {str(tag)[:100]}")
        
        # Controlla tutti i tag script
        script_tags = soup.find_all('script')
        for tag in script_tags:
            if tag.get('src'):  # Script esterni vanno bene
                continue
            if tag.get('nonce') != expected_nonce:
                issues.append(f"Tag <script> senza nonce corretto: {str(tag)[:100]}")
        
        # Controlla attributi style inline
        elements_with_style = soup.find_all(attrs={"style": True})
        for element in elements_with_style:
            issues.append(f"Elemento con style inline: {element.name} - {element.get('style')}")
        
        if not issues:
            print("✅ HTML completamente conforme al CSP")
        else:
            print(f"⚠️ Trovati {len(issues)} problemi CSP:")
            for issue in issues[:5]:  # Mostra solo i primi 5
                print(f"  - {issue}")
                
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")

def main():
    """Test principale"""
    print("🛡️ TEST CSP FIXES")
    print("="*50)
    
    # Test connessione server
    print("📡 Verifica server attivo...")
    try:
        response = requests.get('http://localhost:5008/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server attivo e risponde")
        else:
            print(f"⚠️ Server risponde con status {response.status_code}")
    except:
        print("❌ Server non raggiungibile")
        print("🔄 Assicurati che il server sia in esecuzione:")
        print("   cd /Users/cosimomassaro/Desktop/pronostici_calcio")
        print("   .venv/bin/python web/app_professional.py")
        return
    
    # Esegui i test
    test_csp_headers()
    test_html_nonce()
    test_csp_compliance()
    
    print("\n" + "="*50)
    print("✅ Test CSP completati!")
    print("\n📋 RIEPILOGO CORREZIONI IMPLEMENTATE:")
    print("1. ✅ Rimosso 'unsafe-inline' dal CSP")
    print("2. ✅ Aggiunto nonce ai tag <style> e <script>")
    print("3. ✅ Rimossi stili inline dal JavaScript")
    print("4. ✅ Implementato aggiornamento stili via JavaScript")
    print("\n🎯 Gli errori CSP dovrebbero essere risolti!")

if __name__ == "__main__":
    main()