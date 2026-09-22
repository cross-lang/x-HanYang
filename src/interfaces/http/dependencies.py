"""接口层依赖注入。

通过 FastAPI 的 Depends 机制组装 Handler，将基础设施层的实现注入到应用层。
这是 DDD 中「依赖倒置」在接口层的体现。
"""

from __future__ import annotations

from functools import lru_cache

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
from src.domain.user.repository import UserRepository
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories.user_repository import SqlUserRepository
from src.infrastructure.messaging.event_dispatcher import InMemoryEventBus

_bearer_scheme = HTTPBearer(auto_error=False)


# ── 共享依赖 ──────────────────────────────────────────


def get_event_bus() -> EventBus:
    """获取事件总线实例。"""
    return InMemoryEventBus()


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    """获取用户仓储实例（注入 SQLAlchemy Session）。"""
    return SqlUserRepository(session=session)


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


def _get_auth_domain_service():
    """获取认证领域服务实现（桩，待实现）。"""
    # TODO: 返回 AuthDomainService 的基础设施实现
    raise NotImplementedError("AuthDomainService 尚未实现")


def get_login_handler() -> LoginHandler:
    return LoginHandler(auth_domain_service=_get_auth_domain_service())


def get_refresh_token_handler() -> RefreshTokenHandler:
    return RefreshTokenHandler(auth_domain_service=_get_auth_domain_service())


def get_logout_handler() -> LogoutHandler:
    return LogoutHandler(auth_domain_service=_get_auth_domain_service())


def get_current_user_handler() -> GetCurrentUserHandler:
    return GetCurrentUserHandler(auth_domain_service=_get_auth_domain_service())


# ── 当前用户 ─────────────────────────────────────────


def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUserDTO:
    """解析 Bearer 令牌，返回当前用户（桩，待实现）。"""
    # TODO: 实现令牌解析逻辑
    return CurrentUserDTO(id=0, username="anonymous", email="anonymous@example.com")
