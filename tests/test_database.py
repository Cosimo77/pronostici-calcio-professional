"""
Test Suite: Database Operations
Verifica funzionalità database PostgreSQL con graceful degradation
"""

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.connection import get_database_url, init_db, is_db_available  # noqa: E402
from database.models import BetModel  # noqa: E402


class TestDatabaseConnection:
    """Test connessione database e graceful degradation"""

    def test_get_database_url_returns_env_var(self):
        """Test: get_database_url() legge DATABASE_URL da environment"""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:password@localhost/db"}):
            url = get_database_url()
            assert url == "postgresql://test:password@localhost/db"

    def test_get_database_url_returns_none_if_not_set(self):
        """Test: get_database_url() ritorna None se var non configurata"""
        with patch.dict(os.environ, {}, clear=True):
            url = get_database_url()
            assert url is None

    def test_is_db_available_returns_false_when_no_pool(self):
        """Test: is_db_available() ritorna False se pool non inizializzato"""
        with patch("database.connection._connection_pool", None):
            result = is_db_available()
            assert result is False

    def test_init_db_graceful_degradation_no_url(self):
        """Test: init_db() graceful degradation se DATABASE_URL mancante"""
        with patch.dict(os.environ, {}, clear=True):
            result = init_db()
            assert result is False

    @patch("database.connection.ThreadedConnectionPool")
    def test_init_db_creates_connection_pool(self, mock_pool_class):
        """Test: init_db() crea ThreadedConnectionPool con parametri corretti"""
        mock_pool = MagicMock()
        mock_pool_class.return_value = mock_pool

        # Mock connection test
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchone.return_value = ["PostgreSQL 14.0"]
        mock_conn.cursor.return_value = mock_cursor
        mock_pool.getconn.return_value = mock_conn

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://localhost/test"}):
            with patch("database.connection._ensure_schema_exists"):
                result = init_db()

        # Verifica pool creato con parametri corretti
        mock_pool_class.assert_called_once_with(minconn=2, maxconn=20, dsn="postgresql://localhost/test")
        assert result is True


class TestBetModelWithoutDB:
    """Test BetModel quando database non disponibile"""

    @patch("database.models.is_db_available", return_value=False)
    def test_create_raises_error_when_db_unavailable(self, mock_is_available):
        """Test: create() solleva RuntimeError se DB non disponibile"""
        data = {"partita": "Inter-Milan", "mercato": "1X2", "quota_sisal": 2.5, "stake": 10.0}

        with pytest.raises(RuntimeError, match="Database non disponibile"):
            BetModel.create(data)

    @patch("database.models.is_db_available", return_value=False)
    def test_get_all_returns_empty_list_when_db_unavailable(self, mock_is_available):
        """Test: get_all() ritorna lista vuota se DB non disponibile"""
        result = BetModel.get_all()
        assert result == []


class TestBetModelValidation:
    """Test validazione dati BetModel"""

    @patch("database.models.is_db_available", return_value=True)
    def test_create_requires_mandatory_fields(self, mock_is_available):
        """Test: create() solleva ValueError se campi obbligatori mancanti"""
        incomplete_data = {
            "partita": "Inter-Milan"
            # Mancano mercato, quota_sisal, stake
        }

        with pytest.raises(ValueError, match="Campo obbligatorio mancante"):
            BetModel.create(incomplete_data)

    @patch("database.models.is_db_available", return_value=True)
    @patch("database.models.get_db_connection")
    def test_create_valid_bet(self, mock_get_conn, mock_is_available):
        """Test: create() inserisce bet con dati validi"""
        # Mock database connection e cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchone.return_value = [42]  # ID bet creata

        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor

        mock_get_conn.return_value = mock_conn

        bet_data = {
            "partita": "Inter-Milan",
            "mercato": "1X2",
            "quota_sisal": 2.5,
            "stake": 10.0,
            "ev_modello": "+15.2%",
            "note": "Test bet",
        }

        bet_id = BetModel.create(bet_data)

        # Verifica ID ritornato
        assert bet_id == 42

        # Verifica INSERT SQL chiamato
        mock_cursor.execute.assert_called_once()
        sql_call = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO bets" in sql_call
        assert "RETURNING id" in sql_call

    @patch("database.models.is_db_available", return_value=True)
    @patch("database.models.get_db_connection")
    def test_get_all_fetches_all_bets(self, mock_get_conn, mock_is_available):
        """Test: get_all() fetcha tutte le bet"""
        # Mock risultati database
        mock_rows = [
            (
                1,
                datetime(2026, 4, 1),
                "Inter-Milan",
                "1X2",
                2.5,
                2.5,
                "+15%",
                "+12%",
                "10.0",
                "WIN",
                15.0,
                "Test bet",
                datetime.now(),
                datetime.now(),
                None,
            ),
            (
                2,
                datetime(2026, 4, 2),
                "Juve-Napoli",
                "X",
                3.2,
                3.2,
                "+20%",
                "+18%",
                "5.0",
                "PENDING",
                0.0,
                "",
                datetime.now(),
                datetime.now(),
                None,
            ),
        ]

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchall.return_value = mock_rows

        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor

        mock_get_conn.return_value = mock_conn

        bets = BetModel.get_all()

        # Verifica numero risultati
        assert len(bets) == 2

        # Verifica primo bet
        assert bets[0]["id"] == 1
        assert bets[0]["partita"] == "Inter-Milan"
        assert bets[0]["risultato"] == "WIN"
        assert bets[0]["profit"] == 15.0

    @patch("database.models.is_db_available", return_value=True)
    @patch("database.models.get_db_connection")
    def test_get_all_filters_by_risultato(self, mock_get_conn, mock_is_available):
        """Test: get_all(risultato='WIN') filtra risultati"""
        mock_rows = [
            (
                1,
                datetime(2026, 4, 1),
                "Inter-Milan",
                "1X2",
                2.5,
                2.5,
                "+15%",
                "+12%",
                "10.0",
                "WIN",
                15.0,
                "",
                datetime.now(),
                datetime.now(),
                None,
            )
        ]

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchall.return_value = mock_rows

        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor

        mock_get_conn.return_value = mock_conn

        bets = BetModel.get_all(risultato="WIN")

        # Verifica filtro applicato
        assert len(bets) == 1
        assert bets[0]["risultato"] == "WIN"

        # Verifica SQL con WHERE clause
        sql_call = mock_cursor.execute.call_args[0][0]
        assert "WHERE risultato" in sql_call


class TestBetGroupModel:
    """Test gruppo scommesse multiple"""

    @patch("database.models.is_db_available", return_value=True)
    @patch("database.models.get_db_connection")
    def test_bet_group_references_multiple_bets(self, mock_get_conn, mock_is_available):
        """Test: Bet possono avere group_id per raggruppare multiple"""
        # Mock creazione bet con group_id
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchone.return_value = [100]

        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor

        mock_get_conn.return_value = mock_conn

        bet_data = {
            "partita": "Inter-Milan",
            "mercato": "1X2",
            "quota_sisal": 2.5,
            "stake": 10.0,
            "group_id": "GRP_20260401_001",  # ID gruppo per multipla
        }

        BetModel.create(bet_data)

        # Verifica group_id passato al database
        insert_params = mock_cursor.execute.call_args[0][1]
        assert "GRP_20260401_001" in insert_params
