"""获取角色详情查询及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.role.dto.role_dto import RoleDTO
from src.domain.user.repository import RoleRepository
from src.domain.shared.domain_exception import EntityNotFoundException


@dataclass(frozen=True)
class GetRoleQuery:
    """获取角色详情查询。

    Attributes:
        role_id: 角色 ID
    """

    role_id: int


class GetRoleHandler:
    """获取角色详情查询处理器。"""

    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repo = role_repository

    async def handle(self, query: GetRoleQuery) -> RoleDTO:
        """执行查询。

        Args:
            query: 查询参数

        Returns:
            RoleDTO: 角色详情

        Raises:
            EntityNotFoundException: 角色不存在
        """
        role = await self._role_repo.find_by_id(query.role_id)
        if role is None:
            raise EntityNotFoundException(f"角色 {query.role_id} 不存在")
        return RoleDTO.from_domain(role)
