"""审计日志 ORM 映射。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.database import Base


class AuditLogTable(Base):
    """审计日志表。"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="实体类型")
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="实体ID")
    action: Mapped[str] = mapped_column(String(20), nullable=False, comment="操作类型")
    operator_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="操作人ID")
    operator_name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="操作人名称")
    before_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="变更前数据")
    after_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="变更后数据")
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="IP地址")
    remarks: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )


class LoginLogTable(Base):
    """登录日志表。"""

    __tablename__ = "login_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="用户ID")
    login_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="登录方式")
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment="登录状态")
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="IP地址")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
