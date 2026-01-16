#!/usr/bin/env python3
"""Audit coerenza dati tra locale e Render"""

import requests
import pandas as pd

print("🔍 AUDIT COERENZA DATI\n")

# 1. Dataset locale
print("1️⃣ Dataset Locale:")
df = pd.read_csv('data/dataset_pulito.csv')
print(f"   Partite: {len(df)}")
print(f"   Ultima: {df['Date'].max()}")

# 2. Render API
print("\n2️⃣ Render Production:")
try:
    r = requests.get('https://pronostici-calcio-professional.onrender.com/api/health', timeout=10)
    data = r.json()
    render_records = data.get('database_records', 0)
    print(f"   database_records: {render_records}")
    print(f"   status: {data.get('status')}")
    
    # 3. Confronto
    print("\n3️⃣ Analisi Gap:")
    gap = len(df) - render_records
    print(f"   Locale: {len(df)} partite")
    print(f"   Render: {render_records} partite")
    print(f"   Differenza: {gap} partite")
    
    if gap > 0:
        print(f"\n⚠️  DISCREPANZA: Render ha {gap} partite in meno")
        print("\n🔧 Soluzione:")
        print("   1. Attendere deploy Render (in corso)")
        print("   2. Oppure trigger manuale:")
        print("      curl -X POST https://.../api/automation/force_update")
    else:
        print("\n✅ SINCRONIZZATO")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

print("\n" + "="*50)
