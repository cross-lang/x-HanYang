"""用户/角色/权限仓储接口。

接口定义在领域层，实现在 infrastructure/persistence/repositories/。
聚合根通过此接口持久化，不感知 SQLAlchemy 或任何存储技术。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.shared.repository import Repository
from src.domain.user.user import User
from src.domain.user.role import Role
from src.domain.user.permission import Permission


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
            tuple[list[User], int]: (用户列表, 终数)
        """


class RoleRepository(ABC):
    """角色仓储接口。

    Role 继承 Entity（非 AggregateRoot），因此独立定义仓储接口。
    """

    @abstractmethod
    async def find_by_id(self, id: int) -> Role | None:
        """根据 ID 查找角色。"""

    @abstractmethod
    async def find_by_role_code(self, role_code: str) -> Role | None:
        """根据角色编码查找角色。

        Args:
            role_code: 角色编码（全局唯一）

        Returns:
            Role | None: 找到的角色，不存在时返回 None
        """

    @abstractmethod
    async def search(
        self,
        keyword: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Role], int]:
        """按条件搜索角色（分页）。

        Args:
            keyword: 关键字（匹配角色名称或编码）
            status: 状态过滤
            skip: 偏移量
            limit: 每页数量

        Returns:
            tuple[list[Role], int]: (角色列表, 总数)
        """

    @abstractmethod
    async def save(self, role: Role) -> None:
        """保存角色（新增或更新）。"""

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """软删除角色。

        Args:
            id: 角色唯一标识

        Returns:
            bool: 是否成功删除
        """


class PermissionRepository(ABC):
    """权限仓储接口。

    Permission 继承 Entity（非 AggregateRoot），因此独立定义仓储接口。
    """

    @abstractmethod
    async def find_by_id(self, id: int) -> Permission | None:
        """根据 ID 查找权限。"""

    @abstractmethod
    async def find_by_perm_code(self, perm_code: str) -> Permission | None:
        """根据权限编码查找权限。

        Args:
            perm_code: 权限编码（全局唯一）

        Returns:
            Permission | None: 找到的权限，不存在时返回 None
        """

    @abstractmethod
    async def search(
        self,
        keyword: str | None = None,
        module: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Permission], int]:
        """按条件搜索权限（分页）。

        Args:
            keyword: 关键字（匹配权限名称或编码）
            module: 模块过滤
            skip: 偏移量
            limit: 每页数量

        Returns:
            tuple[list[Permission], int]: (权限列表, 总数)
        """

    @abstractmethod
    async def save(self, permission: Permission) -> None:
        """保存权限（新增或更新）。"""

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """删除权限。

        Args:
            id: 权限唯一标识

        Returns:
            bool: 是否成功删除
        """
