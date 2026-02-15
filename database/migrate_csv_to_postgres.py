"""
Migration script: CSV tracking_giocate.csv → PostgreSQL bets table
Esegue migration completa con validazione dati
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, BetModel, is_db_available
import structlog

logger = structlog.get_logger()


def parse_csv_date(date_str):
    """Parse date da CSV (formato dd/mm/yyyy o yyyy-mm-dd)"""
    try:
        # Prova formato dd/mm/yyyy
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        try:
            # Prova formato yyyy-mm-dd
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"⚠️ Data non parsabile: {date_str}, uso oggi")
            return datetime.now().date()


def migrate_csv_to_postgres(csv_file='tracking_giocate.csv', dry_run=False):
    """
    Migra dati da CSV a PostgreSQL
    
    Args:
        csv_file: Path al CSV
        dry_run: Se True, solo stampa report senza scrivere DB
    
    Returns:
        Dict con statistiche migration
    """
    logger.info("🚀 Avvio migration CSV → PostgreSQL", csv_file=csv_file, dry_run=dry_run)
    
    # Check CSV esiste
    if not os.path.exists(csv_file):
        logger.error(f"❌ File non trovato: {csv_file}")
        return {'success': False, 'error': 'File CSV non trovato'}
    
    # Inizializza database
    if not dry_run:
        if not init_db():
            logger.error("❌ Impossibile inizializzare database")
            return {'success': False, 'error': 'Database init fallito'}
    
    # Leggi CSV
    try:
        df = pd.read_csv(csv_file)
        logger.info(f"📊 CSV caricato: {len(df)} righe")
    except Exception as e:
        logger.error(f"❌ Errore lettura CSV: {e}")
        return {'success': False, 'error': str(e)}
    
    # Statistiche
    stats = {
        'total_rows': len(df),
        'migrated': 0,
        'skipped': 0,
        'errors': []
    }
    
    # Migra ogni riga
    for idx, row in df.iterrows():
        try:
            # Prepara dati bet
            bet_data = {
                'data': parse_csv_date(str(row['Data'])),
                'partita': str(row['Partita']),
                'mercato': str(row['Mercato']),
                'quota_sistema': float(row['Quota_Sistema']) if pd.notna(row['Quota_Sistema']) else None,
                'quota_sisal': float(row['Quota_Sisal']),
                'ev_modello': str(row['EV_Modello']) if pd.notna(row['EV_Modello']) else 'N/A',
                'ev_realistico': str(row['EV_Realistico']) if pd.notna(row['EV_Realistico']) else 'N/A',
                'stake': str(row['Stake']),  # Può essere 'MONITOR' o numero
                'risultato': str(row['Risultato']) if pd.notna(row['Risultato']) else 'PENDING',
                'profit': float(row['Profit']) if pd.notna(row['Profit']) else 0.0,
                'note': str(row['Note']) if pd.notna(row['Note']) else ''
            }
            
            if dry_run:
                logger.info(f"[DRY-RUN] Riga {idx}: {bet_data['partita']} - {bet_data['mercato']}")
            else:
                # Inserisci nel database
                bet_id = BetModel.create(bet_data)
                logger.info(f"✅ Migrata riga {idx} → bet_id={bet_id}", partita=bet_data['partita'])
            
            stats['migrated'] += 1
            
        except Exception as e:
            logger.error(f"❌ Errore riga {idx}: {e}")
            stats['errors'].append({'row': idx, 'error': str(e)})
            stats['skipped'] += 1
    
    # Report finale
    logger.info("=" * 60)
    logger.info("📊 MIGRATION REPORT", **stats)
    logger.info("=" * 60)
    
    stats['success'] = True
    return stats


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migra CSV tracking_giocate.csv → PostgreSQL')
    parser.add_argument('--csv', default='tracking_giocate.csv', help='Path CSV file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no DB write)')
    
    args = parser.parse_args()
    
    result = migrate_csv_to_postgres(csv_file=args.csv, dry_run=args.dry_run)
    
    if result['success']:
        print(f"\n✅ Migration completata!")
        print(f"   • Righe migrate: {result['migrated']}")
        print(f"   • Righe skipped: {result['skipped']}")
        if result['errors']:
            print(f"   • Errori: {len(result['errors'])}")
            for err in result['errors'][:5]:  # Mostra primi 5 errori
                print(f"     - Riga {err['row']}: {err['error']}")
    else:
        print(f"\n❌ Migration fallita: {result.get('error')}")
        sys.exit(1)
