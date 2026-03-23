#!/usr/bin/env python3
"""
Script Completo: Aggiornamento Dati + Reload App
================================================

COSA FA:
1. Scarica dati freschi da football-data.co.uk
2. Rigenera dataset_pulito.csv consolidato
3. Rigenera dataset_features.csv con features ML
4. Triggera reload dataset su app Render (se in produzione)

USO:
    # Locale:
    python3 scripts/update_dataset_and_reload.py
    
    # Con reload Render:
    python3 scripts/update_dataset_and_reload.py --reload-render
    
    # Cron job (ogni giorno alle 6:00):
    0 6 * * * cd /path/to/pronostici_calcio && python3 scripts/update_dataset_and_reload.py --reload-render >> logs/update.log 2>&1
"""

import sys
import os
import subprocess
import argparse
import requests
from datetime import datetime
from pathlib import Path

# Aggiungi root al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

def print_header(text):
    """Print con header decorato"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def run_script(script_name, description):
    """Esegue script Python e cattura output"""
    print(f"\n📌 {description}...")
    script_path = ROOT_DIR / 'scripts' / script_name
    
    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minuti max
        )
        
        if result.returncode == 0:
            # Mostra solo righe con status
            for line in result.stdout.split('\n'):
                if any(x in line for x in ['✅', '❌', '⚠️', 'Totale', 'Ultima', 'partite']):
                    print(f"   {line}")
            print(f"✅ {description} completato")
            return True
        else:
            print(f"❌ Errore {description}:")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout {description} (>5 minuti)")
        return False
    except Exception as e:
        print(f"❌ Errore esecuzione {description}: {e}")
        return False

def trigger_render_reload(render_url="https://pronostici-calcio-professional.onrender.com"):
    """Triggera reload dataset su app Render via API"""
    print(f"\n📡 Triggering reload su Render: {render_url}...")
    
    try:
        endpoint = f"{render_url}/api/reload_dataset"
        response = requests.post(endpoint, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Reload Render completato:")
            print(f"   • Partite totali: {data['data']['partite_totali']}")
            print(f"   • Ultima partita: {data['data']['ultima_partita']}")
            print(f"   • Squadre: {data['data']['squadre']}")
            return True
        else:
            print(f"❌ Errore reload Render (HTTP {response.status_code}):")
            print(f"   {response.text[:200]}")
            return False
            
    except requests.Timeout:
        print("⚠️ Timeout reload Render (server in sleep mode? Riprova tra 1 min)")
        return False
    except Exception as e:
        print(f"❌ Errore reload Render: {e}")
        return False

def verify_dataset_updated():
    """Verifica che dataset sia aggiornato correttamente"""
    print("\n🔍 Verifica dataset aggiornato...")
    
    try:
        import pandas as pd
        
        # Check dataset_pulito.csv
        df_path = ROOT_DIR / 'data' / 'dataset_pulito.csv'
        if not df_path.exists():
            print("❌ dataset_pulito.csv non trovato")
            return False
        
        df = pd.read_csv(df_path)
        ultima_partita = df['Date'].max()
        totale_partite = len(df)
        
        print(f"✅ Dataset verificato:")
        print(f"   • Totale partite: {totale_partite}")
        print(f"   • Ultima partita: {ultima_partita}")
        
        # Check se più recente di 7 giorni
        from datetime import datetime, timedelta
        ultima_date = datetime.strptime(ultima_partita, '%Y-%m-%d')
        days_old = (datetime.now() - ultima_date).days
        
        if days_old > 7:
            print(f"⚠️ Dataset vecchio di {days_old} giorni (considera aggiornamento manuale)")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore verifica dataset: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Aggiorna dataset e ricarica app')
    parser.add_argument('--reload-render', action='store_true', 
                       help='Triggera reload su app Render dopo update')
    parser.add_argument('--render-url', default='https://pronostici-calcio-professional.onrender.com',
                       help='URL app Render (default: production)')
    args = parser.parse_args()
    
    print_header(f"🚀 AGGIORNAMENTO DATASET - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # STEP 1: Download dati freschi
    success_download = run_script(
        'aggiorna_stagione_corrente.py',
        'Download dati Serie A'
    )
    
    if not success_download:
        print("\n❌ FALLITO: Download dati. Aborting.")
        return 1
    
    # STEP 2: Consolida dataset
    print_header("📊 CONSOLIDAMENTO DATASET")
    
    # Usa aggiorna_automatico.py che fa tutto in un colpo
    success_consolidate = run_script(
        'aggiorna_automatico.py',
        'Consolidamento dataset + features'
    )
    
    if not success_consolidate:
        print("\n⚠️ WARNING: Consolidamento con errori. Tento verifica manuale...")
    
    # STEP 3: Verifica dataset
    if not verify_dataset_updated():
        print("\n❌ FALLITO: Verifica dataset. Check manuale richiesto.")
        return 1
    
    # STEP 4: Reload Render (se richiesto)
    if args.reload_render:
        print_header("🌐 RELOAD APP RENDER")
        
        success_reload = trigger_render_reload(args.render_url)
        
        if not success_reload:
            print("\n⚠️ WARNING: Reload Render fallito. Dataset locale aggiornato comunque.")
            print("   Riprova manualmente: curl -X POST " + args.render_url + "/api/reload_dataset")
            return 2
    
    # SUCCESS
    print_header("✅ AGGIORNAMENTO COMPLETATO CON SUCCESSO")
    print(f"\n📅 Dataset aggiornato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.reload_render:
        print("🌐 App Render ricaricata con nuovi dati")
    else:
        print("💡 Per ricaricare Render: curl -X POST " + args.render_url + "/api/reload_dataset")
    
    print("\n🎯 Sistema pronto per predizioni aggiornate!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
