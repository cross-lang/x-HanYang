"""删除用户命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.domain.user.repository import UserRepository
from src.domain.user.events import UserDeleted
from src.domain.shared.domain_exception import EntityNotFoundException


@dataclass(frozen=True)
class DeleteUserCommand:
    """删除用户命令。"""

    user_id: int


class DeleteUserHandler:
    """删除用户命令处理器。"""

    def __init__(self, user_repository: UserRepository, event_bus: EventBus) -> None:
        self._user_repo = user_repository
        self._event_bus = event_bus

    def handle(self, command: DeleteUserCommand) -> bool:
        """执行删除用户命令（软删除）。

        Args:
            command: 删除用户命令

        Returns:
            bool: 是否成功删除

        Raises:
            EntityNotFoundException: 用户不存在
        """
        user = self._user_repo.find_by_id(command.user_id)
        if user is None:
            raise EntityNotFoundException(f"用户 {command.user_id} 不存在")

        username = user.username
        user.soft_delete()
        self._user_repo.save(user)

        # 发布删除事件
        self._event_bus.publish(UserDeleted(user_id=command.user_id, username=username))

        return True
