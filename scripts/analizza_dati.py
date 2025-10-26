import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def carica_dati():
    """Carica e unifica tutti i dati CSV delle stagioni"""
    df_list = []
    data_dir = "data"
    
    # Lista specifica dei file delle stagioni da caricare
    stagioni_files = [
        "I1_2021.csv",
        "I1_2122.csv", 
        "I1_2223.csv",
        "I1_2324.csv",
        "I1_2425.csv",
        "I1_2526.csv"
    ]
    
    for file in stagioni_files:
        path = os.path.join(data_dir, file)
        if os.path.exists(path):
            print(f"Caricando {file}...")
            df_parziale = pd.read_csv(path, parse_dates=["Date"], dayfirst=True, encoding="latin1")
            df_list.append(df_parziale)
        else:
            print(f"⚠️  {file} non trovato, saltato")
    
    df = pd.concat(df_list, ignore_index=True)
    print(f"Dataset unificato: {len(df)} partite, {df.columns.shape[0]} colonne")
    return df

def esplora_dataset(df):
    """Analisi esplorativa del dataset"""
    print("\n=== ANALISI ESPLORATIVA ===")
    
    # Info generali
    print(f"\nPeriodo dati: dal {df['Date'].min()} al {df['Date'].max()}")
    print(f"Stagioni coperte: {len(df['Date'].dt.year.unique())} anni")
    
    # Colonne principali
    colonne_essenziali = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    colonne_quote = [col for col in df.columns if any(x in col for x in ['B365', 'BW', 'IW', 'PS', 'WH', 'VC'])]
    
    print(f"\nColonne essenziali disponibili: {len([col for col in colonne_essenziali if col in df.columns])}/6")
    print(f"Colonne quote disponibili: {len(colonne_quote)}")
    
    # Verifica dati mancanti nelle colonne principali
    print("\n=== COMPLETEZZA DATI ===")
    for col in ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']:
        if col in df.columns:
            missing = df[col].isnull().sum()
            print(f"{col}: {missing} valori mancanti ({missing/len(df)*100:.1f}%)")
    
    return colonne_quote

def analizza_risultati(df):
    """Analizza la distribuzione dei risultati"""
    print("\n=== ANALISI RISULTATI ===")
    
    if 'FTR' in df.columns:
        risultati = df['FTR'].value_counts()
        print("\nDistribuzione risultati:")
        for risultato, count in risultati.items():
            print(f"  {risultato}: {count} ({count/len(df)*100:.1f}%)")
    
    # Analisi gol
    if 'FTHG' in df.columns and 'FTAG' in df.columns:
        print(f"\nMedia gol casa: {df['FTHG'].mean():.2f}")
        print(f"Media gol trasferta: {df['FTAG'].mean():.2f}")
        print(f"Media gol totali: {(df['FTHG'] + df['FTAG']).mean():.2f}")
        
        # Partite con più/meno gol
        gol_totali = df['FTHG'] + df['FTAG']
        print(f"Partite Over 2.5: {(gol_totali > 2.5).sum()} ({(gol_totali > 2.5).mean()*100:.1f}%)")
        print(f"Partite Under 2.5: {(gol_totali <= 2.5).sum()} ({(gol_totali <= 2.5).mean()*100:.1f}%)")

def analizza_squadre(df):
    """Analizza performance delle squadre"""
    print("\n=== ANALISI SQUADRE ===")
    
    if 'HomeTeam' in df.columns and 'AwayTeam' in df.columns:
        # Tutte le squadre
        squadre_casa = set(df['HomeTeam'].unique())
        squadre_trasferta = set(df['AwayTeam'].unique())
        tutte_squadre = squadre_casa.union(squadre_trasferta)
        print(f"Numero squadre totali: {len(tutte_squadre)}")
        
        # Squadre più frequenti
        partite_per_squadra = {}
        for squadra in tutte_squadre:
            partite_casa = (df['HomeTeam'] == squadra).sum()
            partite_trasferta = (df['AwayTeam'] == squadra).sum()
            partite_per_squadra[squadra] = partite_casa + partite_trasferta
        
        print("\nSquadre con più partite:")
        top_squadre = sorted(partite_per_squadra.items(), key=lambda x: x[1], reverse=True)[:10]
        for squadra, partite in top_squadre:
            print(f"  {squadra}: {partite} partite")

def crea_statistiche_base(df):
    """Crea statistiche di base per ogni squadra"""
    print("\n=== CREAZIONE STATISTICHE ===")
    
    stats = {}
    squadre = set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))
    
    for squadra in squadre:
        # Partite in casa
        casa = df[df['HomeTeam'] == squadra]
        # Partite in trasferta  
        trasferta = df[df['AwayTeam'] == squadra]
        
        if len(casa) > 0 or len(trasferta) > 0:
            stats[squadra] = {
                'partite_totali': len(casa) + len(trasferta),
                'partite_casa': len(casa),
                'partite_trasferta': len(trasferta),
                'gol_fatti_casa': casa['FTHG'].sum() if len(casa) > 0 else 0,
                'gol_subiti_casa': casa['FTAG'].sum() if len(casa) > 0 else 0,
                'gol_fatti_trasferta': trasferta['FTAG'].sum() if len(trasferta) > 0 else 0,
                'gol_subiti_trasferta': trasferta['FTHG'].sum() if len(trasferta) > 0 else 0,
                'vittorie_casa': (casa['FTR'] == 'H').sum() if len(casa) > 0 else 0,
                'pareggi_casa': (casa['FTR'] == 'D').sum() if len(casa) > 0 else 0,
                'sconfitte_casa': (casa['FTR'] == 'A').sum() if len(casa) > 0 else 0,
                'vittorie_trasferta': (trasferta['FTR'] == 'A').sum() if len(trasferta) > 0 else 0,
                'pareggi_trasferta': (trasferta['FTR'] == 'D').sum() if len(trasferta) > 0 else 0,
                'sconfitte_trasferta': (trasferta['FTR'] == 'H').sum() if len(trasferta) > 0 else 0,
            }
    
    return stats

def main():
    print("=== ANALISI DATI SERIE A ===")
    
    # Carica dati
    df = carica_dati()
    
    # Esplorazione iniziale
    colonne_quote = esplora_dataset(df)
    
    # Analisi risultati
    analizza_risultati(df)
    
    # Analisi squadre
    analizza_squadre(df)
    
    # Crea statistiche
    stats = crea_statistiche_base(df)
    
    # Salva il dataset pulito
    df_pulito = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR'])
    df_pulito.to_csv('data/dataset_pulito.csv', index=False)
    print(f"\nDataset pulito salvato: {len(df_pulito)} partite")
    
    print("\n=== ANALISI COMPLETATA ===")
    return df, stats

if __name__ == "__main__":
    df, stats = main()