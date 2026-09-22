"""获取用户详情查询及处理器。"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.user.dto.user_dto import UserDTO
from src.domain.user.repository import UserRepository
from src.domain.shared.domain_exception import EntityNotFoundException


@dataclass(frozen=True)
class GetUserQuery:
    """获取用户详情查询。"""

    user_id: int


class GetUserHandler:
    """获取用户详情查询处理器。"""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    def handle(self, query: GetUserQuery) -> UserDTO:
        """执行查询。

        Args:
            query: 查询参数

        Returns:
            UserDTO: 用户详情

        Raises:
            EntityNotFoundException: 用户不存在
        """
        user = self._user_repo.find_by_id(query.user_id)
        if user is None:
            raise EntityNotFoundException(f"用户 {query.user_id} 不存在")
        return UserDTO.from_domain(user)
