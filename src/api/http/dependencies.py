"""接口层依赖注入。

通过 FastAPI 的 Depends 机制组装 Handler，将基础设施层的实现注入到应用层。
这是 DDD 中「依赖倒置」在接口层的体现。
"""

from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.audit.commands.record_login_log import RecordLoginLogHandler
from src.application.audit.queries.search_login_logs import SearchLoginLogsHandler
from src.application.auth.commands.login import LoginHandler
from src.application.auth.commands.refresh_token import RefreshTokenHandler
from src.application.auth.commands.logout import LogoutHandler
from src.application.auth.queries.get_current_user import GetCurrentUserHandler
from src.application.auth.dto.auth_dto import CurrentUserDTO
from src.application.shared.event_bus import EventBus
from src.application.shared.unit_of_work import UnitOfWork
from src.application.user.commands.create_user import CreateUserHandler
from src.application.user.commands.update_user import UpdateUserHandler
from src.application.user.commands.delete_user import DeleteUserHandler
from src.application.user.queries.get_user import GetUserHandler
from src.application.user.queries.search_users import SearchUsersHandler
from src.application.role.commands.create_role import CreateRoleHandler
from src.application.role.commands.update_role import UpdateRoleHandler
from src.application.role.commands.delete_role import DeleteRoleHandler
from src.application.role.queries.get_role import GetRoleHandler
from src.application.role.queries.search_roles import SearchRolesHandler
from src.constants.messages import MSG_INVALID_OR_EXPIRED_TOKEN, MSG_MISSING_TOKEN
from src.domain.audit.repository import LoginLogRepository
from src.domain.auth.auth_service import AuthDomainService
from src.domain.user.repository import RoleRepository, UserRepository
from src.infrastructure.auth.auth_domain_service import InfraAuthDomainService
from src.core.config import get_settings
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.unit_of_work import SqlUnitOfWork
from src.infrastructure.messaging.event_dispatcher import InMemoryEventBus
from src.core.logger import logger

_bearer_scheme = HTTPBearer(auto_error=False)

# ── 全局单例 ─────────────────────────────────────────

_event_bus: EventBus = InMemoryEventBus()


# ── 共享依赖 ──────────────────────────────────────────


def get_event_bus() -> EventBus:
    """获取事件总线单例。

    Returns:
        EventBus: 事件总线实例
    """
    return _event_bus


def get_uow(session: AsyncSession = Depends(get_session)) -> UnitOfWork:
    """获取工作单元实例（注入异步 Session）。

    Returns:
        UnitOfWork: 工作单元实例
    """
    return SqlUnitOfWork(session=session)


def get_user_repository(uow: UnitOfWork = Depends(get_uow)) -> UserRepository:
    """获取用户仓储实例。

    从 UoW 获取以共享同一 Session，查询处理器使用此依赖。
    """
    return uow.user_repo


def get_role_repository(uow: UnitOfWork = Depends(get_uow)) -> RoleRepository:
    """获取角色仓储实例。

    从 UoW 获取以共享同一 Session，查询处理器使用此依赖。
    """
    return uow.role_repo


def get_login_log_repository(
    uow: UnitOfWork = Depends(get_uow),
) -> LoginLogRepository:
    """获取登录日志仓储实例。

    从 UoW 获取以共享同一 Session，查询处理器使用此依赖。
    """
    return uow.login_log_repo


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """提取 Bearer 令牌字符串。

    Returns:
        str: 访问令牌

    Raises:
        HTTPException: 401 缺少令牌
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail=MSG_MISSING_TOKEN)
    return credentials.credentials


# ── 认证领域服务 ─────────────────────────────────────


def get_auth_domain_service(
    uow: UnitOfWork = Depends(get_uow),
) -> AuthDomainService:
    """获取认证领域服务实例。

    通过 UoW 注入，确保认证操作在同一事务中。
    """
    settings = get_settings()
    return InfraAuthDomainService(
        uow=uow,
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
        access_token_expire_minutes=settings.auth_access_token_expire_minutes,
    )


# ── 用户命令 Handler（通过 UoW 注入）────────────────


def get_create_user_handler(
    uow: UnitOfWork = Depends(get_uow),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateUserHandler:
    """获取创建用户处理器。"""
    return CreateUserHandler(uow=uow, event_bus=event_bus)


def get_update_user_handler(
    uow: UnitOfWork = Depends(get_uow),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateUserHandler:
    """获取更新用户处理器。"""
    return UpdateUserHandler(uow=uow, event_bus=event_bus)


def get_delete_user_handler(
    uow: UnitOfWork = Depends(get_uow),
    event_bus: EventBus = Depends(get_event_bus),
) -> DeleteUserHandler:
    """获取删除用户处理器。"""
    return DeleteUserHandler(uow=uow, event_bus=event_bus)


# ── 用户查询 Handler（通过独立仓储注入）─────────────


def get_get_user_handler(
    user_repo: UserRepository = Depends(get_user_repository),
) -> GetUserHandler:
    """获取查询用户处理器。"""
    return GetUserHandler(user_repository=user_repo)


def get_search_users_handler(
    user_repo: UserRepository = Depends(get_user_repository),
) -> SearchUsersHandler:
    """获取搜索用户处理器。"""
    return SearchUsersHandler(user_repository=user_repo)


# ── 认证 Handler ─────────────────────────────────────


def get_login_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
    uow: UnitOfWork = Depends(get_uow),
) -> LoginHandler:
    """获取登录处理器。"""
    return LoginHandler(auth_domain_service=auth_service, uow=uow)


def get_refresh_token_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> RefreshTokenHandler:
    """获取刷新令牌处理器。"""
    return RefreshTokenHandler(auth_domain_service=auth_service)


def get_logout_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
    uow: UnitOfWork = Depends(get_uow),
) -> LogoutHandler:
    """获取退出登录处理器。"""
    return LogoutHandler(auth_domain_service=auth_service, uow=uow)


def get_current_user_handler(
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> GetCurrentUserHandler:
    """获取当前用户查询处理器。"""
    return GetCurrentUserHandler(auth_domain_service=auth_service)


# ── 审计 Handler ─────────────────────────────────────


def get_search_login_logs_handler(
    login_log_repo: LoginLogRepository = Depends(get_login_log_repository),
) -> SearchLoginLogsHandler:
    """获取搜索登录日志处理器。"""
    return SearchLoginLogsHandler(login_log_repository=login_log_repo)


def get_record_login_log_handler(
    uow: UnitOfWork = Depends(get_uow),
) -> RecordLoginLogHandler:
    """获取记录登录日志处理器。"""
    return RecordLoginLogHandler(uow=uow)


# ── 角色命令 Handler（通过 UoW 注入）────────────────


def get_create_role_handler(
    uow: UnitOfWork = Depends(get_uow),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateRoleHandler:
    """获取创建角色处理器。"""
    return CreateRoleHandler(uow=uow, event_bus=event_bus)


def get_update_role_handler(
    uow: UnitOfWork = Depends(get_uow),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateRoleHandler:
    """获取更新角色处理器。"""
    return UpdateRoleHandler(uow=uow, event_bus=event_bus)


def get_delete_role_handler(
    uow: UnitOfWork = Depends(get_uow),
    event_bus: EventBus = Depends(get_event_bus),
) -> DeleteRoleHandler:
    """获取删除角色处理器。"""
    return DeleteRoleHandler(uow=uow, event_bus=event_bus)


# ── 角色查询 Handler（通过独立仓储注入）─────────────


def get_get_role_handler(
    role_repo: RoleRepository = Depends(get_role_repository),
) -> GetRoleHandler:
    """获取查询角色处理器。"""
    return GetRoleHandler(role_repository=role_repo)


def get_search_roles_handler(
    role_repo: RoleRepository = Depends(get_role_repository),
) -> SearchRolesHandler:
    """获取搜索角色处理器。"""
    return SearchRolesHandler(role_repository=role_repo)


# ── 当前用户 ─────────────────────────────────────────


async def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth_service: AuthDomainService = Depends(get_auth_domain_service),
) -> CurrentUserDTO:
    """解析 Bearer 令牌，返回当前用户。

    Args:
        credentials: HTTP Bearer 令牌
        auth_service: 认证领域服务

    Returns:
        CurrentUserDTO: 当前用户信息

    Raises:
        HTTPException: 401 缺少令牌或令牌无效
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail=MSG_MISSING_TOKEN)

    try:
        current_user = await auth_service.get_current_user(credentials.credentials)
    except Exception as e:
        logger.debug("令牌验证失败: {}", e)
        raise HTTPException(status_code=401, detail=MSG_INVALID_OR_EXPIRED_TOKEN)

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
