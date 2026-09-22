"""删除用户命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.shared.domain_exception import EntityNotFoundException


@dataclass(frozen=True)
class DeleteUserCommand:
    """删除用户命令。"""
    user_id: int


class DeleteUserHandler:
    """删除用户命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: DeleteUserCommand) -> bool:
        """执行删除用户命令（软删除）。"""
        user = await self._uow.user_repo.find_by_id(command.user_id)
        if user is None:
            raise EntityNotFoundException(f"用户 {command.user_id} 不存在")

        user.soft_delete()
        await self._uow.user_repo.save(user)

        events = user.collect_and_clear_events()
        await self._event_bus.publish_all(events)

        return True
