"""用户聚合 — 值对象。

值对象不可变（frozen），通过属性值判等。
内含自校验逻辑，确保构造时数据合法。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from src.constants.auth import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
from src.domain.shared.domain_exception import ValidationException
from src.domain.shared.value_object import ValueObject

if TYPE_CHECKING:
    from src.domain.password_hasher import PasswordHasher


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

    使用方式：
        1. 从明文构造：Password.from_raw("my-password")
        2. 从数据库恢复：Password.from_hashed("$2b$...")
        3. 生成哈希：password.hashed(hasher)
        4. 验证密码：password.verify("my-password", hasher)

    Attributes:
        _raw: 原始明文密码（仅在构造时存在）
        _hashed: 密码哈希值
    """

    _raw: str
    _hashed: str = ""

    def __post_init__(self) -> None:
        # 从哈希构造时（_raw 为空）跳过长度校验
        if not self._raw:
            return
        if len(self._raw) < PASSWORD_MIN_LENGTH:
            raise ValidationException(f"密码长度不能少于{PASSWORD_MIN_LENGTH}位")
        if len(self._raw) > PASSWORD_MAX_LENGTH:
            raise ValidationException(f"密码长度不能超过{PASSWORD_MAX_LENGTH}位")

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

    def hashed(self, hasher: "PasswordHasher | None" = None) -> str:
        """获取密码哈希值。

        Args:
            hasher: 密码哈希器（为 None 时使用 bcrypt 兜底，保持向后兼容）

        Returns:
            str: 密码哈希字符串
        """
        if not self._hashed:
            if hasher is not None:
                object.__setattr__(self, "_hashed", hasher.hash(self._raw))
            else:
                # 兜底：直接使用 bcrypt（兼容不传 hasher 的场景）
                import bcrypt
                object.__setattr__(
                    self, "_hashed",
                    bcrypt.hashpw(self._raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                )
        return self._hashed

    def verify(self, plain: str, hasher: "PasswordHasher | None" = None) -> bool:
        """验证明文密码是否匹配。

        Args:
            plain: 待验证的明文密码
            hasher: 密码哈希器（为 None 时使用 bcrypt 兜底）

        Returns:
            bool: 是否匹配
        """
        if hasher is not None:
            return hasher.verify(plain, self._hashed)
        import bcrypt
        return bcrypt.checkpw(plain.encode("utf-8"), self._hashed.encode("utf-8"))
