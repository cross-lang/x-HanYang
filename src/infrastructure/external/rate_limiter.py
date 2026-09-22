"""限流配置。

基于 slowapi 的速率限制中间件配置。
"""

from __future__ import annotations

from functools import lru_cache

from slowapi import Limiter
from slowapi.util import get_remote_address


@lru_cache(maxsize=1)
def get_limiter() -> Limiter:
    """获取速率限制器实例（缓存）。

    Returns:
        Limiter: 速率限制器
    """
    return Limiter(key_func=get_remote_address)
