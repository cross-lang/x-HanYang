"""认证相关请求 Schema。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求。

    Attributes:
        account: 用户名或邮箱
        password: 明文密码
    """

    account: str = Field(..., min_length=1, max_length=100, description="用户名或邮箱")
    password: str = Field(..., min_length=1, max_length=128, description="明文密码")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求。

    Attributes:
        refresh_token: 刷新令牌
    """

    refresh_token: str = Field(..., min_length=1, description="刷新令牌")
