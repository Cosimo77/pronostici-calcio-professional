"""
Gunicorn configuration con pre_fork + post_fork hooks
Risolve problema fork-safety del PostgreSQL connection pool
"""

import structlog

logger = structlog.get_logger()

def pre_fork(server, worker):
    """
    Hook chiamato PRIMA del fork - chiude connessioni master
    """
    logger.info("🔧 Gunicorn pre_fork hook", worker_pid=worker.pid if worker else "master")
    
    try:
        # Chiudi pool nel master PRIMA del fork
        from database import close_db_pool
        close_db_pool()
        logger.info("✅ Database pool chiuso nel master prima del fork")
    except Exception as e:
        logger.warning("⚠️ Errore pre_fork close pool", error=str(e))

def post_fork(server, worker):
    """
    Hook chiamato DOPO che Gunicorn fa fork del worker process
    Reinizializza il connection pool PostgreSQL per essere fork-safe
    """
    logger.info("🔄 Gunicorn post_fork hook", worker_pid=worker.pid)
    
    try:
        # Reinizializza database connection pool nel worker
        from database import init_db
        success = init_db()
        
        if success:
            logger.info("✅ Database pool reinizializzato nel worker", 
                        worker_pid=worker.pid, 
                        result="PostgreSQL connected")
        else:
            logger.warning("⚠️ Database init fallito nel worker - CSV fallback", 
                           worker_pid=worker.pid)
    except Exception as e:
        logger.error("❌ Errore post_fork database init", 
                     worker_pid=worker.pid, 
                     error=str(e), 
                     exc_info=True)

def when_ready(server):
    """Hook chiamato quando Gunicorn master è pronto"""
    logger.info("🚀 Gunicorn master process pronto", 
                workers=server.cfg.workers, 
                worker_class=server.cfg.worker_class)
