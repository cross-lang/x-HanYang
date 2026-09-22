"""用户管理请求 Schema。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    """创建用户请求。

    Attributes:
        username: 用户名
        email: 邮箱
        password: 明文密码
        name: 姓名
        phone: 手机号
        role_id: 角色 ID
    """

    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: str = Field(..., min_length=1, max_length=100, description="邮箱")
    password: str = Field(..., min_length=8, max_length=128, description="明文密码")
    name: str | None = Field(None, max_length=100, description="姓名")
    phone: str | None = Field(None, max_length=20, description="手机号")
    role_id: int | None = Field(None, description="角色 ID")


class UpdateUserRequest(BaseModel):
    """更新用户请求。

    Attributes:
        email: 新邮箱
        name: 姓名
        phone: 手机号
        avatar_url: 头像 URL
        role_id: 角色 ID
        password: 新密码
    """

    email: str | None = Field(None, max_length=100, description="新邮箱")
    name: str | None = Field(None, max_length=100, description="姓名")
    phone: str | None = Field(None, max_length=20, description="手机号")
    avatar_url: str | None = Field(None, max_length=500, description="头像 URL")
    role_id: int | None = Field(None, description="角色 ID")
    password: str | None = Field(None, min_length=8, max_length=128, description="新密码")
