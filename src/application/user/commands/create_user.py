"""创建用户命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.user.user import User
from src.domain.user.value_objects import Email, Password
from src.domain.shared.domain_exception import ConflictException


@dataclass(frozen=True)
class CreateUserCommand:
    """创建用户命令。

    Attributes:
        username: 用户名
        email: 邮箱
        password: 明文密码
        name: 姓名
        phone: 手机号
        role_id: 角色 ID
    """

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
    3. 持久化（通过 UoW 管理事务）
    4. 分发领域事件
    """

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: CreateUserCommand) -> User:
        """执行创建用户命令。

        Args:
            command: 创建用户命令

        Returns:
            User: 创建成功的用户聚合根

        Raises:
            ConflictException: 邮箱或用户名已存在
        """
        email = Email(command.email)
        if await self._uow.user_repo.find_by_email(email.value) is not None:
            raise ConflictException(f"邮箱 {command.email} 已被注册")
        if await self._uow.user_repo.find_by_username(command.username) is not None:
            raise ConflictException(f"用户名 {command.username} 已存在")

        password = Password.from_raw(command.password)
        user = User.create(
            username=command.username, email=email, password=password,
            name=command.name, phone=command.phone, role_id=command.role_id,
        )

        await self._uow.user_repo.save(user)

        events = user.collect_and_clear_events()
        await self._event_bus.publish_all(events)

        return user
