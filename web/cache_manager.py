#!/usr/bin/env python3
"""
Cache Manager con Redis per Performance Optimization
Riduce response time da 1.5s a <500ms e risparmia chiamate API
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import redis

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gestisce cache Redis con strategie intelligenti per:
    - ML Predictions (TTL 1h)
    - Odds API (TTL 30min)
    - Dataset info (TTL 24h)
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Inizializza connessione Redis

        Args:
            redis_url: URL connessione Redis (default: localhost:6379/0)
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connessione
            self.redis_client.ping()
            logger.info("✅ Connessione Redis stabilita")
            self.enabled = True
        except Exception as e:
            logger.warning(f"⚠️ Redis non disponibile, cache disabilitata: {e}")
            self.redis_client = None
            self.enabled = False

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Genera chiave cache unica basata su prefix + parametri

        Args:
            prefix: Prefisso chiave (es: 'predictions', 'odds')
            *args, **kwargs: Parametri per generare hash unico

        Returns:
            Chiave cache formato: prefix:hash
        """
        # Crea stringa rappresentativa dei parametri
        params_str = json.dumps({"args": args, "kwargs": sorted(kwargs.items())}, sort_keys=True)

        # Hash MD5 per chiave compatta
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]

        return f"{prefix}:{params_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera valore da cache

        Args:
            key: Chiave cache

        Returns:
            Valore deserializzato o None se non trovato/scaduto
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"🎯 Cache HIT: {key}")
                return json.loads(value)  # type: ignore
            else:
                logger.debug(f"❌ Cache MISS: {key}")
                return None
        except Exception as e:
            logger.warning(f"⚠️ Errore lettura cache {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        Salva valore in cache con TTL

        Args:
            key: Chiave cache
            value: Valore da cachare (sarà serializzato JSON)
            ttl: Time To Live in secondi

        Returns:
            True se salvato con successo
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Errore scrittura cache {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Elimina chiave da cache

        Args:
            key: Chiave da eliminare

        Returns:
            True se eliminata
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            logger.debug(f"🗑️ Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Errore eliminazione cache {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Elimina tutte le chiavi che matchano pattern

        Args:
            pattern: Pattern Redis (es: 'predictions:*')

        Returns:
            Numero chiavi eliminate
        """
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)  # type: ignore
            if keys:
                deleted = self.redis_client.delete(*keys)  # type: ignore
                logger.info(f"🗑️ Cache CLEAR: {pattern} ({deleted} chiavi)")
                return int(deleted) if deleted else 0  # type: ignore
            return 0
        except Exception as e:
            logger.warning(f"⚠️ Errore clear pattern {pattern}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Recupera statistiche cache Redis

        Returns:
            Dict con statistiche (keys count, memory, hits, misses, etc.)
        """
        if not self.enabled or not self.redis_client:
            return {"enabled": False}

        try:
            info = self.redis_client.info("stats")  # type: ignore
            memory = self.redis_client.info("memory")  # type: ignore

            # Conta chiavi per prefix
            patterns = ["predictions:*", "odds:*", "dataset:*", "squadre:*"]
            keys_count = {}
            for pattern in patterns:
                prefix = pattern.split(":")[0]
                keys_count[prefix] = len(self.redis_client.keys(pattern))  # type: ignore

            # Safe access to dict values with type: ignore
            keyspace_hits = info.get("keyspace_hits", 0) if isinstance(info, dict) else 0  # type: ignore
            keyspace_misses = info.get("keyspace_misses", 0) if isinstance(info, dict) else 0  # type: ignore
            total_ops = max(1, keyspace_hits + keyspace_misses)

            return {
                "enabled": True,
                "total_keys": int(self.redis_client.dbsize()),  # type: ignore
                "keys_by_prefix": keys_count,
                "keyspace_hits": keyspace_hits,
                "keyspace_misses": keyspace_misses,
                "hit_rate": keyspace_hits / total_ops * 100,
                "used_memory_human": memory.get("used_memory_human", "N/A") if isinstance(memory, dict) else "N/A",  # type: ignore
                "used_memory_peak_human": memory.get("used_memory_peak_human", "N/A") if isinstance(memory, dict) else "N/A",  # type: ignore
            }
        except Exception as e:
            logger.warning(f"⚠️ Errore statistiche cache: {e}")
            return {"enabled": True, "error": str(e)}

    # === METODI SPECIFICI PER L'APPLICAZIONE ===

    def cache_ml_predictions(self, home: str, away: str) -> Optional[Dict]:
        """
        Recupera predizioni ML da cache
        TTL: 1 ora (predizioni stabili nel breve termine)

        Args:
            home: Squadra casa
            away: Squadra trasferta

        Returns:
            Dict con predizione o None se non in cache
        """
        key = self._generate_key("predictions", home=home, away=away)
        return self.get(key)

    def set_ml_predictions(self, home: str, away: str, prediction_data: Dict) -> bool:
        """
        Salva predizioni ML in cache

        Args:
            home: Squadra casa
            away: Squadra trasferta
            prediction_data: Dati predizione completi

        Returns:
            True se salvato
        """
        key = self._generate_key("predictions", home=home, away=away)
        ttl = 3600  # 1 ora
        return self.set(key, prediction_data, ttl)

    def cache_odds_api(self, match_id: str) -> Optional[Dict]:
        """
        Recupera odds API da cache
        TTL: 10 ore (allineato con upcoming_matches)

        Args:
            match_id: ID univoco partita (es: 'home_vs_away_timestamp')

        Returns:
            Dict con quote o None
        """
        key = self._generate_key("odds", match_id=match_id)
        return self.get(key)

    def set_odds_api(self, match_id: str, odds_data: Dict) -> bool:
        """
        Salva odds API in cache

        Args:
            match_id: ID univoco partita
            odds_data: Dati quote completi

        Returns:
            True se salvato
        """
        key = self._generate_key("odds", match_id=match_id)
        ttl = 36000  # 10 ore - allineato con upcoming_matches per gestione quota
        return self.set(key, odds_data, ttl)

    def cache_upcoming_matches(self) -> Optional[Dict]:
        """
        Recupera lista partite future da cache
        TTL: 24 ore - ultra-conservativo per quota API (1 call/giorno)
        Budget: 30 calls/mese (94% risparmio su 500 quota)

        Returns:
            Dict con lista partite o None
        """
        key = "upcoming_matches:latest"
        return self.get(key)

    def set_upcoming_matches(self, matches_data: Dict) -> bool:
        """
        Salva lista partite future in cache

        Args:
            matches_data: Response completo API upcoming_matches

        Returns:
            True se salvato
        """
        key = "upcoming_matches:latest"
        ttl = 86400  # 24 ore - 1 call/giorno = 30 calls/mese (470 calls risparmiate!)
        return self.set(key, matches_data, ttl)

    def cache_dataset_info(self) -> Optional[Dict]:
        """
        Recupera info dataset da cache
        TTL: 24 ore (cambia solo con aggiornamenti)

        Returns:
            Dict con info dataset o None
        """
        key = "dataset:info"
        return self.get(key)

    def set_dataset_info(self, info_data: Dict) -> bool:
        """
        Salva info dataset in cache

        Args:
            info_data: Informazioni dataset

        Returns:
            True se salvato
        """
        key = "dataset:info"
        ttl = 86400  # 24 ore
        return self.set(key, info_data, ttl)

    def invalidate_predictions(self) -> int:
        """
        Invalida tutte le predizioni ML (es: dopo retraining)

        Returns:
            Numero chiavi eliminate
        """
        logger.info("🔄 Invalidazione cache predictions dopo retraining")
        return self.clear_pattern("predictions:*")

    def invalidate_all(self) -> bool:
        """
        Svuota completamente la cache

        Returns:
            True se completato
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            logger.info("🗑️ Cache completamente svuotata")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Errore flush cache: {e}")
            return False


# Singleton instance globale
_cache_manager_instance: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Ottiene istanza singleton CacheManager

    Returns:
        Istanza CacheManager globale
    """
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    return _cache_manager_instance
