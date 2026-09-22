"""认证聚合 — 领域事件。"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True)
class UserLoggedIn(DomainEvent):
    """用户登录成功事件。"""

    user_id: int = 0
    ip_address: str | None = None
    login_type: str = "password"


@dataclass(frozen=True)
class UserLoginFailed(DomainEvent):
    """用户登录失败事件。"""

    account: str = ""
    ip_address: str | None = None
    reason: str = ""


@dataclass(frozen=True)
class UserLoggedOut(DomainEvent):
    """用户退出登录事件。"""

    user_id: int = 0
