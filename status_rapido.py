#!/usr/bin/env python3
"""
⚡ VERIFICA RAPIDA SISTEMA
Controllo veloce dello stato di aggiornamento
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def quick_status():
    """Verifica rapida stato sistema"""
    base_path = Path(__file__).parent
    
    print("⚡ VERIFICA RAPIDA SISTEMA")
    print("=" * 30)
    
    # 1. Dataset
    dataset_path = base_path / "data" / "dataset_features.csv"
    if dataset_path.exists():
        dataset_mtime = os.path.getmtime(dataset_path)
        dataset_date = datetime.fromtimestamp(dataset_mtime)
        hours_old = (datetime.now() - dataset_date).total_seconds() / 3600
        
        if hours_old < 24:
            print("📊 Dataset: ✅ FRESCO")
        elif hours_old < 72:
            print("📊 Dataset: ⚠️ ACCETTABILE")
        else:
            print("📊 Dataset: ❌ OBSOLETO")
    else:
        print("📊 Dataset: ❌ MANCANTE")
    
    # 2. Modelli
    models_dir = base_path / "models"
    main_models = ['randomforest_model.pkl', 'gradientboosting_model.pkl', 'logisticregression_model.pkl']
    
    if dataset_path.exists():
        dataset_mtime = os.path.getmtime(dataset_path)
        models_synced = 0
        
        for model_file in main_models:
            model_path = models_dir / model_file
            if model_path.exists():
                model_mtime = os.path.getmtime(model_path)
                if model_mtime >= dataset_mtime:
                    models_synced += 1
        
        if models_synced == len(main_models):
            print("🤖 Modelli: ✅ SINCRONIZZATI")
        elif models_synced > 0:
            print(f"🤖 Modelli: ⚠️ PARZIALI ({models_synced}/{len(main_models)})")
        else:
            print("🤖 Modelli: ❌ OBSOLETI")
    else:
        print("🤖 Modelli: ❓ NON VERIFICABILI")
    
    # 3. Automazione
    config_path = base_path / "config" / "auto_update.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            if 'schedule' in config and 'data_sources' in config:
                print("🔄 Automazione: ✅ CONFIGURATA")
            else:
                print("🔄 Automazione: ⚠️ INCOMPLETA")
        except:
            print("🔄 Automazione: ❌ ERRORE CONFIG")
    else:
        print("🔄 Automazione: ❌ NON CONFIGURATA")
    
    print("\n💡 Per report dettagliato: python verifica_stato_sistema.py")

if __name__ == "__main__":
    quick_status()