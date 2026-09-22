"""仓储接口基类。

仓储接口定义在领域层（依赖倒置），实现在基础设施层。
聚合根通过仓储接口持久化，不感知底层存储技术。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.domain.shared.aggregate_root import AggregateRoot

T = TypeVar("T", bound=AggregateRoot)


class Repository(ABC, Generic[T]):
    """仓储接口基类。

    子类必须指定聚合根类型 T，并实现所有抽象方法。
    接口方法均为异步，以适配异步数据库驱动。

    Example:
        class UserRepository(Repository[User]):
            async def find_by_id(self, id: int) -> User | None: ...
            async def save(self, user: User) -> None: ...
    """

    @abstractmethod
    async def find_by_id(self, id: int) -> T | None:
        """根据 ID 查找聚合根。

        Args:
            id: 聚合根唯一标识

        Returns:
            T | None: 找到的聚合根，不存在时返回 None
        """

    @abstractmethod
    async def save(self, aggregate: T) -> None:
        """保存聚合根（新增或更新）。

        Args:
            aggregate: 要保存的聚合根
        """

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """删除聚合根。

        Args:
            id: 聚合根唯一标识

        Returns:
            bool: 是否成功删除
        """
