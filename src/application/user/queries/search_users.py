"""搜索用户列表查询及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.user.dto.user_dto import UserDTO, PaginatedResult
from src.domain.user.repository import UserRepository


@dataclass(frozen=True)
class SearchUsersQuery:
    """搜索用户列表查询。"""

    keyword: str | None = None
    status: str | None = None
    page: int = 1
    page_size: int = 20


class SearchUsersHandler:
    """搜索用户列表查询处理器。"""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    def handle(self, query: SearchUsersQuery) -> PaginatedResult[UserDTO]:
        """执行搜索。

        Args:
            query: 查询参数

        Returns:
            PaginatedResult[UserDTO]: 分页结果
        """
        skip = (query.page - 1) * query.page_size
        users, total = self._user_repo.search(
            keyword=query.keyword,
            status=query.status,
            skip=skip,
            limit=query.page_size,
        )
        items = [UserDTO.from_domain(u) for u in users]
        return PaginatedResult(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
        )
