"""认证领域服务基础设施实现。

实现 domain/auth/auth_service.py 中定义的 AuthDomainService 接口。
负责用户认证、JWT 令牌签发与验证。
"""

from __future__ import annotations

from datetime import datetime, timezone

import jwt

from src.domain.auth.auth_service import AuthDomainService, CurrentUser, TokenPair
from src.domain.shared.domain_exception import AuthenticationException
from src.domain.user.repository import UserRepository
from src.shared.security import create_access_token, create_refresh_token, decode_token


class InfraAuthDomainService(AuthDomainService):
    """认证领域服务实现。

    通过 UserRepository 查询用户，使用 JWT 实现令牌签发与验证。
    """

    def __init__(
        self,
        user_repository: UserRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 10080,
    ) -> None:
        self._user_repo = user_repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def authenticate(self, account: str, password: str, ip_address: str | None = None) -> TokenPair:
        """用户认证（登录）。

        支持用户名或邮箱登录。

        Raises:
            AuthenticationException: 账号不存在、密码错误或用户已锁定
        """
        # 按用户名或邮箱查找
        user = self._user_repo.find_by_username(account)
        if user is None:
            user = self._user_repo.find_by_email(account)
        if user is None:
            raise AuthenticationException("账号或密码错误")

        if user.is_deleted:
            raise AuthenticationException("账号或密码错误")

        if user.is_locked:
            raise AuthenticationException("账号已被锁定")

        if not user.password_hash:
            raise AuthenticationException("账号或密码错误")

        from src.domain.user.value_objects import Password

        password_vo = Password.from_hashed(user.password_hash)
        if not password_vo.verify(password):
            raise AuthenticationException("账号或密码错误")

        # 记录登录
        user.record_login(ip_address)
        self._user_repo.save(user)

        # 签发令牌
        subject = str(user.id)
        extra = {"username": user.username}
        access_token = create_access_token(
            subject=subject,
            secret_key=self._secret_key,
            algorithm=self._algorithm,
            expires_minutes=self._access_token_expire_minutes,
            extra_claims=extra,
        )
        refresh_token = create_refresh_token(
            subject=subject,
            secret_key=self._secret_key,
            algorithm=self._algorithm,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._access_token_expire_minutes * 60,
        )

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """刷新令牌。

        Raises:
            AuthenticationException: 刷新令牌无效或过期
        """
        try:
            payload = decode_token(refresh_token, self._secret_key, self._algorithm)
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("刷新令牌已过期")
        except jwt.InvalidTokenError:
            raise AuthenticationException("无效的刷新令牌")

        if payload.get("type") != "refresh":
            raise AuthenticationException("无效的刷新令牌")

        user_id = int(payload["sub"])
        user = self._user_repo.find_by_id(user_id)
        if user is None or user.is_deleted or user.is_locked:
            raise AuthenticationException("用户不存在或已被锁定")

        subject = str(user.id)
        extra = {"username": user.username}
        new_access = create_access_token(
            subject=subject,
            secret_key=self._secret_key,
            algorithm=self._algorithm,
            expires_minutes=self._access_token_expire_minutes,
            extra_claims=extra,
        )
        new_refresh = create_refresh_token(
            subject=subject,
            secret_key=self._secret_key,
            algorithm=self._algorithm,
        )

        return TokenPair(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="Bearer",
            expires_in=self._access_token_expire_minutes * 60,
        )

    def get_current_user(self, token: str) -> CurrentUser:
        """解析令牌获取当前用户。

        Raises:
            AuthenticationException: 令牌无效或用户不存在
        """
        try:
            payload = decode_token(token, self._secret_key, self._algorithm)
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("令牌已过期")
        except jwt.InvalidTokenError:
            raise AuthenticationException("无效的令牌")

        if payload.get("type") != "access":
            raise AuthenticationException("无效的访问令牌")

        user_id = int(payload["sub"])
        user = self._user_repo.find_by_id(user_id)
        if user is None or user.is_deleted:
            raise AuthenticationException("用户不存在")

        return CurrentUser(
            id=user.id,
            username=user.username,
            email=user.email.value,
            name=user.name,
            role_id=user.role_id,
            role_code=None,
            status=user.status.value,
            avatar_url=user.avatar_url,
        )

    def logout(self, user_id: int) -> None:
        """退出登录。

        当前为无状态 JWT，退出仅作标记。
        后续接入 Redis 后可实现令牌黑名单。
        """
