"""创建用户用例测试。"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import TracebackType

import pytest

from src.application.shared.event_bus import EventBus
from src.application.shared.unit_of_work import UnitOfWork
from src.application.user.commands.create_user import CreateUserCommand, CreateUserHandler
from src.domain.shared.domain_exception import ConflictException
from src.domain.user.user import User
from src.domain.user.repository import UserRepository


# ── Mock 实现 ─────────────────────────────────────────────


class InMemoryUserRepository(UserRepository):
    """内存用户仓储（测试用）。"""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id: int = 1

    async def find_by_id(self, id: int) -> User | None:
        return self._users.get(id)

    async def find_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email.value == email:
                return user
        return None

    async def find_by_username(self, username: str) -> User | None:
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    async def save(self, entity: User) -> User:
        if entity.id == 0:
            entity.id = self._next_id
            self._next_id += 1
        self._users[entity.id] = entity
        return entity

    async def delete(self, id: int) -> None:
        self._users.pop(id, None)

    async def search(
        self,
        keyword: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        users = list(self._users.values())
        return users[skip:skip + limit], len(users)


class MockUnitOfWork(UnitOfWork):
    """Mock 工作单元（测试用，不真正开启事务）。"""

    def __init__(self) -> None:
        self._user_repo = InMemoryUserRepository()
        self.committed: bool = False
        self.rolled_back: bool = False

    @property
    def user_repo(self) -> InMemoryUserRepository:  # type: ignore[override]
        return self._user_repo

    async def __aenter__(self) -> MockUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    @property
    def role_repo(self):  # type: ignore[override]
        raise NotImplementedError

    @property
    def permission_repo(self):  # type: ignore[override]
        raise NotImplementedError

    @property
    def audit_repo(self):  # type: ignore[override]
        raise NotImplementedError

    @property
    def login_log_repo(self):  # type: ignore[override]
        raise NotImplementedError

    @property
    def role_permission_repo(self):  # type: ignore[override]
        raise NotImplementedError


class MockEventBus(EventBus):
    """Mock 事件总线（记录发布的事件）。"""

    def __init__(self) -> None:
        self.published: list = []

    async def publish(self, event: object) -> None:
        self.published.append(event)

    async def publish_all(self, events: list) -> None:
        self.published.extend(events)

    def subscribe(self, event_type: type, handler: object) -> None:
        pass


# ── 测试用例 ──────────────────────────────────────────────


class TestCreateUserHandler:
    """CreateUserHandler 测试。"""

    @pytest.fixture
    def uow(self) -> MockUnitOfWork:
        return MockUnitOfWork()

    @pytest.fixture
    def event_bus(self) -> MockEventBus:
        return MockEventBus()

    @pytest.fixture
    def handler(self, uow: MockUnitOfWork, event_bus: MockEventBus) -> CreateUserHandler:
        return CreateUserHandler(uow=uow, event_bus=event_bus)

    async def test_create_user_success(
        self, handler: CreateUserHandler, uow: MockUnitOfWork, event_bus: MockEventBus
    ) -> None:
        """正常创建用户应成功返回并发布事件。"""
        command = CreateUserCommand(
            username="testuser",
            email="test@example.com",
            password="12345678",
            name="Test User",
            phone="13800138000",
        )

        user = await handler.handle(command)

        assert user.id > 0
        assert user.username == "testuser"
        assert user.email.value == "test@example.com"
        assert uow.committed is True
        assert len(event_bus.published) == 1

    async def test_duplicate_email_raises_conflict(
        self, handler: CreateUserHandler, uow: MockUnitOfWork
    ) -> None:
        """重复邮箱应抛出 ConflictException。"""
        command1 = CreateUserCommand(username="user1", email="dup@example.com", password="12345678")
        await handler.handle(command1)

        command2 = CreateUserCommand(username="user2", email="dup@example.com", password="12345678")
        with pytest.raises(ConflictException, match="邮箱 .* 已被注册"):
            await handler.handle(command2)

    async def test_duplicate_username_raises_conflict(
        self, handler: CreateUserHandler, uow: MockUnitOfWork
    ) -> None:
        """重复用户名应抛出 ConflictException。"""
        command1 = CreateUserCommand(username="dupuser", email="a@example.com", password="12345678")
        await handler.handle(command1)

        command2 = CreateUserCommand(username="dupuser", email="b@example.com", password="12345678")
        with pytest.raises(ConflictException, match="用户名 .* 已存在"):
            await handler.handle(command2)

    async def test_rollback_on_error(
        self, handler: CreateUserHandler, uow: MockUnitOfWork
    ) -> None:
        """异常时应触发回滚。"""
        command = CreateUserCommand(username="user1", email="a@example.com", password="12345678")
        await handler.handle(command)

        command2 = CreateUserCommand(username="user1", email="a@example.com", password="12345678")
        with pytest.raises(ConflictException):
            await handler.handle(command2)
