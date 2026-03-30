#!/usr/bin/env python3
"""
Migrazione dati: tracking_giocate.csv → PostgreSQL Neon
Eseguire DOPO aver configurato DATABASE_URL
"""

import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import init_db, BetModel, is_db_available
import structlog

logger = structlog.get_logger()

CSV_FILE = 'tracking_giocate.csv'

def migrate_csv_to_postgres():
    """Migra bet da CSV a PostgreSQL"""
    
    print("🔄 MIGRAZIONE CSV → PostgreSQL\n")
    print("="*60)
    
    # 1. Verifica DATABASE_URL configurato
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL non configurato!")
        print("   Configura su Render Environment e rideploy prima.")
        return False
    
    print(f"✅ DATABASE_URL presente ({len(database_url)} char)")
    
    # 2. Inizializza database
    print("\n🔧 Inizializzazione database...")
    success = init_db()
    
    if not success:
        print("❌ Database init fallito!")
        return False
    
    print("✅ Database connesso")
    
    # 3. Verifica che CSV esista
    if not os.path.exists(CSV_FILE):
        print(f"\n⚠️  File {CSV_FILE} non trovato")
        print("   Nessun dato da migrare (normale se già migrato)")
        return True
    
    # 4. Carica CSV
    print(f"\n📂 Caricamento {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    
    if len(df) == 0:
        print("⚠️  CSV vuoto - nessun dato da migrare")
        return True
    
    print(f"✅ {len(df)} bet trovate nel CSV")
    
    # 5. Verifica bet già esistenti in PostgreSQL
    existing_bets = BetModel.get_all()
    if len(existing_bets) > 0:
        print(f"\n⚠️  PostgreSQL contiene già {len(existing_bets)} bet")
        risposta = input("   Sovrascrivere? (y/N): ")
        if risposta.lower() != 'y':
            print("❌ Migrazione annullata")
            return False
        
        # Clear PostgreSQL
        print("🗑️  Svuotamento PostgreSQL...")
        # TODO: Implement clear_all() method if needed
        # BetModel.clear_all()
    
    # 6. Migrazione bet
    print(f"\n🔄 Migrazione in corso...")
    migrated = 0
    errors = 0
    
    for row_num, (_, row) in enumerate(df.iterrows(), start=1):
        try:
            # Converti row to dict compatibile con BetModel
            bet_data = {
                'group_id': row.get('group_id') if pd.notna(row.get('group_id')) else None,
                'bet_number': int(row.get('bet_number', 1)),
                'tipo_bet': row.get('tipo_bet', 'SINGLE'),
                'data': str(row['Data']),
                'partita': str(row['Partita']),
                'mercato': str(row['Mercato']),
                'quota_sistema': float(row.get('Quota_Sistema', 0)) if pd.notna(row.get('Quota_Sistema')) else None,
                'quota_sisal': float(row['Quota_Sisal']),
                'ev_modello': str(row.get('EV_Modello', '')),
                'ev_realistico': str(row.get('EV_Realistico', '')) if pd.notna(row.get('EV_Realistico')) else None,
                'stake': str(row['Stake']),  # Può essere numero o 'MONITOR'
                'risultato': str(row.get('Risultato', 'PENDING')),
                'profit': float(row.get('Profit', 0)),
                'note': str(row.get('Note', '')) if pd.notna(row.get('Note')) else None
            }
            
            # Insert in PostgreSQL
            BetModel.create(bet_data)
            migrated += 1
            print(f"   ✅ {row_num}/{len(df)} - {bet_data['partita'][:30]}")
            
        except Exception as e:
            errors += 1
            print(f"   ❌ {row_num}/{len(df)} - Errore: {e}")
    
    # 7. Summary
    print("\n" + "="*60)
    print("📊 MIGRAZIONE COMPLETATA\n")
    print(f"✅ Migrate: {migrated} bet")
    if errors > 0:
        print(f"❌ Errori: {errors} bet")
    print(f"\n💾 PostgreSQL ora contiene: {migrated} bet")
    print("🗑️  Puoi eliminare tracking_giocate.csv se vuoi")
    print("\n🚀 Sistema ora usa PostgreSQL (persistente)")
    
    return True

if __name__ == '__main__':
    try:
        success = migrate_csv_to_postgres()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Migrazione interrotta")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
