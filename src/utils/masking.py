"""敏感数据脱敏工具。"""

from __future__ import annotations

import re

# 需要脱敏的字段名模式（不区分大小写）
_SENSITIVE_PATTERNS: re.Pattern[str] = re.compile(
    r"password|secret|token|key|authorization|cookie|credit_card|id_card",
    re.IGNORECASE,
)

# 邮箱脱敏正则：保留首尾字符，中间替换为 ***
_EMAIL_PATTERN: re.Pattern[str] = re.compile(r"^(.)(.*?)(.)@(.*)$")


def mask_sensitive(data: dict[str, object]) -> dict[str, object]:
    """递归脱敏字典中的敏感字段。

    将匹配敏感关键字的值替换为 "****"。

    Args:
        data: 待脱敏的字典

    Returns:
        dict[str, object]: 脱敏后的字典（新对象）
    """
    result: dict[str, object] = {}
    for key, value in data.items():
        if _SENSITIVE_PATTERNS.search(key):
            result[key] = "****"
        elif isinstance(value, dict):
            result[key] = mask_sensitive(value)
        else:
            result[key] = value
    return result


def mask_email(email: str) -> str:
    """脱敏邮箱地址。

    user@example.com → u***r@example.com

    Args:
        email: 邮箱地址

    Returns:
        str: 脱敏后的邮箱
    """
    match = _EMAIL_PATTERN.match(email)
    if match:
        return f"{match.group(1)}***{match.group(3)}@{match.group(4)}"
    return email
