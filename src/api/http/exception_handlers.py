"""向后兼容 re-export — 请改用 src.core.exception_handlers。"""

from src.core.exception_handlers import register_exception_handlers  # noqa: F401

__all__ = ["register_exception_handlers"]
