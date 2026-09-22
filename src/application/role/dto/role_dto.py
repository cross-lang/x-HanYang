"""角色 DTO。"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.user.role import Role


@dataclass(frozen=True)
class RoleDTO:
    """角色输出 DTO。

    Attributes:
        id: 角色 ID
        role_name: 角色名称
        role_code: 角色编码
        description: 角色描述
        role_type: 角色类型
        status: 角色状态
    """

    id: int
    role_name: str
    role_code: str
    description: str | None = None
    role_type: str = "custom"
    status: str = "enabled"

    @classmethod
    def from_domain(cls, role: Role) -> RoleDTO:
        """从领域模型转换。

        Args:
            role: 角色实体

        Returns:
            RoleDTO: 角色 DTO
        """
        return cls(
            id=role.id,
            role_name=role.role_name,
            role_code=role.role_code,
            description=role.description,
            role_type=role.role_type.value,
            status=role.status.value,
        )
