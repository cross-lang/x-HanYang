"""角色管理请求 Schema。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateRoleRequest(BaseModel):
    """创建角色请求。

    Attributes:
        role_name: 角色名称
        role_code: 角色编码（全局唯一）
        description: 角色描述
        role_type: 角色类型
    """

    role_name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    role_code: str = Field(..., min_length=1, max_length=50, description="角色编码")
    description: str | None = Field(None, max_length=255, description="角色描述")
    role_type: str = Field("custom", description="角色类型: system | custom")


class UpdateRoleRequest(BaseModel):
    """更新角色请求。

    Attributes:
        role_name: 角色名称
        description: 角色描述
        status: 角色状态
    """

    role_name: str | None = Field(None, max_length=50, description="角色名称")
    description: str | None = Field(None, max_length=255, description="角色描述")
    status: str | None = Field(None, description="角色状态: enabled | disabled")
