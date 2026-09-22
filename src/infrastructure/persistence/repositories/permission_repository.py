"""权限仓储实现。"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.permission import Permission
from src.domain.user.repository import PermissionRepository
from src.infrastructure.persistence.orm.user_mapping import PermissionTable


class SqlPermissionRepository(PermissionRepository):
    """SQLAlchemy 权限仓储实现（异步）。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, id: int) -> Permission | None:
        """根据 ID 查找权限。"""
        row = await self._session.get(PermissionTable, id)
        return self._to_domain(row) if row else None

    async def find_by_perm_code(self, perm_code: str) -> Permission | None:
        """根据权限编码查找权限。"""
        stmt = select(PermissionTable).where(PermissionTable.perm_code == perm_code)
        row = (await self._session.execute(stmt)).scalars().first()
        return self._to_domain(row) if row else None

    async def search(
        self, keyword: str | None = None, module: str | None = None, skip: int = 0, limit: int = 20
    ) -> tuple[list[Permission], int]:
        """按条件搜索权限（分页）。"""
        conditions = []
        if keyword:
            like = f"%{keyword}%"
            conditions.append((PermissionTable.perm_name.like(like)) | (PermissionTable.perm_code.like(like)))
        if module:
            conditions.append(PermissionTable.module == module)

        count_stmt = select(func.count()).select_from(select(PermissionTable).where(*conditions).subquery())
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = select(PermissionTable).where(*conditions).order_by(PermissionTable.sort_order).offset(skip).limit(limit)
        rows = list((await self._session.execute(stmt)).scalars().all())
        return [self._to_domain(r) for r in rows], total

    async def save(self, permission: Permission) -> None:
        """保存权限（新增或更新）。"""
        if permission.id and permission.id > 0:
            existing = await self._session.get(PermissionTable, permission.id)
            if existing:
                self._update_orm(existing, permission)
        else:
            orm = self._to_orm(permission)
            self._session.add(orm)
            await self._session.flush()
            permission.id = orm.id

    async def delete(self, id: int) -> bool:
        """物理删除权限。"""
        row = await self._session.get(PermissionTable, id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True

    @staticmethod
    def _to_domain(row: PermissionTable) -> Permission:
        """ORM → 领域模型。"""
        return Permission(
            id=row.id,
            perm_code=row.perm_code,
            perm_name=row.perm_name,
            module=row.module,
            operation=row.operation,
            description=row.description,
            sort_order=row.sort_order,
        )

    @staticmethod
    def _to_orm(permission: Permission) -> PermissionTable:
        """领域模型 → ORM。"""
        return PermissionTable(
            perm_code=permission.perm_code,
            perm_name=permission.perm_name,
            module=permission.module,
            operation=permission.operation,
            description=permission.description,
            sort_order=permission.sort_order,
        )

    @staticmethod
    def _update_orm(row: PermissionTable, permission: Permission) -> None:
        """同步领域模型变更到 ORM。"""
        row.perm_code = permission.perm_code
        row.perm_name = permission.perm_name
        row.module = permission.module
        row.operation = permission.operation
        row.description = permission.description
        row.sort_order = permission.sort_order
