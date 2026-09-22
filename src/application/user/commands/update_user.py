"""更新用户命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.domain.user.user import User
from src.domain.user.value_objects import Email, Password
from src.domain.user.repository import UserRepository
from src.domain.shared.domain_exception import EntityNotFoundException, ConflictException


@dataclass(frozen=True)
class UpdateUserCommand:
    """更新用户命令（仅传入需要更新的字段）。"""

    user_id: int
    email: str | None = None
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    role_id: int | None = None
    password: str | None = None


class UpdateUserHandler:
    """更新用户命令处理器。"""

    def __init__(self, user_repository: UserRepository, event_bus: EventBus) -> None:
        self._user_repo = user_repository
        self._event_bus = event_bus

    def handle(self, command: UpdateUserCommand) -> User:
        """执行更新用户命令。

        Args:
            command: 更新用户命令

        Returns:
            User: 更新后的用户聚合根

        Raises:
            EntityNotFoundException: 用户不存在
            ConflictException: 邮箱已被其他用户占用
        """
        # 1. 查找用户
        user = self._user_repo.find_by_id(command.user_id)
        if user is None:
            raise EntityNotFoundException(f"用户 {command.user_id} 不存在")

        # 2. 更新邮箱（通过聚合根方法，内含业务规则）
        if command.email is not None:
            new_email = Email(command.email)
            existing = self._user_repo.find_by_email(command.email)
            if existing is not None and existing.id != command.user_id:
                raise ConflictException(f"邮箱 {command.email} 已被其他用户占用")
            user.change_email(new_email)

        # 3. 更新密码
        if command.password is not None:
            password = Password.from_raw(command.password)
            user.change_password(password)

        # 4. 更新其他字段
        if command.name is not None:
            user.name = command.name
        if command.phone is not None:
            user.phone = command.phone
        if command.avatar_url is not None:
            user.avatar_url = command.avatar_url
        if command.role_id is not None:
            user.role_id = command.role_id

        # 5. 持久化
        self._user_repo.save(user)

        # 6. 分发领域事件
        events = user.collect_and_clear_events()
        self._event_bus.publish_all(events)

        return user
