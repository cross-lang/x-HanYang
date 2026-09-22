"""工作单元 SQLAlchemy 实现。

管理事务边界，确保多个仓储操作在同一个事务中完成。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from src.application.shared.unit_of_work import UnitOfWork
from src.domain.user.repository import UserRepository
from src.infrastructure.persistence.repositories.user_repository import SqlUserRepository


class SqlUnitOfWork(UnitOfWork):
    """SQLAlchemy 工作单元实现。

    使用方式：
        with SqlUnitOfWork(session_factory) as uow:
            uow.user_repo.save(user)
            uow.commit()
    """

    def __init__(self, session: Session) -> None:
        self._session = session
        self._user_repo: UserRepository | None = None

    @property
    def user_repo(self) -> UserRepository:
        """用户仓储（共享同一 Session）。"""
        if self._user_repo is None:
            self._user_repo = SqlUserRepository(session=self._session)
        return self._user_repo

    @property
    def session(self) -> Session:
        """底层 Session（供需要直接访问的场景）。"""
        return self._session

    def __enter__(self) -> SqlUnitOfWork:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
