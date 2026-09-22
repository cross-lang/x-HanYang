"""数据库连接管理。

提供 SQLAlchemy 异步引擎、会话工厂和 Base 声明。
采用异步驱动，避免阻塞 FastAPI 事件循环。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类。"""


class DatabaseProvider:
    """数据库提供者（异步）。

    Attributes:
        _engine: SQLAlchemy 异步引擎
        _session_factory: 异步会话工厂
    """

    def __init__(self, url: str) -> None:
        self._engine = create_async_engine(url, echo=False, pool_pre_ping=True)
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def engine(self) -> "AsyncEngine":
        """SQLAlchemy 异步引擎。"""
        return self._engine

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """获取异步会话工厂。"""
        return self._session_factory

    async def close(self) -> None:
        """释放数据库连接池。"""
        await self._engine.dispose()


@lru_cache(maxsize=1)
def get_database_provider() -> DatabaseProvider:
    """获取数据库提供者实例（缓存）。"""
    from src.infrastructure.config.settings import get_settings

    settings = get_settings()
    return DatabaseProvider(url=settings.database_url)


async def get_session() -> AsyncIterator[AsyncSession]:
    """获取异步数据库会话（用于 FastAPI 依赖注入）。

    Yields:
        AsyncSession: 数据库会话

    Raises:
        Exception: 会话操作异常（已回滚后继续抛出）
    """
    session_factory = get_database_provider().get_session_factory()
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
