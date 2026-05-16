#!/usr/bin/env python3
"""
Backup Automatico Database Diario Betting
Esegue export giornaliero del database Render in JSON
Da schedulare con cron o GitHub Actions
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Esegue backup completo database diario betting"""

    print("=" * 60)
    print("🔄 BACKUP AUTOMATICO DATABASE DIARIO")
    print("=" * 60)

    try:
        # Import dopo sys.path fix
        from database import get_db_connection, init_db, is_db_available

        # Inizializza database connection pool
        if not is_db_available():
            init_db()

        # Crea directory backups
        backup_dir = project_root / "backups"
        backup_dir.mkdir(exist_ok=True)

        print(f"📁 Directory backup: {backup_dir}")

        # Connect to database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Export completo bets table
                cur.execute(
                    """
                    SELECT id, data, partita, mercato, quota_sistema, quota_sisal,
                           ev_modello, ev_realistico, stake, risultato, profit, note,
                           created_at, updated_at, group_id, bet_number, tipo_bet
                    FROM bets
                    ORDER BY data, id
                """
                )

                rows = cur.fetchall()
                count = len(rows)

                print(f"📊 Bet trovate: {count}")

                if count == 0:
                    print("⚠️ Nessun bet da backuppare")
                    return

                # Converti a lista di dict
                backup_data = {"export_date": datetime.now().isoformat(), "total_bets": count, "bets": []}

                for row in rows:
                    backup_data["bets"].append(
                        {
                            "id": row[0],
                            "data": row[1].isoformat() if row[1] else None,
                            "partita": row[2],
                            "mercato": row[3],
                            "quota_sistema": float(row[4]) if row[4] else None,
                            "quota_sisal": float(row[5]) if row[5] else None,
                            "ev_modello": row[6],
                            "ev_realistico": row[7],
                            "stake": row[8],
                            "risultato": row[9],
                            "profit": float(row[10]) if row[10] else None,
                            "note": row[11],
                            "created_at": row[12].isoformat() if row[12] else None,
                            "updated_at": row[13].isoformat() if row[13] else None,
                            "group_id": row[14],
                            "bet_number": row[15],
                            "tipo_bet": row[16],
                        }
                    )

                # Salva backup giornaliero
                today = datetime.now().strftime("%Y%m%d")
                backup_file = backup_dir / f"daily_backup_{today}.json"

                with open(backup_file, "w") as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)

                file_size = backup_file.stat().st_size / 1024  # KB
                print(f"✅ Backup salvato: {backup_file.name} ({file_size:.1f} KB)")

                # Cleanup vecchi backup (>30 giorni)
                cleanup_old_backups(backup_dir, days=30)

                # Opzionale: Git commit automatico
                try:
                    import subprocess

                    # Check se ci sono modifiche
                    result = subprocess.run(
                        ["git", "diff", "--quiet", "backups/"], cwd=project_root, capture_output=True
                    )

                    if result.returncode != 0:  # Ci sono modifiche
                        subprocess.run(["git", "add", "backups/"], cwd=project_root, check=True)
                        subprocess.run(
                            ["git", "commit", "-m", f"🔄 Backup automatico {today}"], cwd=project_root, check=True
                        )
                        print("📌 Backup committato su Git")
                    else:
                        print("ℹ️ Nessuna modifica da committare")

                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    print(f"⚠️ Git commit skipped: {e}")

                print("=" * 60)
                print("✅ BACKUP COMPLETATO")
                print("=" * 60)

    except ImportError as e:
        print(f"❌ Errore import: {e}")
        print("⚠️ Database module non disponibile")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Errore durante backup: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def cleanup_old_backups(backup_dir: Path, days: int = 30):
    """
    Cancella backup più vecchi di X giorni

    Args:
        backup_dir: Directory contenente i backup
        days: Giorni di retention (default 30)
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted = 0

    for backup_file in backup_dir.glob("daily_backup_*.json"):
        # Verifica età file
        file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

        if file_mtime < cutoff_date:
            backup_file.unlink()
            deleted += 1
            print(f"🗑️ Rimosso backup vecchio: {backup_file.name}")

    if deleted == 0:
        print(f"ℹ️ Nessun backup da rimuovere (retention: {days} giorni)")
    else:
        print(f"🗑️ {deleted} backup vecchi rimossi")


if __name__ == "__main__":
    main()
