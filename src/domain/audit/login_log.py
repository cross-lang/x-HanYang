"""登录日志聚合根。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.aggregate_root import AggregateRoot


@dataclass
class LoginLog(AggregateRoot):
    """登录日志聚合根。

    记录用户登录行为，用于安全审计和异常登录检测。

    Attributes:
        user_id: 登录用户 ID（未识别用户时为 None）
        login_type: 登录方式（如 password、wechat、github）
        status: 登录状态（success、failed）
        ip_address: 客户端 IP 地址
        created_at: 创建时间
    """

    user_id: int | None = None
    login_type: str = ""
    status: str = ""
    ip_address: str | None = None
    created_at: datetime | None = None
