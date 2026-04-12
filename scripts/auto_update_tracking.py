#!/usr/bin/env python3
"""
Auto Update Tracking Results - Cron Job
Scarica risultati reali e aggiorna tracking automaticamente
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from integrations.football_data_results import get_results_client
from utils.auto_tracking import get_tracker
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_tracking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def normalize_team_name(name: str) -> str:
    """
    Normalizza nome squadra per matching
    
    Gestisce differenze tra football-data.co.uk e tracking CSV
    """
    mappings = {
        # football-data.co.uk → tracking format
        'AC Milan': 'Milan',
        'Inter Milan': 'Inter',
        'AS Roma': 'Roma',
        'Hellas Verona': 'Verona',
        'Atalanta BC': 'Atalanta',
        'Bologna FC': 'Bologna',
        'Cagliari Calcio': 'Cagliari',
        'Como 1907': 'Como',
        'Empoli FC': 'Empoli',
        'ACF Fiorentina': 'Fiorentina',
        'Genoa CFC': 'Genoa',
        'Juventus FC': 'Juventus',
        'SS Lazio': 'Lazio',
        'US Lecce': 'Lecce',
        'SSC Napoli': 'Napoli',
        'Parma Calcio': 'Parma',
        'Torino FC': 'Torino',
        'Udinese Calcio': 'Udinese',
        'Venezia FC': 'Venezia',
    }
    
    # Prova mapping diretto
    if name in mappings:
        return mappings[name]
    
    # Rimuovi suffissi comuni
    clean = name.replace(' FC', '').replace(' Calcio', '').replace(' CFC', '')
    clean = clean.replace('US ', '').replace('SS ', '').replace('SSC ', '')
    clean = clean.replace('AC ', '').replace('ACF ', '').replace('AS ', '')
    
    return clean.strip()


def update_tracking_results(days_back: int = 3):
    """
    Aggiorna tracking con risultati reali recenti
    
    Args:
        days_back: Giorni indietro da controllare (default: 3)
    """
    logger.info("=" * 70)
    logger.info("🔄 AUTO UPDATE TRACKING RESULTS")
    logger.info("=" * 70)
    
    # Ottieni client e tracker
    client = get_results_client()
    tracker = get_tracker()
    
    # Scarica risultati recenti
    logger.info(f"📥 Scarico risultati ultimi {days_back} giorni...")
    results = client.get_results_for_tracking(days_back=days_back)
    
    if not results:
        logger.warning("⚠️ Nessun risultato trovato")
        return
    
    logger.info(f"✅ Trovati {len(results)} risultati")
    
    # Aggiorna tracking per ogni partita
    total_updated = 0
    
    for result in results:
        casa = normalize_team_name(result['casa'])
        ospite = normalize_team_name(result['ospite'])
        data = result['data']
        
        logger.info(f"\n📊 {casa} vs {ospite} ({data})")
        logger.info(f"   Risultato: {result['home_goals']}-{result['away_goals']}")
        
        # Aggiorna mercato 1X2
        updated_1x2 = tracker.update_result(
            casa=casa,
            ospite=ospite,
            data=data,
            risultato_reale=result['1X2'],
            mercato='1X2'
        )
        if updated_1x2:
            logger.info(f"   ✅ 1X2: {result['1X2']} ({updated_1x2} predizioni)")
            total_updated += updated_1x2
        
        # Aggiorna Over/Under 2.5
        updated_ou = tracker.update_result(
            casa=casa,
            ospite=ospite,
            data=data,
            risultato_reale=result['OU25'],
            mercato='OU25'
        )
        if updated_ou:
            logger.info(f"   ✅ OU2.5: {result['OU25']} ({updated_ou} predizioni)")
            total_updated += updated_ou
        
        # Aggiorna Goal/Goal
        updated_gg = tracker.update_result(
            casa=casa,
            ospite=ospite,
            data=data,
            risultato_reale=result['GGNG'],
            mercato='GGNG'
        )
        if updated_gg:
            logger.info(f"   ✅ GGNG: {result['GGNG']} ({updated_gg} predizioni)")
            total_updated += updated_gg
    
    # Report finale
    logger.info("\n" + "=" * 70)
    logger.info(f"✅ AGGIORNAMENTO COMPLETATO")
    logger.info(f"   Partite controllate: {len(results)}")
    logger.info(f"   Predizioni aggiornate: {total_updated}")
    logger.info("=" * 70)
    
    # Mostra statistiche aggiornate
    stats = tracker.get_stats(days=30)
    if stats:
        logger.info(f"\n📊 STATISTICHE AGGIORNATE (ultimi 30 giorni):")
        logger.info(f"   Accuracy: {stats['accuracy_pct']:.1f}% ({stats['correct_predictions']}/{stats['total_predictions']})")
        logger.info(f"   ROI: {stats['roi_pct']:+.2f}%")
        logger.info(f"   Profit: {stats['total_profit']:+.2f} unità")


def main():
    """Entry point per cron job"""
    try:
        # Controlla ultimi 3 giorni (cattura partite weekend)
        update_tracking_results(days_back=3)
        
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
