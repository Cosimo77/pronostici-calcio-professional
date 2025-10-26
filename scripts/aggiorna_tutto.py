#!/usr/bin/env python3
"""
Script di automazione per aggiornare tutto il sistema di pronostici
Esegue in sequenza tutti i passaggi necessari per mantenere i dati aggiornati
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime

def print_step(step_num, title, description=""):
    """Stampa un passaggio con formattazione"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    if description:
        print(f"📋 {description}")
    print('='*60)

def run_script(script_path, description):
    """Esegue uno script Python e gestisce gli errori"""
    print(f"🚀 Eseguendo: {script_path}")
    print(f"📝 {description}")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, check=True)
        print("✅ Completato con successo!")
        if result.stdout:
            print("📊 Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nell'esecuzione di {script_path}")
        print(f"💥 Codice errore: {e.returncode}")
        if e.stdout:
            print("📤 STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("📥 STDERR:")
            print(e.stderr)
        return False

def verifica_dati():
    """Verifica la consistenza dei dati aggiornati"""
    print_step("VERIFICA", "Controllo consistenza dati")
    
    try:
        # Verifica dataset raw stagione corrente
        df_raw = pd.read_csv('data/I1_2526.csv', parse_dates=['Date'], dayfirst=True, encoding='latin1')
        print(f"📊 Dataset stagione corrente: {len(df_raw)} partite")
        print(f"🗓️  Ultima partita: {df_raw['Date'].max().strftime('%d/%m/%Y')}")
        
        # Verifica dataset pulito
        if os.path.exists('data/dataset_pulito.csv'):
            df_pulito = pd.read_csv('data/dataset_pulito.csv', parse_dates=['Date'])
            print(f"📊 Dataset pulito: {len(df_pulito)} partite")
            print(f"🗓️  Ultima partita: {df_pulito['Date'].max().strftime('%d/%m/%Y')}")
        
        # Verifica features
        if os.path.exists('data/dataset_features.csv'):
            df_features = pd.read_csv('data/dataset_features.csv', parse_dates=['Date'])
            print(f"📊 Dataset features: {len(df_features)} partite")
            print(f"🗓️  Ultima partita: {df_features['Date'].max().strftime('%d/%m/%Y')}")
            
            # Conta partite mancanti nelle features
            partite_mancanti = len(df_pulito) - len(df_features)
            if partite_mancanti > 0:
                print(f"⚠️  Partite senza features: {partite_mancanti}")
                print("💡 Questo è normale per le partite più recenti (serve storico di 5+ partite)")
        
        # Verifica modelli
        modelli_esistenti = []
        for modello in ['randomforest_model.pkl', 'gradientboosting_model.pkl', 'logisticregression_model.pkl']:
            if os.path.exists(f'models/{modello}'):
                modelli_esistenti.append(modello)
        
        print(f"🤖 Modelli disponibili: {len(modelli_esistenti)}/3")
        for modello in modelli_esistenti:
            print(f"   ✅ {modello}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella verifica: {e}")
        return False

def main():
    """Processo principale di aggiornamento completo"""
    
    print("🎯 SISTEMA DI AGGIORNAMENTO AUTOMATICO PRONOSTICI")
    print(f"⏰ Avviato il {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')}")
    
    # Vai nella directory corretta
    os.chdir('/Users/cosimomassaro/Desktop/pronostici_calcio')
    print(f"📁 Directory di lavoro: {os.getcwd()}")
    
    success_count = 0
    total_steps = 5
    
    # STEP 1: Aggiorna dati stagione corrente
    print_step(1, "AGGIORNAMENTO DATI STAGIONE CORRENTE", 
               "Scarica e sovrascrive i dati della stagione 2025-26")
    if run_script('scripts/aggiorna_stagione_corrente.py', 
                  "Forza il download dei dati più recenti della Serie A"):
        success_count += 1
    
    # STEP 2: Ricrea dataset pulito
    print_step(2, "CREAZIONE DATASET PULITO", 
               "Unifica tutti i dati storici in un dataset pulito")
    if run_script('scripts/analizza_dati.py', 
                  "Analizza e pulisce tutti i dati storici"):
        success_count += 1
    
    # STEP 3: Rigenera features
    print_step(3, "GENERAZIONE FEATURES", 
               "Calcola le features ML per tutte le partite")
    if run_script('scripts/feature_engineering.py', 
                  "Crea features per machine learning"):
        success_count += 1
    
    # STEP 4: Riqualifica modelli
    print_step(4, "TRAINING MODELLI", 
               "Riqualifica tutti i modelli di machine learning")
    if run_script('scripts/modelli_predittivi.py', 
                  "Addestra modelli con dati aggiornati"):
        success_count += 1
    
    # STEP 5: Verifica finale
    print_step(5, "VERIFICA FINALE", 
               "Controlla che tutti i dati siano consistenti")
    if verifica_dati():
        success_count += 1
    
    # Risultato finale
    print(f"\n{'='*60}")
    print("🏁 AGGIORNAMENTO COMPLETATO")
    print('='*60)
    print(f"✅ Passaggi completati: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("🎉 Tutti i passaggi completati con successo!")
        print("🚀 Il sistema è pronto per fare pronostici aggiornati")
    else:
        print(f"⚠️  {total_steps - success_count} passaggi falliti")
        print("🔧 Controlla gli errori sopra e riprova")
    
    print(f"⏰ Completato il {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')}")

if __name__ == "__main__":
    main()