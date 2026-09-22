"""工作单元接口。

工作单元（Unit of Work）管理一个业务用例中的事务边界，
确保多个仓储操作在同一个事务中完成。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class UnitOfWork(ABC):
    """工作单元接口。

    使用方式（with 语句）：
        with unit_of_work as uow:
            user_repo.save(user)
            audit_repo.save(audit_log)
            uow.commit()  # 显式提交
    # 退出 with 时自动 rollback（未 commit 的情况）
    """

    @abstractmethod
    def __enter__(self) -> UnitOfWork:
        """进入工作单元上下文。"""

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出工作单元上下文（未提交时自动回滚）。"""

    @abstractmethod
    def commit(self) -> None:
        """提交事务。"""

    @abstractmethod
    def rollback(self) -> None:
        """回滚事务。"""
