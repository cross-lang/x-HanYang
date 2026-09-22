"""搜索角色列表查询及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.role.dto.role_dto import RoleDTO
from src.application.user.dto.user_dto import PaginatedResult
from src.constants.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from src.domain.user.repository import RoleRepository


@dataclass(frozen=True)
class SearchRolesQuery:
    """搜索角色列表查询。

    Attributes:
        keyword: 关键字
        status: 状态过滤
        page: 页码
        page_size: 每页数量
    """

    keyword: str | None = None
    status: str | None = None
    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE


class SearchRolesHandler:
    """搜索角色列表查询处理器。"""

    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repo = role_repository

    async def handle(self, query: SearchRolesQuery) -> PaginatedResult[RoleDTO]:
        """执行搜索。

        Args:
            query: 查询参数

        Returns:
            PaginatedResult[RoleDTO]: 分页结果
        """
        skip = (query.page - 1) * query.page_size
        roles, total = await self._role_repo.search(
            keyword=query.keyword, status=query.status, skip=skip, limit=query.page_size
        )
        items = [RoleDTO.from_domain(r) for r in roles]
        return PaginatedResult(items=items, total=total, page=query.page, page_size=query.page_size)
