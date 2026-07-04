#!/usr/bin/env python3
"""
Migrazione Database: Render PostgreSQL → Neon PostgreSQL
Usa psycopg2 (già installato) - NON richiede pg_dump/psql
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("❌ psycopg2 non trovato. Installa con:")
    print("   pip install psycopg2-binary")
    sys.exit(1)


class DatabaseMigrator:
    """Migra dati da Render a Neon PostgreSQL"""

    def __init__(self):
        self.render_conn = None
        self.neon_conn = None
        self.backup_file = f"backup_render_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    def connect_render(self, database_url: str):
        """Connetti a database Render"""
        print("\n📡 Connessione a Render...")
        try:
            self.render_conn = psycopg2.connect(database_url)
            print("✅ Connesso a Render PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Errore connessione Render: {e}")
            return False

    def connect_neon(self, database_url: str):
        """Connetti a database Neon"""
        print("\n📡 Connessione a Neon...")
        try:
            self.neon_conn = psycopg2.connect(database_url)
            self.neon_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print("✅ Connesso a Neon PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Errore connessione Neon: {e}")
            return False

    def export_data(self) -> Dict[str, Any]:
        """Esporta dati da Render"""
        print("\n💾 Esportazione dati in corso...")

        data = {"exported_at": datetime.now().isoformat(), "tables": {}}

        try:
            cursor = self.render_conn.cursor()

            # Lista tabelle
            cursor.execute(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """
            )
            tables = [row[0] for row in cursor.fetchall()]

            if not tables:
                print("⚠️  Nessuna tabella trovata (database vuoto)")
                return data

            print(f"📊 Trovate {len(tables)} tabelle: {', '.join(tables)}")

            # Esporta ogni tabella
            for table in tables:
                print(f"   → Esportazione {table}...")

                # Schema tabella
                cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """,
                    (table,),
                )
                columns = cursor.fetchall()

                # Dati tabella
                cursor.execute('SELECT * FROM "{}"'.format(table))
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]

                # Converti in dict serializzabile
                rows_dict = []
                for row in rows:
                    row_dict = {}
                    for idx, value in enumerate(row):
                        # Converti datetime in string
                        if hasattr(value, "isoformat"):
                            value = value.isoformat()
                        row_dict[column_names[idx]] = value
                    rows_dict.append(row_dict)

                data["tables"][table] = {
                    "schema": {
                        "columns": [
                            {"name": col[0], "type": col[1], "nullable": col[2], "default": col[3]} for col in columns
                        ]
                    },
                    "rows": rows_dict,
                    "count": len(rows_dict),
                }

                print(f"      ✅ {len(rows_dict)} righe esportate")

            cursor.close()

            # Salva backup locale
            with open(self.backup_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

            backup_size = os.path.getsize(self.backup_file) / 1024
            print(f"\n💾 Backup salvato: {self.backup_file} ({backup_size:.1f} KB)")

            return data

        except Exception as e:
            print(f"❌ Errore esportazione: {e}")
            raise

    def import_data(self, data: Dict[str, Any]):
        """Importa dati su Neon"""
        print("\n📤 Importazione dati su Neon...")

        if not data.get("tables"):
            print("⚠️  Nessun dato da importare")
            return

        try:
            cursor = self.neon_conn.cursor()

            for table_name, table_data in data["tables"].items():
                rows = table_data["rows"]
                if not rows:
                    print(f"   ⊘ {table_name}: tabella vuota")
                    continue

                print(f"   → Importazione {table_name} ({len(rows)} righe)...")

                # Genera INSERT per ogni riga
                for row in rows:
                    columns = list(row.keys())
                    values = [row[col] for col in columns]

                    placeholders = ", ".join(["%s"] * len(columns))
                    columns_str = ", ".join([f'"{col}"' for col in columns])

                    query = f"""
                        INSERT INTO "{table_name}" ({columns_str})
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """

                    try:
                        cursor.execute(query, values)
                    except Exception as e:
                        print(f"      ⚠️  Errore riga: {e}")
                        continue

                print(f"      ✅ {table_name} importato")

            cursor.close()
            print("\n✅ Importazione completata")

        except Exception as e:
            print(f"❌ Errore importazione: {e}")
            raise

    def verify_migration(self) -> bool:
        """Verifica che i dati siano stati migrati correttamente"""
        print("\n🔍 Verifica migrazione...")

        try:
            render_cursor = self.render_conn.cursor()
            neon_cursor = self.neon_conn.cursor()

            # Conta righe per tabella
            render_cursor.execute(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
            """
            )
            tables = [row[0] for row in render_cursor.fetchall()]

            print("\n📊 Confronto conteggi:")
            all_match = True

            for table in tables:
                render_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                render_count = render_cursor.fetchone()[0]

                neon_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                neon_count = neon_cursor.fetchone()[0]

                status = "✅" if render_count == neon_count else "❌"
                print(f"   {status} {table}: Render={render_count}, Neon={neon_count}")

                if render_count != neon_count:
                    all_match = False

            render_cursor.close()
            neon_cursor.close()

            return all_match

        except Exception as e:
            print(f"⚠️  Errore verifica: {e}")
            return False

    def close_connections(self):
        """Chiudi connessioni"""
        if self.render_conn:
            self.render_conn.close()
        if self.neon_conn:
            self.neon_conn.close()


def main():
    print("🔄 MIGRAZIONE RENDER → NEON POSTGRESQL")
    print("=" * 50)

    migrator = DatabaseMigrator()

    try:
        # Step 1: Ottieni DATABASE_URL Render
        print("\n📥 Step 1: Connessione a Render...")
        print("Vai su: https://dashboard.render.com/")
        print("→ pronostici-calcio-db → Info → Internal Database URL")
        print()
        render_url = input("Incolla DATABASE_URL Render: ").strip()

        if not render_url:
            print("❌ DATABASE_URL vuoto!")
            return

        if not migrator.connect_render(render_url):
            return

        # Step 2: Esporta dati
        data = migrator.export_data()

        if not data.get("tables"):
            print("\n⚠️  Database Render vuoto - nessun dato da migrare")
            print("Puoi comunque configurare Neon per uso futuro")

        # Step 3: Setup Neon
        print("\n🆕 Step 2: Setup Neon PostgreSQL...")
        print("\n1. Vai su: https://neon.tech")
        print("2. Sign Up (FREE, no carta di credito)")
        print("3. Create Project:")
        print("   - Nome: pronostici-calcio-production")
        print("   - Region: Europe (Frankfurt)")
        print("   - PostgreSQL: 16")
        print("4. Copia Connection String dalla dashboard")
        print()
        neon_url = input("Incolla DATABASE_URL Neon: ").strip()

        if not neon_url:
            print("❌ DATABASE_URL Neon vuoto!")
            return

        if not migrator.connect_neon(neon_url):
            return

        # Step 4: Importa dati
        if data.get("tables"):
            migrator.import_data(data)

            # Step 5: Verifica
            if migrator.verify_migration():
                print("\n" + "=" * 50)
                print("🎉 MIGRAZIONE COMPLETATA CON SUCCESSO!")
                print("=" * 50)
            else:
                print("\n⚠️  Migrazione completata ma con differenze nei conteggi")
                print("Verifica manualmente i dati")
        else:
            print("\n✅ Neon configurato (database vuoto)")

        # Step 6: Istruzioni finali
        print("\n📋 PROSSIMI PASSI:")
        print("\n1️⃣  Aggiorna Render Environment Variable:")
        print("   Dashboard: https://dashboard.render.com/")
        print("   → pronostici-calcio-pro → Environment → DATABASE_URL")
        print("   → Change from 'From Database' to 'Secret'")
        print("   → Paste:")
        print(f"\n   {neon_url}")
        print("\n2️⃣  Render farà automaticamente redeploy (2-3 minuti)")
        print("\n3️⃣  Verifica app funzionante:")
        print("   curl https://pronostici-calcio-pro.onrender.com/api/health")
        print("\n4️⃣  DOPO 7 giorni di test: elimina database Render")
        print("   (Dashboard → pronostici-calcio-db → Delete)")
        print(f"\n💾 BACKUP SALVATO: {migrator.backup_file}")
        print("   (conservalo per 30 giorni come sicurezza)")

    except KeyboardInterrupt:
        print("\n\n⚠️  Migrazione interrotta dall'utente")
    except Exception as e:
        print(f"\n❌ Errore fatale: {e}")
        import traceback

        traceback.print_exc()
    finally:
        migrator.close_connections()


if __name__ == "__main__":
    main()
