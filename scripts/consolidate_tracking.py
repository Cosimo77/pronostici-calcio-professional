#!/usr/bin/env python3
"""
Consolidamento tracking files in singolo file unificato
Unisce tracking_accuracy_live_mar2026.csv, tracking_fase2_febbraio2026.csv, tracking_giocate.csv
Output: tracking_predictions_live.csv (formato standard)
"""

import pandas as pd
import os
from datetime import datetime

# Schema target (basato su tracking_accuracy_live_mar2026.csv)
TARGET_COLUMNS = [
    'Data', 'Giornata', 'Casa', 'Ospite', 'Mercato', 'Predizione',
    'Probabilita_Sistema', 'Quota', 'EV_%', 'Risultato_Reale', 
    'Corretto', 'Profit', 'Note'
]

def normalize_marzo_file(df):
    """File marzo già nel formato corretto"""
    return df[TARGET_COLUMNS] if all(col in df.columns for col in TARGET_COLUMNS) else df

def normalize_febbraio_file(df):
    """
    Normalizza tracking_fase2_febbraio2026.csv
    Colonne: Data,Casa,Ospite,Mercato,Esito,Quota,EV_%,Prob_Modello_%,...
    """
    normalized = pd.DataFrame()
    
    normalized['Data'] = df['Data']
    normalized['Giornata'] = 0  # Non disponibile
    normalized['Casa'] = df['Casa']
    normalized['Ospite'] = df['Ospite']
    normalized['Mercato'] = df['Mercato']
    normalized['Predizione'] = df['Esito']  # Esito → Predizione
    normalized['Probabilita_Sistema'] = df['Prob_Modello_%'] / 100.0  # % → decimale
    normalized['Quota'] = df['Quota']
    normalized['EV_%'] = df['EV_%']
    
    # Mapping Risultato
    normalized['Risultato_Reale'] = df['Risultato'].replace({
        'PENDING': '',
        'WIN': 'W',
        'LOSS': 'L'
    })
    
    normalized['Corretto'] = df['Risultato'].apply(
        lambda x: True if x == 'WIN' else (False if x == 'LOSS' else None)
    )
    
    normalized['Profit'] = df['Profit_Loss']
    normalized['Note'] = df['Note'] + f" | Strategia: {df['Strategia']}" if 'Strategia' in df else df['Note']
    
    return normalized

def normalize_giocate_file(df):
    """
    Normalizza tracking_giocate.csv
    Colonne: group_id,bet_number,tipo_bet,Data,Partita,Mercato,...
    """
    normalized = pd.DataFrame()
    
    normalized['Data'] = df['Data']
    normalized['Giornata'] = 0  # Non disponibile
    
    # Split "Partita" in Casa-Ospite
    if 'Partita' in df.columns:
        partita_split = df['Partita'].str.split('-', n=1, expand=True)
        normalized['Casa'] = partita_split[0].str.strip() if len(partita_split.columns) > 0 else ''
        normalized['Ospite'] = partita_split[1].str.strip() if len(partita_split.columns) > 1 else ''
    else:
        normalized['Casa'] = ''
        normalized['Ospite'] = ''
    
    normalized['Mercato'] = df['Mercato']
    normalized['Predizione'] = ''  # Non disponibile (è nelle quote)
    normalized['Probabilita_Sistema'] = 1.0 / df['Quota_Sistema'] if 'Quota_Sistema' in df else 0.0
    normalized['Quota'] = df['Quota_Sisal'] if 'Quota_Sisal' in df else df.get('Quota_Sistema', 0.0)
    normalized['EV_%'] = df['EV_Realistico'] if 'EV_Realistico' in df else df.get('EV_Modello', 0.0)
    
    # Mapping risultato
    if 'Risultato' in df.columns:
        normalized['Risultato_Reale'] = df['Risultato'].replace({
            'PENDING': '',
            'WIN': 'W',
            'LOSS': 'L',
            'VOID': 'V'
        })
        normalized['Corretto'] = df['Risultato'].apply(
            lambda x: True if x == 'WIN' else (False if x == 'LOSS' else None)
        )
    else:
        normalized['Risultato_Reale'] = ''
        normalized['Corretto'] = None
    
    normalized['Profit'] = df['Profit'] if 'Profit' in df else 0.0
    
    # Note con info gruppo multipla
    if 'tipo_bet' in df.columns and df['tipo_bet'].iloc[0] == 'multipla':
        normalized['Note'] = f"Multipla {df['group_id']} (bet {df['bet_number']}) | {df['Note']}"
    else:
        normalized['Note'] = df['Note'] if 'Note' in df else ''
    
    return normalized

def consolidate_tracking_files():
    """Consolida tutti i file tracking in uno unico"""
    
    print("🔄 Consolidamento tracking files...")
    
    files_config = [
        {
            'path': 'tracking_accuracy_live_mar2026.csv',
            'normalizer': normalize_marzo_file,
            'name': 'Marzo 2026'
        },
        {
            'path': 'tracking_fase2_febbraio2026.csv',
            'normalizer': normalize_febbraio_file,
            'name': 'Febbraio 2026 (FASE2)'
        },
        {
            'path': 'tracking_giocate.csv',
            'normalizer': normalize_giocate_file,
            'name': 'Giocate Diario'
        }
    ]
    
    all_data = []
    stats = {}
    
    for config in files_config:
        filepath = config['path']
        
        if not os.path.exists(filepath):
            print(f"⚠️  {config['name']}: File non trovato ({filepath})")
            continue
        
        try:
            df_raw = pd.read_csv(filepath)
            rows_before = len(df_raw)
            
            # Normalizza
            df_normalized = config['normalizer'](df_raw)
            rows_after = len(df_normalized)
            
            all_data.append(df_normalized)
            stats[config['name']] = {
                'rows': rows_after,
                'file': filepath
            }
            
            print(f"✅ {config['name']}: {rows_after} predizioni caricate")
            
        except Exception as e:
            print(f"❌ {config['name']}: Errore - {e}")
            continue
    
    if not all_data:
        print("❌ Nessun file da consolidare!")
        return False
    
    # Concatena tutti
    df_consolidated = pd.concat(all_data, ignore_index=True)
    
    # Ordina per data
    df_consolidated['Data'] = pd.to_datetime(df_consolidated['Data'])
    df_consolidated = df_consolidated.sort_values('Data', ascending=True)
    df_consolidated['Data'] = df_consolidated['Data'].dt.strftime('%Y-%m-%d')
    
    # Rimuovi duplicati esatti (stessa data, casa, ospite, mercato)
    rows_before_dedup = len(df_consolidated)
    df_consolidated = df_consolidated.drop_duplicates(
        subset=['Data', 'Casa', 'Ospite', 'Mercato'],
        keep='last'  # Mantieni più recente
    )
    rows_after_dedup = len(df_consolidated)
    duplicates_removed = rows_before_dedup - rows_after_dedup
    
    # Salva file unificato
    output_file = 'tracking_predictions_live.csv'
    df_consolidated.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ CONSOLIDAMENTO COMPLETATO")
    print(f"{'='*60}")
    print(f"📊 Statistiche:")
    for name, info in stats.items():
        print(f"   • {name}: {info['rows']} predizioni")
    print(f"\n   TOTALE: {rows_before_dedup} predizioni")
    
    if duplicates_removed > 0:
        print(f"   Duplicati rimossi: {duplicates_removed}")
    
    print(f"\n   📁 Output: {output_file}")
    print(f"   📈 Predizioni finali: {len(df_consolidated)}")
    
    # Statistiche date
    min_date = df_consolidated['Data'].min()
    max_date = df_consolidated['Data'].max()
    print(f"   📅 Range: {min_date} → {max_date}")
    
    # Statistiche accuracy
    corrette = df_consolidated['Corretto'].sum()
    totali = df_consolidated['Corretto'].notna().sum()
    if totali > 0:
        accuracy = (corrette / totali) * 100
        print(f"   🎯 Accuracy: {accuracy:.1f}% ({int(corrette)}/{totali})")
    
    profit_totale = df_consolidated['Profit'].sum()
    print(f"   💰 Profit totale: {profit_totale:+.2f} unità")
    
    print(f"{'='*60}\n")
    
    return True

if __name__ == '__main__':
    success = consolidate_tracking_files()
    exit(0 if success else 1)
