#!/usr/bin/env python3
"""
Script automazione completa Render: scarica dati freschi e riaddestra modelli
Eseguito automaticamente OGNI deploy/restart - zero intervento manuale
"""

import os
import sys
import subprocess
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'

# URL dati Serie A corrente
CURRENT_SEASON = '2526'  # Aggiorna ogni stagione
SERIE_A_URL = f'https://www.football-data.co.uk/mmz4281/{CURRENT_SEASON}/I1.csv'


def log(msg):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")


def download_fresh_data():
    """Scarica dati Serie A freschi da football-data.co.uk"""
    log("📥 Download dati Serie A freschi...")
    
    try:
        response = requests.get(SERIE_A_URL, timeout=30)
        response.raise_for_status()
        
        # Salva CSV
        output_path = DATA_DIR / f'I1_{CURRENT_SEASON}.csv'
        output_path.write_bytes(response.content)
        
        # Verifica data ultima partita
        df = pd.read_csv(output_path)
        if 'Date' in df.columns and len(df) > 0:
            ultima_data = df['Date'].iloc[-1]
            num_partite = len(df)
            log(f"✅ Dati scaricati: {num_partite} partite, ultima {ultima_data}")
            return True
        else:
            log("⚠️ CSV scaricato ma senza colonna Date")
            return False
            
    except Exception as e:
        log(f"❌ Errore download dati: {e}")
        return False


def merge_dataset_completo():
    """Merge dati storici + stagione corrente"""
    log("📊 Merge dataset completo...")
    
    try:
        # Carica storico se esiste
        dataset_path = DATA_DIR / 'dataset_features.csv'
        if dataset_path.exists():
            df_storico = pd.read_csv(dataset_path)
            log(f"   Storico: {len(df_storico)} partite")
        else:
            df_storico = pd.DataFrame()
        
        # Carica stagione corrente
        current_path = DATA_DIR / f'I1_{CURRENT_SEASON}.csv'
        if current_path.exists():
            df_current = pd.read_csv(current_path)
            log(f"   Corrente: {len(df_current)} partite")
            
            # Merge (evita duplicati)
            if not df_storico.empty and 'Date' in df_storico.columns:
                # Rimuovi partite correnti già presenti in storico
                if 'Date' in df_current.columns:
                    df_merged = pd.concat([df_storico, df_current], ignore_index=True)
                    df_merged = df_merged.drop_duplicates(subset=['Date', 'HomeTeam', 'AwayTeam'], keep='last')
                    log(f"   Merged: {len(df_merged)} partite totali")
                    
                    # Salva dataset pulito aggiornato
                    output_path = DATA_DIR / 'dataset_pulito.csv'
                    df_merged.to_csv(output_path, index=False)
                    log(f"✅ Dataset pulito salvato: {output_path}")
                    return True
        
        log("⚠️ Dati insufficienti per merge")
        return False
        
    except Exception as e:
        log(f"❌ Errore merge dataset: {e}")
        return False


def retrain_models():
    """Riaddestra modelli ML con dati freschi"""
    log("🤖 Riaddestramento modelli ML...")
    
    try:
        # Esegui script training come subprocess (no funzione main disponibile)
        script_path = BASE_DIR / 'riaddestra_modelli_rapido.py'
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 5 min timeout
        )
        
        if result.returncode != 0:
            log(f"⚠️ Training script exit code: {result.returncode}")
            if result.stderr:
                log(f"   Stderr: {result.stderr[:200]}")
        else:
            log("✅ Training completato")
        
        # Verifica modelli creati
        expected_models = [
            'randomforest_model.pkl',
            'gradientboosting_model.pkl', 
            'logisticregression_model.pkl',
            'scaler.pkl'
        ]
        
        missing = []
        for model in expected_models:
            model_path = MODELS_DIR / model
            if not model_path.exists():
                missing.append(model)
        
        if not missing:
            log(f"✅ Modelli riaddestrati: {len(expected_models)} file")
            return True
        else:
            log(f"⚠️ Modelli mancanti: {missing}")
            return False
            
    except Exception as e:
        log(f"❌ Errore riaddestramento modelli: {e}")
        return False


def verify_system():
    """Verifica finale sistema completo"""
    log("🔍 Verifica sistema...")
    
    checks = []
    
    # Check 1: Dataset pulito esiste
    dataset_path = DATA_DIR / 'dataset_pulito.csv'
    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        num_partite = len(df)
        
        # Verifica data ultima partita
        if 'Date' in df.columns and len(df) > 0:
            ultima_data_str = df['Date'].iloc[-1]
            try:
                ultima_data = pd.to_datetime(ultima_data_str, format='%d/%m/%Y')
                oggi = datetime.now()
                giorni_diff = (oggi - ultima_data).days
                
                if giorni_diff <= 7:
                    log(f"   ✅ Dataset: {num_partite} partite, {giorni_diff} giorni freschi")
                    checks.append(True)
                else:
                    log(f"   ⚠️ Dataset: ultima partita {giorni_diff} giorni fa")
                    checks.append(False)
            except:
                log(f"   ⚠️ Dataset: impossibile parsare data")
                checks.append(False)
        else:
            log(f"   ⚠️ Dataset: {num_partite} partite ma no Date column")
            checks.append(False)
    else:
        log(f"   ❌ Dataset pulito non trovato")
        checks.append(False)
    
    # Check 2: Modelli ML esistono
    expected_models = [
        'randomforest_model.pkl',
        'gradientboosting_model.pkl',
        'logisticregression_model.pkl',
        'scaler.pkl'
    ]
    
    models_ok = all((MODELS_DIR / m).exists() for m in expected_models)
    if models_ok:
        log(f"   ✅ Modelli ML: {len(expected_models)} file presenti")
        checks.append(True)
    else:
        missing = [m for m in expected_models if not (MODELS_DIR / m).exists()]
        log(f"   ❌ Modelli mancanti: {missing}")
        checks.append(False)
    
    return all(checks)


def main():
    """Workflow completo automazione Render"""
    log("=" * 70)
    log("🚀 AUTOMAZIONE RENDER - Setup Sistema Completo")
    log("=" * 70)
    
    # Crea directory se non esistono
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    success_steps = []
    
    # Step 1: Download dati freschi
    if download_fresh_data():
        success_steps.append("download")
    else:
        log("⚠️ Download fallito, continuo con dati esistenti...")
    
    # Step 2: Merge dataset completo
    if merge_dataset_completo():
        success_steps.append("merge")
    
    # Step 3: Riaddestra modelli (solo se dati aggiornati)
    if "download" in success_steps or "merge" in success_steps:
        if retrain_models():
            success_steps.append("training")
    else:
        log("ℹ️ Skip riaddestramento (dati non aggiornati)")
    
    # Step 4: Verifica finale
    log("=" * 70)
    if verify_system():
        log("✅ SISTEMA PRONTO - Tutti i check superati")
        log("=" * 70)
        return 0
    else:
        log("⚠️ SISTEMA PARZIALE - Alcuni check falliti")
        log("   Continuando con dati/modelli esistenti...")
        log("=" * 70)
        return 0  # Non fallire deploy, usa fallback


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
