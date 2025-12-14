#!/usr/bin/env python3
"""
🔄 AGGIORNAMENTO E ALLENAMENTO UNIFICATO
Script completo che:
1. Scarica nuovi dati da football-data.co.uk
2. Aggiorna dataset pulito
3. Rigenera features
4. Riaddestra modelli ML
5. Pulisce cache

Uso: python3 aggiorna_e_allena.py [--force]
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime
import pickle
import numpy as np
from pathlib import Path
import argparse

# Aggiungi scripts al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def print_header(title):
    """Stampa intestazione sezione"""
    print(f"\n{'='*60}")
    print(f"🔄 {title}")
    print(f"{'='*60}")

def print_step(num, desc):
    """Stampa step corrente"""
    print(f"\n📌 STEP {num}: {desc}")
    print("-" * 50)

def scarica_stagione(anno_inizio, anno_fine):
    """Scarica dati di una stagione"""
    stagione_str = f"{anno_inizio}{anno_fine}"
    url = f"https://www.football-data.co.uk/mmz4281/{stagione_str}/I1.csv"
    file_path = f"data/I1_{stagione_str}.csv"
    
    try:
        print(f"   📥 Scaricamento stagione {anno_inizio}-{anno_fine}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Salva il file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Verifica
        df = pd.read_csv(file_path)
        print(f"   ✅ {len(df)} partite scaricate")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False

def aggiorna_dati(force=False):
    """Step 1: Scarica nuovi dati"""
    print_step(1, "Aggiornamento dati Serie A")
    
    # Stagioni da aggiornare (ultime 3 per sicurezza)
    stagioni = [
        (23, 24),  # 2023-24
        (24, 25),  # 2024-25
        (25, 26)   # 2025-26 (corrente)
    ]
    
    success_count = 0
    for anno_inizio, anno_fine in stagioni:
        if scarica_stagione(anno_inizio, anno_fine):
            success_count += 1
    
    if success_count > 0:
        print(f"\n   ✅ {success_count}/{len(stagioni)} stagioni aggiornate")
        return True
    else:
        print(f"\n   ❌ Nessuna stagione aggiornata")
        return False

def crea_dataset_pulito():
    """Step 2: Crea dataset pulito unificato"""
    print_step(2, "Creazione dataset pulito")
    
    try:
        # Pattern per trovare tutti i file I1_*.csv
        import glob
        csv_files = sorted(glob.glob('data/I1_*.csv'))
        
        if not csv_files:
            print("   ❌ Nessun file CSV trovato!")
            return False
        
        print(f"   📂 Trovati {len(csv_files)} file CSV")
        
        # Unisci tutti i dataset
        dfs = []
        for file in csv_files:
            try:
                df = pd.read_csv(file, parse_dates=['Date'], dayfirst=True)
                
                # Aggiungi Season
                filename = os.path.basename(file)
                season = filename.replace('I1_', '').replace('.csv', '')
                df['Season'] = f"20{season[:2]}-20{season[2:]}"
                
                dfs.append(df)
                print(f"   ✅ {filename}: {len(df)} partite")
            except Exception as e:
                print(f"   ⚠️  Errore su {file}: {e}")
        
        # Concatena tutto
        df_completo = pd.concat(dfs, ignore_index=True)
        df_completo = df_completo.sort_values('Date').reset_index(drop=True)
        
        # Salva
        output_path = 'data/dataset_pulito.csv'
        df_completo.to_csv(output_path, index=False)
        
        print(f"\n   ✅ Dataset pulito creato:")
        print(f"      Partite totali: {len(df_completo)}")
        print(f"      Prima partita: {df_completo['Date'].min().strftime('%d/%m/%Y')}")
        print(f"      Ultima partita: {df_completo['Date'].max().strftime('%d/%m/%Y')}")
        print(f"      File: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def crea_features():
    """Step 3: Crea features per ML"""
    print_step(3, "Creazione features ML")
    
    try:
        from feature_engineering import FeatureEngineer
        
        # Carica dataset pulito
        df = pd.read_csv('data/dataset_pulito.csv', parse_dates=['Date'], dayfirst=True)
        print(f"   📊 Dataset caricato: {len(df)} partite")
        
        # Crea features
        print("   🔧 Generazione features...")
        fe = FeatureEngineer(df)
        df_features = fe.crea_features(min_partite_storiche=10)
        
        # Salva
        output_path = 'data/dataset_features.csv'
        df_features.to_csv(output_path, index=False)
        
        print(f"\n   ✅ Features create:")
        print(f"      Righe: {len(df_features)}")
        print(f"      Colonne: {len(df_features.columns)}")
        print(f"      File: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def allena_modelli():
    """Step 4: Allena modelli ML"""
    print_step(4, "Allenamento modelli ML")
    
    try:
        from modelli_predittivi import PronosticiCalculator
        
        # Carica dataset con features
        df = pd.read_csv('data/dataset_features.csv')
        print(f"   📊 Dataset features caricato: {len(df)} partite")
        
        # Inizializza calculator
        print("   🧠 Inizializzazione modelli...")
        calc = PronosticiCalculator()
        
        # Prepara dati
        print("   🔧 Preparazione dati...")
        X, y = calc.prepara_dati(df)
        
        # Pulisci dati
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
        X = X.replace([np.inf, -np.inf], 0)
        
        print(f"   ✅ Dati preparati: {X.shape[0]} campioni, {X.shape[1]} features")
        
        # Allena
        print("   🏋️  Training in corso...")
        scores = calc.train_models(X, y)
        
        # Salva
        print("   💾 Salvataggio modelli...")
        calc.salva_modelli()
        
        # Mostra risultati
        print(f"\n   ✅ Modelli allenati:")
        if isinstance(scores, dict):
            for model, score in scores.items():
                if 'accuracy' in model:
                    print(f"      {model.replace('_accuracy', '')}: {score*100:.2f}%")
        elif isinstance(scores, tuple):
            print(f"      Models trained: {len(scores)} modelli")
        else:
            try:
                print(f"      Accuracy: {float(scores)*100:.2f}%")
            except:
                print(f"      Training completato")
        
        print(f"      Salvati in: models/")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def pulisci_cache():
    """Step 5: Pulisci cache"""
    print_step(5, "Pulizia cache")
    
    try:
        import glob
        cache_files = glob.glob('cache/*.json')
        
        for file in cache_files:
            try:
                os.remove(file)
            except:
                pass
        
        print(f"   ✅ {len(cache_files)} file cache rimossi")
        return True
        
    except Exception as e:
        print(f"   ⚠️  Errore pulizia cache: {e}")
        return False

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Aggiorna dati e allena modelli')
    parser.add_argument('--force', action='store_true', help='Forza aggiornamento anche se non necessario')
    args = parser.parse_args()
    
    print_header("AGGIORNAMENTO E ALLENAMENTO SISTEMA")
    print(f"⏰ Inizio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📁 Directory: {os.getcwd()}")
    
    # Crea directory se non esistono
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('cache', exist_ok=True)
    
    results = {}
    
    # Esegui gli step
    results['dati'] = aggiorna_dati(args.force)
    results['dataset'] = crea_dataset_pulito()
    results['features'] = crea_features()
    results['modelli'] = allena_modelli()
    results['cache'] = pulisci_cache()
    
    # Riepilogo finale
    print_header("RIEPILOGO")
    
    total = len(results)
    success = sum(1 for v in results.values() if v)
    
    for step, result in results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {step.capitalize()}")
    
    print(f"\n{'='*60}")
    print(f"✅ Completato: {success}/{total} step")
    print(f"⏰ Fine: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if success == total:
        print(f"\n🎉 AGGIORNAMENTO COMPLETATO CON SUCCESSO!")
        return 0
    else:
        print(f"\n⚠️  AGGIORNAMENTO PARZIALE - Controlla gli errori sopra")
        return 1

if __name__ == "__main__":
    sys.exit(main())
