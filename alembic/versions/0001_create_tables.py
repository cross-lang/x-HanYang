"""创建初始表结构

Revision ID: 0001
Revises:
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users 表 ──────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("username", sa.String(50), nullable=False, comment="用户名"),
        sa.Column("email", sa.String(100), nullable=False, comment="邮箱"),
        sa.Column("name", sa.String(100), nullable=True, comment="姓名"),
        sa.Column("age", sa.Integer, nullable=True, comment="年龄"),
        sa.Column("password_hash", sa.String(255), nullable=True, comment="密码哈希"),
        sa.Column("phone", sa.String(20), nullable=True, comment="手机号"),
        sa.Column("avatar_url", sa.String(500), nullable=True, comment="头像URL"),
        sa.Column("role_id", sa.BigInteger, nullable=True, comment="主角色ID"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", comment="状态"),
        sa.Column("last_login_at", sa.DateTime, nullable=True, comment="最后登录时间"),
        sa.Column("last_login_ip", sa.String(45), nullable=True, comment="最后登录IP"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="更新时间"),
        sa.Column("deleted_at", sa.DateTime, nullable=True, comment="软删除时间"),
    )
    op.create_index("uk_email", "users", ["email"], unique=True)
    op.create_index("idx_role_id", "users", ["role_id"])

    # ── roles 表 ──────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("role_name", sa.String(50), nullable=False, comment="角色名称"),
        sa.Column("role_code", sa.String(50), nullable=False, comment="角色编码"),
        sa.Column("description", sa.String(255), nullable=True, comment="角色描述"),
        sa.Column("role_type", sa.String(20), nullable=False, server_default="custom", comment="类型"),
        sa.Column("status", sa.String(20), nullable=False, server_default="enabled", comment="状态"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="更新时间"),
        sa.Column("deleted_at", sa.DateTime, nullable=True, comment="软删除时间"),
    )

    # ── permissions 表 ────────────────────────────────
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("perm_code", sa.String(100), nullable=False, comment="权限编码"),
        sa.Column("perm_name", sa.String(100), nullable=False, comment="权限名称"),
        sa.Column("module", sa.String(50), nullable=False, comment="所属模块"),
        sa.Column("operation", sa.String(20), nullable=False, comment="操作类型"),
        sa.Column("description", sa.String(255), nullable=True, comment="权限说明"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0", comment="排序序号"),
    )
    op.create_index("uk_perm_code", "permissions", ["perm_code"], unique=True)
    op.create_index("idx_module", "permissions", ["module"])

    # ── role_permissions 表 ───────────────────────────
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("role_id", sa.BigInteger, nullable=False, comment="角色ID"),
        sa.Column("permission_id", sa.BigInteger, nullable=False, comment="权限ID"),
    )
    op.create_index("idx_rp_role_id", "role_permissions", ["role_id"])
    op.create_index("idx_rp_permission_id", "role_permissions", ["permission_id"])

    # ── audit_logs 表 ─────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("entity_type", sa.String(50), nullable=False, comment="实体类型"),
        sa.Column("entity_id", sa.Integer, nullable=False, comment="实体ID"),
        sa.Column("action", sa.String(20), nullable=False, comment="操作类型"),
        sa.Column("operator_id", sa.Integer, nullable=True, comment="操作人ID"),
        sa.Column("operator_name", sa.String(50), nullable=True, comment="操作人名称"),
        sa.Column("before_data", sa.Text, nullable=True, comment="变更前数据"),
        sa.Column("after_data", sa.Text, nullable=True, comment="变更后数据"),
        sa.Column("ip_address", sa.String(45), nullable=True, comment="IP地址"),
        sa.Column("remarks", sa.String(255), nullable=True, comment="备注"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
    )

    # ── login_logs 表 ─────────────────────────────────
    op.create_table(
        "login_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("user_id", sa.Integer, nullable=True, comment="用户ID"),
        sa.Column("login_type", sa.String(20), nullable=False, comment="登录方式"),
        sa.Column("status", sa.String(20), nullable=False, comment="登录状态"),
        sa.Column("ip_address", sa.String(45), nullable=True, comment="IP地址"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
    )


def downgrade() -> None:
    op.drop_table("login_logs")
    op.drop_table("audit_logs")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
