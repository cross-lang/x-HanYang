"""缓存提供者。

基础设施层定义接口契约，业务层仅依赖抽象接口。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

import redis.asyncio as aioredis

from src.shared.logger import logger


class CacheProvider(ABC):
    """缓存提供者接口。

    所有缓存实现必须继承此类，便于替换和单元测试 Mock。
    """

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """获取缓存值。

        Args:
            key: 缓存键

        Returns:
            str | None: 缓存值，不存在时返回 None
        """

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """设置缓存值。

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """删除缓存。

        Args:
            key: 缓存键
        """

    @abstractmethod
    async def atomic_incr(self, key: str, ttl: int | None = None) -> int:
        """原子递增。

        Args:
            key: 缓存键
            ttl: 首次递增时设置的过期时间（秒）

        Returns:
            int: 递增后的值
        """

    @abstractmethod
    async def close(self) -> None:
        """关闭连接。"""


class RedisCacheProvider(CacheProvider):
    """Redis 缓存提供者异步实现。"""

    def __init__(self, url: str) -> None:
        self._client = aioredis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        """获取缓存值。"""
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.warning(f"Redis GET 失败: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """设置缓存值。"""
        try:
            if ttl:
                await self._client.setex(key, ttl, value)
            else:
                await self._client.set(key, value)
        except Exception as e:
            logger.warning(f"Redis SET 失败: {e}")

    async def delete(self, key: str) -> None:
        """删除缓存。"""
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE 失败: {e}")

    async def atomic_incr(self, key: str, ttl: int | None = None) -> int:
        """原子递增。"""
        try:
            value = await self._client.incr(key)
            if ttl and value == 1:
                await self._client.expire(key, ttl)
            return value
        except Exception as e:
            logger.warning(f"Redis INCR 失败: {e}")
            return 0

    async def close(self) -> None:
        """关闭连接。"""
        await self._client.aclose()


@lru_cache(maxsize=1)
def get_cache_provider() -> CacheProvider:
    """获取缓存提供者实例（缓存）。

    Returns:
        CacheProvider: 缓存提供者实例

    Raises:
        ValueError: Redis URL 未配置时抛出
    """
    from src.infrastructure.config.settings import get_settings

    settings = get_settings()
    if not settings.redis_url:
        raise ValueError("REDIS_URL 未配置，无法创建缓存提供者")
    return RedisCacheProvider(url=settings.redis_url)
