"""用户聚合根。

User 作为聚合根，管理用户的核心业务规则。
包含角色、权限等关联实体，但通过聚合边界隔离。

依赖方向：本模块仅依赖 domain.shared，不依赖任何外部框架。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.user.value_objects import Email, Password, UserStatus


@dataclass
class User(AggregateRoot):
    """用户聚合根。

    业务规则内聚于此，不散落在 Service 或 Repository 中。

    Attributes:
        username: 用户名（全局唯一）
        email: 邮箱（值对象，内含格式校验）
        password_hash: 密码哈希（通过 Password 值对象生成）
        name: 姓名
        age: 年龄
        phone: 手机号
        avatar_url: 头像 URL
        role_id: 主角色 ID
        status: 用户状态（值对象）
        last_login_at: 最后登录时间
        last_login_ip: 最后登录 IP
        created_at: 创建时间
        updated_at: 更新时间
        deleted_at: 软删除时间
    """

    username: str = ""
    email: Email = field(default_factory=lambda: Email("placeholder@example.com"))
    password_hash: str = ""
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    avatar_url: str | None = None
    role_id: int | None = None
    status: UserStatus = UserStatus.ACTIVE
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    # ── 工厂方法 ──────────────────────────────────────────

    @classmethod
    def create(
        cls,
        username: str,
        email: Email,
        password: Password,
        name: str | None = None,
        phone: str | None = None,
        role_id: int | None = None,
    ) -> User:
        """创建新用户（工厂方法，封装创建逻辑）。

        Args:
            username: 用户名
            email: 邮箱值对象
            password: 密码值对象（含强度校验）
            name: 姓名
            phone: 手机号
            role_id: 角色 ID

        Returns:
            User: 新建的用户聚合根（已添加 UserCreated 事件）
        """
        from src.domain.user.events import UserCreated

        user = cls(
            username=username,
            email=email,
            password_hash=password.hashed(),
            name=name,
            phone=phone,
            role_id=role_id,
            status=UserStatus.ACTIVE,
        )
        user._add_event(UserCreated(user_id=0, username=username, email=email.value))
        return user

    # ── 业务行为 ──────────────────────────────────────────

    def change_email(self, new_email: Email) -> None:
        """变更邮箱。

        Args:
            new_email: 新邮箱值对象

        Raises:
            DomainException: 邮箱未变化时抛出
        """
        from src.domain.shared.domain_exception import ValidationException
        from src.domain.user.events import EmailChanged

        if self.email == new_email:
            raise ValidationException("新邮箱与当前邮箱相同")

        old_email = self.email
        self.email = new_email
        self._add_event(EmailChanged(user_id=self.id, old_email=old_email.value, new_email=new_email.value))

    def change_password(self, new_password: Password) -> None:
        """变更密码。

        Args:
            new_password: 新密码值对象（含强度校验）
        """
        from src.domain.user.events import PasswordChanged

        self.password_hash = new_password.hashed()
        self._add_event(PasswordChanged(user_id=self.id))

    def lock(self) -> None:
        """锁定用户。"""
        from src.domain.shared.domain_exception import ValidationException
        from src.domain.user.events import UserLocked

        if self.status == UserStatus.LOCKED:
            raise ValidationException("用户已处于锁定状态")
        self.status = UserStatus.LOCKED
        self._add_event(UserLocked(user_id=self.id))

    def unlock(self) -> None:
        """解锁用户。"""
        from src.domain.shared.domain_exception import ValidationException

        if self.status != UserStatus.LOCKED:
            raise ValidationException("用户未处于锁定状态")
        self.status = UserStatus.ACTIVE

    def soft_delete(self) -> None:
        """软删除用户（添加 UserDeleted 领域事件）。"""
        from datetime import datetime, timezone
        from src.domain.user.events import UserDeleted

        self.deleted_at = datetime.now(timezone.utc)
        self._add_event(UserDeleted(user_id=self.id, username=self.username))

    def record_login(self, ip_address: str | None) -> None:
        """记录登录信息。

        Args:
            ip_address: 客户端 IP 地址
        """
        from datetime import datetime, timezone

        self.last_login_at = datetime.now(timezone.utc)
        self.last_login_ip = ip_address

    @property
    def is_deleted(self) -> bool:
        """判断用户是否已软删除。

        Returns:
            bool: 是否已删除
        """
        return self.deleted_at is not None

    @property
    def is_locked(self) -> bool:
        """判断用户是否已锁定。

        Returns:
            bool: 是否已锁定
        """
        return self.status == UserStatus.LOCKED
