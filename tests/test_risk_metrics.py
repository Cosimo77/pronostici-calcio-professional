"""Regressione: metriche di rischio del diario (equity curve cronologica, Sharpe per puntata)."""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import web.app_professional as app_mod  # noqa: E402


def _bets_dal_db():
    # Cronologico: -3, -2, +5, -1 (multipla, stesso giorno), +4. Date GG/MM/AAAA, come nel DB:
    # "12/10/2026" e "20/10/2026" lette mese-per-primo sarebbero dicembre e un valore non valido.
    cronologico = [
        {"id": 1, "data": "12/10/2026", "stake": 1, "Profit": -3.0},
        {"id": 2, "data": "20/10/2026", "stake": 1, "Profit": -2.0},
        {"id": 3, "data": "03/11/2026", "stake": 2, "Profit": 5.0},
        {"id": "G1", "data": "03/11/2026", "stake": 1, "Profit": -1.0},
        {"id": 4, "data": "05/11/2026", "stake": 2, "Profit": 4.0},
    ]
    c = cronologico
    return pd.DataFrame([c[4], c[2], c[1], c[0], c[3]])


def test_max_drawdown_usa_ordine_cronologico_e_capitale_iniziale(monkeypatch):
    monkeypatch.setattr(app_mod, "load_bankroll_config", lambda: {"bankroll_iniziale": 100.0})
    r = app_mod.calculate_risk_metrics(_bets_dal_db())
    # Le prime due perdite (-5) partono dal capitale iniziale e sono il drawdown massimo
    assert r["max_drawdown"] == 5.0
    assert r["max_drawdown_pct"] == 5.0


def test_sharpe_per_puntata_non_annualizzato(monkeypatch):
    monkeypatch.setattr(app_mod, "load_bankroll_config", lambda: {"bankroll_iniziale": 100.0})
    r = app_mod.calculate_risk_metrics(_bets_dal_db())
    rendimenti = np.array([-3, -2, 2.5, -1, 2.0])
    assert r["sharpe_ratio"] == round(rendimenti.mean() / rendimenti.std(ddof=1), 2)


def test_ordina_cronologico_stessa_data_per_id():
    bets = [{"id": "G1", "data": "03/11/2026"}, {"id": 3, "data": "03/11/2026"}, {"id": 9, "data": "20/10/2026"}]
    assert [b["id"] for b in app_mod.ordina_cronologico(bets)] == [9, 3, "G1"]


def test_senza_puntate_restituisce_zeri():
    assert app_mod.calculate_risk_metrics(pd.DataFrame())["max_drawdown"] == 0.0


def test_gambe_multiple_chiuse_solo_eventi_decisi_con_quota_valida():
    bets = [
        {
            "group_id": "7",
            "mercato": "OVER_25",
            "quota_sisal": 1.8,
            "risultato": "WIN",
            "partita": "A vs B",
            "data": "01/11/2026",
        },
        {
            "group_id": "7",
            "mercato": "GG",
            "quota_sisal": "1.9",
            "risultato": "LOSS",
            "partita": "C vs D",
            "data": "01/11/2026",
        },
        {"group_id": "7", "mercato": "1", "quota_sisal": 1.5, "risultato": "PENDING"},
        {"group_id": "7", "mercato": "X", "quota_sisal": 1.0, "risultato": "WIN"},
        {"group_id": None, "mercato": "2", "quota_sisal": 2.1, "risultato": "WIN"},
    ]
    gambe = app_mod.gambe_multiple_chiuse(bets)
    assert [(g["mercato"], g["quota"], g["risultato"]) for g in gambe] == [("OVER_25", 1.8, "WIN"), ("GG", 1.9, "LOSS")]
