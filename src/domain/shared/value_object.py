"""值对象基类。

值对象（Value Object）没有唯一标识，通过属性值判等，具有不可变性。
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):
    """值对象基类。

    所有值对象必须继承此类。frozen=True 保证不可变性。

    子类应通过 __post_init__ 实现自校验，确保值始终合法。

    Example:
        @dataclass(frozen=True)
        class Email(ValueObject):
            value: str

            def __post_init__(self):
                if "@" not in self.value:
                    raise DomainException(f"无效邮箱: {self.value}")
    """

    pass
