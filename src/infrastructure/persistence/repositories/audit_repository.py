"""审计日志仓储实现。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.audit.audit_log import AuditLog
from src.domain.audit.repository import AuditLogRepository
from src.infrastructure.persistence.orm.audit_mapping import AuditLogTable


class SqlAuditLogRepository(AuditLogRepository):
    """SQLAlchemy 审计日志仓储实现。"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, id: int) -> AuditLog | None:
        row = self._session.get(AuditLogTable, id)
        return self._to_domain(row) if row else None

    def find_by_entity(
        self, entity_type: str, entity_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[AuditLog], int]:
        from sqlalchemy import func

        conditions = [AuditLogTable.entity_type == entity_type, AuditLogTable.entity_id == entity_id]
        count_stmt = select(func.count()).select_from(select(AuditLogTable).where(*conditions).subquery())
        total = self._session.execute(count_stmt).scalar() or 0

        stmt = (
            select(AuditLogTable)
            .where(*conditions)
            .order_by(AuditLogTable.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = list(self._session.execute(stmt).scalars().all())
        return [self._to_domain(r) for r in rows], total

    def save(self, aggregate: AuditLog) -> None:
        orm = self._to_orm(aggregate)
        self._session.add(orm)
        self._session.flush()
        aggregate.id = orm.id

    def delete(self, id: int) -> bool:
        row = self._session.get(AuditLogTable, id)
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True

    @staticmethod
    def _to_domain(row: AuditLogTable) -> AuditLog:
        import json

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
        import json

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
