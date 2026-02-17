#!/usr/bin/env python3
"""
Applica migrazione 002: Aggiunta tabella bet_groups per scommesse multiple
Esegui: python database/run_migration_002.py
"""

import os
import sys

# Aggiungi path per import moduli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_connection, release_db_connection
import structlog

logger = structlog.get_logger()


def run_migration_002():
    """Applica migrazione 002: bet_groups e group_id"""
    
    migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '002_add_bet_groups.sql')
    
    if not os.path.exists(migration_file):
        logger.error("File migrazione non trovato", file=migration_file)
        return False
    
    # Leggi SQL migration
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("🚀 Inizio migrazione 002...")
        
        # Esegui SQL (potenzialmente multi-statement)
        cursor.execute(sql)
        
        conn.commit()
        
        logger.info("✅ Migrazione 002 completata con successo")
        
        # Verifica tabella creata
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('bets', 'bet_groups')
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        logger.info("📊 Tabelle presenti", tables=tables)
        
        # Verifica campo group_id aggiunto
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'bets' AND column_name = 'group_id'
        """)
        
        group_id_exists = cursor.fetchone() is not None
        logger.info("🔗 Campo group_id aggiunto", exists=group_id_exists)
        
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error("❌ Errore migrazione 002", error=str(e))
        return False
        
    finally:
        if conn:
            release_db_connection(conn)


if __name__ == '__main__':
    print("=" * 60)
    print("Migrazione 002: Supporto scommesse multiple")
    print("=" * 60)
    
    success = run_migration_002()
    
    if success:
        print("\n✅ Migrazione completata con successo!")
        print("Ora puoi usare le scommesse multiple nel sistema.")
        sys.exit(0)
    else:
        print("\n❌ Migrazione fallita. Controlla i log.")
        sys.exit(1)
