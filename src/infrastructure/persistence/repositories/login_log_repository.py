"""登录日志仓储实现。"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.audit.login_log import LoginLog
from src.domain.audit.repository import LoginLogRepository
from src.infrastructure.persistence.orm.audit_mapping import LoginLogTable


class SqlLoginLogRepository(LoginLogRepository):
    """SQLAlchemy 登录日志仓储实现（异步）。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, id: int) -> LoginLog | None:
        """根据 ID 查找登录日志。"""
        row = await self._session.get(LoginLogTable, id)
        return self._to_domain(row) if row else None

    async def find_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[LoginLog], int]:
        """按用户 ID 查找登录日志（分页）。"""
        conditions = [LoginLogTable.user_id == user_id]
        count_stmt = select(func.count()).select_from(
            select(LoginLogTable).where(*conditions).subquery()
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(LoginLogTable)
            .where(*conditions)
            .order_by(LoginLogTable.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = list((await self._session.execute(stmt)).scalars().all())
        return [self._to_domain(r) for r in rows], total

    async def search(
        self,
        keyword: str | None = None,
        status: str | None = None,
        user_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[LoginLog], int]:
        """按条件搜索登录日志（分页）。"""
        conditions: list = []
        if keyword:
            like = f"%{keyword}%"
            conditions.append(LoginLogTable.ip_address.like(like))
        if status:
            conditions.append(LoginLogTable.status == status)
        if user_id is not None:
            conditions.append(LoginLogTable.user_id == user_id)

        count_stmt = select(func.count()).select_from(
            select(LoginLogTable).where(*conditions).subquery()
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(LoginLogTable)
            .where(*conditions)
            .order_by(LoginLogTable.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = list((await self._session.execute(stmt)).scalars().all())
        return [self._to_domain(r) for r in rows], total

    async def save(self, aggregate: LoginLog) -> None:
        """保存登录日志（追加）。"""
        orm = self._to_orm(aggregate)
        self._session.add(orm)
        await self._session.flush()
        aggregate.id = orm.id

    async def delete(self, id: int) -> bool:
        """物理删除登录日志。"""
        row = await self._session.get(LoginLogTable, id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True

    @staticmethod
    def _to_domain(row: LoginLogTable) -> LoginLog:
        """ORM → 领域模型。"""
        return LoginLog(
            id=row.id,
            user_id=row.user_id,
            login_type=row.login_type,
            status=row.status,
            ip_address=row.ip_address,
            created_at=row.created_at,
        )

    @staticmethod
    def _to_orm(log: LoginLog) -> LoginLogTable:
        """领域模型 → ORM。"""
        return LoginLogTable(
            user_id=log.user_id,
            login_type=log.login_type,
            status=log.status,
            ip_address=log.ip_address,
        )
