"""用户 DTO。

DTO（Data Transfer Object）是应用层的输入输出数据结构。
与领域模型解耦，通过 from_domain 方法从领域模型转换。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from src.domain.user.user import User

T = TypeVar("T")


@dataclass
class UserDTO:
    """用户输出 DTO。

    Attributes:
        id: 用户 ID
        username: 用户名
        email: 邮箱
        name: 姓名
        age: 年龄
        phone: 手机号
        avatar_url: 头像 URL
        role_id: 角色 ID
        status: 状态
        last_login_at: 最后登录时间
        last_login_ip: 最后登录 IP
        created_at: 创建时间
        updated_at: 更新时间
    """

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
    def from_domain(cls, user: User) -> UserDTO:
        """从领域模型转换。

        Args:
            user: 用户聚合根

        Returns:
            UserDTO: 用户 DTO
        """
        return cls(
            id=user.id,
            username=user.username,
            email=user.email.value,
            name=user.name,
            age=user.age,
            phone=user.phone,
            avatar_url=user.avatar_url,
            role_id=user.role_id,
            status=user.status.value,
            last_login_at=user.last_login_at,
            last_login_ip=user.last_login_ip,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@dataclass
class PaginatedResult(Generic[T]):
    """分页结果。

    Attributes:
        items: 当前页数据
        total: 总数
        page: 当前页码
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
