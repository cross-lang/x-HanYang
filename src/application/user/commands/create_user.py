"""创建用户命令及处理器。

命令（Command）表示一个写操作意图。
处理器（Handler）编排领域对象完成用例，不含业务规则。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.domain.user.user import User
from src.domain.user.value_objects import Email, Password
from src.domain.user.repository import UserRepository
from src.domain.shared.domain_exception import ConflictException


@dataclass(frozen=True)
class CreateUserCommand:
    """创建用户命令。"""

    username: str
    email: str
    password: str
    name: str | None = None
    phone: str | None = None
    role_id: int | None = None


class CreateUserHandler:
    """创建用户命令处理器。

    编排领域对象完成用户创建用例：
    1. 校验唯一性（邮箱、用户名）
    2. 调用聚合根工厂方法创建用户
    3. 持久化
    4. 分发领域事件
    """

    def __init__(self, user_repository: UserRepository, event_bus: EventBus) -> None:
        self._user_repo = user_repository
        self._event_bus = event_bus

    def handle(self, command: CreateUserCommand) -> User:
        """执行创建用户命令。

        Args:
            command: 创建用户命令

        Returns:
            User: 创建成功的用户聚合根

        Raises:
            ConflictException: 邮箱或用户名已存在
        """
        # 1. 校验唯一性
        email = Email(command.email)
        if self._user_repo.find_by_email(email.value) is not None:
            raise ConflictException(f"邮箱 {command.email} 已被注册")
        if self._user_repo.find_by_username(command.username) is not None:
            raise ConflictException(f"用户名 {command.username} 已存在")

        # 2. 创建用户（领域逻辑内聚在聚合根中）
        password = Password.from_raw(command.password)
        user = User.create(
            username=command.username,
            email=email,
            password=password,
            name=command.name,
            phone=command.phone,
            role_id=command.role_id,
        )

        # 3. 持久化
        self._user_repo.save(user)

        # 4. 分发领域事件
        events = user.collect_and_clear_events()
        self._event_bus.publish_all(events)

        return user
