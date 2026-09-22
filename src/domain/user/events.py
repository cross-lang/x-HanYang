"""用户聚合 — 领域事件。

领域事件描述用户聚合中发生的有意义的事情。
事件对象不可变（frozen），由聚合根收集，应用层分发。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True)
class UserCreated(DomainEvent):
    """用户已创建事件。"""

    user_id: int = 0
    username: str = ""
    email: str = ""


@dataclass(frozen=True)
class EmailChanged(DomainEvent):
    """邮箱已变更事件。"""

    user_id: int = 0
    old_email: str = ""
    new_email: str = ""


@dataclass(frozen=True)
class PasswordChanged(DomainEvent):
    """密码已变更事件。"""

    user_id: int = 0


@dataclass(frozen=True)
class UserLocked(DomainEvent):
    """用户已锁定事件。"""

    user_id: int = 0


@dataclass(frozen=True)
class UserDeleted(DomainEvent):
    """用户已删除事件。"""

    user_id: int = 0
    username: str = ""
