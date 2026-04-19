#!/usr/bin/env python3
"""
Script per aggiornare risultati pending in tracking_predictions_live.csv
Recupera risultati reali da I1_2526.csv e popola colonne Risultato_Reale, Corretto, Profit
"""

import pandas as pd
from datetime import datetime
import os
import sys

# Aggiungi path per import moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def normalize_team_name(team):
    """Normalizza nomi squadre per matching"""
    mapping = {
        'Inter Milan': 'Inter',
        'AC Milan': 'Milan',
        'AS Roma': 'Roma',
        'Hellas Verona': 'Verona',
        'Atalanta BC': 'Atalanta',
        'Udinese Calcio': 'Udinese'
    }
    team = str(team).strip()
    return mapping.get(team, team)

def parse_risultato(fthg, ftag, mercato, predizione):
    """
    Determina se predizione è W o L basandosi su risultato finale
    
    Args:
        fthg: Full Time Home Goals
        ftag: Full Time Away Goals
        mercato: Tipo mercato (1X2, Over/Under 2.5, Double Chance, etc.)
        predizione: Predizione fatta (Casa, Pareggio, Trasferta, Over 2.5, etc.)
    
    Returns:
        'W' se corretta, 'L' se errata, None se non determinabile
    """
    try:
        fthg = int(fthg)
        ftag = int(ftag)
    except (ValueError, TypeError):
        return None
    
    total_goals = fthg + ftag
    
    # 1X2
    if mercato == '1X2':
        if predizione == 'Casa' and fthg > ftag:
            return 'W'
        elif predizione == 'Pareggio' and fthg == ftag:
            return 'W'
        elif predizione == 'Trasferta' and fthg < ftag:
            return 'W'
        else:
            return 'L'
    
    # Over/Under 2.5
    elif mercato == 'Over/Under 2.5':
        if predizione == 'Over 2.5' and total_goals > 2:
            return 'W'
        elif predizione == 'Under 2.5' and total_goals < 3:
            return 'W'
        else:
            return 'L'
    
    # Double Chance
    elif mercato == 'Double Chance':
        if predizione == '1X' and fthg >= ftag:  # Casa o Pareggio
            return 'W'
        elif predizione == '12' and fthg != ftag:  # Casa o Trasferta
            return 'W'
        elif predizione == 'X2' and fthg <= ftag:  # Pareggio o Trasferta
            return 'W'
        else:
            return 'L'
    
    # GG/NG (Goal/No Goal)
    elif mercato == 'GG/NG':
        if predizione == 'GG' and fthg > 0 and ftag > 0:
            return 'W'
        elif predizione == 'NG' and (fthg == 0 or ftag == 0):
            return 'W'
        else:
            return 'L'
    
    return None

def aggiorna_risultati_pending():
    """Funzione principale per aggiornare risultati pending"""
    
    print("🔄 AGGIORNAMENTO RISULTATI PENDING\n")
    
    # 1. Carica tracking_predictions_live.csv
    tracking_file = 'tracking_predictions_live.csv'
    if not os.path.exists(tracking_file):
        print(f"❌ File {tracking_file} non trovato!")
        return
    
    df_tracking = pd.read_csv(tracking_file)
    print(f"📊 Caricato {tracking_file}: {len(df_tracking)} righe")
    
    # 2. Carica dataset Serie A 2025-26
    dataset_file = 'data/I1_2526.csv'
    if not os.path.exists(dataset_file):
        print(f"❌ File {dataset_file} non trovato!")
        return
    
    df_dataset = pd.read_csv(dataset_file)
    print(f"📊 Caricato {dataset_file}: {len(df_dataset)} partite")
    
    # Normalizza nomi squadre nel dataset
    df_dataset['HomeTeam'] = df_dataset['HomeTeam'].apply(normalize_team_name)
    df_dataset['AwayTeam'] = df_dataset['AwayTeam'].apply(normalize_team_name)
    
    # Converti date
    df_dataset['Date'] = pd.to_datetime(df_dataset['Date'], format='%d/%m/%Y', errors='coerce')
    df_tracking['Data'] = pd.to_datetime(df_tracking['Data'], errors='coerce')
    
    # 3. Filtra solo predizioni PENDING (senza FILTERED_OUT)
    pending_mask = (
        df_tracking['Risultato_Reale'].isna() &
        (~df_tracking['Note'].str.contains('FILTERED_OUT', na=False))
    )
    df_pending = df_tracking[pending_mask].copy()
    
    print(f"\n🕐 Predizioni PENDING da aggiornare: {len(df_pending)}")
    
    if len(df_pending) == 0:
        print("✅ Nessuna predizione pending da aggiornare!")
        return
    
    # 4. Aggiorna ogni predizione pending
    updated_count = 0
    not_found_count = 0
    
    for idx, pred in df_pending.iterrows():
        casa = normalize_team_name(pred['Casa'])
        ospite = normalize_team_name(pred['Ospite'])
        data_pred = pred['Data']
        mercato = pred['Mercato']
        predizione = pred['Predizione']
        quota = pred['Quota']
        
        # Cerca partita nel dataset
        match = df_dataset[
            (df_dataset['HomeTeam'] == casa) &
            (df_dataset['AwayTeam'] == ospite) &
            (df_dataset['Date'] == data_pred)
        ]
        
        if len(match) == 0:
            # Prova con tolleranza ±1 giorno
            date_min = data_pred - pd.Timedelta(days=1)
            date_max = data_pred + pd.Timedelta(days=1)
            match = df_dataset[
                (df_dataset['HomeTeam'] == casa) &
                (df_dataset['AwayTeam'] == ospite) &
                (df_dataset['Date'] >= date_min) &
                (df_dataset['Date'] <= date_max)
            ]
        
        if len(match) > 0:
            # Partita trovata!
            match_row = match.iloc[0]
            fthg = match_row['FTHG']
            ftag = match_row['FTAG']
            
            # Determina risultato
            risultato = parse_risultato(fthg, ftag, mercato, predizione)
            
            if risultato:
                # Calcola profit
                if risultato == 'W':
                    profit = (quota - 1) * 10  # Stake €10
                    corretto = True
                else:
                    profit = -10
                    corretto = False
                
                # Aggiorna DataFrame
                df_tracking.loc[idx, 'Risultato_Reale'] = risultato
                df_tracking.loc[idx, 'Corretto'] = corretto
                df_tracking.loc[idx, 'Profit'] = profit
                
                updated_count += 1
                print(f"✅ {casa} vs {ospite} ({data_pred.strftime('%d/%m')}) - {mercato}: {predizione} → {risultato} (€{profit:.2f})")
            else:
                print(f"⚠️  {casa} vs {ospite} - Mercato {mercato} non supportato")
        else:
            not_found_count += 1
            # Probabilmente partita futura
            # print(f"⏭️  {casa} vs {ospite} ({data_pred.strftime('%d/%m')}) - Partita non trovata (futura?)")
    
    print(f"\n📊 SUMMARY:")
    print(f"  ✅ Aggiornate: {updated_count}")
    print(f"  ⏭️  Non trovate (future): {not_found_count}")
    
    # 5. Salva CSV aggiornato
    if updated_count > 0:
        # Backup
        backup_file = f'tracking_predictions_live_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df_tracking.to_csv(backup_file, index=False)
        print(f"\n💾 Backup salvato: {backup_file}")
        
        # Salva file aggiornato
        df_tracking.to_csv(tracking_file, index=False)
        print(f"💾 File aggiornato: {tracking_file}")
        
        # Statistiche finali
        completed = df_tracking[df_tracking['Risultato_Reale'].notna() & 
                               (~df_tracking['Note'].str.contains('FILTERED_OUT', na=False))]
        
        if len(completed) > 0:
            wins = (completed['Risultato_Reale'] == 'W').sum()
            total = len(completed)
            win_rate = (wins / total * 100) if total > 0 else 0
            total_profit = completed['Profit'].sum()
            
            print(f"\n📈 STATISTICHE AGGIORNATE:")
            print(f"  Predizioni completate: {total}")
            print(f"  Win Rate: {win_rate:.1f}% ({wins}/{total})")
            print(f"  Profit totale: €{total_profit:.2f}")
    else:
        print("\n⏭️  Nessun aggiornamento effettuato (tutte partite future)")

if __name__ == "__main__":
    aggiorna_risultati_pending()
