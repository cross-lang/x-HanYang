"""退出登录命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.auth.auth_service import AuthDomainService


@dataclass(frozen=True)
class LogoutCommand:
    """退出登录命令。

    Attributes:
        user_id: 用户 ID
    """

    user_id: int


class LogoutHandler:
    """退出登录命令处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService) -> None:
        self._auth_service = auth_domain_service

    async def handle(self, command: LogoutCommand) -> None:
        """执行退出登录。

        Args:
            command: 退出登录命令
        """
        await self._auth_service.logout(command.user_id)
