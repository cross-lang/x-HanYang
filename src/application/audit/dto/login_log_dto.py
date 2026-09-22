"""登录日志 DTO。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.audit.login_log import LoginLog


@dataclass(frozen=True)
class LoginLogDTO:
    """登录日志输出 DTO。

    Attributes:
        id: 日志 ID
        user_id: 用户 ID
        login_type: 登录方式
        status: 登录状态
        ip_address: 客户端 IP
        created_at: 创建时间
    """

    id: int
    user_id: int | None
    login_type: str
    status: str
    ip_address: str | None
    created_at: datetime | None

    @classmethod
    def from_domain(cls, log: LoginLog) -> LoginLogDTO:
        """从领域模型转换。

        Args:
            log: 登录日志聚合根

        Returns:
            LoginLogDTO: 登录日志 DTO
        """
        return cls(
            id=log.id,
            user_id=log.user_id,
            login_type=log.login_type,
            status=log.status,
            ip_address=log.ip_address,
            created_at=log.created_at,
        )
