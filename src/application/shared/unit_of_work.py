"""工作单元接口。

工作单元（Unit of Work）管理一个业务用例中的事务边界，
确保多个仓储操作在同一个事务中完成。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from src.domain.audit.repository import AuditLogRepository, LoginLogRepository
from src.domain.user.repository import UserRepository, RoleRepository, PermissionRepository, RolePermissionRepository


class UnitOfWork(ABC):
    """工作单元接口。

    使用方式（async with 语句）：
        async with unit_of_work as uow:
            await uow.user_repo.save(user)
            # 退出时自动 commit（无异常）或 rollback（有异常）
    """

    @property
    @abstractmethod
    def user_repo(self) -> UserRepository:
        """用户仓储。"""

    @property
    @abstractmethod
    def role_repo(self) -> RoleRepository:
        """角色仓储。"""

    @property
    @abstractmethod
    def permission_repo(self) -> PermissionRepository:
        """权限仓储。"""

    @property
    @abstractmethod
    def audit_repo(self) -> AuditLogRepository:
        """审计日志仓储。"""

    @property
    @abstractmethod
    def login_log_repo(self) -> LoginLogRepository:
        """登录日志仓储。"""

    @property
    @abstractmethod
    def role_permission_repo(self) -> RolePermissionRepository:
        """角色-权限关联仓储。"""

    @abstractmethod
    async def __aenter__(self) -> UnitOfWork:
        """进入工作单元上下文。"""

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """退出工作单元上下文。

        无异常时自动 commit，有异常时自动 rollback。
        """

    @abstractmethod
    async def commit(self) -> None:
        """显式提交事务。"""

    @abstractmethod
    async def rollback(self) -> None:
        """显式回滚事务。"""
