"""审计日志仓储接口。"""

from __future__ import annotations

from abc import abstractmethod

from src.domain.audit.audit_log import AuditLog
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
