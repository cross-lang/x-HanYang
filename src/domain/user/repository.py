"""用户仓储接口。

接口定义在领域层，实现在 infrastructure/persistence/repositories/。
聚合根通过此接口持久化，不感知 SQLAlchemy 或任何存储技术。
"""

from __future__ import annotations

from abc import abstractmethod

from src.domain.shared.repository import Repository
from src.domain.user.user import User


class UserRepository(Repository[User]):
    """用户仓储接口。

    继承 Repository[User] 提供的基础 CRUD，扩展用户特有的查询。
    所有方法均为异步。
    """

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """根据邮箱查找用户。

        Args:
            email: 邮箱地址

        Returns:
            User | None: 找到的用户，不存在时返回 None
        """

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """根据用户名查找用户。

        Args:
            username: 用户名

        Returns:
            User | None: 找到的用户，不存在时返回 None
        """

    @abstractmethod
    async def search(
        self,
        keyword: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        """按条件搜索用户（分页）。

        Args:
            keyword: 关键字（匹配用户名或邮箱）
            status: 状态过滤
            skip: 偏移量
            limit: 每页数量

        Returns:
            tuple[list[User], int]: (用户列表, 总数)
        """
