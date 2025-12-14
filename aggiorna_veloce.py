#!/usr/bin/env python3
"""
🚀 AGGIORNAMENTO VELOCE
Script semplificato che:
1. Scarica nuovi dati
2. Unisce in dataset_pulito
3. Copia come dataset_features (usa features esistenti)
4. Riallena solo i modelli enterprise
"""

import os
import requests
import pandas as pd
from datetime import datetime
import glob
import shutil

def download_stagione(anno_inizio, anno_fine):
    """Scarica dati stagione"""
    stagione = f"{anno_inizio}{anno_fine}"
    url = f"https://www.football-data.co.uk/mmz4281/{stagione}/I1.csv"
    file_path = f"data/I1_{stagione}.csv"
    
    print(f"📥 Scaricamento {anno_inizio}-{anno_fine}...", end=" ")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(r.content)
        df = pd.read_csv(file_path)
        print(f"✅ {len(df)} partite")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False

def main():
    print("🚀 AGGIORNAMENTO VELOCE")
    print("="*50)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}\n")
    
    # 1. Scarica dati
    print("📊 STEP 1: Download dati")
    for anno_i, anno_f in [(23,24), (24,25), (25,26)]:
        download_stagione(anno_i, anno_f)
    
    # 2. Unisci dataset
    print("\n📊 STEP 2: Unione dataset")
    csv_files = sorted(glob.glob('data/I1_*.csv'))
    dfs = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, parse_dates=['Date'], dayfirst=True)
            filename = os.path.basename(file)
            season = filename.replace('I1_', '').replace('.csv', '')
            df['Season'] = f"20{season[:2]}-20{season[2:]}"
            dfs.append(df)
            print(f"   ✅ {filename}: {len(df)} partite")
        except:
            pass
    
    df_completo = pd.concat(dfs, ignore_index=True)
    df_completo = df_completo.sort_values('Date').reset_index(drop=True)
    
    # Salva dataset pulito
    df_completo.to_csv('data/dataset_pulito.csv', index=False)
    print(f"\n   ✅ Dataset pulito: {len(df_completo)} partite")
    print(f"      Ultima partita: {df_completo['Date'].max().strftime('%d/%m/%Y')}")
    
    # 3. Copia come dataset_features (temporaneo)
    print("\n📊 STEP 3: Preparazione features")
    shutil.copy('data/dataset_pulito.csv', 'data/dataset_features.csv')
    print("   ✅ Dataset features pronto")
    
    # 4. Allena modelli enterprise
    print("\n🤖 STEP 4: Training modelli enterprise")
    
    import sys
    sys.path.insert(0, 'scripts')
    from modelli_predittivi import PronosticiCalculator
    
    df = pd.read_csv('data/dataset_features.csv')
    print(f"   📊 {len(df)} partite caricatean")
    
    calc = PronosticiCalculator()
    X, y = calc.prepara_dati(df)
    
    # Pulizia dati
    import numpy as np
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
    X = X.replace([np.inf, -np.inf], 0)
    
    print(f"   🔧 {X.shape[0]} campioni, {X.shape[1]} features")
    print("   🏋️  Training...")
    
    scores = calc.train_models(X, y)
    calc.salva_modelli()
    
    print("   ✅ Modelli salvati in models/")
    
    # 5. Pulisci cache
    print("\n🧹 STEP 5: Pulizia cache")
    for file in glob.glob('cache/*.json'):
        try:
            os.remove(file)
        except:
            pass
    print("   ✅ Cache pulita")
    
    print("\n" + "="*50)
    print("✅ AGGIORNAMENTO COMPLETATO!")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print(f"📊 Dataset: {len(df_completo)} partite")
    print(f"📅 Aggiornato a: {df_completo['Date'].max().strftime('%d/%m/%Y')}")

if __name__ == "__main__":
    main()
