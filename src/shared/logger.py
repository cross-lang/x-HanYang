"""日志模块。

使用 loguru 提供统一的日志能力。
"""

from __future__ import annotations

import sys

from loguru import logger as _logger

# 移除默认 handler，按需重新配置
_logger.remove()
_logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="INFO",
)

logger = _logger
