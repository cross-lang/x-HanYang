"""通用工具函数。"""

from __future__ import annotations

from starlette.requests import Request

from src.constants.http import HEADER_FORWARDED_FOR, HEADER_REAL_IP


def get_client_ip(request: Request) -> str | None:
    """获取客户端真实 IP。

    优先从 X-Forwarded-For 和 X-Real-IP 头获取。

    Args:
        request: HTTP 请求对象

    Returns:
        str | None: 客户端 IP 地址，无法获取时返回 None
    """
    forwarded = request.headers.get(HEADER_FORWARDED_FOR)
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get(HEADER_REAL_IP)
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else None
