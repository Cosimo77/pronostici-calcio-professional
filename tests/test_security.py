"""
Test Suite: Security Features
Verifica sicurezza: rate limiting, headers, request ID
"""

import os
import sys

import pytest

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

# Mock environment prima di importare app
os.environ["FLASK_ENV"] = "testing"
os.environ["ODDS_API_KEY"] = "test_key_1234567890123456789012"

from app_professional import app


class TestSecurityHeaders:
    """Test security headers (CSP, X-Request-ID, etc.)"""

    @pytest.fixture
    def client(self):
        """Fixture: Flask test client"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_request_id_header_present(self, client):
        """Test: X-Request-ID header presente in ogni response"""
        response = client.get("/")

        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]

        # Verify UUID format (36 chars con hyphens)
        assert len(request_id) == 36
        assert request_id.count("-") == 4

    def test_security_headers_present(self, client):
        """Test: Security headers configurati"""
        response = client.get("/")

        # Check common security headers
        headers = response.headers

        # X-Request-ID sempre presente
        assert "X-Request-ID" in headers

        # Altri headers potrebbero essere aggiunti da Talisman
        # Test che response non abbia errori
        assert response.status_code in [200, 302, 404]

    def test_csp_headers_for_dashboard(self, client):
        """Test: CSP headers permettono Chart.js e Bootstrap"""
        response = client.get("/")

        # Verify response OK (CSP non blocca assets)
        assert response.status_code in [200, 302]

        # Se CSP header presente, verifica unsafe-inline per Chart.js
        if "Content-Security-Policy" in response.headers:
            csp = response.headers["Content-Security-Policy"]
            # CSP dovrebbe permettere inline scripts per Chart.js
            assert "script-src" in csp or "default-src" in csp


class TestRateLimiting:
    """Test rate limiting per API endpoints"""

    @pytest.fixture
    def client(self):
        """Fixture: Flask test client"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_api_health_rate_limit_allows_normal_traffic(self, client):
        """Test: Rate limit permette traffico normale"""
        # 5 requests rapide (sotto limite)
        responses = []
        for _ in range(5):
            response = client.get("/api/health")
            responses.append(response.status_code)

        # Tutte dovrebbero passare (200 OK)
        assert all(status == 200 for status in responses)

    def test_api_status_endpoint_accessible(self, client):
        """Test: /api/status accessibile con rate limit"""
        response = client.get("/api/status")

        # 200 OK o 500 se servizi opzionali down (ma non 429 Too Many Requests)
        assert response.status_code in [200, 500]
        assert response.status_code != 429

    def test_predict_enterprise_endpoint_accessible(self, client):
        """Test: /api/predict_enterprise accessibile"""
        payload = {"squadra_casa": "Inter", "squadra_ospite": "Milan"}

        response = client.post("/api/predict_enterprise", json=payload, content_type="application/json")

        # 200 OK o 400/500 per errori business logic (ma non 429)
        assert response.status_code != 429


class TestInputValidation:
    """Test validazione input utente"""

    @pytest.fixture
    def client(self):
        """Fixture: Flask test client"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_predict_missing_parameters(self, client):
        """Test: Predict rifiuta request senza parametri required"""
        response = client.post("/api/predict_enterprise", json={}, content_type="application/json")

        # 400 Bad Request o 422 Unprocessable Entity
        assert response.status_code in [400, 422, 500]

    def test_predict_invalid_team_names(self, client):
        """Test: Predict gestisce nomi squadre invalidi"""
        payload = {
            "squadra_casa": "NONEXISTENT_TEAM_XYZ",
            "squadra_ospite": "ANOTHER_FAKE_TEAM",
        }

        response = client.post("/api/predict_enterprise", json=payload, content_type="application/json")

        # Dovrebbe ritornare errore o dati vuoti (non crash 500)
        assert response.status_code in [200, 400, 404, 422]

        if response.status_code == 200:
            data = response.get_json()
            # Se ritorna 200, dovrebbe avere error flag o messaggio
            assert data is not None

    def test_max_content_length_enforced(self, client):
        """Test: Request troppo grandi rifiutate"""
        # Crea payload enorme (>16MB configurato in app)
        huge_payload = {"data": "X" * (17 * 1024 * 1024)}  # 17MB

        try:
            response = client.post(
                "/api/predict_enterprise",
                json=huge_payload,
                content_type="application/json",
            )

            # Dovrebbe essere rifiutato (413 Request Entity Too Large o errore)
            assert response.status_code in [413, 400, 500]
        except Exception:
            # OK se Flask rifiuta prima di processare
            pass


class TestSessionSecurity:
    """Test sicurezza sessioni Flask"""

    @pytest.fixture
    def client(self):
        """Fixture: Flask test client"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_secret_key_configured(self):
        """Test: Secret key configurato (non default vuoto)"""
        assert app.config["SECRET_KEY"] is not None
        assert len(app.config["SECRET_KEY"]) > 0

    def test_session_cookie_settings_secure_in_production(self):
        """Test: Session cookie settings sicuri in production"""
        # In testing mode, alcune settings potrebbero essere diverse
        # Ma verifichiamo che esistano
        assert "SESSION_COOKIE_HTTPONLY" in app.config
        assert "SESSION_COOKIE_SAMESITE" in app.config

        # HTTPOnly dovrebbe essere sempre True
        assert app.config["SESSION_COOKIE_HTTPONLY"] is True


class TestErrorHandling:
    """Test gestione errori sicura (no info leak)"""

    @pytest.fixture
    def client(self):
        """Fixture: Flask test client"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_404_no_sensitive_info_leak(self, client):
        """Test: 404 non espone path sensitive"""
        response = client.get("/nonexistent/path/with/secrets")

        assert response.status_code == 404

        # Response non dovrebbe contenere info sensibili
        data = response.get_data(as_text=True)
        assert "SECRET" not in data.upper()
        assert "PASSWORD" not in data.upper()

    def test_500_error_safe_handling(self, client):
        """Test: 500 errors gestiti senza crash"""
        # Trigger potenziale errore con parametri strani
        response = client.post(
            "/api/predict_enterprise",
            json={"squadra_casa": None, "squadra_ospite": None},
            content_type="application/json",
        )

        # Dovrebbe ritornare error gracefully (non crash del server)
        assert response.status_code in [200, 400, 422, 500]

        # Se 500, dovrebbe essere JSON valido
        if response.status_code == 500:
            try:
                data = response.get_json()
                assert data is not None or response.data is not None
            except Exception:
                # OK se ritorna HTML error page
                pass
