#!/usr/bin/env python3
"""
Allenamento rapido modelli ML
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from modelli_predittivi import PronosticiCalculator
import pandas as pd
from datetime import datetime

def allena_modelli():
    print("🤖 ALLENAMENTO MODELLI ML - RAPIDO")
    print("=" * 50)
    print(f"⏰ Inizio: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # 1. Carica dati
        print("\n📊 Caricamento dataset...")
        
        # Prova prima dataset_pulito, poi dataset_features
        try:
            df = pd.read_csv('data/dataset_pulito.csv')
            print(f"✅ Dataset pulito caricato: {len(df)} partite")
        except:
            try:
                df = pd.read_csv('data/dataset_features.csv')
                print(f"✅ Dataset features caricato: {len(df)} partite")
            except Exception as e:
                print(f"❌ Errore caricamento dataset: {e}")
                return
        
        # 2. Inizializza modelli
        print("\n🧠 Inizializzazione modelli...")
        calculator = PronosticiCalculator()
        
        # 3. Allena modelli
        print("\n🏋️ Allenamento in corso...")
        
        # Prepara i dati
        X, y = calculator.prepara_dati(df)
        print(f"✅ Dati preparati: {X.shape[0]} campioni, {X.shape[1]} features")
        
        # Controllo e pulizia dati numerici
        print("\n🧹 Pulizia dati...")
        # Converti tutto in numerico forzando errori a NaN
        X = X.apply(pd.to_numeric, errors='coerce')
        # Riempi NaN con 0
        X = X.fillna(0)
        print(f"✅ Dati puliti: {X.isnull().sum().sum()} valori NaN rimossi")
        
        # Allena i modelli
        scores = calculator.train_models(X, y)
        if isinstance(scores, dict):
            print(f"✅ Allenamento completato! Accuratezza: {scores.get('rf_accuracy', 0):.3f}")
        else:
            print(f"✅ Allenamento completato! Scores: {scores}")
        
        # 4. Salva modelli
        print("\n💾 Salvataggio modelli...")
        calculator.salva_modelli()
        print("✅ Modelli salvati in models/")
        
        print(f"\n🎉 ALLENAMENTO COMPLETATO!")
        print(f"⏰ Fine: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Errore durante allenamento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    allena_modelli()