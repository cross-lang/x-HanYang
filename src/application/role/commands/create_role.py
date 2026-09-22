"""创建角色命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.user.role import Role, RoleType
from src.domain.shared.domain_exception import ConflictException


@dataclass(frozen=True)
class CreateRoleCommand:
    """创建角色命令。"""
    role_name: str
    role_code: str
    description: str | None = None
    role_type: str = "custom"


class CreateRoleHandler:
    """创建角色命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: CreateRoleCommand) -> Role:
        """执行创建角色命令。

        Raises:
            ConflictException: 角色编码已存在
        """
        async with self._uow:
            if await self._uow.role_repo.find_by_role_code(command.role_code) is not None:
                raise ConflictException(f"角色编码 {command.role_code} 已存在")

            role = Role(
                role_name=command.role_name, role_code=command.role_code,
                description=command.description, role_type=RoleType(command.role_type),
            )
            await self._uow.role_repo.save(role)
            return role
