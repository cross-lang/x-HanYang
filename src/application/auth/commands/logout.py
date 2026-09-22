"""退出登录命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.shared.unit_of_work import UnitOfWork
from src.domain.auth.auth_service import AuthDomainService


@dataclass(frozen=True)
class LogoutCommand:
    """退出登录命令。

    Attributes:
        user_id: 用户 ID
        token: 访问令牌（用于加入黑名单）
    """

    user_id: int
    token: str


class LogoutHandler:
    """退出登录命令处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService, uow: UnitOfWork) -> None:
        self._auth_service = auth_domain_service
        self._uow = uow

    async def handle(self, command: LogoutCommand) -> None:
        """执行退出登录。

        Args:
            command: 退出登录命令
        """
        async with self._uow:
            await self._auth_service.logout(command.user_id, command.token)
