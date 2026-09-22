"""应用配置。

使用 pydantic-settings 从环境变量 / .env 文件加载配置。
集中管理所有配置项，避免散落在各处。
"""

from __future__ import annotations

import logging
from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 已知弱密钥列表（生产环境禁止使用）
_WEAK_SECRET_KEYS: frozenset[str] = frozenset({
    "change-me", "change-me-to-a-random-string", "change-me-jwt-secret",
    "secret", "default", "password", "123456",
})

logger = logging.getLogger(__name__)


class AppSettings(BaseSettings):
    """应用配置。

    Attributes:
        app_env: 运行环境（development/production）
        app_debug: 是否启用调试模式
        server_host: 监听地址
        server_port: 监听端口
        server_workers: 工作进程数
        server_debug: 服务器调试模式
        database_url: 数据库连接 URL
        redis_url: Redis 连接 URL
        auth_secret_key: JWT 签名密钥
        auth_algorithm: JWT 签名算法
        auth_access_token_expire_minutes: 访问令牌过期时间（分钟）
        cors_origins: CORS 允许的来源
        storage_provider: 存储提供者类型
        storage_local_path: 本地存储路径
        password_reset_token_expire_minutes: 密码重置令牌过期时间
        password_reset_max_attempts_per_hour: 密码重置每小时最大尝试次数
        rate_limit_default: 默认速率限制
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── 应用 ─────────────────────────────────────
    app_env: str = "development"
    app_debug: bool = False

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

    # ── 限流 ─────────────────────────────────────
    rate_limit_default: str = "60/minute"

    # ── SMTP ─────────────────────────────────────
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "HanYang"
    smtp_from_address: str = ""
    smtp_use_tls: bool = True

    # ── HTTP 客户端 ──────────────────────────────
    http_timeout: int = 30
    http_max_retries: int = 3

    @property
    def is_production(self) -> bool:
        """判断是否为生产环境。

        Returns:
            bool: 是否为生产环境
        """
        return self.app_env == "production"

    @model_validator(mode="after")
    def validate_production_safety(self) -> "AppSettings":
        """生产环境安全校验。

        在生产环境下检查危险配置并发出警告。

        Returns:
            AppSettings: 配置实例

        Raises:
            ValueError: 生产环境存在严重安全问题时抛出
        """
        if not self.is_production:
            return self

        # 检查 JWT 密钥
        if self.auth_secret_key in _WEAK_SECRET_KEYS:
            raise ValueError(
                f"生产环境禁止使用弱 JWT 密钥: '{self.auth_secret_key}'。"
                "请设置 AUTH_SECRET_KEY 环境变量为至少 32 位的随机字符串。"
            )
        if len(self.auth_secret_key) < 32:
            logger.warning("JWT 密钥长度不足 32 位，建议使用更长的随机密钥。")

        # 检查 CORS
        if "*" in self.cors_origins:
            raise ValueError("生产环境禁止 CORS 来源设置为 '*'。")

        # 检查调试模式
        if self.app_debug:
            logger.warning("生产环境检测到调试模式已启用，建议关闭。")

        # 检查数据库
        if not self.database_url:
            raise ValueError("生产环境必须配置 DATABASE_URL。")

        return self


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """获取全局配置实例（缓存）。

    Returns:
        AppSettings: 配置实例
    """
    return AppSettings()
