"""审计应用层 — 命令、查询、DTO。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.application.shared.paginated_result import PaginatedResult
from src.application.shared.unit_of_work import UnitOfWork
from src.constants.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from src.domain.audit.login_log import LoginLog
from src.domain.audit.repository import LoginLogRepository


# ══════════════════════════════════════════════════
#  DTO
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class LoginLogDTO:
    """登录日志输出 DTO。"""

    id: int
    user_id: int | None
    login_type: str
    status: str
    ip_address: str | None
    created_at: datetime | None

    @classmethod
    def from_domain(cls, log: LoginLog) -> LoginLogDTO:
        """从领域模型转换。"""
        return cls(
            id=log.id, user_id=log.user_id, login_type=log.login_type,
            status=log.status, ip_address=log.ip_address, created_at=log.created_at,
        )


# ══════════════════════════════════════════════════
#  写操作 — Command + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class RecordLoginLogCommand:
    """记录登录日志命令。"""

    user_id: int | None
    login_type: str
    status: str
    ip_address: str | None = None


class RecordLoginLogHandler:
    """记录登录日志命令处理器。"""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: RecordLoginLogCommand) -> LoginLog:
        """执行记录登录日志命令。"""
        async with self._uow:
            log = LoginLog(
                user_id=command.user_id, login_type=command.login_type,
                status=command.status, ip_address=command.ip_address,
            )
            await self._uow.login_log_repo.save(log)
            return log


# ══════════════════════════════════════════════════
#  读操作 — Query + Handler
# ══════════════════════════════════════════════════

@dataclass(frozen=True)
class SearchLoginLogsQuery:
    """搜索登录日志查询。"""

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
        """执行搜索。"""
        skip = (query.page - 1) * query.page_size
        logs, total = await self._login_log_repo.search(
            keyword=query.keyword, status=query.status, user_id=query.user_id,
            skip=skip, limit=query.page_size,
        )
        items = [LoginLogDTO.from_domain(log) for log in logs]
        return PaginatedResult(items=items, total=total, page=query.page, page_size=query.page_size)
