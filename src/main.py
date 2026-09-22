#!/usr/bin/env python3
"""应用入口模块。

本模块是 FastAPI 应用的核心入口，提供应用工厂函数和启动命令。
负责编排所有组件的初始化顺序：配置加载 → 中间件注册 →
异常处理器注册 → 路由挂载。

DDD 架构下的初始化顺序：
    1. 加载配置（infrastructure.config）
    2. 初始化数据库连接（infrastructure.persistence）
    3. 注册中间件（interfaces.http.middleware）
    4. 注册异常处理器（interfaces.http.exception_handlers）
    5. 挂载路由（interfaces.http.router）

Usage:
    # 启动服务
    uv run x-HanYang

    # 启用热重载（开发模式）
    uv run x-HanYang --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.constants.app import APP_NAME, APP_VERSION, APP_DESCRIPTION
from src.constants.http import DOCS_URL, REDOC_URL
from src.constants.messages import MSG_INTERNAL_SERVER_ERROR
from src.api.http.router import api_router
from src.api.http.middleware import (
    ExceptionHandlingMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from src.api.http.exception_handlers import register_exception_handlers
from src.infrastructure.config.settings import get_settings
from src.infrastructure.external.rate_limiter import get_limiter
from src.shared.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。

    启动时初始化数据库和缓存连接，关闭时释放资源。

    Args:
        app: FastAPI 应用实例
    """
    settings = get_settings()
    has_db = bool(settings.database_url)
    has_redis = bool(settings.redis_url)

    logger.info(f"{APP_NAME} v{APP_VERSION} starting up...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.app_debug}")

    if has_db:
        try:
            from src.infrastructure.persistence.database import get_database_provider, Base

            # 导入 ORM 映射以注册表
            import src.infrastructure.persistence.orm.user_mapping  # noqa: F401
            import src.infrastructure.persistence.orm.audit_mapping  # noqa: F401

            db = get_database_provider()
            async with db.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.warning(f"Database initialization skipped: {e}")
    else:
        logger.info("Database URL not configured, database features disabled")

    yield

    logger.info(f"{APP_NAME} shutting down...")

    if has_db:
        try:
            from src.infrastructure.persistence.database import get_database_provider

            await get_database_provider().close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.warning(f"Error closing database: {e}")

    if has_redis:
        try:
            from src.infrastructure.external.cache_provider import get_cache_provider

            await get_cache_provider().close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis: {e}")


def create_app() -> FastAPI:
    """应用工厂函数。

    创建并配置 FastAPI 应用实例：
        1. 注册中间件（异常兜底 → 请求日志 → 请求 ID → CORS）
        2. 注册领域异常 → HTTP 状态码映射
        3. 挂载 API 路由

    Returns:
        FastAPI: 应用实例
    """
    settings = get_settings()

    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        lifespan=lifespan,
        docs_url=DOCS_URL,
        redoc_url=REDOC_URL,
        openapi_url="/openapi.json" if settings.app_debug else None
    )

    # 限流器
    limiter: Limiter = get_limiter()
    app.state.limiter = limiter

    # 限流超限处理
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        """速率限制超限处理。"""
        return JSONResponse(
            status_code=429,
            content={"code": 429, "message": "请求过于频繁，请稍后重试", "data": None},
        )

    # 注册领域异常处理器
    register_exception_handlers(app)

    # 中间件顺序：后注册的在外层
    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials="*" not in settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载路由
    app.include_router(api_router)

    return app


app: FastAPI = create_app()


def main() -> None:
    """命令行启动入口（pyproject.toml 中的 entry point）。

    Usage:
        uv run x-HanYang                # 默认启动
        uv run x-HanYang --reload        # 热重载
        uv run x-HanYang --port 9000     # 自定义端口
        uv run x-HanYang -V              # 查看版本
    """
    import argparse

    settings = get_settings()

    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description=APP_DESCRIPTION,
    )
    parser.add_argument("-V", "--version", action="version", version=f"x-HanYang {APP_VERSION}")
    parser.add_argument("--host", default=settings.server_host, help=f"监听地址（默认 {settings.server_host}）")
    parser.add_argument("--port", type=int, default=settings.server_port, help=f"监听端口（默认 {settings.server_port}）")
    parser.add_argument("--reload", action="store_true", help="启用热重载（开发模式）")
    args = parser.parse_args()

    reload = args.reload or settings.app_debug

    logger.info(f"Starting {APP_NAME} v{APP_VERSION}...")
    logger.info(f"  Address: http://{args.host}:{args.port}")
    logger.info(f"  Reload:  {reload}")

    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=reload,
        workers=1 if reload else settings.server_workers,
    )


if __name__ == "__main__":
    main()
