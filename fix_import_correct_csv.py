#!/usr/bin/env python3
"""
Corregge importazione database: cancella 8 bet sbagliate e importa 28 corrette
da tracking_predictions_live.csv
"""

import os
import sys
from datetime import datetime

import pandas as pd

# Add project root
sys.path.insert(0, os.path.dirname(__file__))


def fix_database_import():
    """Cancella bet vecchie e importa tracking_predictions_live.csv corretto"""

    print("=" * 80)
    print("FIX IMPORTAZIONE DATABASE - TRACKING_PREDICTIONS_LIVE.CSV")
    print("=" * 80)

    # 1. Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL non configurato")
        return False

    print(f"✅ DATABASE_URL configurato ({len(database_url)} chars)")

    # 2. Check CSV
    csv_file = "tracking_predictions_live.csv"
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} non trovato")
        return False

    # 3. Load CSV
    df = pd.read_csv(csv_file)
    print(f"✅ CSV caricato: {len(df)} righe totali")

    # 4. Filtra solo scommesse effettive (con Risultato_Reale)
    scommesse = df[df["Risultato_Reale"].notna()].copy()
    print(f"✅ Scommesse effettive: {len(scommesse)}")

    # 5. Init database
    try:
        from database import init_db, is_db_available
        from database.connection import get_db_connection
        from database.models import BetModel

        if not is_db_available():
            print("⚠️  Database non disponibile, provo init...")
            if not init_db():
                print("❌ Impossibile inizializzare database")
                return False

        print("✅ Database connesso")

    except Exception as e:
        print(f"❌ Errore import moduli: {e}")
        return False

    # 6. CANCELLA bet vecchie
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM bets")
        old_count = cursor.fetchone()[0]
        print(f"\n🗑️  Bet vecchie da cancellare: {old_count}")

        cursor.execute("DELETE FROM bets")
        conn.commit()
        print(f"✅ {old_count} bet vecchie cancellate")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Errore cancellazione: {e}")
        return False

    # 7. IMPORTA bet corrette
    migrated = 0
    errors = []

    print(f"\n📥 Importo {len(scommesse)} scommesse da tracking_predictions_live.csv...")

    for idx, row in scommesse.iterrows():
        try:
            # Parse data
            data_str = str(row["Data"])  # es. "2026-02-09"

            # Costruisci partita
            casa = str(row.get("Casa", ""))
            ospite = str(row.get("Ospite", ""))

            # Se Casa contiene "vs" (formato alternativo), splitta
            if " vs " in casa:
                parts = casa.split(" vs ")
                casa = parts[0]
                ospite = parts[1] if len(parts) > 1 else ospite

            partita = f"{casa} vs {ospite}".strip()

            # Mercato e predizione
            mercato = str(row.get("Mercato", ""))
            predizione = str(row.get("Predizione", ""))

            # Combina mercato - predizione se necessario
            if predizione and predizione != "nan":
                mercato_completo = f"{mercato} - {predizione}"
            else:
                mercato_completo = mercato

            # Quote
            quota = float(row.get("Quota", 0))

            # EV
            ev_str = str(row.get("EV_%", ""))
            if ev_str and ev_str != "nan":
                ev_modello = f"+{ev_str}%" if not ev_str.startswith(("+", "-")) else f"{ev_str}%"
            else:
                ev_modello = None

            # Stake (default 10 se presente risultato, 0 altrimenti)
            stake = 10.0

            # Risultato
            risultato_reale = str(row.get("Risultato_Reale", ""))
            risultato = "WIN" if risultato_reale == "W" else "LOSS" if risultato_reale == "L" else "PENDING"

            # Profit
            profit = float(row.get("Profit", 0))

            # Note
            note = str(row.get("Note", "")) if pd.notna(row.get("Note")) else ""

            # Add bet
            bet_id = BetModel.add_bet(
                data=data_str,
                partita=partita,
                mercato=mercato_completo,
                quota_sistema=quota,
                quota_sisal=quota,
                ev_modello=ev_modello,
                ev_realistico=None,
                stake=str(stake),
                risultato=risultato,
                profit=profit,
                note=note,
            )

            if bet_id:
                migrated += 1
                if migrated <= 5 or migrated % 10 == 0:
                    print(f"   ✅ #{migrated}: {partita} - {mercato_completo} ({risultato})")

        except Exception as e:
            error_msg = f"Errore row {idx}: {str(e)}"
            errors.append(error_msg)
            print(f"   ❌ {error_msg}")

    # 8. Summary
    print("\n" + "=" * 80)
    print("RISULTATO MIGRAZIONE")
    print("=" * 80)
    print(f"✅ Bet migrate: {migrated}/{len(scommesse)}")
    print(f"❌ Errori: {len(errors)}")

    if errors:
        print("\n⚠️  ERRORI:")
        for err in errors[:10]:
            print(f"   - {err}")

    # 9. Verifica finale
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bets")
        final_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        print(f"\n📊 Bet totali nel database: {final_count}")

    except Exception as e:
        print(f"⚠️  Verifica finale fallita: {e}")

    print("=" * 80)
    return migrated > 0


if __name__ == "__main__":
    success = fix_database_import()
    sys.exit(0 if success else 1)
