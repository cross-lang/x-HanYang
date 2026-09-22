"""审计日志仓储实现。"""

from __future__ import annotations

import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.audit.audit_log import AuditLog
from src.domain.audit.repository import AuditLogRepository
from src.infrastructure.persistence.orm.audit_mapping import AuditLogTable


class SqlAuditLogRepository(AuditLogRepository):
    """SQLAlchemy 审计日志仓储实现（异步）。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, id: int) -> AuditLog | None:
        """根据 ID 查找审计日志。"""
        row = await self._session.get(AuditLogTable, id)
        return self._to_domain(row) if row else None

    async def find_by_entity(
        self, entity_type: str, entity_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[AuditLog], int]:
        """按实体查找审计日志（分页）。"""
        conditions = [AuditLogTable.entity_type == entity_type, AuditLogTable.entity_id == entity_id]
        count_stmt = select(func.count()).select_from(select(AuditLogTable).where(*conditions).subquery())
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(AuditLogTable)
            .where(*conditions)
            .order_by(AuditLogTable.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = list((await self._session.execute(stmt)).scalars().all())
        return [self._to_domain(r) for r in rows], total

    async def save(self, aggregate: AuditLog) -> None:
        """保存审计日志（追加）。"""
        orm = self._to_orm(aggregate)
        self._session.add(orm)
        await self._session.flush()
        aggregate.id = orm.id

    async def delete(self, id: int) -> bool:
        """物理删除审计日志。"""
        row = await self._session.get(AuditLogTable, id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True

    @staticmethod
    def _to_domain(row: AuditLogTable) -> AuditLog:
        """ORM → 领域模型。"""
        return AuditLog(
            id=row.id,
            entity_type=row.entity_type,
            entity_id=row.entity_id,
            action=row.action,
            operator_id=row.operator_id,
            operator_name=row.operator_name,
            before_data=json.loads(row.before_data) if row.before_data else None,
            after_data=json.loads(row.after_data) if row.after_data else None,
            ip_address=row.ip_address,
            remarks=row.remarks,
            created_at=row.created_at,
        )

    @staticmethod
    def _to_orm(log: AuditLog) -> AuditLogTable:
        """领域模型 → ORM。"""
        return AuditLogTable(
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action,
            operator_id=log.operator_id,
            operator_name=log.operator_name,
            before_data=json.dumps(log.before_data, ensure_ascii=False) if log.before_data else None,
            after_data=json.dumps(log.after_data, ensure_ascii=False) if log.after_data else None,
            ip_address=log.ip_address,
            remarks=log.remarks,
        )
