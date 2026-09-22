"""向后兼容 re-export — 请改用 src.core.seed。"""

from src.core.seed import init_seed_data  # noqa: F401

__all__ = ["init_seed_data"]
