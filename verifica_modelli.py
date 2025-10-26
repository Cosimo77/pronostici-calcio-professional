#!/usr/bin/env python3
"""
Controlla stato modelli e necessità di riaddestramento
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import pickle

def check_model_status():
    print("🔍 CONTROLLO STATO MODELLI")
    print("=" * 50)
    
    # Controlla date modelli
    models_dir = "models/"
    data_dir = "data/"
    
    if not os.path.exists(models_dir):
        print("❌ Directory models/ non trovata")
        return
    
    print("📅 DATE MODELLI:")
    model_files = ['randomforest_model.pkl', 'gradientboosting_model.pkl', 'logisticregression_model.pkl']
    model_dates = {}
    
    for model_file in model_files:
        path = os.path.join(models_dir, model_file)
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            model_date = datetime.fromtimestamp(mtime)
            model_dates[model_file] = model_date
            print(f"  {model_file}: {model_date.strftime('%d/%m/%Y %H:%M')}")
        else:
            print(f"  {model_file}: MANCANTE ❌")
    
    # Controlla dataset
    print("\n📊 DATASET:")
    dataset_files = ['dataset_features.csv', 'dataset_pulito.csv', 'I1_2526.csv']
    
    for dataset_file in dataset_files:
        path = os.path.join(data_dir, dataset_file)
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            data_date = datetime.fromtimestamp(mtime)
            print(f"  {dataset_file}: {data_date.strftime('%d/%m/%Y %H:%M')}")
            
            # Controlla se dati più recenti dei modelli
            if model_dates and data_date > min(model_dates.values()):
                print(f"    ⚠️ Dati più recenti dei modelli!")
        else:
            print(f"  {dataset_file}: MANCANTE")
    
    # Controlla contenuto dataset attuale
    try:
        print("\n📈 ANALISI DATASET FEATURES:")
        df = pd.read_csv('data/dataset_features.csv')
        print(f"  Righe totali: {len(df)}")
        print(f"  Colonne: {len(df.columns)}")
        
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            ultima_partita = df['Date'].max()
            print(f"  Ultima partita: {ultima_partita.strftime('%d/%m/%Y')}")
            
            # Partite recenti (ultimi 7 giorni)
            una_settimana_fa = datetime.now() - timedelta(days=7)
            partite_recenti = df[df['Date'] > una_settimana_fa]
            print(f"  Partite ultime 7 giorni: {len(partite_recenti)}")
            
            if len(partite_recenti) > 5:
                print("  ⚠️ Molte partite nuove, considera riaddestramento")
        
    except Exception as e:
        print(f"  ❌ Errore lettura dataset: {e}")
    
    # Raccomandazioni
    print("\n🎯 RACCOMANDAZIONI:")
    
    if not model_dates:
        print("  🔴 CRITICO: Riaddestra tutti i modelli (file mancanti)")
    else:
        oldest_model = min(model_dates.values())
        giorni_fa = (datetime.now() - oldest_model).days
        
        if giorni_fa > 7:
            print(f"  🟡 CONSIGLIATO: Riaddestramento (modelli di {giorni_fa} giorni fa)")
        elif giorni_fa > 3:
            print(f"  🟠 OPZIONALE: Riaddestramento (modelli di {giorni_fa} giorni fa)")  
        else:
            print(f"  🟢 OK: Modelli recenti ({giorni_fa} giorni fa)")
    
    # Comando per riaddestramento
    print("\n🔧 COMANDI RIADDESTRAMENTO:")
    print("  Veloce: python3 aggiorna_rapido.py")
    print("  Completo: python3 aggiorna_tutto_completo.py")

if __name__ == "__main__":
    check_model_status()