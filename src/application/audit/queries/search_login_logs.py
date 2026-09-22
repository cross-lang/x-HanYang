"""搜索登录日志查询及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.audit.dto.login_log_dto import LoginLogDTO
from src.application.shared.paginated_result import PaginatedResult
from src.constants.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from src.domain.audit.repository import LoginLogRepository


@dataclass(frozen=True)
class SearchLoginLogsQuery:
    """搜索登录日志查询。

    Attributes:
        keyword: 关键字（匹配 IP 地址）
        status: 登录状态过滤（success、failed）
        user_id: 用户 ID 过滤
        page: 页码（从 1 开始）
        page_size: 每页数量
    """

    keyword: str | None = None
    status: str | None = None
    user_id: int | None = None
    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE


class SearchLoginLogsHandler:
    """搜索登录日志查询处理器。"""

    def __init__(self, login_log_repository: LoginLogRepository) -> None:
        self._login_log_repo = login_log_repository

    async def handle(self, query: SearchLoginLogsQuery) -> PaginatedResult[LoginLogDTO]:
        """执行搜索。

        Args:
            query: 查询参数

        Returns:
            PaginatedResult[LoginLogDTO]: 分页结果
        """
        skip = (query.page - 1) * query.page_size
        logs, total = await self._login_log_repo.search(
            keyword=query.keyword,
            status=query.status,
            user_id=query.user_id,
            skip=skip,
            limit=query.page_size,
        )
        items = [LoginLogDTO.from_domain(log) for log in logs]
        return PaginatedResult(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
        )
