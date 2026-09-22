"""刷新令牌命令及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.auth.dto.auth_dto import TokenPairDTO
from src.domain.auth.auth_service import AuthDomainService


@dataclass(frozen=True)
class RefreshTokenCommand:
    """刷新令牌命令。"""

    refresh_token: str


class RefreshTokenHandler:
    """刷新令牌命令处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService) -> None:
        self._auth_service = auth_domain_service

    def handle(self, command: RefreshTokenCommand) -> TokenPairDTO:
        """执行令牌刷新。

        Args:
            command: 刷新令牌命令

        Returns:
            TokenPairDTO: 新的令牌对
        """
        token_pair = self._auth_service.refresh_tokens(command.refresh_token)
        return TokenPairDTO(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type=token_pair.token_type,
            expires_in=token_pair.expires_in,
        )
