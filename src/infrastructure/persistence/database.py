"""数据库连接管理。

提供 SQLAlchemy 引擎、会话工厂和 Base 声明。
"""

from __future__ import annotations

from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类。"""
    pass


class DatabaseProvider:
    """数据库提供者。"""

    def __init__(self, url: str) -> None:
        self._engine = create_engine(url, echo=False, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def engine(self):
        return self._engine

    def get_session_factory(self) -> sessionmaker:
        return self._session_factory

    def close(self) -> None:
        self._engine.dispose()


@lru_cache(maxsize=1)
def get_database_provider() -> DatabaseProvider:
    """获取数据库提供者实例（缓存）。"""
    from src.infrastructure.config.settings import get_settings

    settings = get_settings()
    return DatabaseProvider(url=settings.database_url)


def get_session() -> Generator[Session, None, None]:
    """获取数据库会话（用于 FastAPI DI）。"""
    session_factory = get_database_provider().get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
