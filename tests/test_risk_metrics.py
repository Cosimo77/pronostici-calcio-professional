"""Regressione: metriche di rischio del diario (equity curve cronologica, Sharpe per puntata)."""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import web.app_professional as app_mod  # noqa: E402


def _bets_dal_db():
    # Cronologico: -3, -2, +5, -1 (multipla), +4. Dal DB arrivano singole DESC e multiple in coda.
    cronologico = [
        {"id": 1, "data": "2026-10-01", "stake": 1, "Profit": -3.0},
        {"id": 2, "data": "2026-10-02", "stake": 1, "Profit": -2.0},
        {"id": 3, "data": "2026-10-03", "stake": 2, "Profit": 5.0},
        {"id": "G1", "data": "2026-10-04", "stake": 1, "Profit": -1.0},
        {"id": 4, "data": "2026-10-05", "stake": 2, "Profit": 4.0},
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


def test_senza_puntate_restituisce_zeri():
    assert app_mod.calculate_risk_metrics(pd.DataFrame())["max_drawdown"] == 0.0
