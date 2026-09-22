"""用户 DTO。

DTO（Data Transfer Object）是应用层的输入输出数据结构。
与领域模型解耦，通过 from_domain / to_domain 方法双向转换。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class UserDTO:
    """用户输出 DTO。"""

    id: int
    username: str
    email: str
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    avatar_url: str | None = None
    role_id: int | None = None
    status: str = "active"
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, user: object) -> UserDTO:
        """从领域模型转换。

        Args:
            user: 用户聚合根

        Returns:
            UserDTO: 用户 DTO
        """
        return cls(
            id=user.id,
            username=user.username,
            email=user.email.value if hasattr(user.email, "value") else str(user.email),
            name=user.name,
            age=user.age,
            phone=user.phone,
            avatar_url=user.avatar_url,
            role_id=user.role_id,
            status=user.status.value if hasattr(user.status, "value") else str(user.status),
            last_login_at=user.last_login_at,
            last_login_ip=user.last_login_ip,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@dataclass
class PaginatedResult(Generic[T]):
    """分页结果。"""

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
