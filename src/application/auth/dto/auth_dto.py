"""认证 DTO — 认证相关的数据传输对象。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPairDTO:
    """令牌对 DTO。"""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 604800


@dataclass(frozen=True)
class CurrentUserDTO:
    """当前用户 DTO。"""

    id: int
    username: str
    email: str
    name: str | None = None
    role_id: int | None = None
    role_code: str | None = None
    status: str = "active"
    avatar_url: str | None = None
