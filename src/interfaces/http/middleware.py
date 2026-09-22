"""HTTP 中间件。"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from src.constants.http import HEADER_REQUEST_ID
from src.constants.messages import MSG_INTERNAL_SERVER_ERROR
from src.shared.logger import logger

_REQUEST_ID_LENGTH: int = 16


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求 ID 中间件 — 为每个请求分配唯一标识。"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """为请求分配唯一标识。

        Args:
            request: HTTP 请求
            call_next: 下一个中间件

        Returns:
            Response: HTTP 响应
        """
        request_id = request.headers.get(HEADER_REQUEST_ID, uuid.uuid4().hex[:_REQUEST_ID_LENGTH])
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers[HEADER_REQUEST_ID] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件 — 记录请求耗时。"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """记录请求耗时。

        Args:
            request: HTTP 请求
            call_next: 下一个中间件

        Returns:
            Response: HTTP 响应
        """
        start = time.time()
        response: Response = await call_next(request)
        duration = (time.time() - start) * 1000
        request_id = getattr(request.state, "request_id", "-")
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"-> {response.status_code} ({duration:.1f}ms)"
        )
        return response


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """全局异常兜底中间件。"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """捕获未处理异常并返回 500 响应。

        Args:
            request: HTTP 请求
            call_next: 下一个中间件

        Returns:
            Response: HTTP 响应
        """
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"未捕获异常: {e}")
            return JSONResponse(
                status_code=500,
                content={"code": 500, "message": MSG_INTERNAL_SERVER_ERROR, "data": None},
            )
