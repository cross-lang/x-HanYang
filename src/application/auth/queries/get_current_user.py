"""获取当前用户查询及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.auth.dto.auth_dto import CurrentUserDTO
from src.domain.auth.auth_service import AuthDomainService


@dataclass(frozen=True)
class GetCurrentUserQuery:
    """获取当前用户查询。

    Attributes:
        token: 访问令牌
    """

    token: str


class GetCurrentUserHandler:
    """获取当前用户查询处理器。"""

    def __init__(self, auth_domain_service: AuthDomainService) -> None:
        self._auth_service = auth_domain_service

    async def handle(self, query: GetCurrentUserQuery) -> CurrentUserDTO:
        """执行查询。

        Args:
            query: 查询参数

        Returns:
            CurrentUserDTO: 当前用户信息
        """
        current_user = await self._auth_service.get_current_user(query.token)
        return CurrentUserDTO(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            name=current_user.name,
            role_id=current_user.role_id,
            role_code=current_user.role_code,
            status=current_user.status,
            avatar_url=current_user.avatar_url,
        )
