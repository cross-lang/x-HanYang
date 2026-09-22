"""Redis 缓存提供者。"""

from __future__ import annotations

from functools import lru_cache

import redis

from src.shared.logger import logger


class CacheProvider:
    """Redis 缓存提供者。"""

    def __init__(self, url: str) -> None:
        self._client = redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> str | None:
        try:
            return self._client.get(key)
        except Exception as e:
            logger.warning(f"Redis GET 失败: {e}")
            return None

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        try:
            if ttl:
                self._client.setex(key, ttl, value)
            else:
                self._client.set(key, value)
        except Exception as e:
            logger.warning(f"Redis SET 失败: {e}")

    def delete(self, key: str) -> None:
        try:
            self._client.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE 失败: {e}")

    def atomic_incr(self, key: str, ttl: int | None = None) -> int:
        try:
            value = self._client.incr(key)
            if ttl and value == 1:
                self._client.expire(key, ttl)
            return value
        except Exception as e:
            logger.warning(f"Redis INCR 失败: {e}")
            return 0

    def close(self) -> None:
        self._client.close()


@lru_cache(maxsize=1)
def get_cache_provider() -> CacheProvider:
    """获取缓存提供者实例（缓存）。"""
    from src.infrastructure.config.settings import get_settings

    settings = get_settings()
    return CacheProvider(url=settings.redis_url)
