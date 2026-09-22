"""删除角色命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.domain.user.repository import RoleRepository
from src.domain.shared.domain_exception import EntityNotFoundException


@dataclass(frozen=True)
class DeleteRoleCommand:
    """删除角色命令。

    Attributes:
        role_id: 角色 ID
    """

    role_id: int


class DeleteRoleHandler:
    """删除角色命令处理器。"""

    def __init__(self, role_repository: RoleRepository, event_bus: EventBus) -> None:
        self._role_repo = role_repository
        self._event_bus = event_bus

    async def handle(self, command: DeleteRoleCommand) -> bool:
        """执行删除角色命令（软删除）。

        Args:
            command: 删除角色命令

        Returns:
            bool: 是否成功删除

        Raises:
            EntityNotFoundException: 角色不存在
        """
        role = await self._role_repo.find_by_id(command.role_id)
        if role is None:
            raise EntityNotFoundException(f"角色 {command.role_id} 不存在")

        return await self._role_repo.delete(command.role_id)
