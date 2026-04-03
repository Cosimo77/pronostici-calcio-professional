"""
Test Suite: Cache Manager
Verifica funzionalità caching Redis con graceful degradation
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

from cache_manager import CacheManager, get_cache_manager  # noqa: E402


class TestCacheManagerDisabled:
    """Test CacheManager quando Redis non disponibile"""

    @pytest.fixture
    def disabled_cache(self):
        """Fixture: CacheManager con Redis non disponibile"""
        with patch("cache_manager.redis.from_url") as mock_redis:
            # Simula Redis non disponibile
            mock_redis.side_effect = Exception("Redis not available")
            manager = CacheManager()
            yield manager

    def test_initialization_graceful_degradation(self, disabled_cache):
        """Test: Graceful degradation se Redis non disponibile"""
        assert disabled_cache.enabled is False
        assert disabled_cache.redis_client is None

    def test_get_returns_none_when_disabled(self, disabled_cache):
        """Test: get() ritorna None quando cache disabilitata"""
        result = disabled_cache.get("any_key")
        assert result is None

    def test_set_returns_false_when_disabled(self, disabled_cache):
        """Test: set() ritorna False quando cache disabilitata"""
        result = disabled_cache.set("key", {"data": "test"}, 3600)
        assert result is False

    def test_delete_returns_false_when_disabled(self, disabled_cache):
        """Test: delete() ritorna False quando cache disabilitata"""
        result = disabled_cache.delete("key")
        assert result is False


class TestCacheManagerEnabled:
    """Test CacheManager con Redis mockato funzionante"""

    @pytest.fixture
    def enabled_cache(self):
        """Fixture: CacheManager con Redis mock funzionante"""
        with patch("cache_manager.redis.from_url") as mock_redis_class:
            # Mock Redis client funzionante
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_client.setex.return_value = True
            mock_client.delete.return_value = 1
            mock_client.keys.return_value = []
            mock_client.dbsize.return_value = 0
            mock_redis_class.return_value = mock_client

            manager = CacheManager()
            yield manager, mock_client

    def test_initialization_successful(self, enabled_cache):
        """Test: Inizializzazione successo con Redis disponibile"""
        manager, _ = enabled_cache
        assert manager.enabled is True
        assert manager.redis_client is not None

    def test_set_calls_redis_setex(self, enabled_cache):
        """Test: set() chiama Redis setex correttamente"""
        manager, mock_client = enabled_cache

        key = "test:key"
        value = {"squadra": "Inter", "prob": 0.65}
        ttl = 3600

        result = manager.set(key, value, ttl)

        assert result is True
        mock_client.setex.assert_called_once()
        call_args = mock_client.setex.call_args[0]
        assert call_args[0] == key
        assert call_args[1] == ttl
        assert json.loads(call_args[2]) == value

    def test_get_returns_none_on_miss(self, enabled_cache):
        """Test: get() ritorna None se chiave non in cache"""
        manager, mock_client = enabled_cache
        mock_client.get.return_value = None

        result = manager.get("nonexistent:key")
        assert result is None

    def test_get_returns_value_on_hit(self, enabled_cache):
        """Test: get() ritorna valore deserializzato su hit"""
        manager, mock_client = enabled_cache

        cached_value = {"squadra": "Milan", "prob": 0.72}
        mock_client.get.return_value = json.dumps(cached_value)

        result = manager.get("test:key")
        assert result == cached_value
        assert result["squadra"] == "Milan"
        assert result["prob"] == 0.72

    def test_delete_calls_redis_delete(self, enabled_cache):
        """Test: delete() chiama Redis delete"""
        manager, mock_client = enabled_cache
        mock_client.delete.return_value = 1

        result = manager.delete("test:key")
        assert result is True
        mock_client.delete.assert_called_once_with("test:key")

    def test_generate_key_creates_unique_hash(self, enabled_cache):
        """Test: _generate_key crea chiavi univoche"""
        manager, _ = enabled_cache

        key1 = manager._generate_key("predictions", "Inter", "Milan")
        key2 = manager._generate_key("predictions", "Inter", "Napoli")
        key3 = manager._generate_key("predictions", "Inter", "Milan")  # Stesso di key1

        # Key differenti per parametri diversi
        assert key1 != key2
        # Stessa key per stessi parametri (deterministic)
        assert key1 == key3
        # Formato corretto
        assert key1.startswith("predictions:")

    def test_clear_pattern_deletes_matching_keys(self, enabled_cache):
        """Test: clear_pattern elimina chiavi matchate"""
        manager, mock_client = enabled_cache

        # Mock keys return + delete
        mock_client.keys.return_value = ["pred:1", "pred:2", "pred:3"]
        mock_client.delete.return_value = 3

        deleted_count = manager.clear_pattern("pred:*")

        assert deleted_count == 3
        mock_client.keys.assert_called_once_with("pred:*")
        mock_client.delete.assert_called_once()

    def test_get_stats_returns_info(self, enabled_cache):
        """Test: get_stats ritorna statistiche cache"""
        manager, mock_client = enabled_cache

        # Mock Redis info calls
        mock_client.info.return_value = {
            "keyspace_hits": 100,
            "keyspace_misses": 20,
            "used_memory_human": "1M",
            "used_memory_peak_human": "2M",
        }
        mock_client.dbsize.return_value = 42
        mock_client.keys.return_value = []

        stats = manager.get_stats()

        assert stats["enabled"] is True
        assert stats["total_keys"] == 42
        assert "hit_rate" in stats

    def test_redis_connection_error_graceful(self, enabled_cache):
        """Test: Errori Redis gestiti gracefully"""
        manager, mock_client = enabled_cache

        # Simula errore Redis
        mock_client.get.side_effect = Exception("Connection lost")

        # get() non dovrebbe crashare
        result = manager.get("test:key")
        assert result is None


class TestCacheManagerSingleton:
    """Test singleton pattern get_cache_manager"""

    def test_get_cache_manager_returns_singleton(self):
        """Test: get_cache_manager ritorna sempre stessa istanza"""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        assert manager1 is manager2
        assert id(manager1) == id(manager2)
