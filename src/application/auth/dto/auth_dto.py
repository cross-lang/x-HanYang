"""认证 DTO — 认证相关的数据传输对象。"""

from __future__ import annotations

from dataclasses import dataclass

from src.constants.auth import AUTH_SCHEME, DEFAULT_TOKEN_EXPIRES_IN_SECONDS


@dataclass(frozen=True)
class TokenPairDTO:
    """令牌对 DTO。

    Attributes:
        access_token: 访问令牌
        refresh_token: 刷新令牌
        token_type: 令牌类型
        expires_in: 访问令牌有效期（秒）
    """

    access_token: str
    refresh_token: str
    token_type: str = AUTH_SCHEME
    expires_in: int = DEFAULT_TOKEN_EXPIRES_IN_SECONDS


@dataclass(frozen=True)
class CurrentUserDTO:
    """当前用户 DTO。

    Attributes:
        id: 用户 ID
        username: 用户名
        email: 邮箱
        name: 姓名
        role_id: 角色 ID
        role_code: 角色编码
        status: 状态
        avatar_url: 头像 URL
    """

    id: int
    username: str
    email: str
    name: str | None = None
    role_id: int | None = None
    role_code: str | None = None
    status: str = "active"
    avatar_url: str | None = None
