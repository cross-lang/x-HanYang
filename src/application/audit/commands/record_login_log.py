"""记录登录日志命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.unit_of_work import UnitOfWork
from src.domain.audit.login_log import LoginLog


@dataclass(frozen=True)
class RecordLoginLogCommand:
    """记录登录日志命令。

    Attributes:
        user_id: 登录用户 ID（未识别用户时为 None）
        login_type: 登录方式（如 password、wechat、github）
        status: 登录状态（success、failed）
        ip_address: 客户端 IP 地址
    """

    user_id: int | None
    login_type: str
    status: str
    ip_address: str | None = None


class RecordLoginLogHandler:
    """记录登录日志命令处理器。"""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: RecordLoginLogCommand) -> LoginLog:
        """执行记录登录日志命令。

        Args:
            command: 记录登录日志命令

        Returns:
            LoginLog: 创建的登录日志聚合根
        """
        async with self._uow:
            log = LoginLog(
                user_id=command.user_id,
                login_type=command.login_type,
                status=command.status,
                ip_address=command.ip_address,
            )
            await self._uow.login_log_repo.save(log)
            return log
