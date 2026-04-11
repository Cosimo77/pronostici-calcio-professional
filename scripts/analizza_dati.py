#!/usr/bin/env python3
"""
Script per consolidare tutti i file CSV delle stagioni Serie A
in un unico dataset_pulito.csv
"""

import glob
import os
from pathlib import Path

import pandas as pd


def main():
    print("=" * 60)
    print("  CONSOLIDAMENTO DATASET SERIE A")
    print("=" * 60)

    # Directory dati
    data_dir = Path(__file__).parent.parent / "data"

    # Trova tutti i file I1_*.csv (stagioni Serie A)
    csv_files = sorted(glob.glob(str(data_dir / "I1_*.csv")))

    if not csv_files:
        print("❌ Nessun file I1_*.csv trovato in data/")
        return False

    print(f"\n📁 Trovati {len(csv_files)} file stagioni:")
    for f in csv_files:
        print(f"   • {os.path.basename(f)}")

    # Carica e concatena tutti i CSV
    all_dataframes = []
    total_matches = 0

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)

            # Verifica colonne obbligatorie
            required_cols = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
            if not all(col in df.columns for col in required_cols):
                print(f"⚠️ Skipping {os.path.basename(csv_file)}: colonne mancanti")
                continue

            # Aggiungi colonna stagione per tracciabilità
            season = os.path.basename(csv_file).replace("I1_", "").replace(".csv", "")
            df["Div"] = "I1"  # Serie A

            all_dataframes.append(df)
            total_matches += len(df)
            print(f"   ✅ {os.path.basename(csv_file)}: {len(df)} partite")

        except Exception as e:
            print(f"   ❌ Errore caricamento {os.path.basename(csv_file)}: {e}")
            continue

    if not all_dataframes:
        print("\n❌ Nessun dataset valido caricato")
        return False

    # Concatena tutti i dataframes
    print(f"\n🔄 Concatenamento {len(all_dataframes)} dataset...")
    df_consolidated = pd.concat(all_dataframes, ignore_index=True, sort=False)

    # Rimuovi duplicati (stessa data, casa, trasferta)
    print("🔄 Rimozione duplicati...")
    before_dedup = len(df_consolidated)
    df_consolidated = df_consolidated.drop_duplicates(subset=["Date", "HomeTeam", "AwayTeam"], keep="last")
    after_dedup = len(df_consolidated)
    duplicates_removed = before_dedup - after_dedup

    if duplicates_removed > 0:
        print(f"   ⚠️ Rimossi {duplicates_removed} duplicati")

    # Ordina per data (parse prima perché formato DD/MM/YYYY)
    print("🔄 Ordinamento per data...")
    try:
        df_consolidated["DateParsed"] = pd.to_datetime(
            df_consolidated["Date"], dayfirst=True, format="mixed", errors="coerce"
        )
        df_consolidated = df_consolidated.sort_values("DateParsed").reset_index(drop=True)
        df_consolidated = df_consolidated.drop("DateParsed", axis=1)
    except:
        # Fallback: ordina come stringa (meno affidabile)
        df_consolidated = df_consolidated.sort_values("Date").reset_index(drop=True)

    # Mostra info dataset finale
    print(f"\n📊 Dataset consolidato:")
    print(f"   • Totale partite: {len(df_consolidated)}")

    if len(df_consolidated) > 0:
        # Conta partite per anno
        df_temp = df_consolidated.copy()
        try:
            df_temp["DateParsed"] = pd.to_datetime(df_temp["Date"], dayfirst=True, format="mixed", errors="coerce")
            prima_data = df_temp["DateParsed"].min()
            ultima_data = df_temp["DateParsed"].max()
            print(f"   • Periodo: {prima_data.strftime('%d/%m/%Y') if pd.notna(prima_data) else df_temp['Date'].min()}")
            print(
                f"            → {ultima_data.strftime('%d/%m/%Y') if pd.notna(ultima_data) else df_temp['Date'].max()}"
            )
        except:
            print(f"   • Prima partita: {df_consolidated['Date'].iloc[0]}")
            print(f"   • Ultima partita: {df_consolidated['Date'].iloc[-1]}")

    # Salva dataset pulito
    output_path = data_dir / "dataset_pulito.csv"
    df_consolidated.to_csv(output_path, index=False)
    print(f"\n✅ Dataset salvato: {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

    return True


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
