"""种子数据管理模块。

应用启动时检测并自动创建系统内置种子数据：
    1. 超级管理员角色（roles 表，role_type=system，role_code=super_admin）
    2. 超级管理员用户（users 表，username=superadmin，绑定上述角色）
    3. 内置权限（permissions 表，perm_code=user:view）
    4. 角色权限关联（role_permissions 表，将上述权限绑定到超级管理员角色）

若数据已存在则跳过，保证幂等。
"""

from __future__ import annotations

from sqlalchemy import select

from src.core.logger import logger
from src.core.security import hash_password
from src.infrastructure.persistence.database import get_database_provider
from src.infrastructure.persistence.orm.user_mapping import (
    PermissionTable,
    RolePermissionTable,
    RoleTable,
    UserTable,
)

# 种子数据常量（系统内置，禁止随意修改）
_SEED_ROLE_CODE: str = "super_admin"
_SEED_ROLE_NAME: str = "超级管理员"
_SEED_ADMIN_USERNAME: str = "superadmin"
_SEED_ADMIN_PASSWORD: str = "admin@123456"
_SEED_ADMIN_EMAIL: str = "superadmin@system.local"
_SEED_PERM_CODE: str = "user:view"
_SEED_PERM_NAME: str = "查看用户"
_SEED_PERM_MODULE: str = "user"
_SEED_PERM_OPERATION: str = "view"


async def init_seed_data() -> None:
    """初始化系统种子数据（幂等，可重复调用）。

    检测顺序：
        1. roles 表中是否存在 role_code=super_admin 的角色，无则创建
        2. users 表中是否存在 username=superadmin 的用户，无则创建（绑定超管角色）
        3. permissions 表中是否存在 perm_code=user:view 的权限，无则创建
        4. role_permissions 表中是否存在该角色与权限的关联，无则创建
    """
    session_factory = get_database_provider().get_session_factory()
    async with session_factory() as session:
        try:
            # 1. 超级管理员角色
            result = await session.execute(
                select(RoleTable).where(RoleTable.role_code == _SEED_ROLE_CODE)
            )
            role = result.scalars().first()

            if role is None:
                role = RoleTable(
                    role_name=_SEED_ROLE_NAME,
                    role_code=_SEED_ROLE_CODE,
                    description="系统内置超级管理员角色，拥有全部权限",
                    role_type="system",
                    status="enabled",
                )
                session.add(role)
                await session.flush()
                logger.info(f"Seed role created: role_code={_SEED_ROLE_CODE}")
            else:
                logger.info(f"Seed role already exists: role_code={_SEED_ROLE_CODE}")

            # 2. 超级管理员用户
            result = await session.execute(
                select(UserTable).where(UserTable.username == _SEED_ADMIN_USERNAME)
            )
            admin = result.scalars().first()

            if admin is None:
                admin = UserTable(
                    username=_SEED_ADMIN_USERNAME,
                    email=_SEED_ADMIN_EMAIL,
                    password_hash=hash_password(_SEED_ADMIN_PASSWORD),
                    phone=None,
                    avatar_url=None,
                    role_id=role.id,
                    status="active",
                )
                session.add(admin)
                await session.flush()
                logger.info(f"Seed admin user created: username={_SEED_ADMIN_USERNAME}")
            else:
                logger.info(
                    f"Seed admin user already exists: username={_SEED_ADMIN_USERNAME}"
                )

            # 3. 内置权限
            result = await session.execute(
                select(PermissionTable).where(PermissionTable.perm_code == _SEED_PERM_CODE)
            )
            permission = result.scalars().first()

            if permission is None:
                permission = PermissionTable(
                    perm_code=_SEED_PERM_CODE,
                    perm_name=_SEED_PERM_NAME,
                    module=_SEED_PERM_MODULE,
                    operation=_SEED_PERM_OPERATION,
                    description="查看用户列表与详情",
                    sort_order=1,
                )
                session.add(permission)
                await session.flush()
                logger.info(f"Seed permission created: perm_code={_SEED_PERM_CODE}")
            else:
                logger.info(f"Seed permission already exists: perm_code={_SEED_PERM_CODE}")

            # 4. 角色权限关联（将内置权限绑定到超级管理员角色）
            result = await session.execute(
                select(RolePermissionTable).where(
                    RolePermissionTable.role_id == role.id,
                    RolePermissionTable.permission_id == permission.id,
                )
            )
            relation = result.scalars().first()

            if relation is None:
                relation = RolePermissionTable(
                    role_id=role.id,
                    permission_id=permission.id,
                )
                session.add(relation)
                await session.flush()
                logger.info(
                    f"Seed role-permission created: role_id={role.id} permission_id={permission.id}"
                )
            else:
                logger.info(
                    f"Seed role-permission already exists: role_id={role.id} permission_id={permission.id}"
                )

            await session.commit()
            logger.info("Seed data initialization completed")
        except Exception as e:  # noqa: BLE001
            await session.rollback()
            logger.warning(f"Seed data initialization skipped: {e}")
            # 种子初始化失败不应阻断应用启动
