"""
Model per gestione scommesse multiple (combo/sistemi)
Data: 17/02/2026
"""

from datetime import date, datetime
from typing import Dict, List, Optional

import structlog

from database.connection import get_db_connection

logger = structlog.get_logger(__name__)


class BetGroupModel:
    """Model per scommesse multiple (doppia, tripla, ecc.)"""

    @staticmethod
    def create(data: Dict) -> int:
        """
        Crea nuova multipla con eventi associati

        Args:
            data: {
                'data': date object,
                'nome': str (opzionale),
                'tipo_multipla': str ('doppia', 'tripla', ecc.),
                'num_eventi': int,
                'quota_totale': float,
                'stake': float,
                'note': str (opzionale)
            }

        Returns:
            group_id: ID della multipla creata
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO bet_groups
                        (data, nome, tipo_multipla, num_eventi, quota_totale, stake, risultato, profit, note)
                        VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', 0.0, %s)
                        RETURNING id
                    """,
                        (
                            data["data"],
                            data.get("nome", ""),
                            data["tipo_multipla"],
                            data["num_eventi"],
                            round(float(data["quota_totale"]), 2),
                            float(data["stake"]),
                            data.get("note", ""),
                        ),
                    )

                    group_id = cursor.fetchone()[0]

                    logger.info(
                        "Multipla creata",
                        group_id=group_id,
                        tipo=data["tipo_multipla"],
                        quota=data["quota_totale"],
                        num_eventi=data["num_eventi"],
                    )

                    return group_id

        except Exception as e:
            logger.error("Errore creazione multipla", error=str(e))
            raise

    @staticmethod
    def get_by_id(group_id: int) -> Optional[Dict]:
        """Recupera multipla per ID"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, data, nome, tipo_multipla, num_eventi, quota_totale,
                               stake, risultato, profit, note, created_at
                        FROM bet_groups
                        WHERE id = %s
                    """,
                        (group_id,),
                    )

                    row = cursor.fetchone()
                    if not row:
                        return None

                    return {
                        "id": row[0],
                        "data": row[1].strftime("%d/%m/%Y") if row[1] else "",
                        "nome": row[2],
                        "tipo_multipla": row[3],
                        "num_eventi": row[4],
                        "quota_totale": float(row[5]),
                        "stake": float(row[6]),
                        "risultato": row[7],
                        "profit": float(row[8]),
                        "note": row[9],
                        "created_at": row[10].isoformat() if row[10] else None,
                    }

        except Exception as e:
            logger.error("Errore get multipla", group_id=group_id, error=str(e))
            return None

    @staticmethod
    def get_all(risultato: Optional[str] = None) -> List[Dict]:
        """
        Recupera tutte le multiple (con filtro opzionale per risultato)

        Args:
            risultato: 'PENDING', 'WIN', 'LOSS', 'VOID' (None = tutte)
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if risultato:
                        cursor.execute(
                            """
                            SELECT id, data, nome, tipo_multipla, num_eventi, quota_totale,
                                   stake, risultato, profit, note
                            FROM bet_groups
                            WHERE risultato = %s
                            ORDER BY data DESC, id DESC
                        """,
                            (risultato,),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT id, data, nome, tipo_multipla, num_eventi, quota_totale,
                                   stake, risultato, profit, note
                            FROM bet_groups
                            ORDER BY data DESC, id DESC
                        """
                        )

                    rows = cursor.fetchall()

                    groups = []
                    for row in rows:
                        groups.append(
                            {
                                "id": row[0],
                                "data": row[1].strftime("%d/%m/%Y") if row[1] else "",
                                "nome": row[2],
                                "tipo_multipla": row[3],
                                "num_eventi": row[4],
                                "quota_totale": float(row[5]),
                                "stake": float(row[6]),
                                "risultato": row[7],
                                "profit": float(row[8]),
                                "note": row[9],
                            }
                        )

                    return groups

        except Exception as e:
            logger.error("Errore get all multiple", error=str(e))
            return []

    @staticmethod
    def update_risultato(group_id: int) -> float:
        """
        Aggiorna risultato multipla basandosi sugli eventi associati

        Logica:
        - Tutti WIN → multipla WIN
        - Almeno un LOSS → multipla LOSS
        - Almeno un VOID (senza LOSS) → multipla VOID
        - Altrimenti → PENDING

        Returns:
            profit: Profit della multipla
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Recupera info multipla
                    cursor.execute(
                        """
                        SELECT quota_totale, stake, num_eventi
                        FROM bet_groups
                        WHERE id = %s
                    """,
                        (group_id,),
                    )

                    row = cursor.fetchone()
                    if not row:
                        raise ValueError(f"Multipla {group_id} non trovata")

                    quota_totale, stake, num_eventi = row

                    # Conta risultati eventi associati
                    cursor.execute(
                        """
                        SELECT risultato, COUNT(*) as cnt
                        FROM bets
                        WHERE group_id = %s
                        GROUP BY risultato
                    """,
                        (group_id,),
                    )

                    risultati = {r[0]: r[1] for r in cursor.fetchall()}

                    # Determina risultato finale
                    num_win = risultati.get("WIN", 0)
                    num_loss = risultati.get("LOSS", 0)
                    num_void = risultati.get("VOID", 0)
                    num_skip = risultati.get("SKIP", 0)
                    num_pending = risultati.get("PENDING", 0)

                    if num_loss > 0 or num_skip > 0:
                        # Almeno un LOSS o SKIP → Multipla LOSS
                        risultato_finale = "LOSS"
                        profit = -stake
                    elif num_win == num_eventi:
                        # Tutti WIN → Multipla WIN
                        risultato_finale = "WIN"
                        vincita = quota_totale * stake
                        profit = vincita - stake
                    elif num_void > 0 and num_pending == 0 and num_loss == 0:
                        # Almeno un VOID (senza LOSS/PENDING) → Multipla VOID
                        risultato_finale = "VOID"
                        profit = 0.0
                    else:
                        # Ancora eventi pending
                        risultato_finale = "PENDING"
                        profit = 0.0

                    # Aggiorna multipla
                    cursor.execute(
                        """
                        UPDATE bet_groups
                        SET risultato = %s, profit = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """,
                        (risultato_finale, round(profit, 2), group_id),
                    )

                    logger.info(
                        "Multipla aggiornata",
                        group_id=group_id,
                        risultato=risultato_finale,
                        profit=profit,
                        win=num_win,
                        loss=num_loss,
                        void=num_void,
                    )

                    return profit

        except Exception as e:
            logger.error("Errore update risultato multipla", group_id=group_id, error=str(e))
            raise

    @staticmethod
    def delete(group_id: int) -> bool:
        """
        Elimina multipla (CASCADE elimina anche eventi associati in bets)
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM bet_groups WHERE id = %s", (group_id,))

                    logger.info("Multipla eliminata", group_id=group_id)
                    return True

        except Exception as e:
            logger.error("Errore delete multipla", group_id=group_id, error=str(e))
            return False
