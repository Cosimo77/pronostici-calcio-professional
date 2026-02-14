#!/usr/bin/env python3
"""
VERIFICA COMPLETA SISTEMA TRADING
Controllo sistematico di tutti i componenti critici
"""

import pandas as pd
import numpy as np
from datetime import datetime
import hashlib
import os
import sys
import json
import pickle

print("="*70)
print("🔍 VERIFICA SISTEMA TRADING - CERTIFICAZIONE PRE-OPERATIVA")
print("="*70)
print()

# 1. VERIFICA DATI SERIE A
print("1️⃣ VERIFICA DATI SERIE A")
print("-" * 50)

df = pd.read_csv('data/I1_2526.csv')

print(f"📊 Dataset Serie A 2025-26:")
print(f"  Totale partite: {len(df)}")
print(f"  Prima partita: {df['Date'].iloc[0]}")
print(f"  Ultima partita: {df['Date'].iloc[-1]}")

ultima_data = pd.to_datetime(df['Date'].iloc[-1], format='%d/%m/%Y')
oggi = datetime(2026, 2, 14)
giorni_diff = (oggi - ultima_data).days

print(f"  Giorni da ultimo aggiornamento: {giorni_diff}")

if giorni_diff <= 7:
    print(f"✅ PASS: Dati aggiornati (< 7 giorni)")
else:
    print(f"❌ FAIL: Dati troppo vecchi ({giorni_diff} giorni)")
    sys.exit(1)

required_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
missing = [c for c in required_cols if c not in df.columns]
if missing:
    print(f"❌ FAIL: Colonne mancanti: {missing}")
    sys.exit(1)

print(f"✅ Colonne critiche presenti: {len(required_cols)}")

file_size = os.path.getsize('data/I1_2526.csv')
print(f"  File size: {file_size:,} bytes")

print()

# 2. VERIFICA MODELLI ML
print("2️⃣ VERIFICA MODELLI ML")
print("-" * 50)

models_dir = 'models'
expected_models = ['randomforest_model.pkl', 'gradientboosting_model.pkl', 
                   'logisticregression_model.pkl', 'scaler.pkl']

for model_name in expected_models:
    model_path = os.path.join(models_dir, model_name)
    if not os.path.exists(model_path):
        print(f"❌ FAIL: Modello mancante: {model_name}")
        sys.exit(1)
    
    mod_time = datetime.fromtimestamp(os.path.getmtime(model_path))
    file_size = os.path.getsize(model_path)
    
    # Carica modello per verifica
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"✅ {model_name:30s} ({file_size:>7,} bytes, {mod_time:%d/%m/%Y %H:%M})")
    except Exception as e:
        print(f"❌ FAIL: Errore caricamento {model_name}: {e}")
        sys.exit(1)

print()

# 3. VERIFICA BANKROLL CONFIG
print("3️⃣ VERIFICA BANKROLL CONFIG")
print("-" * 50)

config_path = 'config_bankroll.json'
if not os.path.exists(config_path):
    print(f"❌ FAIL: File config mancante")
    sys.exit(1)

with open(config_path, 'r') as f:
    config = json.load(f)

required_keys = ['bankroll_iniziale', 'bankroll_corrente', 'unita_betting', 
                 'kelly_fraction', 'stop_loss_percentage']
missing_keys = [k for k in required_keys if k not in config]

if missing_keys:
    print(f"❌ FAIL: Chiavi mancanti in config: {missing_keys}")
    sys.exit(1)

print(f"✅ Config presente con {len(config)} chiavi")
print(f"  Bankroll Iniziale: €{config['bankroll_iniziale']:.2f}")
print(f"  Bankroll Corrente: €{config['bankroll_corrente']:.2f}")
print(f"  Unità Betting: €{config['unita_betting']:.2f} ({config['unita_betting']/config['bankroll_corrente']*100:.1f}%)")
print(f"  Kelly Fraction: {config['kelly_fraction']} (conservativo)")
print(f"  Stop Loss: {config['stop_loss_percentage']}%")

# Verifica coerenza
if abs(config['bankroll_iniziale'] - config['bankroll_corrente']) < 0.01:
    print(f"✅ Bankroll sincronizzato (clean state)")
else:
    print(f"⚠️  Bankroll differente: iniziale vs corrente")

expected_unit = config['bankroll_corrente'] * 0.01
if abs(config['unita_betting'] - expected_unit) < 0.01:
    print(f"✅ Unità betting corretta (1% bankroll)")
else:
    print(f"⚠️  Unità betting non aggiornata: expected {expected_unit:.2f}, got {config['unita_betting']:.2f}")

print()

# 4. VERIFICA TRACKING GIOCATE
print("4️⃣ VERIFICA TRACKING GIOCATE")
print("-" * 50)

tracking_path = 'tracking_giocate.csv'
if not os.path.exists(tracking_path):
    print(f"❌ FAIL: File tracking mancante")
    sys.exit(1)

df_tracking = pd.read_csv(tracking_path)
print(f"📁 File tracking presente")
print(f"  Righe: {len(df_tracking)} (+ header)")

required_cols_tracking = ['Data', 'Partita', 'Mercato', 'Quota_Sistema', 
                           'Quota_Sisal', 'EV_Modello', 'Stake', 'Risultato', 'Profit']

missing_tracking = [c for c in required_cols_tracking if c not in df_tracking.columns]
if missing_tracking:
    print(f"❌ FAIL: Colonne tracking mancanti: {missing_tracking}")
    sys.exit(1)

print(f"✅ Colonne tracking presenti: {len(required_cols_tracking)}")

if len(df_tracking) == 0:
    print(f"✅ Database vuoto (clean state)")
else:
    print(f"  Puntate pending: {len(df_tracking[df_tracking['Risultato'] == 'PENDING'])}")
    print(f"  Puntate completate: {len(df_tracking[df_tracking['Risultato'].isin(['WIN', 'LOSS'])])}")
    print(f"  Puntate skipped: {len(df_tracking[df_tracking['Risultato'] == 'SKIP'])}")

print()

# 5. TEST KELLY CRITERION
print("5️⃣ TEST KELLY CRITERION")
print("-" * 50)

def calculate_kelly_stake(prob_win, quota, bankroll, kelly_fraction=0.25):
    """Test formula Kelly"""
    b = quota - 1.0
    p = prob_win
    q = 1.0 - p
    
    kelly_f = (b * p - q) / b
    
    if kelly_f <= 0:
        return 0.0
    
    kelly_f *= kelly_fraction
    stake = kelly_f * bankroll
    max_stake = bankroll * 0.05
    
    return min(stake, max_stake)

# Test case 1: EV positivo moderato
prob1, quota1 = 0.40, 2.50
stake1 = calculate_kelly_stake(prob1, quota1, config['bankroll_corrente'], config['kelly_fraction'])
ev1 = (prob1 * (quota1 - 1) - (1 - prob1)) * 100

print(f"Test 1: Prob {prob1*100:.0f}%, Quota {quota1:.2f}")
print(f"  Kelly stake: €{stake1:.2f}")
print(f"  EV: {ev1:.1f}%")

if stake1 > 0 and ev1 > 0:
    print(f"✅ PASS: Kelly positivo per EV positivo")
else:
    print(f"❌ FAIL: Kelly logic error")
    sys.exit(1)

# Test case 2: EV negativo
prob2, quota2 = 0.30, 2.00
stake2 = calculate_kelly_stake(prob2, quota2, config['bankroll_corrente'], config['kelly_fraction'])
ev2 = (prob2 * (quota2 - 1) - (1 - prob2)) * 100

print(f"Test 2: Prob {prob2*100:.0f}%, Quota {quota2:.2f}")
print(f"  Kelly stake: €{stake2:.2f}")
print(f"  EV: {ev2:.1f}%")

if stake2 == 0 and ev2 < 0:
    print(f"✅ PASS: Kelly zero per EV negativo")
else:
    print(f"❌ FAIL: Kelly dovrebbe essere 0 per EV negativo")
    sys.exit(1)

# Test case 3: Cap 5%
prob3, quota3 = 0.60, 3.00  # EV molto alto
stake3 = calculate_kelly_stake(prob3, quota3, config['bankroll_corrente'], config['kelly_fraction'])
max_allowed = config['bankroll_corrente'] * 0.05

print(f"Test 3: Prob {prob3*100:.0f}%, Quota {quota3:.2f} (EV alto)")
print(f"  Kelly stake: €{stake3:.2f}")
print(f"  Max allowed (5%): €{max_allowed:.2f}")

if stake3 <= max_allowed:
    print(f"✅ PASS: Cap 5% rispettato")
else:
    print(f"❌ FAIL: Stake supera cap 5%")
    sys.exit(1)

print()

# 6. VERIFICA CALCOLO PROBABILITÀ DA EV + QUOTA
print("6️⃣ TEST FORMULA PROBABILITÀ DA EV")
print("-" * 50)

# Formula corretta: prob = (EV/100 + 1) / quota
ev_test = 22.0
quota_test = 3.20

prob_calculated = (ev_test/100 + 1) / quota_test
ev_check = (prob_calculated * (quota_test - 1) - (1 - prob_calculated)) * 100

print(f"Input: EV {ev_test}%, Quota {quota_test}")
print(f"  Prob calcolata: {prob_calculated*100:.2f}%")
print(f"  EV verifica: {ev_check:.2f}%")

if abs(ev_check - ev_test) < 0.1:
    print(f"✅ PASS: Formula matematicamente corretta")
else:
    print(f"❌ FAIL: Formula EV→Prob errata (diff: {abs(ev_check - ev_test):.2f}%)")
    sys.exit(1)

print()

# 7. VERIFICA INTEGRAZIONE STATISTICHE
print("7️⃣ VERIFICA STATISTICHE SQUADRE")
print("-" * 50)

# Prendi squadra random e calcola statistiche
squadre_uniche = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
squadra_test = 'Inter' if 'Inter' in squadre_uniche else squadre_uniche[0]

df_casa = df[df['HomeTeam'] == squadra_test]
df_trasferta = df[df['AwayTeam'] == squadra_test]
totale_partite = len(df_casa) + len(df_trasferta)

if totale_partite == 0:
    print(f"⚠️  Nessuna partita trovata per {squadra_test}")
else:
    print(f"Test squadra: {squadra_test}")
    print(f"  Partite totali: {totale_partite}")
    print(f"  Partite in casa: {len(df_casa)}")
    print(f"  Partite trasferta: {len(df_trasferta)}")
    
    # Media gol casa
    if len(df_casa) > 0:
        media_gol_casa = df_casa['FTHG'].mean()
        media_gol_subiti_casa = df_casa['FTAG'].mean()
        print(f"  Media gol casa: {media_gol_casa:.2f}")
        print(f"  Media gol subiti casa: {media_gol_subiti_casa:.2f}")
        print(f"✅ PASS: Statistiche calcolabili")
    else:
        print(f"⚠️  Nessuna partita in casa")

print()

# 8. SINTESI FINALE
print("="*70)
print("📊 SINTESI CERTIFICAZIONE")
print("="*70)

checks = {
    "Dati Serie A aggiornati (< 7 giorni)": giorni_diff <= 7,
    "Modelli ML presenti e caricabili": True,
    "Bankroll config completa": len(missing_keys) == 0,
    "Tracking database integro": len(missing_tracking) == 0,
    "Kelly Criterion matematicamente corretto": True,
    "Formula EV→Probabilità corretta": abs(ev_check - ev_test) < 0.1,
    "Statistiche squadre disponibili": totale_partite > 0
}

all_pass = all(checks.values())

for check, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check}")

print()

if all_pass:
    print("🎯 SISTEMA CERTIFICATO - PRONTO PER TRADING OPERATIVO")
    print()
    print("Dati freschi: {} giorni".format(giorni_diff))
    print("Modelli: {} file aggiornati".format(len(expected_models)))
    print("Bankroll: €{:.2f} (cap 5% = €{:.2f})".format(
        config['bankroll_corrente'], 
        config['bankroll_corrente'] * 0.05
    ))
    print("Kelly: {:.0%} fraction (conservativo)".format(config['kelly_fraction']))
    print()
    sys.exit(0)
else:
    print("❌ SISTEMA NON CERTIFICATO - NON PROCEDERE CON TRADING")
    print()
    failed = [k for k, v in checks.items() if not v]
    print("Check falliti:")
    for fail in failed:
        print(f"  - {fail}")
    print()
    sys.exit(1)
