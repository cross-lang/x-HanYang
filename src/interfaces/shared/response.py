"""统一响应格式。"""

from __future__ import annotations

from starlette.requests import Request


def success_response(data: object, request: Request, code: int = 200) -> dict[str, object]:
    """构造成功响应。

    Args:
        data: 响应数据
        request: HTTP 请求（用于获取 request_id）
        code: 业务状态码

    Returns:
        dict[str, object]: 统一格式的响应体
    """
    request_id = getattr(request.state, "request_id", None)
    return {
        "code": code,
        "message": "success",
        "data": data,
        "request_id": request_id,
    }


def error_response(message: str, code: int = 400, data: object = None) -> dict[str, object]:
    """构造错误响应。

    Args:
        message: 错误消息
        code: 业务状态码
        data: 附加数据

    Returns:
        dict[str, object]: 统一格式的错误响应体
    """
    return {
        "code": code,
        "message": message,
        "data": data,
    }
