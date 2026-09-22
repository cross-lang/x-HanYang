"""用户应用层 — 命令、查询、DTO。

所有用户相关的 Command/Query Handler 和数据传输对象。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.application.shared.event_bus import EventBus
from src.application.shared.common import PaginatedResult
from src.application.shared.unit_of_work import UnitOfWork
from src.constants.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from src.domain.user.user import User
from src.domain.user.value_objects import Email, Password
from src.domain.user.repository import UserRepository
from src.domain.shared.domain_exception import ConflictException, EntityNotFoundException


# ══════════════════════════════════════════════════
#  DTO
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class UserDTO:
    """用户输出 DTO。"""

    id: int
    username: str
    email: str
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    avatar_url: str | None = None
    role_id: int | None = None
    status: str = "active"
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, user: User) -> UserDTO:
        """从领域模型转换。"""
        return cls(
            id=user.id, username=user.username, email=user.email.value,
            name=user.name, age=user.age, phone=user.phone, avatar_url=user.avatar_url,
            role_id=user.role_id, status=user.status.value,
            last_login_at=user.last_login_at, last_login_ip=user.last_login_ip,
            created_at=user.created_at, updated_at=user.updated_at,
        )


# ══════════════════════════════════════════════════
#  写操作 — Command + Handler
# ══════════════════════════════════════════════════

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
    """创建用户命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: CreateUserCommand) -> User:
        """执行创建用户命令。

        Raises:
            ConflictException: 邮箱或用户名已存在
        """
        async with self._uow:
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
        async with self._uow:
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
        async with self._uow:
            user = await self._uow.user_repo.find_by_id(command.user_id)
            if user is None:
                raise EntityNotFoundException(f"用户 {command.user_id} 不存在")
            user.soft_delete()
            await self._uow.user_repo.save(user)

        events = user.collect_and_clear_events()
        await self._event_bus.publish_all(events)
        return True


# ══════════════════════════════════════════════════
#  读操作 — Query + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class GetUserQuery:
    """获取用户详情查询。"""

    user_id: int


class GetUserHandler:
    """获取用户详情查询处理器。"""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    async def handle(self, query: GetUserQuery) -> UserDTO:
        """执行查询。

        Raises:
            EntityNotFoundException: 用户不存在
        """
        user = await self._user_repo.find_by_id(query.user_id)
        if user is None:
            raise EntityNotFoundException(f"用户 {query.user_id} 不存在")
        return UserDTO.from_domain(user)


@dataclass(frozen=True)
class SearchUsersQuery:
    """搜索用户列表查询。"""

    keyword: str | None = None
    status: str | None = None
    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE


class SearchUsersHandler:
    """搜索用户列表查询处理器。"""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    async def handle(self, query: SearchUsersQuery) -> PaginatedResult[UserDTO]:
        """执行搜索。"""
        skip = (query.page - 1) * query.page_size
        users, total = await self._user_repo.search(
            keyword=query.keyword, status=query.status, skip=skip, limit=query.page_size,
        )
        items = [UserDTO.from_domain(u) for u in users]
        return PaginatedResult(items=items, total=total, page=query.page, page_size=query.page_size)
