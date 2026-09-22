"""更新角色命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.user.role import Role, RoleStatus
from src.domain.shared.domain_exception import EntityNotFoundException


@dataclass(frozen=True)
class UpdateRoleCommand:
    """更新角色命令。"""
    role_id: int
    role_name: str | None = None
    description: str | None = None
    status: str | None = None


class UpdateRoleHandler:
    """更新角色命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: UpdateRoleCommand) -> Role:
        """执行更新角色命令。

        Raises:
            EntityNotFoundException: 角色不存在
        """
        async with self._uow:
            role = await self._uow.role_repo.find_by_id(command.role_id)
            if role is None:
                raise EntityNotFoundException(f"角色 {command.role_id} 不存在")

            if command.role_name is not None:
                role.role_name = command.role_name
            if command.description is not None:
                role.description = command.description
            if command.status is not None:
                role.status = RoleStatus(command.status)

            await self._uow.role_repo.save(role)
            return role
