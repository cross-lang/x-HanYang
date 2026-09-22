"""Alembic 环境配置。

注入应用配置中的 DATABASE_URL，并通过 src.infrastructure.persistence.database.Base.metadata
获取模型定义，避免在迁移脚本中重复声明表结构。
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.infrastructure.config.settings import get_settings
from src.infrastructure.persistence.database import Base

# 注册 ORM 映射，确保 Base.metadata 包含所有表
import src.infrastructure.persistence.orm.user_mapping  # noqa: F401
import src.infrastructure.persistence.orm.audit_mapping  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 用应用配置覆盖默认 URL，将异步驱动转换为同步驱动（Alembic 迁移使用同步引擎）
settings = get_settings()
if settings.database_url:
    url = settings.database_url
    url = url.replace("mysql+asyncmy://", "mysql+pymysql://")
    url = url.replace("mysql+aiomysql://", "mysql+pymysql://")
    url = url.replace("sqlite+aiosqlite://", "sqlite://")
    config.set_main_option("sqlalchemy.url", url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：只生成 SQL 脚本，不连数据库。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：直连数据库执行迁移。"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
