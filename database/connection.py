"""
PostgreSQL connection pool e gestione database
Supporta sia Render PostgreSQL che graceful degradation a CSV fallback
"""

import os
from psycopg2.pool import SimpleConnectionPool  # type: ignore[import-not-found]
from psycopg2 import Error  # type: ignore[import-not-found]
from contextlib import contextmanager
import structlog

logger = structlog.get_logger()

# Connection pool globale
_connection_pool = None

def get_database_url():
    """Ottieni DATABASE_URL da environment (Render lo inietta automaticamente)"""
    return os.environ.get('DATABASE_URL')

def init_db():
    """
    Inizializza connection pool PostgreSQL
    Render inietta automaticamente DATABASE_URL come env var
    """
    global _connection_pool
    
    database_url = get_database_url()
    
    logger.info(f"🔧 init_db() chiamato - DATABASE_URL presente: {database_url is not None}, length: {len(database_url) if database_url else 0}")
    
    if not database_url:
        logger.warning("⚠️ DATABASE_URL non configurata - falling back a CSV storage")
        return False
    
    try:
        logger.info("🔧 Creando SimpleConnectionPool...")
        # Crea connection pool (min 1, max 10 connessioni)
        _connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
        logger.info("🔧 Connection pool creato")
        
        # Test connessione DIRETTO (no context manager per evitare ricorsione)
        logger.info("🔧 Test connessione diretto...")
        test_conn = None
        try:
            test_conn = _connection_pool.getconn()
            logger.info("🔧 Connection ottenuta da pool")
            with test_conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info("✅ PostgreSQL connesso", version=version[:50])
        finally:
            if test_conn:
                _connection_pool.putconn(test_conn)
                logger.info("🔧 Connection restituita al pool")
        
        # Esegui schema (idempotent - CREATE IF NOT EXISTS)
        logger.info("🔧 Chiamata _ensure_schema_exists()...")
        _ensure_schema_exists()
        logger.info("🔧 _ensure_schema_exists() completato")
        
        return True
        
    except Exception as e:
        logger.error("❌ Errore connessione PostgreSQL", error=str(e), exc_info=True)
        _connection_pool = None
        return False

def _ensure_schema_exists():
    """Esegue schema.sql se tabelle non esistono"""
    logger.info("🔧 _ensure_schema_exists() iniziato")
    try:
        logger.info("🔧 Tentativo get_db_connection()...")
        with get_db_connection() as conn:
            logger.info("🔧 Connection ottenuta, creando cursor...")
            with conn.cursor() as cur:
                logger.info("🔧 Check esistenza table bets...")
                # Check se table bets esiste
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'bets'
                    );
                """)
                exists = cur.fetchone()[0]
                logger.info(f"🔧 Table bets exists: {exists}")
                
                if not exists:
                    logger.info("📋 Creando schema database...")
                    
                    # Leggi e esegui schema.sql
                    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
                    logger.info(f"🔧 Schema path: {schema_path}")
                    
                    if not os.path.exists(schema_path):
                        raise FileNotFoundError(f"schema.sql non trovato: {schema_path}")
                    
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()
                    
                    logger.info(f"🔧 Schema SQL caricato ({len(schema_sql)} chars)")
                    cur.execute(schema_sql)
                    conn.commit()
                    logger.info("✅ Schema database creato")
                else:
                    logger.info("✅ Schema database già esistente")
                    
    except Exception as e:
        logger.error("❌ Errore creazione schema", error=str(e), exc_info=True)
        raise

@contextmanager
def get_db_connection():
    """
    Context manager per ottenere connessione dal pool
    
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM bets")
                results = cur.fetchall()
    """
    if _connection_pool is None:
        raise RuntimeError("Database non inizializzato. Chiama init_db() o is_db_available() prima.")
    
    conn = None
    try:
        conn = _connection_pool.getconn()
        yield conn
        conn.commit()  # Auto-commit se nessuna exception
    except Exception as e:
        if conn:
            conn.rollback()  # Rollback su errore
        logger.error("❌ Errore query database", error=str(e))
        raise
    finally:
        if conn:
            _connection_pool.putconn(conn)

def close_db_pool():
    """Chiudi tutte le connessioni pool (chiamare a shutdown app)"""
    global _connection_pool
    
    if _connection_pool:
        _connection_pool.closeall()
        logger.info("🔴 Connection pool chiuso")
        _connection_pool = None

def is_db_available():
    """Check se database è disponibile (con lazy initialization)"""
    global _connection_pool
    
    # Se pool già inizializzato, return True
    if _connection_pool is not None:
        return True
    
    # Altrimenti tenta lazy initialization
    database_url = get_database_url()
    if not database_url:
        logger.warning("is_db_available: DATABASE_URL vuota")
        return False
    
    # Tenta init_db() in background
    logger.info(f"🔄 Lazy init triggered - DATABASE_URL length: {len(database_url)}")
    try:
        result = init_db()
        logger. info(f"Lazy init result: {result}, pool state: {_connection_pool is not None}")
        return result
    except Exception as e:
        logger.error(f"❌ Lazy init FAILED", error=str(e), exc_info=True)
        return False

def execute_query(query, params=None, fetch=True):
    """
    Helper per eseguire query semplici
    
    Args:
        query: SQL query
        params: Parametri query (tuple)
        fetch: Se True, ritorna fetchall(), altrimenti None
    
    Returns:
        List di tuple se fetch=True, None altrimenti
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            
            if fetch:
                return cur.fetchall()
            else:
                return None
