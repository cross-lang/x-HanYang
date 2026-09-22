"""HTTP 相关常量。"""

from __future__ import annotations

# ── 请求头 ─────────────────────────────────────
HEADER_REQUEST_ID: str = "X-Request-ID"
HEADER_FORWARDED_FOR: str = "X-Forwarded-For"
HEADER_REAL_IP: str = "X-Real-IP"

# ── 文档路由 ────────────────────────────────────
DOCS_URL: str = "/docs"
REDOC_URL: str = "/redoc"
