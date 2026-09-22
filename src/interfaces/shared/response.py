"""统一响应格式。"""

from __future__ import annotations

from typing import Any

from starlette.requests import Request


def success_response(data: Any, request: Request, code: int = 200) -> dict:
    """构造成功响应。

    Args:
        data: 响应数据
        request: HTTP 请求（用于获取 request_id）
        code: 业务状态码

    Returns:
        dict: 统一格式的响应体
    """
    request_id = getattr(request.state, "request_id", None)
    return {
        "code": code,
        "message": "success",
        "data": data,
        "request_id": request_id,
    }


def error_response(message: str, code: int = 400, data: Any = None) -> dict:
    """构造错误响应。"""
    return {
        "code": code,
        "message": message,
        "data": data,
    }
