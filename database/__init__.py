"""
Database module - PostgreSQL connection e ORM semplificato
Gestisce connessione pool, queries, migration da CSV
"""

from .connection import get_db_connection, init_db, close_db_pool, is_db_available
from .models import BetModel

__all__ = ['get_db_connection', 'init_db', 'close_db_pool', 'is_db_available', 'BetModel']
