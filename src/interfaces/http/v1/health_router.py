"""健康检查 API 路由。"""

from fastapi import APIRouter, Request

from src.interfaces.shared.response import success_response

router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="健康检查")
async def health_check(request: Request):
    """健康检查接口。"""
    return success_response({"status": "ok"}, request)
