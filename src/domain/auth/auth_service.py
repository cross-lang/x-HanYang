"""认证领域服务接口。

领域服务接口定义在领域层，处理跨聚合的认证逻辑。
实现在 infrastructure/auth/。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.constants.auth import AUTH_SCHEME, DEFAULT_TOKEN_EXPIRES_IN_SECONDS


@dataclass(frozen=True)
class TokenPair:
    """令牌对。

    Attributes:
        access_token: 访问令牌
        refresh_token: 刷新令牌
        token_type: 令牌类型（默认 Bearer）
        expires_in: 访问令牌有效期（秒）
    """

    access_token: str
    refresh_token: str
    token_type: str = AUTH_SCHEME
    expires_in: int = DEFAULT_TOKEN_EXPIRES_IN_SECONDS


@dataclass(frozen=True)
class CurrentUser:
    """当前登录用户信息。"""

    id: int
    username: str
    email: str
    name: str | None = None
    role_id: int | None = None
    role_code: str | None = None
    status: str = "active"
    avatar_url: str | None = None


class AuthDomainService(ABC):
    """认证领域服务接口。

    处理认证相关的跨聚合业务逻辑，如登录、令牌刷新。
    所有方法均为异步。
    """

    @abstractmethod
    async def authenticate(self, account: str, password: str, ip_address: str | None = None) -> TokenPair:
        """用户认证（登录）。

        Args:
            account: 用户名或邮箱
            password: 明文密码
            ip_address: 客户端 IP

        Returns:
            TokenPair: 访问令牌和刷新令牌

        Raises:
            AuthenticationException: 认证失败
        """

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """刷新令牌。

        Args:
            refresh_token: 刷新令牌

        Returns:
            TokenPair: 新的令牌对

        Raises:
            AuthenticationException: 令牌无效或过期
        """

    @abstractmethod
    async def get_current_user(self, token: str) -> CurrentUser:
        """解析令牌获取当前用户。

        Args:
            token: 访问令牌

        Returns:
            CurrentUser: 当前用户信息

        Raises:
            AuthenticationException: 令牌无效
        """

    @abstractmethod
    async def logout(self, user_id: int) -> None:
        """退出登录。

        Args:
            user_id: 用户 ID
        """
