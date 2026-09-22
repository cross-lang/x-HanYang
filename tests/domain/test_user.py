"""用户聚合根领域模型测试。"""

from __future__ import annotations

import pytest

from src.domain.shared.domain_exception import ValidationException
from src.domain.user.user import User
from src.domain.user.value_objects import Email, Password, UserStatus
from src.domain.user.events import UserCreated, EmailChanged, PasswordChanged, UserLocked, UserDeleted


class TestUser:
    """User 聚合根测试。"""

    def test_create_user_emits_event(self) -> None:
        """创建用户应产生 UserCreated 事件。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password, name="Test")

        events = user.collect_and_clear_events()
        assert len(events) == 1
        assert isinstance(events[0], UserCreated)
        assert events[0].username == "testuser"
        assert events[0].email == "test@example.com"

    def test_change_email_emits_event(self) -> None:
        """变更邮箱应产生 EmailChanged 事件。"""
        email = Email("old@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)
        user.collect_and_clear_events()  # 清除创建事件

        new_email = Email("new@example.com")
        user.change_email(new_email)

        events = user.collect_and_clear_events()
        assert len(events) == 1
        assert isinstance(events[0], EmailChanged)
        assert events[0].old_email == "old@example.com"
        assert events[0].new_email == "new@example.com"
        assert user.email == new_email

    def test_change_email_same_raises(self) -> None:
        """变更邮箱为相同邮箱应抛出 ValidationException。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)

        with pytest.raises(ValidationException, match="新邮箱与当前邮箱相同"):
            user.change_email(Email("test@example.com"))

    def test_change_password_emits_event(self) -> None:
        """变更密码应产生 PasswordChanged 事件。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)
        user.collect_and_clear_events()

        new_password = Password.from_raw("87654321")
        user.change_password(new_password)

        events = user.collect_and_clear_events()
        assert len(events) == 1
        assert isinstance(events[0], PasswordChanged)

    def test_lock_user(self) -> None:
        """锁定用户应改变状态并产生事件。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)
        user.collect_and_clear_events()

        user.lock()

        assert user.status == UserStatus.LOCKED
        assert user.is_locked is True
        events = user.collect_and_clear_events()
        assert len(events) == 1
        assert isinstance(events[0], UserLocked)

    def test_lock_already_locked_raises(self) -> None:
        """锁定已锁定用户应抛出 ValidationException。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)
        user.lock()

        with pytest.raises(ValidationException, match="用户已处于锁定状态"):
            user.lock()

    def test_unlock_user(self) -> None:
        """解锁用户应恢复状态。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)
        user.lock()

        user.unlock()

        assert user.status == UserStatus.ACTIVE
        assert user.is_locked is False

    def test_unlock_not_locked_raises(self) -> None:
        """解锁未锁定用户应抛出 ValidationException。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)

        with pytest.raises(ValidationException, match="用户未处于锁定状态"):
            user.unlock()

    def test_soft_delete(self) -> None:
        """软删除应设置 deleted_at 并产生事件。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)
        user.collect_and_clear_events()

        user.soft_delete()

        assert user.is_deleted is True
        assert user.deleted_at is not None
        events = user.collect_and_clear_events()
        assert len(events) == 1
        assert isinstance(events[0], UserDeleted)
        assert events[0].username == "testuser"

    def test_record_login(self) -> None:
        """记录登录应更新 last_login_at 和 last_login_ip。"""
        email = Email("test@example.com")
        password = Password.from_raw("12345678")
        user = User.create(username="testuser", email=email, password=password)

        user.record_login("192.168.1.1")

        assert user.last_login_at is not None
        assert user.last_login_ip == "192.168.1.1"


class TestEmail:
    """Email 值对象测试。"""

    def test_valid_email(self) -> None:
        """合法邮箱应成功构造。"""
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_valid_email_with_dots(self) -> None:
        """包含点号的合法邮箱应成功构造。"""
        email = Email("first.last@example.co.uk")
        assert email.value == "first.last@example.co.uk"

    def test_invalid_email_raises(self) -> None:
        """非法邮箱应抛出 ValidationException。"""
        with pytest.raises(ValidationException, match="无效邮箱格式"):
            Email("not-an-email")

    def test_invalid_email_no_domain(self) -> None:
        """缺少域名的邮箱应抛出 ValidationException。"""
        with pytest.raises(ValidationException, match="无效邮箱格式"):
            Email("user@")

    def test_email_equality(self) -> None:
        """相同值的 Email 应相等。"""
        assert Email("a@b.com") == Email("a@b.com")
        assert Email("a@b.com") != Email("c@d.com")


class TestPassword:
    """Password 值对象测试。"""

    def test_short_password_raises(self) -> None:
        """短密码应抛出 ValidationException。"""
        with pytest.raises(ValidationException, match="密码长度不能少于"):
            Password.from_raw("123")

    def test_valid_password_creation(self) -> None:
        """合法长度密码应成功构造。"""
        password = Password.from_raw("12345678")
        assert password is not None

    def test_password_hashing(self) -> None:
        """密码哈希应可验证。"""
        password = Password.from_raw("12345678")
        hashed = password.hashed()
        assert hashed != "12345678"
        assert password.verify("12345678") is True
        assert password.verify("wrongpassword") is False

    def test_password_from_hashed(self) -> None:
        """从哈希构造的 Password 应能验证原始密码。"""
        password = Password.from_raw("12345678")
        hashed = password.hashed()
        restored = Password.from_hashed(hashed)
        assert restored.verify("12345678") is True

    def test_password_equality(self) -> None:
        """相同原始密码的 Password 应相等。"""
        assert Password.from_raw("12345678") == Password.from_raw("12345678")
