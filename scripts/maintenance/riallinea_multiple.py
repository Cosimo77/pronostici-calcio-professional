#!/usr/bin/env python3
"""
Riallinea l'esito delle multiple alle regole attuali: una multipla resta PENDING finche' tutti
i suoi eventi non sono validati. Utile per le multiple spostate tra le completate con la regola
precedente (una gamba LOSS con altre ancora in attesa).

Uso (DATABASE_URL deve puntare al database):
    python scripts/maintenance/riallinea_multiple.py            # elenca soltanto
    python scripts/maintenance/riallinea_multiple.py --applica  # aggiorna il database
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from database import init_db, is_db_available  # noqa: E402
from database.bet_group_model import BetGroupModel  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--applica", action="store_true", help="aggiorna le multiple (senza: solo elenco)")
    args = parser.parse_args()

    if not is_db_available() and not init_db():
        print("Database non disponibile: imposta DATABASE_URL")
        return 1

    modifiche = BetGroupModel.riallinea_esiti(applica=args.applica)
    if not modifiche:
        print("Nessuna multipla da riallineare")
        return 0

    for m in modifiche:
        print(f"Multipla {m['id']}: {m['da']} -> {m['a']} (profit {m['profit']:.2f})")
    print(f"\n{len(modifiche)} multiple " + ("aggiornate" if args.applica else "da riallineare (usa --applica)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
