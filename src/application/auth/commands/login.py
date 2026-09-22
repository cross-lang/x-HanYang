"""登录命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.auth.dto.auth_dto import TokenPairDTO
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.auth.auth_service import AuthDomainService


@dataclass(frozen=True)
class LoginCommand:
    """登录命令。

    Attributes:
        account: 用户名或邮箱
        password: 明文密码
        ip_address: 客户端 IP
    """

    account: str
    password: str
    ip_address: str | None = None


class LoginHandler:
    """登录命令处理器。

    编排认证领域服务完成登录流程。
    """

    def __init__(self, auth_domain_service: AuthDomainService, uow: UnitOfWork) -> None:
        self._auth_service = auth_domain_service
        self._uow = uow

    async def handle(self, command: LoginCommand) -> TokenPairDTO:
        """执行登录。

        Args:
            command: 登录命令

        Returns:
            TokenPairDTO: 令牌对
        """
        async with self._uow:
            token_pair = await self._auth_service.authenticate(
                account=command.account,
                password=command.password,
                ip_address=command.ip_address,
            )
        return TokenPairDTO(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type=token_pair.token_type,
            expires_in=token_pair.expires_in,
        )
