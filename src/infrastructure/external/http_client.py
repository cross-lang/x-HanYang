"""HTTP 客户端抽象。

提供 HTTP 请求的抽象接口和 httpx 异步实现。
支持重试、超时、JSON 自动解析。
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any

import httpx

from src.core.logger import logger


class HttpProvider(ABC):
    """HTTP 客户端接口。

    所有外部 HTTP 调用应通过此接口，便于 Mock 测试。
    """

    @abstractmethod
    async def get(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 GET 请求。

        Args:
            url: 请求 URL
            params: 查询参数
            headers: 请求头

        Returns:
            dict[str, Any]: 响应 JSON
        """

    @abstractmethod
    async def post(self, url: str, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 POST 请求。

        Args:
            url: 请求 URL
            json: JSON 请求体
            headers: 请求头

        Returns:
            dict[str, Any]: 响应 JSON
        """

    @abstractmethod
    async def put(self, url: str, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 PUT 请求。

        Args:
            url: 请求 URL
            json: JSON 请求体
            headers: 请求头

        Returns:
            dict[str, Any]: 响应 JSON
        """

    @abstractmethod
    async def delete(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 DELETE 请求。

        Args:
            url: 请求 URL
            headers: 请求头

        Returns:
            dict[str, Any]: 响应 JSON
        """

    @abstractmethod
    async def close(self) -> None:
        """关闭客户端连接。"""


class HttpxProvider(HttpProvider):
    """基于 httpx 的异步 HTTP 客户端实现。

    支持指数退避重试和可配置超时。
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)

    async def get(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 GET 请求。"""
        return await self._request("GET", url, params=params, headers=headers)

    async def post(self, url: str, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 POST 请求。"""
        return await self._request("POST", url, json=json, headers=headers)

    async def put(self, url: str, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 PUT 请求。"""
        return await self._request("PUT", url, json=json, headers=headers)

    async def delete(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """发送 DELETE 请求。"""
        return await self._request("DELETE", url, headers=headers)

    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        """发送 HTTP 请求（带重试）。

        Args:
            method: HTTP 方法
            url: 请求 URL
            **kwargs: 传递给 httpx 的参数

        Returns:
            dict[str, Any]: 响应 JSON

        Raises:
            httpx.HTTPStatusError: 请求失败且重试耗尽
        """
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"HTTP {method} {url} 失败 (尝试 {attempt + 1}/{self._max_retries}): {e}, {wait}s 后重试")
                    await asyncio.sleep(wait)
        raise last_error  # type: ignore[misc]

    async def close(self) -> None:
        """关闭客户端连接。"""
        await self._client.aclose()


@lru_cache(maxsize=1)
def get_http_provider() -> HttpProvider:
    """获取 HTTP 客户端实例（缓存）。

    Returns:
        HttpProvider: HTTP 客户端实例
    """
    from src.core.config import get_settings

    settings = get_settings()
    return HttpxProvider(timeout=settings.http_timeout, max_retries=settings.http_max_retries)
