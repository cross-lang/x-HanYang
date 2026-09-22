"""认证领域服务接口。

领域服务接口定义在领域层，处理跨聚合的认证逻辑。
实现在 application/auth/commands/ 中。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPair:
    """令牌对。"""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 604800  # 7 天


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
    """

    @abstractmethod
    def authenticate(self, account: str, password: str, ip_address: str | None = None) -> TokenPair:
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
    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """刷新令牌。

        Args:
            refresh_token: 刷新令牌

        Returns:
            TokenPair: 新的令牌对

        Raises:
            AuthenticationException: 令牌无效或过期
        """

    @abstractmethod
    def get_current_user(self, token: str) -> CurrentUser:
        """解析令牌获取当前用户。

        Args:
            token: 访问令牌

        Returns:
            CurrentUser: 当前用户信息

        Raises:
            AuthenticationException: 令牌无效
        """

    @abstractmethod
    def logout(self, user_id: int) -> None:
        """退出登录。

        Args:
            user_id: 用户 ID
        """
