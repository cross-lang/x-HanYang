"""角色实体。

角色（Role）是用户聚合内的实体，通过聚合根 User 间接管理。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.domain.shared.entity import Entity


class RoleType(str, Enum):
    """角色类型。"""

    SYSTEM = "system"
    CUSTOM = "custom"


class RoleStatus(str, Enum):
    """角色状态。"""

    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass
class Role(Entity):
    """角色实体。

    Attributes:
        role_name: 角色名称
        role_code: 角色编码（全局唯一）
        description: 角色描述
        role_type: 角色类型
        status: 角色状态
    """

    role_name: str = ""
    role_code: str = ""
    description: str | None = None
    role_type: RoleType = RoleType.CUSTOM
    status: RoleStatus = RoleStatus.ENABLED
