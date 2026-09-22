"""角色应用层 — 命令、查询、DTO。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.event_bus import EventBus
from src.application.shared.paginated_result import PaginatedResult
from src.application.shared.unit_of_work import UnitOfWork
from src.constants.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from src.domain.user.role import Role, RoleType, RoleStatus
from src.domain.user.repository import RoleRepository
from src.domain.shared.domain_exception import ConflictException, EntityNotFoundException


# ══════════════════════════════════════════════════
#  DTO
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class RoleDTO:
    """角色输出 DTO。"""

    id: int
    role_name: str
    role_code: str
    description: str | None = None
    role_type: str = "custom"
    status: str = "enabled"

    @classmethod
    def from_domain(cls, role: Role) -> RoleDTO:
        """从领域模型转换。"""
        return cls(
            id=role.id, role_name=role.role_name, role_code=role.role_code,
            description=role.description, role_type=role.role_type.value, status=role.status.value,
        )


# ══════════════════════════════════════════════════
#  写操作 — Command + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class CreateRoleCommand:
    """创建角色命令。"""

    role_name: str
    role_code: str
    description: str | None = None
    role_type: str = "custom"


class CreateRoleHandler:
    """创建角色命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: CreateRoleCommand) -> Role:
        """执行创建角色命令。

        Raises:
            ConflictException: 角色编码已存在
        """
        async with self._uow:
            if await self._uow.role_repo.find_by_role_code(command.role_code) is not None:
                raise ConflictException(f"角色编码 {command.role_code} 已存在")
            role = Role(
                role_name=command.role_name, role_code=command.role_code,
                description=command.description, role_type=RoleType(command.role_type),
            )
            await self._uow.role_repo.save(role)
            return role


@dataclass(frozen=True)
class UpdateRoleCommand:
    """更新角色命令。"""

    role_id: int
    role_name: str | None = None
    description: str | None = None
    status: str | None = None


class UpdateRoleHandler:
    """更新角色命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: UpdateRoleCommand) -> Role:
        """执行更新角色命令。

        Raises:
            EntityNotFoundException: 角色不存在
        """
        async with self._uow:
            role = await self._uow.role_repo.find_by_id(command.role_id)
            if role is None:
                raise EntityNotFoundException(f"角色 {command.role_id} 不存在")
            if command.role_name is not None:
                role.role_name = command.role_name
            if command.description is not None:
                role.description = command.description
            if command.status is not None:
                role.status = RoleStatus(command.status)
            await self._uow.role_repo.save(role)
            return role


@dataclass(frozen=True)
class DeleteRoleCommand:
    """删除角色命令。"""

    role_id: int


class DeleteRoleHandler:
    """删除角色命令处理器。"""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: DeleteRoleCommand) -> bool:
        """执行删除角色命令（软删除）。"""
        async with self._uow:
            role = await self._uow.role_repo.find_by_id(command.role_id)
            if role is None:
                raise EntityNotFoundException(f"角色 {command.role_id} 不存在")
            return await self._uow.role_repo.delete(command.role_id)


# ══════════════════════════════════════════════════
#  读操作 — Query + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class GetRoleQuery:
    """获取角色详情查询。"""

    role_id: int


class GetRoleHandler:
    """获取角色详情查询处理器。"""

    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repo = role_repository

    async def handle(self, query: GetRoleQuery) -> RoleDTO:
        """执行查询。

        Raises:
            EntityNotFoundException: 角色不存在
        """
        role = await self._role_repo.find_by_id(query.role_id)
        if role is None:
            raise EntityNotFoundException(f"角色 {query.role_id} 不存在")
        return RoleDTO.from_domain(role)


@dataclass(frozen=True)
class SearchRolesQuery:
    """搜索角色列表查询。"""

    keyword: str | None = None
    status: str | None = None
    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE


class SearchRolesHandler:
    """搜索角色列表查询处理器。"""

    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repo = role_repository

    async def handle(self, query: SearchRolesQuery) -> PaginatedResult[RoleDTO]:
        """执行搜索。"""
        skip = (query.page - 1) * query.page_size
        roles, total = await self._role_repo.search(
            keyword=query.keyword, status=query.status, skip=skip, limit=query.page_size,
        )
        items = [RoleDTO.from_domain(r) for r in roles]
        return PaginatedResult(items=items, total=total, page=query.page, page_size=query.page_size)
