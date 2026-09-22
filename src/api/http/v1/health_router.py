"""健康检查 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Request

from src.api.shared.response import success_response

router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="健康检查")
async def health_check(request: Request) -> dict:
    """健康检查接口。

    Returns:
        dict: 健康状态响应
    """
    return success_response({"status": "ok"}, request)
