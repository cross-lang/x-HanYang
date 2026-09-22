"""HTTP 异常处理器。

将领域层异常转换为 HTTP 响应。
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.shared.domain_exception import (
    DomainException,
    EntityNotFoundException,
    ConflictException,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
)
from src.shared.logger import logger


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。

    Args:
        app: FastAPI 应用实例
    """

    @app.exception_handler(EntityNotFoundException)
    async def not_found_handler(request: Request, exc: EntityNotFoundException) -> JSONResponse:
        """实体未找到异常处理。"""
        return JSONResponse(status_code=404, content={"code": 404, "message": exc.message, "data": None})

    @app.exception_handler(ConflictException)
    async def conflict_handler(request: Request, exc: ConflictException) -> JSONResponse:
        """业务冲突异常处理。"""
        return JSONResponse(status_code=409, content={"code": 409, "message": exc.message, "data": None})

    @app.exception_handler(AuthenticationException)
    async def auth_handler(request: Request, exc: AuthenticationException) -> JSONResponse:
        """认证失败异常处理。"""
        return JSONResponse(status_code=401, content={"code": 401, "message": exc.message, "data": None})

    @app.exception_handler(AuthorizationException)
    async def forbidden_handler(request: Request, exc: AuthorizationException) -> JSONResponse:
        """授权失败异常处理。"""
        return JSONResponse(status_code=403, content={"code": 403, "message": exc.message, "data": None})

    @app.exception_handler(ValidationException)
    async def validation_handler(request: Request, exc: ValidationException) -> JSONResponse:
        """业务规则校验异常处理。"""
        return JSONResponse(status_code=422, content={"code": 422, "message": exc.message, "data": None})

    @app.exception_handler(DomainException)
    async def domain_handler(request: Request, exc: DomainException) -> JSONResponse:
        """通用领域异常处理。"""
        return JSONResponse(status_code=400, content={"code": 400, "message": exc.message, "data": None})
