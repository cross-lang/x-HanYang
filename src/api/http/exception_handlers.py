"""HTTP 异常处理器。

将领域层异常和技术层异常转换为统一格式的 HTTP 响应。
所有错误响应包含 request_id 以便追踪。
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.shared.domain_exception import (
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    DomainException,
    EntityNotFoundException,
    ValidationException,
)
from src.shared.exceptions import FrameworkException
from src.shared.logger import logger


def _error_body(request: Request, code: int, message: str) -> dict:
    """构建统一错误响应体。"""
    return {
        "code": code,
        "message": message,
        "data": None,
        "request_id": getattr(request.state, "request_id", None),
    }


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。

    Args:
        app: FastAPI 应用实例
    """

    @app.exception_handler(EntityNotFoundException)
    async def not_found_handler(request: Request, exc: EntityNotFoundException) -> JSONResponse:
        """实体未找到异常处理。"""
        return JSONResponse(status_code=404, content=_error_body(request, 404, exc.message))

    @app.exception_handler(ConflictException)
    async def conflict_handler(request: Request, exc: ConflictException) -> JSONResponse:
        """业务冲突异常处理。"""
        return JSONResponse(status_code=409, content=_error_body(request, 409, exc.message))

    @app.exception_handler(AuthenticationException)
    async def auth_handler(request: Request, exc: AuthenticationException) -> JSONResponse:
        """认证失败异常处理。"""
        return JSONResponse(status_code=401, content=_error_body(request, 401, exc.message))

    @app.exception_handler(AuthorizationException)
    async def forbidden_handler(request: Request, exc: AuthorizationException) -> JSONResponse:
        """授权失败异常处理。"""
        return JSONResponse(status_code=403, content=_error_body(request, 403, exc.message))

    @app.exception_handler(ValidationException)
    async def validation_handler(request: Request, exc: ValidationException) -> JSONResponse:
        """业务规则校验异常处理。"""
        return JSONResponse(status_code=422, content=_error_body(request, 422, exc.message))

    @app.exception_handler(DomainException)
    async def domain_handler(request: Request, exc: DomainException) -> JSONResponse:
        """通用领域异常处理。"""
        return JSONResponse(status_code=400, content=_error_body(request, 400, exc.message))

    @app.exception_handler(FrameworkException)
    async def framework_handler(request: Request, exc: FrameworkException) -> JSONResponse:
        """框架层异常处理（数据库、缓存、外部服务等）。"""
        logger.error("框架异常: %s", exc.message, exc_info=True)
        return JSONResponse(status_code=exc.code, content=_error_body(request, exc.code, exc.message))

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        """未捕获异常兜底处理。"""
        logger.error("未捕获异常: %s", str(exc), exc_info=True)
        return JSONResponse(status_code=500, content=_error_body(request, 500, "服务器内部错误"))
