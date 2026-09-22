"""HTTP 中间件。"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.shared.logger import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求 ID 中间件 — 为每个请求分配唯一标识。"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:16])
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件 — 记录请求耗时。"""

    async def dispatch(self, request: Request, call_next):
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

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"未捕获异常: {e}")
            from starlette.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={"code": 500, "message": "服务器内部错误", "data": None},
            )
