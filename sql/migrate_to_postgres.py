"""
🗄️ MIGRATION SCRIPT: CSV → PostgreSQL
Migra dataset_completo_con_quote.csv nel database PostgreSQL per produzione
"""

import pandas as pd
from typing import Optional
import os
from datetime import datetime

try:
    import psycopg2  # type: ignore[import-not-found]
    from psycopg2.extras import execute_values  # type: ignore[import-not-found]
    from psycopg2.extensions import connection, cursor as pg_cursor  # type: ignore[import-not-found]
except ImportError:
    print("⚠️ psycopg2 non installato. Installa con: pip install psycopg2-binary")
    psycopg2 = None  # type: ignore

class DatabaseMigration:
    def __init__(self, db_url: Optional[str] = None):
        """
        Inizializza connessione database
        db_url format: postgresql://user:password@host:port/dbname
        """
        if psycopg2 is None:
            raise ImportError("psycopg2 richiesto. Installa con: pip install psycopg2-binary")
            
        self.db_url = db_url or os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL non configurato. Usa env variable o passa come parametro.")
        
        self.conn: Optional[connection] = None
        self.cursor: Optional[pg_cursor] = None
    
    def connect(self):
        """Connetti al database PostgreSQL"""
        if psycopg2 is None:
            raise ImportError("psycopg2 non disponibile")
            
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.cursor = self.conn.cursor()
            print("✅ Connessione PostgreSQL stabilita")
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            raise
    
    def create_tables(self):
        """Crea schema database per pronostici calcio"""
        
        if not self.conn or not self.cursor:
            raise RuntimeError("Database non connesso. Chiama connect() prima.")
        
        # Tabella partite (match data)
        create_matches_table = """
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            home_team VARCHAR(100) NOT NULL,
            away_team VARCHAR(100) NOT NULL,
            full_time_home_goals INTEGER,
            full_time_away_goals INTEGER,
            full_time_result VARCHAR(1),
            half_time_home_goals INTEGER,
            half_time_away_goals INTEGER,
            half_time_result VARCHAR(1),
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(date, home_team, away_team)
        );
        
        CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date);
        CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(home_team, away_team);
        """
        
        # Tabella features statistiche
        create_features_table = """
        CREATE TABLE IF NOT EXISTS match_features (
            id SERIAL PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id) ON DELETE CASCADE,
            
            -- Forma generale
            casa_forma_punti FLOAT,
            casa_forma_media_punti FLOAT,
            casa_forma_gol_fatti FLOAT,
            casa_forma_gol_subiti FLOAT,
            casa_forma_media_gol_fatti FLOAT,
            casa_forma_media_gol_subiti FLOAT,
            
            -- Performance in casa
            casa_home_punti FLOAT,
            casa_home_media_punti FLOAT,
            casa_home_gol_fatti FLOAT,
            casa_home_gol_subiti FLOAT,
            casa_home_media_gol_fatti FLOAT,
            casa_home_media_gol_subiti FLOAT,
            
            -- Forma trasferta
            trasferta_forma_punti FLOAT,
            trasferta_forma_media_punti FLOAT,
            trasferta_forma_gol_fatti FLOAT,
            trasferta_forma_gol_subiti FLOAT,
            trasferta_forma_media_gol_fatti FLOAT,
            trasferta_forma_media_gol_subiti FLOAT,
            
            -- Performance in trasferta
            trasferta_away_punti FLOAT,
            trasferta_away_media_punti FLOAT,
            trasferta_away_gol_fatti FLOAT,
            trasferta_away_gol_subiti FLOAT,
            trasferta_away_media_gol_fatti FLOAT,
            trasferta_away_media_gol_subiti FLOAT,
            
            -- Head to head
            h2h_vittorie_casa INTEGER,
            h2h_vittorie_trasferta INTEGER,
            h2h_pareggi INTEGER,
            h2h_partite INTEGER,
            
            -- Differenziali
            differenza_forma_punti FLOAT,
            differenza_attacco FLOAT,
            differenza_difesa FLOAT,
            casa_home_vs_trasferta_away_punti FLOAT,
            
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_features_match ON match_features(match_id);
        """
        
        # Tabella odds bookmaker
        create_odds_table = """
        CREATE TABLE IF NOT EXISTS match_odds (
            id SERIAL PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id) ON DELETE CASCADE,
            
            -- Bet365
            b365_home FLOAT,
            b365_draw FLOAT,
            b365_away FLOAT,
            b365_over_2_5 FLOAT,
            b365_under_2_5 FLOAT,
            
            -- BetVictor
            bw_home FLOAT,
            bw_draw FLOAT,
            bw_away FLOAT,
            
            -- Odds medie (se calcolate)
            avg_home FLOAT,
            avg_draw FLOAT,
            avg_away FLOAT,
            
            -- Metadata
            bookmaker_margin FLOAT,
            closing_line BOOLEAN DEFAULT FALSE,
            scraped_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_odds_match ON match_odds(match_id);
        """
        
        # Tabella predictions (per storico)
        create_predictions_table = """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id) ON DELETE CASCADE,
            
            -- Prediction
            predicted_result VARCHAR(1) NOT NULL,
            probability_home FLOAT,
            probability_draw FLOAT,
            probability_away FLOAT,
            
            -- Model info
            model_version VARCHAR(50),
            features_used INTEGER,
            ensemble_accuracy FLOAT,
            
            -- Value betting
            expected_value FLOAT,
            kelly_stake FLOAT,
            recommended_bet BOOLEAN DEFAULT FALSE,
            
            -- Outcome
            actual_result VARCHAR(1),
            bet_won BOOLEAN,
            profit_loss FLOAT,
            
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id);
        CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at);
        """
        
        try:
            print("\n🏗️ Creazione schema database...")
            self.cursor.execute(create_matches_table)
            print("   ✅ Tabella 'matches' creata")
            
            self.cursor.execute(create_features_table)
            print("   ✅ Tabella 'match_features' creata")
            
            self.cursor.execute(create_odds_table)
            print("   ✅ Tabella 'match_odds' creata")
            
            self.cursor.execute(create_predictions_table)
            print("   ✅ Tabella 'predictions' creata")
            
            self.conn.commit()
            print("✅ Schema database completato\n")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Errore creazione tabelle: {e}")
            raise
    
    def migrate_csv_data(self, csv_path='data/dataset_completo_con_quote.csv'):
        """Migra dati da CSV a PostgreSQL"""
        
        if not self.conn or not self.cursor:
            raise RuntimeError("Database non connesso. Chiama connect() prima.")
        
        print(f"📂 Caricamento {csv_path}...")
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"   Righe: {len(df):,}")
        print(f"   Colonne: {len(df.columns)}")
        
        migrated = 0
        skipped = 0
        
        for idx, row in df.iterrows():
            try:
                # 1. Insert match (se non esiste)
                insert_match = """
                INSERT INTO matches (date, home_team, away_team, 
                                   full_time_home_goals, full_time_away_goals, full_time_result,
                                   half_time_home_goals, half_time_away_goals, half_time_result)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, home_team, away_team) DO NOTHING
                RETURNING id;
                """
                
                self.cursor.execute(insert_match, (
                    row['Date'].date(),
                    row['HomeTeam'],
                    row['AwayTeam'],
                    int(row['FTHG']) if pd.notna(row['FTHG']) else None,
                    int(row['FTAG']) if pd.notna(row['FTAG']) else None,
                    row['FTR'],
                    int(row['HTHG']) if pd.notna(row.get('HTHG')) else None,
                    int(row['HTAG']) if pd.notna(row.get('HTAG')) else None,
                    row.get('HTR')
                ))
                
                result = self.cursor.fetchone()
                if not result:
                    # Match già esistente, prendi ID
                    self.cursor.execute("""
                        SELECT id FROM matches 
                        WHERE date = %s AND home_team = %s AND away_team = %s
                    """, (row['Date'].date(), row['HomeTeam'], row['AwayTeam']))
                    result = self.cursor.fetchone()
                    skipped += 1
                
                if not result:
                    print(f"⚠️ Match ID non trovato per {row['HomeTeam']} vs {row['AwayTeam']}")
                    continue
                    
                match_id = result[0]
                
                # 2. Insert features
                insert_features = """
                INSERT INTO match_features (
                    match_id,
                    casa_forma_punti, casa_forma_media_punti, casa_forma_gol_fatti, casa_forma_gol_subiti,
                    casa_forma_media_gol_fatti, casa_forma_media_gol_subiti,
                    casa_home_punti, casa_home_media_punti, casa_home_gol_fatti, casa_home_gol_subiti,
                    casa_home_media_gol_fatti, casa_home_media_gol_subiti,
                    trasferta_forma_punti, trasferta_forma_media_punti, trasferta_forma_gol_fatti,
                    trasferta_forma_gol_subiti, trasferta_forma_media_gol_fatti, trasferta_forma_media_gol_subiti,
                    trasferta_away_punti, trasferta_away_media_punti, trasferta_away_gol_fatti,
                    trasferta_away_gol_subiti, trasferta_away_media_gol_fatti, trasferta_away_media_gol_subiti,
                    h2h_vittorie_casa, h2h_vittorie_trasferta, h2h_pareggi, h2h_partite,
                    differenza_forma_punti, differenza_attacco, differenza_difesa, casa_home_vs_trasferta_away_punti
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """
                
                self.cursor.execute(insert_features, (
                    match_id,
                    row.get('casa_forma_punti'), row.get('casa_forma_media_punti'),
                    row.get('casa_forma_gol_fatti'), row.get('casa_forma_gol_subiti'),
                    row.get('casa_forma_media_gol_fatti'), row.get('casa_forma_media_gol_subiti'),
                    row.get('casa_home_punti'), row.get('casa_home_media_punti'),
                    row.get('casa_home_gol_fatti'), row.get('casa_home_gol_subiti'),
                    row.get('casa_home_media_gol_fatti'), row.get('casa_home_media_gol_subiti'),
                    row.get('trasferta_forma_punti'), row.get('trasferta_forma_media_punti'),
                    row.get('trasferta_forma_gol_fatti'), row.get('trasferta_forma_gol_subiti'),
                    row.get('trasferta_forma_media_gol_fatti'), row.get('trasferta_forma_media_gol_subiti'),
                    row.get('trasferta_away_punti'), row.get('trasferta_away_media_punti'),
                    row.get('trasferta_away_gol_fatti'), row.get('trasferta_away_gol_subiti'),
                    row.get('trasferta_away_media_gol_fatti'), row.get('trasferta_away_media_gol_subiti'),
                    int(row.get('h2h_vittorie_casa', 0)), int(row.get('h2h_vittorie_trasferta', 0)),
                    int(row.get('h2h_pareggi', 0)), int(row.get('h2h_partite', 0)),
                    row.get('differenza_forma_punti'), row.get('differenza_attacco'),
                    row.get('differenza_difesa'), row.get('casa_home_vs_trasferta_away_punti')
                ))
                
                # 3. Insert odds
                insert_odds = """
                INSERT INTO match_odds (
                    match_id,
                    b365_home, b365_draw, b365_away, b365_over_2_5, b365_under_2_5,
                    bw_home, bw_draw, bw_away
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """
                
                self.cursor.execute(insert_odds, (
                    match_id,
                    row.get('B365H'), row.get('B365D'), row.get('B365A'),
                    row.get('B365>2.5'), row.get('B365<2.5'),
                    row.get('BWH'), row.get('BWD'), row.get('BWA')
                ))
                
                migrated += 1
                
                # Commit ogni 100 righe
                if migrated % 100 == 0:
                    self.conn.commit()
                    print(f"   Migrate: {migrated}/{len(df)} ({migrated/len(df)*100:.1f}%)", end='\r')
                
            except Exception as e:
                print(f"\n⚠️ Errore riga {idx}: {e}")
                self.conn.rollback()
                continue
        
        # Final commit
        self.conn.commit()
        
        print(f"\n\n✅ Migrazione completata!")
        print(f"   Migrate: {migrated:,} partite")
        print(f"   Skipped: {skipped:,} duplicati")
        print(f"   Totale:  {len(df):,} righe\n")
    
    def verify_migration(self):
        """Verifica integrità dati migrati"""
        
        if not self.conn or not self.cursor:
            raise RuntimeError("Database non connesso. Chiama connect() prima.")
        
        print("🔍 Verifica integrità database...\n")
        
        queries = {
            'Matches': 'SELECT COUNT(*) FROM matches',
            'Features': 'SELECT COUNT(*) FROM match_features',
            'Odds': 'SELECT COUNT(*) FROM match_odds',
            'Predictions': 'SELECT COUNT(*) FROM predictions'
        }
        
        for table, query in queries.items():
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            print(f"   {table:15} {count:,} righe")
        
        # Sample data
        print("\n📊 Sample match data:")
        self.cursor.execute("""
            SELECT m.date, m.home_team, m.away_team, m.full_time_result,
                   o.b365_home, o.b365_draw, o.b365_away
            FROM matches m
            LEFT JOIN match_odds o ON m.id = o.match_id
            ORDER BY m.date DESC
            LIMIT 5
        """)
        
        for row in self.cursor.fetchall():
            print(f"   {row[0]} | {row[1]:20} vs {row[2]:20} | {row[3]} | Odds: {row[4]:.2f}/{row[5]:.2f}/{row[6]:.2f}")
        
        print("\n✅ Verifica completata\n")
    
    def close(self):
        """Chiudi connessioni"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Connessione chiusa")


def main():
    """Script principale di migrazione"""
    
    print("=" * 70)
    print("🗄️  MIGRATION: CSV → PostgreSQL")
    print("=" * 70)
    print()
    
    # Prompt per DATABASE_URL se non in env
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("⚠️  DATABASE_URL non trovato in environment variables")
        print("\nFormato: postgresql://user:password@host:port/dbname")
        print("Esempio: postgresql://postgres:password@localhost:5432/pronostici_calcio\n")
        db_url = input("Inserisci DATABASE_URL: ").strip()
        
        if not db_url:
            print("❌ DATABASE_URL richiesto per procedere")
            return
    
    try:
        # Inizializza migrazione
        migration = DatabaseMigration(db_url)
        
        # Connetti
        migration.connect()
        
        # Crea tabelle
        migration.create_tables()
        
        # Migra dati
        migration.migrate_csv_data()
        
        # Verifica
        migration.verify_migration()
        
        # Chiudi
        migration.close()
        
        print("=" * 70)
        print("✅ MIGRAZIONE COMPLETATA CON SUCCESSO")
        print("=" * 70)
        print("\n💡 Next steps:")
        print("   1. Aggiorna app_professional.py per usare PostgreSQL")
        print("   2. Testa queries su database")
        print("   3. Setup backup automatici")
        print("   4. Deploy su Render con PostgreSQL addon\n")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Verifica DATABASE_URL corretto")
        print("   2. PostgreSQL server attivo?")
        print("   3. Permessi utente database?")
        print("   4. Firewall/network raggiungibile?\n")


if __name__ == "__main__":
    main()
