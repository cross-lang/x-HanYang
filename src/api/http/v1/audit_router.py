"""审计 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.application.audit.handlers import SearchLoginLogsQuery, SearchLoginLogsHandler
from src.application.auth.handlers import CurrentUserDTO
from src.api.http.dependencies import (
    get_search_login_logs_handler,
    get_current_user_dep,
)
from src.api.http.response import success_response

router = APIRouter(prefix="/audit", tags=["审计日志"])


@router.get("/login-logs", summary="登录日志列表")
async def list_login_logs(
    request: Request,
    keyword: str | None = None,
    status: str | None = None,
    user_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
    handler: SearchLoginLogsHandler = Depends(get_search_login_logs_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """登录日志列表接口。

    Args:
        request: HTTP 请求
        keyword: 搜索关键字（匹配 IP 地址）
        status: 登录状态过滤（success、failed）
        user_id: 用户 ID 过滤
        page: 页码
        page_size: 每页数量
        handler: 搜索登录日志处理器
        current_user: 当前用户

    Returns:
        dict: 分页登录日志列表
    """
    query = SearchLoginLogsQuery(
        keyword=keyword,
        status=status,
        user_id=user_id,
        page=page,
        page_size=page_size,
    )
    result = await handler.handle(query)
    return success_response(
        {
            "items": [vars(item) for item in result.items],
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
        },
        request,
    )
