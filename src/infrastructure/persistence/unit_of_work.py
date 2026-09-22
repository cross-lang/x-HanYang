"""工作单元 SQLAlchemy 异步实现。

管理事务边界，确保多个仓储操作在同一个事务中完成。
退出 async with 时：无异常自动 commit，有异常自动 rollback。
"""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.shared.unit_of_work import UnitOfWork
from src.domain.audit.repository import AuditLogRepository, LoginLogRepository
from src.domain.user.repository import UserRepository, RoleRepository, PermissionRepository
from src.infrastructure.persistence.repositories.user_repository import SqlUserRepository
from src.infrastructure.persistence.repositories.role_repository import SqlRoleRepository
from src.infrastructure.persistence.repositories.permission_repository import SqlPermissionRepository
from src.infrastructure.persistence.repositories.audit_repository import SqlAuditLogRepository
from src.infrastructure.persistence.repositories.login_log_repository import SqlLoginLogRepository


class SqlUnitOfWork(UnitOfWork):
    """SQLAlchemy 工作单元异步实现。

    使用方式：
        async with SqlUnitOfWork(session) as uow:
            await uow.user_repo.save(user)
            # 退出时自动 commit
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo: UserRepository | None = None
        self._role_repo: RoleRepository | None = None
        self._permission_repo: PermissionRepository | None = None
        self._audit_repo: AuditLogRepository | None = None
        self._login_log_repo: LoginLogRepository | None = None

    @property
    def user_repo(self) -> UserRepository:
        """用户仓储（共享同一 Session）。"""
        if self._user_repo is None:
            self._user_repo = SqlUserRepository(session=self._session)
        return self._user_repo

    @property
    def role_repo(self) -> RoleRepository:
        """角色仓储。"""
        if self._role_repo is None:
            self._role_repo = SqlRoleRepository(session=self._session)
        return self._role_repo

    @property
    def permission_repo(self) -> PermissionRepository:
        """权限仓储。"""
        if self._permission_repo is None:
            self._permission_repo = SqlPermissionRepository(session=self._session)
        return self._permission_repo

    @property
    def audit_repo(self) -> AuditLogRepository:
        """审计日志仓储。"""
        if self._audit_repo is None:
            self._audit_repo = SqlAuditLogRepository(session=self._session)
        return self._audit_repo

    @property
    def login_log_repo(self) -> LoginLogRepository:
        """登录日志仓储。"""
        if self._login_log_repo is None:
            self._login_log_repo = SqlLoginLogRepository(session=self._session)
        return self._login_log_repo

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
        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.close()

    async def commit(self) -> None:
        """显式提交事务。"""
        await self._session.commit()

    async def rollback(self) -> None:
        """显式回滚事务。"""
        await self._session.rollback()
