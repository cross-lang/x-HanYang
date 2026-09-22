"""审计日志仓储接口。"""

from __future__ import annotations

from abc import abstractmethod

from src.domain.audit.audit_log import AuditLog
from src.domain.audit.login_log import LoginLog
from src.domain.shared.repository import Repository


class AuditLogRepository(Repository[AuditLog]):
    """审计日志仓储接口。"""

    @abstractmethod
    async def find_by_entity(
        self, entity_type: str, entity_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[AuditLog], int]:
        """按实体查找审计日志（分页）。

        Args:
            entity_type: 实体类型
            entity_id: 实体 ID
            skip: 偏移量
            limit: 每页数量

        Returns:
            tuple[list[AuditLog], int]: (日志列表, 总数)
        """


class LoginLogRepository(Repository[LoginLog]):
    """登录日志仓储接口。"""

    @abstractmethod
    async def find_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[LoginLog], int]:
        """按用户 ID 查找登录日志（分页）。

        Args:
            user_id: 用户 ID
            skip: 偏移量
            limit: 每页数量

        Returns:
            tuple[list[LoginLog], int]: (日志列表, 总数)
        """

    @abstractmethod
    async def search(
        self,
        keyword: str | None = None,
        status: str | None = None,
        user_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[LoginLog], int]:
        """按条件搜索登录日志（分页）。

        Args:
            keyword: 关键字（匹配 IP 地址）
            status: 登录状态过滤（success、failed）
            user_id: 用户 ID 过滤
            skip: 偏移量
            limit: 每页数量

        Returns:
            tuple[list[LoginLog], int]: (日志列表, 总数)
        """
