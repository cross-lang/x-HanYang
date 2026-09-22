"""用户聚合 — 值对象。

值对象不可变（frozen），通过属性值判等。
内含自校验逻辑，确保构造时数据合法。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from src.domain.shared.domain_exception import ValidationException
from src.domain.shared.value_object import ValueObject


# ── 枚举 ─────────────────────────────────────────────────


class UserStatus(str, Enum):
    """用户状态枚举。"""

    ACTIVE = "active"
    LOCKED = "locked"


# ── 值对象 ───────────────────────────────────────────────


@dataclass(frozen=True)
class Email(ValueObject):
    """邮箱值对象。

    构造时自动校验格式，非法邮箱在实例化阶段即被拒绝。

    Attributes:
        value: 邮箱地址字符串
    """

    value: str

    def __post_init__(self) -> None:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.value):
            raise ValidationException(f"无效邮箱格式: {self.value}")


@dataclass(frozen=True)
class Password(ValueObject):
    """密码值对象。

    封装密码的明文和哈希值，提供密码强度校验。
    哈希操作延迟到首次调用 hashed() 时执行。

    Attributes:
        _raw: 原始明文密码（仅在构造时存在）
        _hashed: 密码哈希值
    """

    _raw: str
    _hashed: str = ""

    def __post_init__(self) -> None:
        if len(self._raw) < 8:
            raise ValidationException("密码长度不能少于8位")
        if len(self._raw) > 128:
            raise ValidationException("密码长度不能超过128位")

    @classmethod
    def from_raw(cls, raw: str) -> Password:
        """从明文密码构造（含强度校验）。

        Args:
            raw: 原始明文密码

        Returns:
            Password: 密码值对象
        """
        return cls(_raw=raw)

    @classmethod
    def from_hashed(cls, hashed: str) -> Password:
        """从已哈希的密码构造（从数据库恢复时使用）。

        Args:
            hashed: 已哈希的密码字符串

        Returns:
            Password: 密码值对象
        """
        return cls(_raw="", _hashed=hashed)

    def hashed(self) -> str:
        """获取密码哈希值。

        Returns:
            str: 密码哈希字符串
        """
        if not self._hashed:
            # 延迟导入，避免 domain 层直接依赖 shared.security
            from src.shared.security import hash_password

            object.__setattr__(self, "_hashed", hash_password(self._raw))
        return self._hashed

    def verify(self, plain: str) -> bool:
        """验证明文密码是否匹配。

        Args:
            plain: 待验证的明文密码

        Returns:
            bool: 是否匹配
        """
        from src.shared.security import verify_password

        return verify_password(plain, self._hashed)
