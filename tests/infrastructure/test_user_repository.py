"""用户仓储实现测试。

使用 SQLite 内存数据库进行集成测试，验证仓储层的领域模型 ↔ ORM 双向转换。
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.user.user import User
from src.domain.user.value_objects import Email, Password
from src.infrastructure.persistence.database import Base
from src.infrastructure.persistence.repositories.user_repository import SqlUserRepository


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:  # type: ignore[misc]
    """创建 SQLite 内存数据库会话。"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


class TestSqlUserRepository:
    """SqlUserRepository 集成测试。"""

    async def test_save_and_find_by_id(self, db_session: AsyncSession) -> None:
        """保存后应能通过 ID 查找。"""
        repo = SqlUserRepository(db_session)
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password, name="Test")
        user.collect_and_clear_events()

        await repo.save(user)
        await db_session.commit()

        found = await repo.find_by_id(user.id)
        assert found is not None
        assert found.username == "testuser"
        assert found.email.value == "test@example.com"
        assert found.name == "Test"

    async def test_find_by_email(self, db_session: AsyncSession) -> None:
        """应能通过邮箱查找用户。"""
        repo = SqlUserRepository(db_session)
        email = Email("findme@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)
        user.collect_and_clear_events()

        await repo.save(user)
        await db_session.commit()

        found = await repo.find_by_email("findme@example.com")
        assert found is not None
        assert found.username == "testuser"

    async def test_find_by_username(self, db_session: AsyncSession) -> None:
        """应能通过用户名查找用户。"""
        repo = SqlUserRepository(db_session)
        email = Email("user@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="findme", email=email, password=password)
        user.collect_and_clear_events()

        await repo.save(user)
        await db_session.commit()

        found = await repo.find_by_username("findme")
        assert found is not None
        assert found.email.value == "user@example.com"

    async def test_find_by_id_not_found(self, db_session: AsyncSession) -> None:
        """查找不存在的 ID 应返回 None。"""
        repo = SqlUserRepository(db_session)
        found = await repo.find_by_id(9999)
        assert found is None

    async def test_domain_orm_conversion(self, db_session: AsyncSession) -> None:
        """领域模型与 ORM 模型应能正确双向转换。"""
        repo = SqlUserRepository(db_session)
        email = Email("convert@example.com")
        password = Password.from_raw("12345678")
        user = User.create(
            username="convertuser",
            email=email,
            password=password,
            name="Convert Test",
            phone="13800138000",
            role_id=1,
        )
        user.collect_and_clear_events()

        await repo.save(user)
        await db_session.commit()

        found = await repo.find_by_id(user.id)
        assert found is not None
        assert found.username == "convertuser"
        assert found.email.value == "convert@example.com"
        assert found.name == "Convert Test"
        assert found.phone == "13800138000"
        assert found.role_id == 1
        assert found.password_hash != ""  # 密码已哈希

    async def test_update_user(self, db_session: AsyncSession) -> None:
        """更新用户信息应正确持久化。"""
        repo = SqlUserRepository(db_session)
        email = Email("update@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="updateuser", email=email, password=password, name="Before")
        user.collect_and_clear_events()

        await repo.save(user)
        await db_session.commit()

        user.name = "After"
        user.change_email(Email("updated@example.com"))
        user.collect_and_clear_events()
        await repo.save(user)
        await db_session.commit()

        found = await repo.find_by_id(user.id)
        assert found is not None
        assert found.name == "After"
        assert found.email.value == "updated@example.com"

    async def test_search_users(self, db_session: AsyncSession) -> None:
        """搜索应返回匹配的用户列表和总数。"""
        repo = SqlUserRepository(db_session)
        for i in range(3):
            email = Email(f"user{i}@example.com")
            password = Password.from_raw("12345678")
            user = User.create(username=f"user{i}", email=email, password=password)
            user.collect_and_clear_events()
            await repo.save(user)
        await db_session.commit()

        users, total = await repo.search()
        assert total == 3
        assert len(users) == 3

    async def test_search_with_keyword(self, db_session: AsyncSession) -> None:
        """关键字搜索应过滤结果。"""
        repo = SqlUserRepository(db_session)
        for name in ["alice", "bob", "charlie"]:
            email = Email(f"{name}@example.com")
            password = Password.from_raw("12345678")
            user = User.create(username=name, email=email, password=password)
            user.collect_and_clear_events()
            await repo.save(user)
        await db_session.commit()

        users, total = await repo.search(keyword="alice")
        assert total == 1
        assert users[0].username == "alice"
