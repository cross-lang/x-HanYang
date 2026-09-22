"""接口层依赖注入。

通过 FastAPI 的 Depends 机制组装 Handler，将基础设施层的实现注入到应用层。
这是 DDD 中「依赖倒置」在接口层的体现。
"""

from __future__ import annotations

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.application.auth.commands.login import LoginHandler
from src.application.auth.commands.refresh_token import RefreshTokenHandler
from src.application.auth.commands.logout import LogoutHandler
from src.application.auth.queries.get_current_user import GetCurrentUserHandler
from src.application.auth.dto.auth_dto import CurrentUserDTO
from src.application.shared.event_bus import EventBus
from src.application.user.commands.create_user import CreateUserHandler
from src.application.user.commands.update_user import UpdateUserHandler
from src.application.user.commands.delete_user import DeleteUserHandler
from src.application.user.queries.get_user import GetUserHandler
from src.application.user.queries.search_users import SearchUsersHandler
from src.domain.auth.auth_service import AuthDomainService
from src.domain.user.repository import UserRepository
from src.infrastructure.auth.auth_domain_service import InfraAuthDomainService
from src.infrastructure.config.settings import get_settings
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories.user_repository import SqlUserRepository
from src.infrastructure.messaging.event_dispatcher import InMemoryEventBus

_bearer_scheme = HTTPBearer(auto_error=False)

# ── 全局单例 ─────────────────────────────────────────

_event_bus: EventBus = InMemoryEventBus()


# ── 共享依赖 ──────────────────────────────────────────


def get_event_bus() -> EventBus:
    """获取事件总线单例。"""
    return _event_bus


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    """获取用户仓储实例（注入 SQLAlchemy Session）。"""
    return SqlUserRepository(session=session)


# ── 认证领域服务 ─────────────────────────────────────


def get_auth_domain_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthDomainService:
    """获取认证领域服务实例。"""
    settings = get_settings()
    return InfraAuthDomainService(
        user_repository=user_repo,
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
        access_token_expire_minutes=settings.auth_access_token_expire_minutes,
    )


# ── 用户 Handler ─────────────────────────────────────


def get_create_user_handler(
    user_repo: UserRepository = Depends(get_user_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateUserHandler:
    return CreateUserHandler(user_repository=user_repo, event_bus=event_bus)


def get_update_user_handler(
    user_repo: UserRepository = Depends(get_user_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateUserHandler:
    return UpdateUserHandler(user_repository=user_repo, event_bus=event_bus)


def get_delete_user_handler(
    user_repo: UserRepository = Depends(get_user_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> DeleteUserHandler:
    return DeleteUserHandler(user_repository=user_repo, event_bus=event_bus)


def get_get_user_handler(
    user_repo: UserRepository = Depends(get_user_repository),
) -> GetUserHandler:
    return GetUserHandler(user_repository=user_repo)


def get_search_users_handler(
    user_repo: UserRepository = Depends(get_user_repository),
) -> SearchUsersHandler:
    return SearchUsersHandler(user_repository=user_repo)


# ── 认证 Handler ─────────────────────────────────────


def get_login_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> LoginHandler:
    return LoginHandler(auth_domain_service=auth_service)


def get_refresh_token_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> RefreshTokenHandler:
    return RefreshTokenHandler(auth_domain_service=auth_service)


def get_logout_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> LogoutHandler:
    return LogoutHandler(auth_domain_service=auth_service)


def get_current_user_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> GetCurrentUserHandler:
    return GetCurrentUserHandler(auth_domain_service=auth_service)


# ── 当前用户 ─────────────────────────────────────────


def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> CurrentUserDTO:
    """解析 Bearer 令牌，返回当前用户。"""
    from fastapi import HTTPException

    if credentials is None:
        raise HTTPException(status_code=401, detail="缺少认证令牌")

    try:
        current_user = auth_service.get_current_user(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")

    return CurrentUserDTO(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=current_user.name,
        role_id=current_user.role_id,
        role_code=current_user.role_code,
        status=current_user.status,
        avatar_url=current_user.avatar_url,
    )