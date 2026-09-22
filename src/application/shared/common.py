"""应用层公共数据结构。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    """通用分页结果。

    Attributes:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码（从 1 开始）
        page_size: 每页数量
    """

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """总页数。"""
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size
