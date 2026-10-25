"""Test regole multiple e contabilita' (singole + multiple)"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.multipla_rules import esito_multipla  # noqa: E402
from web.diario_storage import DiarioStorage  # noqa: E402


class TestEsitoMultipla:
    def test_una_gamba_persa_perde_subito(self):
        gambe = [("WIN", 2.0), ("LOSS", 1.5), ("PENDING", 1.8)]
        assert esito_multipla(gambe, 5.4, 10.0) == ("LOSS", -10.0)

    def test_gambe_in_attesa_restano_pending(self):
        assert esito_multipla([("WIN", 2.0), ("PENDING", 1.5)], 3.0, 10.0) == ("PENDING", 0.0)

    def test_tutte_vinte_usa_quota_schedina(self):
        # quota schedina con bonus (6.0) invece del prodotto (2.0 * 1.5 = 3.0)
        assert esito_multipla([("WIN", 2.0), ("WIN", 1.5)], 6.0, 10.0) == ("WIN", 50.0)

    def test_gamba_void_ricalcola_la_quota(self):
        # la gamba annullata vale 1: restano 2.0 * 1.5 = 3.0
        assert esito_multipla([("WIN", 2.0), ("VOID", 1.8), ("WIN", 1.5)], 5.4, 10.0) == ("WIN", 20.0)

    def test_gamba_skip_non_e_una_perdita(self):
        assert esito_multipla([("WIN", 2.0), ("SKIP", 1.8)], 3.6, 10.0) == ("WIN", 10.0)

    def test_tutte_annullate_stake_restituito(self):
        assert esito_multipla([("VOID", 2.0), ("SKIP", 1.5)], 3.0, 10.0) == ("VOID", 0.0)


@pytest.fixture
def storage_csv(monkeypatch):
    """Giocate in modalita' CSV: 1 singola vinta + tripla persa (gambe con stake ripetuto)"""
    bets = [
        {
            "id": 0,
            "group_id": None,
            "data": "01/10/2026",
            "partita": "Inter vs Milan",
            "mercato": "1",
            "quota_sisal": 2.0,
            "stake": "10",
            "risultato": "WIN",
            "profit": 10.0,
        },
        {
            "id": 1,
            "group_id": "M1",
            "data": "02/10/2026",
            "partita": "A vs B",
            "mercato": "1",
            "quota_sisal": 2.0,
            "stake": "5",
            "risultato": "WIN",
            "profit": -5.0,
        },
        {
            "id": 2,
            "group_id": "M1",
            "data": "02/10/2026",
            "partita": "C vs D",
            "mercato": "X",
            "quota_sisal": 3.0,
            "stake": "5",
            "risultato": "LOSS",
            "profit": -5.0,
        },
        {
            "id": 3,
            "group_id": "M1",
            "data": "02/10/2026",
            "partita": "E vs F",
            "mercato": "2",
            "quota_sisal": 1.5,
            "stake": "5",
            "risultato": "PENDING",
            "profit": -5.0,
        },
    ]
    monkeypatch.setattr(DiarioStorage, "_use_database", staticmethod(lambda: False))
    monkeypatch.setattr(DiarioStorage, "get_all_bets", staticmethod(lambda risultato=None: bets))
    return bets


class TestContabilita:
    def test_la_multipla_conta_una_volta_sola(self, storage_csv):
        voci = DiarioStorage.get_accounting_bets()
        assert len(voci) == 2  # 1 singola + 1 multipla (non 4 righe)

    def test_profit_della_multipla_non_triplicato(self, storage_csv):
        voci = DiarioStorage.get_accounting_bets()
        multipla = next(v for v in voci if v["mercato"] == "MULTIPLA")
        assert multipla["risultato"] == "LOSS"
        assert multipla["profit"] == -5.0
        assert sum(v["profit"] for v in voci) == 5.0  # +10 singola, -5 multipla
