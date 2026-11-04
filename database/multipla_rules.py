"""
Regole di calcolo delle scommesse multiple (puro, senza accesso a database)
Usato sia dal database PostgreSQL sia dal fallback CSV
"""

from math import prod
from typing import List, Tuple

# Risultati di una gamba che non pesano sulla multipla (la quota della gamba vale 1)
GAMBE_NEUTRE = ("VOID", "SKIP")


def esito_multipla(gambe: List[Tuple[str, float]], quota_totale: float, stake: float) -> Tuple[str, float]:
    """
    Calcola risultato e profit di una multipla

    Args:
        gambe: lista di (risultato, quota) per ogni evento
        quota_totale: quota finale della schedina (con eventuale bonus)
        stake: importo puntato sulla multipla

    Regole:
        - finche' c'e' una gamba PENDING la multipla resta PENDING (anche se un'altra gamba e' LOSS):
          passa tra le completate solo quando tutti gli eventi sono validati
        - a gambe tutte validate, una gamba LOSS perde la multipla
        - gambe VOID/SKIP vengono escluse e la quota si ricalcola sulle sole gambe vincenti
        - se tutte le gambe sono VOID/SKIP la multipla e' VOID (stake restituito)
    """
    risultati = [risultato for risultato, _ in gambe]

    if "PENDING" in risultati:
        return "PENDING", 0.0
    if "LOSS" in risultati:
        return "LOSS", round(-stake, 2)

    quote_vincenti = [quota for risultato, quota in gambe if risultato == "WIN"]
    if not quote_vincenti:
        return "VOID", 0.0

    # Nessuna gamba annullata: vale la quota della schedina (puo' includere un bonus)
    quota = quota_totale if len(quote_vincenti) == len(gambe) else prod(quote_vincenti)
    return "WIN", round(stake * (quota - 1), 2)
