"""向后兼容 re-export — 请改用 src.core.logger。"""

from src.core.logger import logger, setup_logging  # noqa: F401

__all__ = ["logger", "setup_logging"]
