#!/usr/bin/env python3
"""
Setup Validation Tracking System
Crea infrastruttura per tracking predizioni vs risultati reali
"""

import os
import pandas as pd
from datetime import datetime

def setup_tracking_files():
    """Crea/verifica file tracking necessari"""

    # 1. Tracking predizioni live
    tracking_file = 'tracking_predictions_live.csv'

    if not os.path.exists(tracking_file):
        print(f"📝 Creazione {tracking_file}...")
        df = pd.DataFrame(columns=[
            'Date', 'Match', 'Pred_Casa', 'Pred_Pareggio', 'Pred_Trasferta',
            'Quote_Casa', 'Quote_Pareggio', 'Quote_Trasferta',
            'Market_Implied_Casa', 'Market_Implied_Pareggio', 'Market_Implied_Trasferta',
            'Discrepancy_Casa', 'Discrepancy_Pareggio', 'Discrepancy_Trasferta',
            'Risultato', 'Esito_Casa', 'Esito_Pareggio', 'Esito_Trasferta',
            'Brier_Score', 'Recommended_Bet', 'Actual_Bet', 'Outcome', 'Notes'
        ])
        df.to_csv(tracking_file, index=False)
        print(f"✅ {tracking_file} creato")
    else:
        print(f"✅ {tracking_file} già esistente")

    # 2. Tracking accuracy by match type
    accuracy_file = 'tracking_accuracy_by_type.csv'

    if not os.path.exists(accuracy_file):
        print(f"📝 Creazione {accuracy_file}...")
        df = pd.DataFrame(columns=[
            'Match_Type', 'Total_Predictions', 'Avg_Brier_Score',
            'Correct_Winners', 'Winner_Accuracy',
            'Avg_Discrepancy', 'Skip_Rate', 'Correct_Skips'
        ])
        df.to_csv(accuracy_file, index=False)
        print(f"✅ {accuracy_file} creato")
    else:
        print(f"✅ {accuracy_file} già esistente")

    # 3. Match schedule con predizioni pending
    schedule_file = 'tracking_match_schedule.csv'

    if not os.path.exists(schedule_file):
        print(f"📝 Creazione {schedule_file}...")
        df = pd.DataFrame(columns=[
            'Date', 'Time', 'Home_Team', 'Away_Team',
            'Predicted', 'Prediction_Time', 'Result_Tracked', 'Notes'
        ])
        df.to_csv(schedule_file, index=False)
        print(f"✅ {schedule_file} creato")
    else:
        print(f"✅ {schedule_file} già esistente")

    return tracking_file, accuracy_file, schedule_file


def classify_match_type(home_tier, away_tier):
    """
    Classifica tipo match per tracking granulare

    Tiers basati su posizione classifica:
    - TOP: 1-4 (Champions)
    - MID: 5-14 (Mid-table)
    - BOTTOM: 15-20 (Relegation fight)
    """
    tier_map = {
        ('TOP', 'TOP'): 'Top vs Top',
        ('TOP', 'MID'): 'Top vs Mid (asym)',
        ('TOP', 'BOTTOM'): 'Top vs Bottom (HIGH asym)',
        ('MID', 'TOP'): 'Mid vs Top (asym)',
        ('MID', 'MID'): 'Mid vs Mid',
        ('MID', 'BOTTOM'): 'Mid vs Bottom',
        ('BOTTOM', 'TOP'): 'Bottom vs Top (HIGH asym)',
        ('BOTTOM', 'MID'): 'Bottom vs Mid',
        ('BOTTOM', 'BOTTOM'): 'Bottom vs Bottom'
    }

    return tier_map.get((home_tier, away_tier), 'Unknown')


def get_team_tier_simple(team_name):
    """
    Classificazione temporanea team tier (Serie A 2025-26)

    TODO: Automatizzare con API classifica live
    """

    # Tier basato su posizione stimata classifica 6 Apr 2026
    tiers = {
        # TOP 4 (Champions League)
        'Inter': 'TOP',
        'Napoli': 'TOP',
        'Juventus': 'TOP',
        'Atalanta': 'TOP',
        'Milan': 'TOP',  # Borderline ma brand value

        # MID-TABLE (5-14)
        'Roma': 'MID',
        'Lazio': 'MID',
        'Fiorentina': 'MID',
        'Bologna': 'MID',
        'Torino': 'MID',
        'Udinese': 'MID',
        'Genoa': 'MID',
        'Parma': 'MID',
        'Como': 'MID',
        'Hellas Verona': 'MID',

        # BOTTOM (15-20 - Relegation fight)
        'Cagliari': 'BOTTOM',
        'Lecce': 'BOTTOM',
        'Cremonese': 'BOTTOM',
        'Sassuolo': 'BOTTOM',
        'Pisa': 'BOTTOM',
    }

    return tiers.get(team_name, 'MID')  # Default mid se sconosciuto


def log_prediction(home, away, model_probs, bookmaker_odds=None):
    """
    Logga predizione nel tracking system

    Args:
        home: Nome squadra casa
        away: Nome squadra ospite
        model_probs: Dict {'H': 0.xx, 'D': 0.xx, 'A': 0.xx}
        bookmaker_odds: Dict {'H': 2.xx, 'D': 3.xx, 'A': 2.xx} (optional)
    """

    tracking_file = 'tracking_predictions_live.csv'
    schedule_file = 'tracking_match_schedule.csv'

    # Calcola discrepancy se quote disponibili
    if bookmaker_odds:
        # Converti quote in probabilità implicite (rimuovi overround)
        total_implied = sum(1/odd for odd in bookmaker_odds.values())
        market_probs = {k: (1/v)/total_implied for k, v in bookmaker_odds.items()}

        discrepancies = {
            k: model_probs[k] - market_probs[k]
            for k in model_probs.keys()
        }

        # Flag se large discrepancy
        max_disc = max(abs(v) for v in discrepancies.values())
        warning = "⚠️ LARGE DISCREPANCY" if max_disc > 0.15 else ""
    else:
        market_probs = {'H': None, 'D': None, 'A': None}
        discrepancies = {'H': None, 'D': None, 'A': None}
        bookmaker_odds = {'H': None, 'D': None, 'A': None}
        warning = "No market data"

    # Classifica match type
    home_tier = get_team_tier_simple(home)
    away_tier = get_team_tier_simple(away)
    match_type = classify_match_type(home_tier, away_tier)

    # Aggiungi a schedule
    schedule_entry = {
        'Date': datetime.now().strftime('%Y-%m-%d'),
        'Time': datetime.now().strftime('%H:%M'),
        'Home_Team': home,
        'Away_Team': away,
        'Predicted': 'YES',
        'Prediction_Time': datetime.now().isoformat(),
        'Result_Tracked': 'PENDING',
        'Notes': f"{match_type} | {warning}"
    }

    df_schedule = pd.read_csv(schedule_file)
    df_schedule = pd.concat([df_schedule, pd.DataFrame([schedule_entry])], ignore_index=True)
    df_schedule.to_csv(schedule_file, index=False)

    # Prepara entry tracking (risultato da aggiungere dopo)
    tracking_entry = {
        'Date': datetime.now().strftime('%Y-%m-%d'),
        'Match': f"{home} vs {away}",
        'Pred_Casa': round(model_probs['H'] * 100, 1),
        'Pred_Pareggio': round(model_probs['D'] * 100, 1),
        'Pred_Trasferta': round(model_probs['A'] * 100, 1),
        'Quote_Casa': bookmaker_odds['H'],
        'Quote_Pareggio': bookmaker_odds['D'],
        'Quote_Trasferta': bookmaker_odds['A'],
        'Market_Implied_Casa': round(market_probs['H'] * 100, 1) if market_probs['H'] else None,
        'Market_Implied_Pareggio': round(market_probs['D'] * 100, 1) if market_probs['D'] else None,
        'Market_Implied_Trasferta': round(market_probs['A'] * 100, 1) if market_probs['A'] else None,
        'Discrepancy_Casa': round(discrepancies['H'] * 100, 1) if discrepancies['H'] else None,
        'Discrepancy_Pareggio': round(discrepancies['D'] * 100, 1) if discrepancies['D'] else None,
        'Discrepancy_Trasferta': round(discrepancies['A'] * 100, 1) if discrepancies['A'] else None,
        'Risultato': 'PENDING',
        'Esito_Casa': None,
        'Esito_Pareggio': None,
        'Esito_Trasferta': None,
        'Brier_Score': None,
        'Recommended_Bet': 'TBD',
        'Actual_Bet': None,
        'Outcome': 'PENDING',
        'Notes': f"{match_type} | {warning}"
    }

    df_tracking = pd.read_csv(tracking_file)
    df_tracking = pd.concat([df_tracking, pd.DataFrame([tracking_entry])], ignore_index=True)
    df_tracking.to_csv(tracking_file, index=False)

    print(f"\n✅ Predizione logged: {home} vs {away}")
    print(f"   Match Type: {match_type}")
    print(f"   Model: H {model_probs['H']*100:.1f}% | D {model_probs['D']*100:.1f}% | A {model_probs['A']*100:.1f}%")

    # Type guard: verifica che bookmaker odds e derived data siano disponibili
    if (bookmaker_odds['H'] is not None and
        market_probs['H'] is not None and
        discrepancies['H'] is not None):
        print(f"   Market: H {market_probs['H']*100:.1f}% | D {market_probs['D']*100:.1f}% | A {market_probs['A']*100:.1f}%")  # type: ignore
        print(f"   Discrepancy: H {discrepancies['H']*100:+.1f}pp | D {discrepancies['D']*100:+.1f}pp | A {discrepancies['A']*100:+.1f}pp")  # type: ignore

        # Calcola max discrepancy se disponibile
        if discrepancies['H'] is not None:
            max_disc = max(abs(discrepancies[k]) for k in ['H', 'D', 'A'] if discrepancies[k] is not None)  # type: ignore
            if max_disc > 0.15:
                print(f"   ⚠️  WARNING: Max discrepancy {max_disc*100:.1f}pp - Review antes de bet!")


def update_result(home, away, result):
    """
    Aggiorna tracking con risultato effettivo

    Args:
        home: Nome squadra casa
        away: Nome squadra ospite
        result: 'H' (casa), 'D' (pareggio), 'A' (trasferta)
    """

    tracking_file = 'tracking_predictions_live.csv'
    df = pd.read_csv(tracking_file)

    # Trova match
    mask = (df['Match'] == f"{home} vs {away}") & (df['Risultato'] == 'PENDING')

    if not mask.any():
        print(f"❌ Match {home} vs {away} non trovato in tracking")
        return

    # Aggiorna risultato
    result_map = {'H': 'Casa WIN', 'D': 'Pareggio', 'A': 'Trasferta WIN'}
    df.loc[mask, 'Risultato'] = result_map[result]

    # Esiti binari
    df.loc[mask, 'Esito_Casa'] = 1 if result == 'H' else 0
    df.loc[mask, 'Esito_Pareggio'] = 1 if result == 'D' else 0
    df.loc[mask, 'Esito_Trasferta'] = 1 if result == 'A' else 0

    # Calcola Brier Score
    row = df[mask].iloc[0]
    pred = [row['Pred_Casa']/100, row['Pred_Pareggio']/100, row['Pred_Trasferta']/100]
    actual = [1 if result == 'H' else 0, 1 if result == 'D' else 0, 1 if result == 'A' else 0]
    brier = sum((p - a)**2 for p, a in zip(pred, actual)) / 3

    df.loc[mask, 'Brier_Score'] = round(brier, 4)

    # Salva
    df.to_csv(tracking_file, index=False)

    print(f"\n✅ Risultato aggiornato: {home} vs {away} → {result_map[result]}")
    print(f"   Brier Score: {brier:.4f}")

    # Update schedule
    schedule_file = 'tracking_match_schedule.csv'
    df_schedule = pd.read_csv(schedule_file)
    mask_schedule = (df_schedule['Home_Team'] == home) & (df_schedule['Away_Team'] == away)
    df_schedule.loc[mask_schedule, 'Result_Tracked'] = 'YES'
    df_schedule.to_csv(schedule_file, index=False)


def generate_performance_report():
    """Genera report performance aggregato"""

    tracking_file = 'tracking_predictions_live.csv'

    if not os.path.exists(tracking_file):
        print("❌ Nessun dato tracking disponibile")
        return

    df = pd.read_csv(tracking_file)

    # Filtra solo match completati
    df_completed = df[df['Risultato'] != 'PENDING']

    if len(df_completed) == 0:
        print("⏳ Nessun match completato ancora")
        return

    print("\n" + "="*60)
    print("📊 PERFORMANCE REPORT")
    print("="*60)

    # Overall metrics
    avg_brier = df_completed['Brier_Score'].mean()
    total_matches = len(df_completed)

    print(f"\n📈 OVERALL METRICS:")
    print(f"   Total Matches: {total_matches}")
    print(f"   Avg Brier Score: {avg_brier:.4f}")
    print(f"   Target: <0.2657 {'✅' if avg_brier < 0.2657 else '❌'}")

    # By match type (se abbastanza dati)
    if 'Notes' in df_completed.columns:
        match_types = df_completed['Notes'].str.extract(r'(.*?) \|')[0]
        if not match_types.isna().all():
            print(f"\n📊 BY MATCH TYPE:")
            for mtype in match_types.unique():
                if pd.notna(mtype):
                    subset = df_completed[match_types == mtype]
                    avg_brier_type = subset['Brier_Score'].mean()
                    print(f"   {mtype}: {len(subset)} matches, Brier {avg_brier_type:.4f}")

    # Discrepancy analysis
    if 'Discrepancy_Casa' in df_completed.columns:
        max_disc_cols = ['Discrepancy_Casa', 'Discrepancy_Pareggio', 'Discrepancy_Trasferta']
        df_completed['Max_Disc'] = df_completed[max_disc_cols].abs().max(axis=1)

        high_disc = df_completed[df_completed['Max_Disc'] > 15]
        if len(high_disc) > 0:
            print(f"\n⚠️  HIGH DISCREPANCY MATCHES: {len(high_disc)}")
            print(f"   Avg Brier (high disc): {high_disc['Brier_Score'].mean():.4f}")

    print("\n" + "="*60)


if __name__ == '__main__':
    print("🚀 Setup Validation Tracking System\n")

    # Setup files
    tracking_file, accuracy_file, schedule_file = setup_tracking_files()

    print(f"\n✅ Setup completato!")
    print(f"\nFile creati/verificati:")
    print(f"  • {tracking_file}")
    print(f"  • {accuracy_file}")
    print(f"  • {schedule_file}")

    print(f"\n📖 USAGE:")
    print(f"\n1. Log predizione:")
    print(f"   from scripts.setup_validation_tracking import log_prediction")
    print(f"   log_prediction('Juventus', 'Genoa', {{'H': 0.45, 'D': 0.30, 'A': 0.25}}, {{'H': 1.40, 'D': 4.50, 'A': 8.00}})")

    print(f"\n2. Update risultato:")
    print(f"   from scripts.setup_validation_tracking import update_result")
    print(f"   update_result('Juventus', 'Genoa', 'H')  # H=casa, D=pareggio, A=trasferta")

    print(f"\n3. Report performance:")
    print(f"   from scripts.setup_validation_tracking import generate_performance_report")
    print(f"   generate_performance_report()")

    print(f"\n🎯 Ready per tracking predizioni!")
