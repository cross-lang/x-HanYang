"""认证领域服务基础设施实现。

实现 domain/auth/auth_service.py 中定义的 AuthDomainService 接口。
负责用户认证、JWT 令牌签发与验证。
"""

from __future__ import annotations

import logging

import jwt

from src.constants.auth import (
    AUTH_SCHEME,
    DEFAULT_JWT_ALGORITHM,
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    LOGIN_TYPE_PASSWORD,
    LOGIN_STATUS_SUCCESS,
    LOGIN_STATUS_FAILED,
)
from src.constants.messages import (
    MSG_INVALID_CREDENTIALS,
    MSG_ACCOUNT_LOCKED,
    MSG_ACCESS_TOKEN_EXPIRED,
    MSG_REFRESH_TOKEN_EXPIRED,
    MSG_INVALID_TOKEN,
    MSG_INVALID_ACCESS_TOKEN,
    MSG_INVALID_REFRESH_TOKEN,
    MSG_USER_NOT_FOUND,
)
from src.constants.auth import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from src.domain.audit.login_log import LoginLog
from src.domain.audit.repository import LoginLogRepository
from src.domain.auth.auth_service import AuthDomainService, CurrentUser, TokenPair
from src.domain.shared.domain_exception import AuthenticationException
from src.domain.user.repository import UserRepository
from src.shared.security import create_access_token, create_refresh_token, decode_token

logger = logging.getLogger(__name__)


class InfraAuthDomainService(AuthDomainService):
    """认证领域服务实现。

    通过 UserRepository 查询用户，使用 JWT 实现令牌签发与验证。
    可选注入 LoginLogRepository 以记录登录日志。
    所有方法均为异步。
    """

    def __init__(
        self,
        user_repository: UserRepository,
        secret_key: str,
        algorithm: str = DEFAULT_JWT_ALGORITHM,
        access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        login_log_repository: LoginLogRepository | None = None,
    ) -> None:
        self._user_repo = user_repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._login_log_repo = login_log_repository

    async def authenticate(self, account: str, password: str, ip_address: str | None = None) -> TokenPair:
        """用户认证（登录）。

        支持用户名或邮箱登录。成功或失败均记录登录日志。

        Args:
            account: 用户名或邮箱
            password: 明文密码
            ip_address: 客户端 IP

        Returns:
            TokenPair: 访问令牌和刷新令牌

        Raises:
            AuthenticationException: 账号不存在、密码错误或用户已锁定
        """
        # 按用户名或邮箱查找
        user = await self._user_repo.find_by_username(account)
        if user is None:
            user = await self._user_repo.find_by_email(account)
        if user is None:
            await self._record_login_log(None, LOGIN_STATUS_FAILED, ip_address)
            raise AuthenticationException(MSG_INVALID_CREDENTIALS)

        if user.is_deleted:
            await self._record_login_log(user.id, LOGIN_STATUS_FAILED, ip_address)
            raise AuthenticationException(MSG_INVALID_CREDENTIALS)

        if user.is_locked:
            await self._record_login_log(user.id, LOGIN_STATUS_FAILED, ip_address)
            raise AuthenticationException(MSG_ACCOUNT_LOCKED)

        if not user.password_hash:
            await self._record_login_log(user.id, LOGIN_STATUS_FAILED, ip_address)
            raise AuthenticationException(MSG_INVALID_CREDENTIALS)

        from src.domain.user.value_objects import Password

        password_vo = Password.from_hashed(user.password_hash)
        if not password_vo.verify(password):
            await self._record_login_log(user.id, LOGIN_STATUS_FAILED, ip_address)
            raise AuthenticationException(MSG_INVALID_CREDENTIALS)

        # 记录登录
        user.record_login(ip_address)
        await self._user_repo.save(user)

        # 记录成功登录日志
        await self._record_login_log(user.id, LOGIN_STATUS_SUCCESS, ip_address)

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
            token_type=AUTH_SCHEME,
            expires_in=self._access_token_expire_minutes * 60,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """刷新令牌。

        Args:
            refresh_token: 刷新令牌

        Returns:
            TokenPair: 新的令牌对

        Raises:
            AuthenticationException: 刷新令牌无效或过期
        """
        try:
            payload = decode_token(refresh_token, self._secret_key, self._algorithm)
        except jwt.ExpiredSignatureError:
            raise AuthenticationException(MSG_REFRESH_TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise AuthenticationException(MSG_INVALID_REFRESH_TOKEN)

        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise AuthenticationException(MSG_INVALID_REFRESH_TOKEN)

        user_id = int(payload["sub"])
        user = await self._user_repo.find_by_id(user_id)
        if user is None or user.is_deleted or user.is_locked:
            raise AuthenticationException(MSG_USER_NOT_FOUND)

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
            token_type=AUTH_SCHEME,
            expires_in=self._access_token_expire_minutes * 60,
        )

    async def get_current_user(self, token: str) -> CurrentUser:
        """解析令牌获取当前用户。

        Args:
            token: 访问令牌

        Returns:
            CurrentUser: 当前用户信息

        Raises:
            AuthenticationException: 令牌无效或用户不存在
        """
        try:
            payload = decode_token(token, self._secret_key, self._algorithm)
        except jwt.ExpiredSignatureError:
            raise AuthenticationException(MSG_ACCESS_TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise AuthenticationException(MSG_INVALID_TOKEN)

        if payload.get("type") != TOKEN_TYPE_ACCESS:
            raise AuthenticationException(MSG_INVALID_ACCESS_TOKEN)

        user_id = int(payload["sub"])
        user = await self._user_repo.find_by_id(user_id)
        if user is None or user.is_deleted:
            raise AuthenticationException(MSG_USER_NOT_FOUND)

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

    async def logout(self, user_id: int) -> None:
        """退出登录。

        当前为无状态 JWT，退出仅作标记。
        后续接入 Redis 后可实现令牌黑名单。

        Args:
            user_id: 用户 ID
        """

    async def _record_login_log(
        self, user_id: int | None, status: str, ip_address: str | None
    ) -> None:
        """记录登录日志。

        通过 LoginLogRepository 持久化登录行为。
        记录失败时仅打印警告日志，不影响主流程。

        Args:
            user_id: 登录用户 ID（未识别用户时为 None）
            status: 登录状态（success、failed）
            ip_address: 客户端 IP 地址
        """
        if not self._login_log_repo:
            return
        try:
            log = LoginLog(
                user_id=user_id,
                login_type=LOGIN_TYPE_PASSWORD,
                status=status,
                ip_address=ip_address,
            )
            await self._login_log_repo.save(log)
        except Exception:
            logger.warning("记录登录日志失败: user_id=%s, status=%s", user_id, status, exc_info=True)
