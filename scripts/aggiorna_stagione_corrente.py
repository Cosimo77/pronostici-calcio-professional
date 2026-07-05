#!/usr/bin/env python3
"""
Script per scaricare dati aggiornati stagione corrente Serie A
Chiamato da aggiorna_automatico.py

LOGICA STAGIONALE INTELLIGENTE:
- Agosto-Maggio: Scarica stagione corrente
- Giugno-Luglio: Prova nuova stagione, fallback su precedente
- Auto-retry se 404 (dati non ancora disponibili)
"""

import os
import sys
from datetime import datetime

import pandas as pd
import requests


def determina_stagioni():
    """
    Determina quali stagioni provare a scaricare
    Returns: list di tuple (season_code, year_display)
    """
    now = datetime.now()
    stagioni_da_provare = []

    if now.month >= 8:
        # Agosto-Dicembre: stagione corrente (es. 2026-27 se siamo ad agosto 2026)
        current_season = f"{str(now.year)[2:]}{str(now.year + 1)[2:]}"
        stagioni_da_provare.append((current_season, f"{now.year}-{now.year + 1}"))

    elif now.month >= 6:
        # Giugno-Luglio: PAUSA ESTIVA
        # Prova PRIMA la nuova stagione (potrebbe essere pubblicata in anticipo)
        # Poi fallback su stagione appena conclusa
        next_season = f"{str(now.year)[2:]}{str(now.year + 1)[2:]}"
        prev_season = f"{str(now.year - 1)[2:]}{str(now.year)[2:]}"

        stagioni_da_provare.append((next_season, f"{now.year}-{now.year + 1}"))
        stagioni_da_provare.append((prev_season, f"{now.year - 1}-{now.year}"))

    else:
        # Gennaio-Maggio: stagione in corso
        current_season = f"{str(now.year - 1)[2:]}{str(now.year)[2:]}"
        stagioni_da_provare.append((current_season, f"{now.year - 1}-{now.year}"))

    return stagioni_da_provare


def download_stagione(season_code, year_display):
    """
    Tenta download di una specifica stagione
    Returns: (success, num_partite, ultima_data)
    """
    url = f"https://www.football-data.co.uk/mmz4281/{season_code}/I1.csv"
    output_file = f"data/I1_{season_code}.csv"

    print(f"📥 Tentativo download stagione {year_display} (codice: {season_code})...")
    print(f"   URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Salva
        os.makedirs("data", exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(response.content)

        # Verifica
        df = pd.read_csv(output_file)
        num_partite = len(df)

        if num_partite == 0:
            print("⚠️  File vuoto - dati non ancora disponibili")
            return False, 0, None

        ultima_data = df["Date"].iloc[-1] if "Date" in df.columns and len(df) > 0 else "N/A"

        print(f"✅ Download completato: {num_partite} partite")
        print(f"   Ultima partita: {ultima_data}")

        return True, num_partite, ultima_data

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"⏳ Stagione {year_display} non ancora disponibile (404)")
        else:
            print(f"❌ Errore HTTP {e.response.status_code}: {e}")
        return False, 0, None

    except Exception as e:
        print(f"❌ Errore download: {e}")
        return False, 0, None


def download_stagione_corrente():
    """
    Scarica CSV stagione corrente con logica intelligente
    Prova multiple stagioni se necessario (es. periodo estivo)
    """
    stagioni = determina_stagioni()

    print(f"🔍 Stagioni da controllare: {len(stagioni)}")
    for season_code, year_display in stagioni:
        print(f"   - {year_display} (codice: {season_code})")
    print()

    # Prova ogni stagione in ordine
    for season_code, year_display in stagioni:
        success, num_partite, ultima_data = download_stagione(season_code, year_display)

        if success:
            print(f"\n✅ Successo! Scaricata stagione {year_display}")
            return True
        else:
            print(f"❌ Fallito download stagione {year_display}, provo successiva...\n")

    # Se nessuna stagione disponibile
    print("\n⚠️  ATTENZIONE: Nessuna stagione disponibile")
    print("   Possibili cause:")
    print("   - Periodo estivo (giugno-luglio) senza dati")
    print("   - Nuova stagione non ancora iniziata")
    print("   - Problema connessione a football-data.co.uk")
    print("\n   Il sistema userà i dati storici esistenti.")

    return False


if __name__ == "__main__":
    success = download_stagione_corrente()
    sys.exit(0 if success else 1)
