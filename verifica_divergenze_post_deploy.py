#!/usr/bin/env python3
"""
Verifica divergenze dopo deploy dataset ampliato
Confronta predizioni locali vs produzione vs quote bookmaker
"""

import requests
import time
from datetime import datetime

RENDER_URL = "https://pronostici-calcio-professional.onrender.com"

def attendi_deploy(max_tentativi=20):
    """Attende che Render completi il deploy"""
    print("⏳ Attesa deploy Render...")
    for i in range(max_tentativi):
        try:
            resp = requests.get(f"{RENDER_URL}/api/status", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                squadre = data.get('squadre_disponibili', 0)
                if squadre >= 20:
                    print(f"✅ Deploy completato! ({squadre} squadre)")
                    return True
            print(f"   Tentativo {i+1}/{max_tentativi}... (status={resp.status_code})")
        except Exception as e:
            print(f"   Tentativo {i+1}/{max_tentativi}... ({e})")
        time.sleep(15)  # Attende 15 secondi tra tentativi
    return False

def ottieni_predizione_render(casa, ospite):
    """Ottiene predizione da Render"""
    try:
        resp = requests.post(
            f"{RENDER_URL}/api/predici",
            json={"casa": casa, "ospite": ospite},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                'predizione': data.get('predizione'),
                'probabilita': data.get('probabilita', {}),
                'confidenza': data.get('confidenza', 0)
            }
    except Exception as e:
        print(f"   ❌ Errore Render: {e}")
    return None

def main():
    print("🔍 VERIFICA DIVERGENZE POST-DEPLOY")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Attende deploy
    if not attendi_deploy():
        print("❌ Timeout deploy - verifica manualmente su Render Dashboard")
        return
    
    print("\n📊 CONFRONTO PREDIZIONI:\n")
    
    partite = [
        ('Lecce', 'Pisa', "Prima divergenza 36.7%"),
        ('Napoli', 'Juventus', "Big match"),
        ('Milan', 'Sassuolo', "Divergenza 50%"),
        ('Atalanta', 'Cagliari', "Divergenza 42%")
    ]
    
    baseline_locale = {
        'Lecce vs Pisa': {'H': 32.6, 'D': 39.8, 'A': 27.6},
        'Napoli vs Juventus': {'H': 46.5, 'D': 30.1, 'A': 23.4},
        'Milan vs Sassuolo': {'H': 47.6, 'D': 31.0, 'A': 21.4},
        'Atalanta vs Cagliari': {'H': 46.9, 'D': 33.2, 'A': 19.9}
    }
    
    for casa, ospite, nota in partite:
        key = f"{casa} vs {ospite}"
        print(f"🏆 {key} ({nota})")
        
        # Baseline locale (già calcolato)
        locale = baseline_locale.get(key, {})
        print(f"   LOCALE:  H={locale.get('H', 0):.1f}% D={locale.get('D', 0):.1f}% A={locale.get('A', 0):.1f}%")
        
        # Predizione Render
        render = ottieni_predizione_render(casa, ospite)
        if render:
            prob = render['probabilita']
            h = prob.get('H', 0) * 100
            d = prob.get('D', 0) * 100
            a = prob.get('A', 0) * 100
            print(f"   RENDER:  H={h:.1f}% D={d:.1f}% A={a:.1f}%")
            
            # Calcola differenza
            if locale:
                diff_h = abs(h - locale['H'])
                diff_d = abs(d - locale['D'])
                diff_a = abs(a - locale['A'])
                max_diff = max(diff_h, diff_d, diff_a)
                
                if max_diff < 1:
                    print(f"   ✅ IDENTICO (diff max {max_diff:.1f}%)")
                elif max_diff < 5:
                    print(f"   ⚠️ LEGGERA DIFF (max {max_diff:.1f}%)")
                else:
                    print(f"   ❌ DIFFERENZA SIGNIFICATIVA (max {max_diff:.1f}%)")
        else:
            print(f"   ❌ RENDER: Non disponibile")
        
        print()
        time.sleep(2)  # Evita rate limiting
    
    print("=" * 60)
    print("✅ Verifica completata!")
    print("\n💡 PROSSIMI PASSI:")
    print("1. Controlla sito web manualmente")
    print("2. Verifica cache Redis invalidata (se divergenze diverse)")
    print("3. Confronta con quote bookmaker per divergenze reali")

if __name__ == "__main__":
    main()
