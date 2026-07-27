"""
Optional Redis wrapper. If Redis is unreachable or not installed,
every method degrades to a no-op / cache-miss instead of raising.
"""
import json
import logging
import os

try:
    import redis
    from redis.exceptions import RedisError
except Exception:  # pragma: no cover - optional dependency fallback
    redis = None

    class RedisError(Exception):
        pass


logger = logging.getLogger(__name__)


class CacheClient:
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.environ.get('REDIS_URL')
        self._client = None
        self._available = False
        self._connect()

    def _connect(self):
        if not self.redis_url:
            logger.info("REDIS_URL not set - caching disabled, running without Redis.")
            return
        if redis is None:
            logger.info("redis package not installed - caching disabled.")
            return
        try:
            client = redis.from_url(
                self.redis_url,
                socket_connect_timeout=2,
                socket_timeout=2,
                decode_responses=True,
            )
            client.ping()
            self._client = client
            self._available = True
            logger.info("Connected to Redis - caching enabled.")
        except RedisError as e:
            logger.warning(f"Redis unavailable ({e}) - falling back to no-cache mode.")
            self._client = None
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def get(self, key: str):
        if not self._available:
            return None
        try:
            value = self._client.get(key)
            return json.loads(value) if value is not None else None
        except RedisError as e:
            logger.warning(f"Redis GET failed for key={key}: {e}")
            return None

    def set(self, key: str, value, ttl_seconds: int = 3600):
        if not self._available:
            return False
        try:
            self._client.set(key, json.dumps(value), ex=ttl_seconds)
            return True
        except RedisError as e:
            logger.warning(f"Redis SET failed for key={key}: {e}")
            return False

    def delete(self, key: str):
        if not self._available:
            return False
        try:
            self._client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Redis DELETE failed for key={key}: {e}")
            return False


cache = CacheClient()