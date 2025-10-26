#!/usr/bin/env python3
"""
Script di Test e Validazione del Sistema Pronostici
Verifica che tutto funzioni correttamente
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import joblib

def test_struttura_progetto():
    """Testa la struttura del progetto"""
    print("🔍 Test Struttura Progetto...")
    
    # File essenziali
    files_essenziali = [
        'scripts/scarica_dati_storici.py',
        'scripts/analizza_dati.py', 
        'scripts/feature_engineering.py',
        'scripts/modelli_predittivi.py',
        'scripts/sistema_pronostici.py',
        'main.py',
        'README.md'
    ]
    
    # Cartelle essenziali
    cartelle_essenziali = ['data', 'scripts']
    
    tutti_ok = True
    
    for cartella in cartelle_essenziali:
        if os.path.exists(cartella):
            print(f"  ✅ Cartella {cartella} presente")
        else:
            print(f"  ❌ Cartella {cartella} mancante")
            tutti_ok = False
    
    for file in files_essenziali:
        if os.path.exists(file):
            print(f"  ✅ File {file} presente")
        else:
            print(f"  ❌ File {file} mancante")
            tutti_ok = False
    
    return tutti_ok

def test_dati():
    """Testa la presenza e qualità dei dati"""
    print("\n📊 Test Dati...")
    
    # Dataset originali
    dataset_originali = [
        'data/I1_2021.csv', 'data/I1_2122.csv', 'data/I1_2223.csv',
        'data/I1_2324.csv', 'data/I1_2425.csv', 'data/I1_2526.csv'
    ]
    
    dati_ok = True
    
    for dataset in dataset_originali:
        if os.path.exists(dataset):
            try:
                df = pd.read_csv(dataset)
                print(f"  ✅ {dataset}: {len(df)} partite")
            except Exception as e:
                print(f"  ❌ {dataset}: Errore lettura - {e}")
                dati_ok = False
        else:
            print(f"  ❌ {dataset}: Non trovato")
            dati_ok = False
    
    # Dataset processati
    if os.path.exists('data/dataset_pulito.csv'):
        df_pulito = pd.read_csv('data/dataset_pulito.csv')
        print(f"  ✅ Dataset pulito: {len(df_pulito)} partite")
    else:
        print(f"  ❌ Dataset pulito: Non trovato")
        dati_ok = False
    
    if os.path.exists('data/dataset_features.csv'):
        df_features = pd.read_csv('data/dataset_features.csv')
        print(f"  ✅ Dataset features: {len(df_features)} partite, {len(df_features.columns)} colonne")
    else:
        print(f"  ❌ Dataset features: Non trovato")
        dati_ok = False
    
    return dati_ok

def test_modelli():
    """Testa la presenza e funzionalità dei modelli"""
    print("\n🤖 Test Modelli...")
    
    modelli_ok = True
    
    # File modelli
    files_modelli = [
        'models/randomforest_model.pkl',
        'models/gradientboosting_model.pkl', 
        'models/logisticregression_model.pkl',
        'models/scaler.pkl',
        'models/metadata.pkl'
    ]
    
    for file_modello in files_modelli:
        if os.path.exists(file_modello):
            try:
                joblib.load(file_modello)
                print(f"  ✅ {file_modello}: OK")
            except Exception as e:
                print(f"  ❌ {file_modello}: Errore caricamento - {e}")
                modelli_ok = False
        else:
            print(f"  ❌ {file_modello}: Non trovato")
            modelli_ok = False
    
    return modelli_ok

def test_predizione():
    """Testa una predizione completa"""
    print("\n🔮 Test Predizione...")
    
    try:
        # Import sistema
        sys.path.append('scripts')
        from modelli_predittivi import PronosticiCalculator
        
        # Carica sistema
        calc = PronosticiCalculator()
        calc.carica_modelli()
        
        # Carica dati
        df_features = pd.read_csv('data/dataset_features.csv')
        df_features['Date'] = pd.to_datetime(df_features['Date'])
        
        # Test predizione
        pred, prob = calc.predici_partita('Juventus', 'Inter', df_features)
        
        if pred:
            risultato_map = {'H': 'Casa', 'A': 'Trasferta', 'D': 'Pareggio'}
            print(f"  ✅ Predizione test: Juventus vs Inter = {risultato_map[pred]} ({prob.max():.1%})")
            return True
        else:
            print(f"  ❌ Predizione fallita")
            return False
            
    except Exception as e:
        print(f"  ❌ Errore durante test predizione: {e}")
        return False

def test_performance_modelli():
    """Analizza le performance dei modelli"""
    print("\n📈 Analisi Performance Modelli...")
    
    try:
        # Carica metadata
        metadata = joblib.load('models/metadata.pkl')
        models_info = metadata['models_info']
        
        print("  📊 Performance Modelli:")
        for model_name, info in models_info.items():
            accuracy = info.get('accuracy', 0)
            cv_score = info.get('cv_score', 0)
            print(f"    {model_name}:")
            print(f"      - Accuracy: {accuracy:.1%}")
            print(f"      - CV Score: {cv_score:.1%}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore analisi performance: {e}")
        return False

def test_squadre_disponibili():
    """Testa le squadre disponibili"""
    print("\n🏟️  Test Squadre...")
    
    try:
        df_features = pd.read_csv('data/dataset_features.csv')
        
        squadre_casa = set(df_features['HomeTeam'].unique())
        squadre_trasferta = set(df_features['AwayTeam'].unique())
        tutte_squadre = sorted(squadre_casa.union(squadre_trasferta))
        
        print(f"  ✅ {len(tutte_squadre)} squadre disponibili:")
        
        # Mostra prime 10 squadre
        for i, squadra in enumerate(tutte_squadre[:10]):
            partite = len(df_features[
                (df_features['HomeTeam'] == squadra) | 
                (df_features['AwayTeam'] == squadra)
            ])
            print(f"    {i+1:2d}. {squadra} ({partite} partite)")
        
        if len(tutte_squadre) > 10:
            print(f"    ... e altre {len(tutte_squadre)-10} squadre")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore test squadre: {e}")
        return False

def genera_report_completo():
    """Genera un report completo del sistema"""
    print("\n📋 REPORT COMPLETO SISTEMA")
    print("="*50)
    
    # Info generali
    now = datetime.now()
    print(f"Data report: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Statistiche dati
    if os.path.exists('data/dataset_features.csv'):
        df = pd.read_csv('data/dataset_features.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"\n📊 STATISTICHE DATI:")
        print(f"  - Partite totali: {len(df):,}")
        print(f"  - Periodo: {df['Date'].min().strftime('%d/%m/%Y')} - {df['Date'].max().strftime('%d/%m/%Y')}")
        print(f"  - Features: {len(df.columns)-6}")  # -6 per escludere info base
        
        # Distribuzione risultati
        risultati = df['FTR'].value_counts()
        print(f"  - Vittorie Casa: {risultati.get('H', 0)} ({risultati.get('H', 0)/len(df)*100:.1f}%)")
        print(f"  - Vittorie Trasferta: {risultati.get('A', 0)} ({risultati.get('A', 0)/len(df)*100:.1f}%)")
        print(f"  - Pareggi: {risultati.get('D', 0)} ({risultati.get('D', 0)/len(df)*100:.1f}%)")
    
    # Info modelli
    if os.path.exists('models/metadata.pkl'):
        metadata = joblib.load('models/metadata.pkl')
        print(f"\n🤖 MODELLI:")
        print(f"  - Numero modelli: {len(metadata['models_info'])}")
        
        for name, info in metadata['models_info'].items():
            print(f"  - {name}: Accuracy {info.get('accuracy', 0):.1%}")
    
    # Dimensioni files
    print(f"\n💾 DIMENSIONI FILES:")
    files_importanti = [
        'data/dataset_features.csv',
        'models/randomforest_model.pkl',
        'models/gradientboosting_model.pkl',
        'models/logisticregression_model.pkl'
    ]
    
    for file_path in files_importanti:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / 1024 / 1024
            print(f"  - {file_path}: {size_mb:.1f} MB")

def main():
    """Test completo del sistema"""
    print("🧪 TEST COMPLETO SISTEMA PRONOSTICI")
    print("="*60)
    
    tests = [
        ("Struttura Progetto", test_struttura_progetto),
        ("Dati", test_dati),
        ("Modelli", test_modelli),
        ("Squadre", test_squadre_disponibili),
        ("Performance", test_performance_modelli),
        ("Predizione", test_predizione)
    ]
    
    risultati = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            risultati[test_name] = test_func()
        except Exception as e:
            print(f"❌ Errore durante {test_name}: {e}")
            risultati[test_name] = False
    
    # Riepilogo
    print(f"\n{'='*60}")
    print("🏁 RIEPILOGO TEST")
    print("="*60)
    
    tests_passati = sum(risultati.values())
    tests_totali = len(risultati)
    
    for test_name, result in risultati.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 RISULTATO FINALE: {tests_passati}/{tests_totali} test passati")
    
    if tests_passati == tests_totali:
        print("🎉 SISTEMA COMPLETAMENTE FUNZIONANTE! 🎉")
        genera_report_completo()
    else:
        print("⚠️  Alcuni test sono falliti. Controlla i messaggi di errore sopra.")
    
    # Suggerimenti per l'uso
    if tests_passati >= tests_totali * 0.8:  # 80% test passati
        print(f"\n💡 SUGGERIMENTI PER L'USO:")
        print(f"  1. Esegui: python3 main.py")
        print(f"  2. Seleziona opzione 4 per i pronostici")
        print(f"  3. Oppure: python3 scripts/sistema_pronostici.py")
        print(f"\n📚 Leggi README.md per documentazione completa")

if __name__ == "__main__":
    main()