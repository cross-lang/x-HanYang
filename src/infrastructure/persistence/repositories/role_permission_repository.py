"""角色-权限关联仓储实现。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.orm.user_mapping import RolePermissionTable


class SqlRolePermissionRepository:
    """SQLAlchemy 角色-权限关联仓储实现（异步）。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_permission_ids_by_role(self, role_id: int) -> list[int]:
        """获取角色关联的所有权限 ID。"""
        stmt = select(RolePermissionTable.permission_id).where(RolePermissionTable.role_id == role_id)
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def assign(self, role_id: int, permission_id: int) -> None:
        """为角色分配权限（幂等）。"""
        stmt = select(RolePermissionTable).where(
            RolePermissionTable.role_id == role_id,
            RolePermissionTable.permission_id == permission_id,
        )
        existing = (await self._session.execute(stmt)).scalars().first()
        if existing is not None:
            return
        orm = RolePermissionTable(role_id=role_id, permission_id=permission_id)
        self._session.add(orm)
        await self._session.flush()

    async def revoke(self, role_id: int, permission_id: int) -> bool:
        """移除角色的指定权限（物理删除）。"""
        stmt = select(RolePermissionTable).where(
            RolePermissionTable.role_id == role_id,
            RolePermissionTable.permission_id == permission_id,
        )
        row = (await self._session.execute(stmt)).scalars().first()
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True

    async def revoke_all_for_role(self, role_id: int) -> int:
        """移除角色的所有权限。"""
        stmt = select(RolePermissionTable).where(RolePermissionTable.role_id == role_id)
        rows = list((await self._session.execute(stmt)).scalars().all())
        for row in rows:
            await self._session.delete(row)
        await self._session.flush()
        return len(rows)

    async def set_permissions_for_role(self, role_id: int, permission_ids: list[int]) -> None:
        """设置角色的权限列表（全量替换）。"""
        current_ids = set(await self.get_permission_ids_by_role(role_id))
        new_ids = set(permission_ids)
        for pid in current_ids - new_ids:
            await self.revoke(role_id, pid)
        for pid in new_ids - current_ids:
            await self.assign(role_id, pid)
