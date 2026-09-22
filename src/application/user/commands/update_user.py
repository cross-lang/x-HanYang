"""更新用户命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.user.user import User
from src.domain.user.value_objects import Email, Password
from src.domain.shared.domain_exception import EntityNotFoundException, ConflictException


@dataclass(frozen=True)
class UpdateUserCommand:
    """更新用户命令。"""

    user_id: int
    email: str | None = None
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    role_id: int | None = None
    password: str | None = None


class UpdateUserHandler:
    """更新用户命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: UpdateUserCommand) -> User:
        """执行更新用户命令。

        Raises:
            EntityNotFoundException: 用户不存在
            ConflictException: 邮箱已被其他用户占用
        """
        user = await self._uow.user_repo.find_by_id(command.user_id)
        if user is None:
            raise EntityNotFoundException(f"用户 {command.user_id} 不存在")

        if command.email is not None:
            new_email = Email(command.email)
            existing = await self._uow.user_repo.find_by_email(command.email)
            if existing is not None and existing.id != command.user_id:
                raise ConflictException(f"邮箱 {command.email} 已被其他用户占用")
            user.change_email(new_email)

        if command.password is not None:
            user.change_password(Password.from_raw(command.password))

        if command.name is not None:
            user.name = command.name
        if command.phone is not None:
            user.phone = command.phone
        if command.avatar_url is not None:
            user.avatar_url = command.avatar_url
        if command.role_id is not None:
            user.role_id = command.role_id

        await self._uow.user_repo.save(user)

        events = user.collect_and_clear_events()
        await self._event_bus.publish_all(events)

        return user
