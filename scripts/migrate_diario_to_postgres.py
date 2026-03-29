#!/usr/bin/env python3
"""
🗄️ Migrazione Diario CSV → PostgreSQL
Migra tracking_giocate.csv nel database PostgreSQL Neon
"""

import pandas as pd
import os
import sys
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("❌ psycopg2 non installato!")
    print("   Installa con: pip install psycopg2-binary")
    sys.exit(1)

def migrate_diario_to_postgres():
    """Migra tracking_giocate.csv → PostgreSQL"""
    
    # 1. Check DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL non configurato!")
        print("\n📋 Per usare questo script:")
        print("   1. Copia DATABASE_URL da Neon.tech dashboard")
        print("   2. export DATABASE_URL='postgresql://...'")
        print("   3. Riprova")
        sys.exit(1)
    
    print("🔄 Migrazione Diario CSV → PostgreSQL\n")
    print(f"📊 Database: {db_url[:30]}...{db_url[-20:]}")
    
    # 2. Leggi CSV
    csv_file = 'tracking_giocate.csv'
    if not os.path.exists(csv_file):
        print(f"❌ File {csv_file} non trovato!")
        sys.exit(1)
    
    df = pd.read_csv(csv_file)
    print(f"✅ Letto {csv_file}: {len(df)} bet\n")
    
    # 3. Connessione PostgreSQL
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        print("✅ Connesso a PostgreSQL")
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        sys.exit(1)
    
    # 4. Verifica schema esiste
    try:
        cur.execute("SELECT COUNT(*) FROM bets;")
        existing_count = cur.fetchone()[0]
        print(f"ℹ️  Tabella 'bets' già contiene {existing_count} record")
        
        if existing_count > 0:
            risposta = input("\n⚠️  Tabella non vuota. Continuare? (y/n): ")
            if risposta.lower() != 'y':
                print("❌ Migrazione annullata")
                sys.exit(0)
    except psycopg2.Error:
        print("⚠️  Tabella 'bets' non esiste ancora (sarà creata da app)")
        print("   Avvia prima l'app con DATABASE_URL configurato")
        sys.exit(1)
    
    # 5. Prepara dati per inserimento
    records = []
    for _, row in df.iterrows():
        # Parse data (formato CSV: 2026-02-14 o 14/02/2026)
        data_str = str(row['Data'])
        try:
            if '/' in data_str:
                data = datetime.strptime(data_str, '%d/%m/%Y').date()
            else:
                data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except:
            print(f"⚠️  Formato data non valido: {data_str}, uso oggi")
            data = datetime.now().date()
        
        # Parse stake (può essere numero o 'MONITOR')
        stake_str = str(row['Stake']).strip()
        
        # Parse quote
        quota_sisal = float(row['Quota_Sisal']) if pd.notna(row['Quota_Sisal']) else 0.0
        quota_sistema = float(row['Quota_Sistema']) if pd.notna(row['Quota_Sistema']) else quota_sisal
        
        # Parse risultato
        risultato = str(row['Risultato']).upper()
        if risultato not in ['PENDING', 'WIN', 'LOSS', 'VOID', 'SKIP']:
            risultato = 'PENDING'
        
        # Parse profit
        profit = float(row['Profit']) if pd.notna(row['Profit']) and row['Profit'] != '' else 0.0
        
        record = (
            data,                                          # data
            row['Partita'],                               # partita
            row['Mercato'],                               # mercato
            quota_sistema,                                # quota_sistema
            quota_sisal,                                  # quota_sisal
            row.get('EV_Modello', 'N/A'),                # ev_modello
            row.get('EV_Realistico', 'N/A'),             # ev_realistico
            stake_str,                                    # stake
            risultato,                                    # risultato
            profit,                                       # profit
            row.get('Note', '')                          # note
        )
        records.append(record)
    
    # 6. Inserimento batch
    try:
        insert_query = """
        INSERT INTO bets (
            data, partita, mercato, quota_sistema, quota_sisal,
            ev_modello, ev_realistico, stake, risultato, profit, note
        ) VALUES %s
        ON CONFLICT DO NOTHING;
        """
        
        execute_values(cur, insert_query, records)
        conn.commit()
        
        inserted = cur.rowcount
        print(f"\n✅ Migrazione completata: {inserted} bet inserite")
        
        # 7. Verifica finale
        cur.execute("SELECT COUNT(*) FROM bets;")
        total = cur.fetchone()[0]
        print(f"📊 Totale bet nel database: {total}")
        
        # 8. Statistiche
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE risultato = 'PENDING') as pending,
                COUNT(*) FILTER (WHERE risultato = 'WIN') as wins,
                COUNT(*) FILTER (WHERE risultato = 'LOSS') as losses,
                COALESCE(SUM(profit), 0) as total_profit
            FROM bets;
        """)
        stats = cur.fetchone()
        print(f"\n📈 Statistiche:")
        print(f"   Pending: {stats[0]}")
        print(f"   Win: {stats[1]}")
        print(f"   Loss: {stats[2]}")
        print(f"   Profit totale: {stats[3]:+.2f}€")
        
    except Exception as e:
        print(f"❌ Errore inserimento: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()
    
    print("\n🎉 Migrazione completata con successo!")
    print("\n📋 Prossimi step:")
    print("   1. Configura DATABASE_URL su Render")
    print("   2. Deploy su Render")
    print("   3. Diario sarà persistente ✅")

if __name__ == '__main__':
    migrate_diario_to_postgres()
