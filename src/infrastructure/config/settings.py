"""应用配置。

使用 pydantic-settings 从环境变量 / .env 文件加载配置。
集中管理所有配置项，避免散落在各处。
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """应用配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── 应用 ─────────────────────────────────────
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str = "change-me"

    # ── 服务器 ───────────────────────────────────
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_workers: int = 1
    server_debug: bool = False

    # ── 数据库 ───────────────────────────────────
    database_url: str = ""

    # ── Redis ────────────────────────────────────
    redis_url: str = ""

    # ── 认证 ─────────────────────────────────────
    auth_secret_key: str = "change-me-jwt-secret"
    auth_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = 10080  # 7 天

    # ── CORS ─────────────────────────────────────
    cors_origins: list[str] = Field(default=["http://localhost:3000"])

    # ── 存储 ─────────────────────────────────────
    storage_provider: str = "local"
    storage_local_path: str = "./uploads"

    # ── 密码重置 ─────────────────────────────────
    password_reset_token_expire_minutes: int = 30
    password_reset_max_attempts_per_hour: int = 5

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """获取全局配置实例（缓存）。"""
    return AppSettings()
