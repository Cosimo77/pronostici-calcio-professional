"""
BetModel - ORM semplificato per tabella bets
Gestisce CRUD operations con validazione
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional
import structlog

from .connection import get_db_connection, is_db_available

logger = structlog.get_logger()


class BetModel:
    """Model per puntate nel database"""
    
    VALID_RISULTATI = ['PENDING', 'WIN', 'LOSS', 'VOID', 'SKIP']
    
    @staticmethod
    def create(data: Dict) -> int:
        """
        Crea nuova bet nel database
        
        Args:
            data: Dict con campi bet (partita, mercato, quota_sisal, stake, ecc.)
        
        Returns:
            ID della bet creata
        """
        if not is_db_available():
            raise RuntimeError("Database non disponibile")
        
        # Validazione
        required = ['partita', 'mercato', 'quota_sisal', 'stake']
        for field in required:
            if field not in data:
                raise ValueError(f"Campo obbligatorio mancante: {field}")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO bets (
                        data, partita, mercato, quota_sistema, quota_sisal,
                        ev_modello, ev_realistico, stake, risultato, profit, note
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id;
                """, (
                    data.get('data', datetime.now().date()),
                    data['partita'],
                    data['mercato'],
                    data.get('quota_sistema', data['quota_sisal']),
                    data['quota_sisal'],
                    data.get('ev_modello', 'N/A'),
                    data.get('ev_realistico', 'N/A'),
                    str(data['stake']),  # Può essere 'MONITOR' o numero
                    data.get('risultato', 'PENDING'),
                    data.get('profit', 0.0),
                    data.get('note', '')
                ))
                
                bet_id = cur.fetchone()[0]
                logger.info("✅ Bet creata", bet_id=bet_id, partita=data['partita'])
                return bet_id
    
    @staticmethod
    def get_all(risultato: Optional[str] = None) -> List[Dict]:
        """
        Ottieni tutte le bet, opzionalmente filtrate per risultato
        
        Args:
            risultato: 'PENDING', 'WIN', 'LOSS', ecc. (None = tutte)
        
        Returns:
            Lista di dict con dati bet
        """
        if not is_db_available():
            return []
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if risultato:
                    cur.execute("""
                        SELECT id, data, partita, mercato, quota_sistema, quota_sisal,
                               ev_modello, ev_realistico, stake, risultato, profit, note,
                               created_at, updated_at
                        FROM bets
                        WHERE risultato = %s
                        ORDER BY data DESC, id DESC;
                    """, (risultato,))
                else:
                    cur.execute("""
                        SELECT id, data, partita, mercato, quota_sistema, quota_sisal,
                               ev_modello, ev_realistico, stake, risultato, profit, note,
                               created_at, updated_at
                        FROM bets
                        ORDER BY data DESC, id DESC;
                    """)
                
                rows = cur.fetchall()
                
                # Converte in lista di dict
                bets = []
                for row in rows:
                    bets.append({
                        'id': row[0],
                        'data': row[1].strftime('%d/%m/%Y'),
                        'partita': row[2],
                        'mercato': row[3],
                        'quota_sistema': float(row[4]) if row[4] else None,
                        'quota_sisal': float(row[5]),
                        'ev_modello': row[6],
                        'ev_realistico': row[7],
                        'stake': row[8],
                        'risultato': row[9],
                        'profit': float(row[10]),
                        'note': row[11] or '',
                        'created_at': row[12].isoformat() if row[12] else None,
                        'updated_at': row[13].isoformat() if row[13] else None
                    })
                
                return bets
    
    @staticmethod
    def get_by_id(bet_id: int) -> Optional[Dict]:
        """Ottieni singola bet per ID"""
        bets = BetModel.get_all()
        for bet in bets:
            if bet['id'] == bet_id:
                return bet
        return None
    
    @staticmethod
    def update_risultato(bet_id: int, risultato: str) -> float:
        """
        Aggiorna risultato bet e calcola profit
        
        Args:
            bet_id: ID bet
            risultato: 'WIN', 'LOSS', 'VOID', 'SKIP'
        
        Returns:
            Profit calcolato
        """
        if risultato not in BetModel.VALID_RISULTATI:
            raise ValueError(f"Risultato non valido: {risultato}")
        
        if not is_db_available():
            raise RuntimeError("Database non disponibile")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ottieni quota e stake
                cur.execute("SELECT quota_sisal, stake FROM bets WHERE id = %s;", (bet_id,))
                row = cur.fetchone()
                
                if not row:
                    raise ValueError(f"Bet {bet_id} non trovata")
                
                quota = float(row[0])
                stake_raw = row[1]
                
                # Calcola profit
                try:
                    stake = float(stake_raw)
                except (ValueError, TypeError):
                    stake = 0.0  # MONITOR
                
                if risultato == 'WIN':
                    profit = stake * (quota - 1)
                elif risultato == 'LOSS':
                    profit = -stake
                else:  # VOID, SKIP
                    profit = 0.0
                
                # Update database
                cur.execute("""
                    UPDATE bets
                    SET risultato = %s, profit = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                """, (risultato, profit, bet_id))
                
                logger.info("✅ Risultato aggiornato", bet_id=bet_id, risultato=risultato, profit=profit)
                return profit
    
    @staticmethod
    def update_fields(bet_id: int, updates: Dict):
        """Aggiorna campi specifici bet (stake, quota, note)"""
        if not is_db_available():
            raise RuntimeError("Database non disponibile")
        
        allowed_fields = ['stake', 'quota_sisal', 'note']
        fields_to_update = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not fields_to_update:
            return
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Costruisci query dinamica
                set_clause = ', '.join([f"{k} = %s" for k in fields_to_update.keys()])
                values = list(fields_to_update.values()) + [bet_id]
                
                cur.execute(f"""
                    UPDATE bets
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                """, values)
                
                logger.info("✅ Bet modificata", bet_id=bet_id, updates=fields_to_update)
    
    @staticmethod
    def delete(bet_id: int):
        """Elimina bet dal database"""
        if not is_db_available():
            raise RuntimeError("Database non disponibile")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ottieni info per log
                cur.execute("SELECT partita, risultato FROM bets WHERE id = %s;", (bet_id,))
                row = cur.fetchone()
                
                if not row:
                    raise ValueError(f"Bet {bet_id} non trovata")
                
                partita, risultato = row
                
                # Delete
                cur.execute("DELETE FROM bets WHERE id = %s;", (bet_id,))
                
                logger.info("🗑️ Bet eliminata", bet_id=bet_id, partita=partita, risultato=risultato)
    
    @staticmethod
    def get_stats() -> Dict:
        """Ottieni statistiche aggregate (usa view v_bet_stats)"""
        if not is_db_available():
            return {
                'total': 0,
                'pending': 0,
                'completed': 0,
                'wins': 0,
                'losses': 0,
                'skipped': 0,
                'total_profit': 0.0,
                'avg_profit': 0.0
            }
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM v_bet_stats;")
                row = cur.fetchone()
                
                if not row:
                    return {'total': 0, 'pending': 0}
                
                return {
                    'total': row[0],
                    'pending': row[1],
                    'completed': row[2],
                    'wins': row[3],
                    'losses': row[4],
                    'skipped': row[5],
                    'total_profit': float(row[6]),
                    'avg_profit': float(row[7])
                }
    
    @staticmethod
    def check_duplicate(partita: str, mercato: str) -> Optional[Dict]:
        """
        Verifica se esiste già bet pending con stessa partita+mercato
        
        Returns:
            Dict bet esistente o None
        """
        if not is_db_available():
            return None
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, quota_sisal, stake
                    FROM bets
                    WHERE partita = %s AND mercato = %s AND risultato = 'PENDING'
                    LIMIT 1;
                """, (partita, mercato))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'quota': float(row[1]),
                        'stake': row[2]
                    }
                
                return None
