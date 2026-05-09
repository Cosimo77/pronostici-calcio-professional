#!/usr/bin/env python3
"""
Migrazione automatica tracking_giocate.csv → PostgreSQL Render
Eseguito automaticamente al primo avvio con DATABASE_URL configurato
"""

import os
import sys
from datetime import datetime

import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def migrate_csv_to_postgres():
    """Migra dati CSV → PostgreSQL se database disponibile"""

    print("=" * 80)
    print("MIGRAZIONE CSV → POSTGRESQL")
    print("=" * 80)

    # 1. Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL non configurato - migrazione non possibile")
        return False

    print(f"✅ DATABASE_URL configurato ({len(database_url)} chars)")

    # 2. Check CSV exists
    csv_file = "tracking_giocate.csv"
    if not os.path.exists(csv_file):
        print(f"⚠️  {csv_file} non trovato - probabilmente già migrato")
        return True

    # 3. Load CSV
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ CSV caricato: {len(df)} righe")
    except Exception as e:
        print(f"❌ Errore lettura CSV: {e}")
        return False

    # 4. Init database
    try:
        from database import init_db, is_db_available

        if not is_db_available():
            print("📦 Inizializzazione database...")
            success = init_db()
            if not success:
                print("❌ Inizializzazione database fallita")
                return False

        print("✅ Database connesso")
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return False

    # 5. Migrate data
    try:
        from database.models import BetModel

        migrated = 0
        skipped = 0

        for idx, row in df.iterrows():
            # Skip header or invalid rows
            if pd.isna(row.get("Partita")):
                skipped += 1
                continue

            # Map CSV columns to database model
            bet_data = {
                "group_id": row.get("group_id", ""),
                "bet_number": int(row["bet_number"]) if pd.notna(row.get("bet_number")) else idx + 1,
                "tipo_bet": row.get("tipo_bet", "SINGLE"),
                "data_giocata": row.get("Data", ""),
                "partita": row["Partita"],
                "mercato": row.get("Mercato", ""),
                "quota_sistema": float(row["Quota_Sistema"]) if pd.notna(row.get("Quota_Sistema")) else 0.0,
                "quota_sisal": float(row["Quota_Sisal"]) if pd.notna(row.get("Quota_Sisal")) else 0.0,
                "ev_modello": row.get("EV_Modello", ""),
                "ev_realistico": row.get("EV_Realistico", ""),
                "stake": float(row["Stake"]) if pd.notna(row.get("Stake")) else 0.0,
                "risultato": row.get("Risultato", "PENDING"),
                "profit": float(row["Profit"]) if pd.notna(row.get("Profit")) else 0.0,
                "note": row.get("Note", ""),
            }

            # Insert into database
            BetModel.add_bet(**bet_data)
            migrated += 1
            print(f"  ✅ Migrato bet #{bet_data['bet_number']}: {bet_data['partita']} ({bet_data['risultato']})")

        print(f"\n✅ Migrazione completata: {migrated} bets migrati, {skipped} skipped")

        # 6. Verify migration
        all_bets = BetModel.get_all()
        print(f"✅ Verifica: {len(all_bets)} bets totali nel database")

        return True

    except Exception as e:
        print(f"❌ Errore migrazione dati: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_csv_to_postgres()

    if success:
        print("\n" + "=" * 80)
        print("✅ MIGRAZIONE COMPLETATA CON SUCCESSO")
        print("=" * 80)
        print("\nPROSSIMI PASSI:")
        print("1. Verifica dati: curl .../api/diario/stats")
        print("2. Rimuovi CSV: git rm tracking_giocate.csv && git commit && git push")
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ MIGRAZIONE FALLITA")
        print("=" * 80)
        sys.exit(1)
