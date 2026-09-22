"""用户管理 API 路由。

接口层只做请求解析和响应格式化，业务逻辑委托给应用层 Handler。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.application.user.handlers import (
    CreateUserCommand, CreateUserHandler, UpdateUserCommand, UpdateUserHandler,
    DeleteUserCommand, DeleteUserHandler, GetUserQuery, GetUserHandler,
    SearchUsersQuery, SearchUsersHandler,
)
from src.application.auth.handlers import CurrentUserDTO
from src.constants.messages import MSG_USER_DELETED
from src.api.http.dependencies import (
    get_create_user_handler,
    get_update_user_handler,
    get_delete_user_handler,
    get_get_user_handler,
    get_search_users_handler,
    get_current_user_dep,
)
from src.api.http.schemas.user import CreateUserRequest, UpdateUserRequest
from src.api.shared.response import success_response

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("", summary="创建用户", status_code=201)
async def create_user(
    body: CreateUserRequest,
    request: Request,
    handler: CreateUserHandler = Depends(get_create_user_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """创建用户接口。

    Args:
        body: 创建用户请求体
        request: HTTP 请求
        handler: 创建用户处理器
        current_user: 当前用户

    Returns:
        dict: 创建成功的用户信息
    """
    command = CreateUserCommand(
        username=body.username,
        email=body.email,
        password=body.password,
        name=body.name,
        phone=body.phone,
        role_id=body.role_id,
    )
    result = await handler.handle(command)
    return success_response(
        {"id": result.id, "username": result.username, "email": result.email.value},
        request,
        code=201,
    )


@router.get("", summary="用户列表")
async def list_users(
    request: Request,
    keyword: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    handler: SearchUsersHandler = Depends(get_search_users_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """用户列表接口。

    Args:
        request: HTTP 请求
        keyword: 搜索关键字
        status: 状态过滤
        page: 页码
        page_size: 每页数量
        handler: 搜索用户处理器
        current_user: 当前用户

    Returns:
        dict: 分页用户列表
    """
    query = SearchUsersQuery(keyword=keyword, status=status, page=page, page_size=page_size)
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


@router.get("/{user_id}", summary="查询用户")
async def get_user(
    user_id: int,
    request: Request,
    handler: GetUserHandler = Depends(get_get_user_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """查询单个用户接口。

    Args:
        user_id: 用户 ID
        request: HTTP 请求
        handler: 查询用户处理器
        current_user: 当前用户

    Returns:
        dict: 用户详情
    """
    result = await handler.handle(GetUserQuery(user_id=user_id))
    return success_response(vars(result), request)


@router.put("/{user_id}", summary="更新用户")
async def update_user(
    user_id: int,
    body: UpdateUserRequest,
    request: Request,
    handler: UpdateUserHandler = Depends(get_update_user_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """更新用户接口。

    Args:
        user_id: 用户 ID
        body: 更新用户请求体
        request: HTTP 请求
        handler: 更新用户处理器
        current_user: 当前用户

    Returns:
        dict: 更新后的用户信息
    """
    command = UpdateUserCommand(
        user_id=user_id,
        email=body.email,
        name=body.name,
        phone=body.phone,
        avatar_url=body.avatar_url,
        role_id=body.role_id,
        password=body.password,
    )
    result = await handler.handle(command)
    return success_response(
        {"id": result.id, "username": result.username, "email": result.email.value},
        request,
    )


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    request: Request,
    handler: DeleteUserHandler = Depends(get_delete_user_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """删除用户接口（软删除）。

    Args:
        user_id: 用户 ID
        request: HTTP 请求
        handler: 删除用户处理器
        current_user: 当前用户

    Returns:
        dict: 删除成功响应
    """
    await handler.handle(DeleteUserCommand(user_id=user_id))
    return success_response({"message": MSG_USER_DELETED}, request)
