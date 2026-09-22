"""审计日志聚合根。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.aggregate_root import AggregateRoot


@dataclass
class AuditLog(AggregateRoot):
    """审计日志聚合根。

    记录系统中所有数据变更操作，用于安全审计和问题追溯。

    Attributes:
        entity_type: 被操作的实体类型（如 user、role）
        entity_id: 被操作的实体 ID
        action: 操作类型（create、update、delete）
        operator_id: 操作人 ID
        operator_name: 操作人用户名
        before_data: 变更前数据（JSON）
        after_data: 变更后数据（JSON）
        ip_address: 操作人 IP 地址
        remarks: 备注
        created_at: 创建时间
    """

    entity_type: str = ""
    entity_id: int = 0
    action: str = ""
    operator_id: int | None = None
    operator_name: str | None = None
    before_data: dict | None = None
    after_data: dict | None = None
    ip_address: str | None = None
    remarks: str | None = None
    created_at: datetime | None = None
