"""通用工具函数。"""

from __future__ import annotations

from starlette.requests import Request


def get_client_ip(request: Request) -> str | None:
    """获取客户端真实 IP。

    优先从 X-Forwarded-For 和 X-Real-IP 头获取。
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else None
