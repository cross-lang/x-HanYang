"""工作单元接口。

工作单元（Unit of Work）管理一个业务用例中的事务边界，
确保多个仓储操作在同一个事务中完成。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType


class UnitOfWork(ABC):
    """工作单元接口。

    使用方式（async with 语句）：
        async with unit_of_work as uow:
            await uow.user_repo.save(user)
            await uow.commit()  # 显式提交
    # 退出 async with 时自动 rollback（未 commit 的情况）
    """

    @abstractmethod
    async def __aenter__(self) -> UnitOfWork:
        """进入工作单元上下文。"""

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """退出工作单元上下文（未提交时自动回滚）。"""

    @abstractmethod
    async def commit(self) -> None:
        """提交事务。"""

    @abstractmethod
    async def rollback(self) -> None:
        """回滚事务。"""
