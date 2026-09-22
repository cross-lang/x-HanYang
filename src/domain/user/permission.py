"""权限实体。

权限（Permission）是用户聚合内的实体，描述对模块的操作能力。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.shared.entity import Entity


@dataclass
class Permission(Entity):
    """权限实体。

    Attributes:
        perm_code: 权限编码（全局唯一，如 user:create）
        perm_name: 权限名称
        module: 所属模块
        operation: 操作类型
        description: 权限说明
        sort_order: 排序序号
    """

    perm_code: str = ""
    perm_name: str = ""
    module: str = ""
    operation: str = ""
    description: str | None = None
    sort_order: int = 0
