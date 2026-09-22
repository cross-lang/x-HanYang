"""认证应用层 — 命令、查询、DTO。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.unit_of_work import UnitOfWork
from src.constants.auth import AUTH_SCHEME, DEFAULT_TOKEN_EXPIRES_IN_SECONDS
from src.domain.auth.auth_service import AuthDomainService


# ══════════════════════════════════════════════════
#  DTO
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class TokenPairDTO:
    """令牌对 DTO。"""

    access_token: str
    refresh_token: str
    token_type: str = AUTH_SCHEME
    expires_in: int = DEFAULT_TOKEN_EXPIRES_IN_SECONDS


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


# ══════════════════════════════════════════════════
#  写操作 — Command + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class LoginCommand:
    """登录命令。"""

    account: str
    password: str
    ip_address: str | None = None


class LoginHandler:
    """登录命令处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService, uow: UnitOfWork) -> None:
        self._auth_service = auth_domain_service
        self._uow = uow

    async def handle(self, command: LoginCommand) -> TokenPairDTO:
        """执行登录。"""
        async with self._uow:
            token_pair = await self._auth_service.authenticate(
                account=command.account, password=command.password, ip_address=command.ip_address,
            )
        return TokenPairDTO(
            access_token=token_pair.access_token, refresh_token=token_pair.refresh_token,
            token_type=token_pair.token_type, expires_in=token_pair.expires_in,
        )


@dataclass(frozen=True)
class LogoutCommand:
    """退出登录命令。"""

    user_id: int
    token: str


class LogoutHandler:
    """退出登录命令处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService, uow: UnitOfWork) -> None:
        self._auth_service = auth_domain_service
        self._uow = uow

    async def handle(self, command: LogoutCommand) -> None:
        """执行退出登录。"""
        async with self._uow:
            await self._auth_service.logout(command.user_id, command.token)


@dataclass(frozen=True)
class RefreshTokenCommand:
    """刷新令牌命令。"""

    refresh_token: str


class RefreshTokenHandler:
    """刷新令牌命令处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService) -> None:
        self._auth_service = auth_domain_service

    async def handle(self, command: RefreshTokenCommand) -> TokenPairDTO:
        """执行令牌刷新。"""
        token_pair = await self._auth_service.refresh_tokens(command.refresh_token)
        return TokenPairDTO(
            access_token=token_pair.access_token, refresh_token=token_pair.refresh_token,
            token_type=token_pair.token_type, expires_in=token_pair.expires_in,
        )


# ══════════════════════════════════════════════════
#  读操作 — Query + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class GetCurrentUserQuery:
    """获取当前用户查询。"""

    token: str


class GetCurrentUserHandler:
    """获取当前用户查询处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService) -> None:
        self._auth_service = auth_domain_service

    async def handle(self, query: GetCurrentUserQuery) -> CurrentUserDTO:
        """执行查询。"""
        current_user = await self._auth_service.get_current_user(query.token)
        return CurrentUserDTO(
            id=current_user.id, username=current_user.username, email=current_user.email,
            name=current_user.name, role_id=current_user.role_id, role_code=current_user.role_code,
            status=current_user.status, avatar_url=current_user.avatar_url,
        )
