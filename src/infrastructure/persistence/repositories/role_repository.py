"""角色仓储实现。"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.role import Role, RoleType, RoleStatus
from src.domain.user.repository import RoleRepository
from src.infrastructure.persistence.orm.user_mapping import RoleTable


class SqlRoleRepository(RoleRepository):
    """SQLAlchemy 角色仓储实现（异步）。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, id: int) -> Role | None:
        """根据 ID 查找角色（排除软删除）。"""
        stmt = select(RoleTable).where(RoleTable.id == id, RoleTable.deleted_at.is_(None))
        row = (await self._session.execute(stmt)).scalars().first()
        return self._to_domain(row) if row else None

    async def find_by_role_code(self, role_code: str) -> Role | None:
        """根据角色编码查找角色。"""
        stmt = select(RoleTable).where(RoleTable.role_code == role_code, RoleTable.deleted_at.is_(None))
        row = (await self._session.execute(stmt)).scalars().first()
        return self._to_domain(row) if row else None

    async def search(
        self, keyword: str | None = None, status: str | None = None, skip: int = 0, limit: int = 20
    ) -> tuple[list[Role], int]:
        """按条件搜索角色（分页）。"""
        conditions = [RoleTable.deleted_at.is_(None)]
        if keyword:
            like = f"%{keyword}%"
            conditions.append((RoleTable.role_name.like(like)) | (RoleTable.role_code.like(like)))
        if status:
            conditions.append(RoleTable.status == status)

        count_stmt = select(func.count()).select_from(select(RoleTable).where(*conditions).subquery())
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = select(RoleTable).where(*conditions).offset(skip).limit(limit)
        rows = list((await self._session.execute(stmt)).scalars().all())
        return [self._to_domain(r) for r in rows], total

    async def save(self, role: Role) -> None:
        """保存角色（新增或更新）。"""
        if role.id and role.id > 0:
            existing = await self._session.get(RoleTable, role.id)
            if existing:
                self._update_orm(existing, role)
        else:
            orm = self._to_orm(role)
            self._session.add(orm)
            await self._session.flush()
            role.id = orm.id

    async def delete(self, id: int) -> bool:
        """软删除角色。"""
        row = await self._session.get(RoleTable, id)
        if row is None:
            return False
        row.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()
        return True

    @staticmethod
    def _to_domain(row: RoleTable) -> Role:
        """ORM → 领域模型。"""
        return Role(
            id=row.id,
            role_name=row.role_name,
            role_code=row.role_code,
            description=row.description,
            role_type=RoleType(row.role_type) if row.role_type else RoleType.CUSTOM,
            status=RoleStatus(row.status) if row.status else RoleStatus.ENABLED,
        )

    @staticmethod
    def _to_orm(role: Role) -> RoleTable:
        """领域模型 → ORM。"""
        return RoleTable(
            role_name=role.role_name,
            role_code=role.role_code,
            description=role.description,
            role_type=role.role_type.value,
            status=role.status.value,
        )

    @staticmethod
    def _update_orm(row: RoleTable, role: Role) -> None:
        """同步领域模型变更到 ORM。"""
        row.role_name = role.role_name
        row.role_code = role.role_code
        row.description = role.description
        row.role_type = role.role_type.value
        row.status = role.status.value
