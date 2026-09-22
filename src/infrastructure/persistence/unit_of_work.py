"""工作单元 SQLAlchemy 异步实现。

管理事务边界，确保多个仓储操作在同一个事务中完成。
"""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.shared.unit_of_work import UnitOfWork
from src.domain.user.repository import UserRepository
from src.infrastructure.persistence.repositories.user_repository import SqlUserRepository


class SqlUnitOfWork(UnitOfWork):
    """SQLAlchemy 工作单元异步实现。

    使用方式：
        async with SqlUnitOfWork(session) as uow:
            await uow.user_repo.save(user)
            await uow.commit()
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo: UserRepository | None = None

    @property
    def user_repo(self) -> UserRepository:
        """用户仓储（共享同一 Session）。"""
        if self._user_repo is None:
            self._user_repo = SqlUserRepository(session=self._session)
        return self._user_repo

    @property
    def session(self) -> AsyncSession:
        """底层 Session（供需要直接访问的场景）。"""
        return self._session

    async def __aenter__(self) -> SqlUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        """提交事务。"""
        await self._session.commit()

    async def rollback(self) -> None:
        """回滚事务。"""
        await self._session.rollback()
