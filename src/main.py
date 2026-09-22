#!/usr/bin/env python3
"""
应用入口模块

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

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interfaces.http.router import api_router
from src.interfaces.http.middleware import (
    ExceptionHandlingMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from src.interfaces.http.exception_handlers import register_exception_handlers
from src.infrastructure.config.settings import get_settings
from src.shared.logger import logger

APP_NAME = "汉阳（HanYang）"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "一个基于 DDD 架构的 FastAPI 生产级 Python Web 项目"

_has_db = False
_has_redis = False


def _check_infrastructure():
    """检查基础设施可用性。"""
    global _has_db, _has_redis
    settings = get_settings()
    if settings.database_url:
        _has_db = True
    if settings.redis_url:
        _has_redis = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。

    启动时初始化数据库和缓存连接，关闭时释放资源。
    """
    _check_infrastructure()
    settings = get_settings()

    logger.info(f"{APP_NAME} v{APP_VERSION} starting up...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.app_debug}")

    if _has_db:
        try:
            from src.infrastructure.persistence.database import get_database_provider

            db = get_database_provider()
            from src.infrastructure.persistence.database import Base

            # 导入 ORM 映射以注册表
            import src.infrastructure.persistence.orm.user_mapping  # noqa: F401
            import src.infrastructure.persistence.orm.audit_mapping  # noqa: F401

            Base.metadata.create_all(bind=db.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.warning(f"Database initialization skipped: {e}")
    else:
        logger.info("Database URL not configured, database features disabled")

    if _has_redis:
        try:
            from src.infrastructure.external.cache_provider import get_cache_provider

            get_cache_provider()
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis initialization skipped: {e}")

    yield

    logger.info(f"{APP_NAME} shutting down...")

    if _has_db:
        try:
            from src.infrastructure.persistence.database import get_database_provider

            get_database_provider().close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.warning(f"Error closing database: {e}")

    if _has_redis:
        try:
            from src.infrastructure.external.cache_provider import get_cache_provider

            get_cache_provider().close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis: {e}")


def create_app() -> FastAPI:
    """应用工厂函数。

    创建并配置 FastAPI 应用实例：
        1. 注册中间件（异常兜底 → 请求日志 → 请求 ID → CORS）
        2. 注册领域异常 → HTTP 状态码映射
        3. 挂载 API 路由
    """
    settings = get_settings()

    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 中间件顺序：后注册的在外层
    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # CORS（最后注册 → 最外层）
    cors_origins = settings.cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials="*" not in cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册领域异常处理器
    register_exception_handlers(app)

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
        prog="汉阳（HanYang）",
        description="一个基于 DDD 架构的 FastAPI 生产级 Web 应用框架",
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
