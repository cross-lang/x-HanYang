"""用户管理 API 路由。

接口层只做请求解析和响应格式化，业务逻辑委托给应用层 Handler。
"""

from fastapi import APIRouter, Depends, Request

from src.application.user.commands.create_user import CreateUserCommand, CreateUserHandler
from src.application.user.commands.update_user import UpdateUserCommand, UpdateUserHandler
from src.application.user.commands.delete_user import DeleteUserCommand, DeleteUserHandler
from src.application.user.queries.get_user import GetUserQuery, GetUserHandler
from src.application.user.queries.search_users import SearchUsersQuery, SearchUsersHandler
from src.interfaces.http.dependencies import (
    get_create_user_handler,
    get_update_user_handler,
    get_delete_user_handler,
    get_get_user_handler,
    get_search_users_handler,
    get_current_user_dep,
)
from src.interfaces.shared.response import success_response
from src.application.auth.dto.auth_dto import CurrentUserDTO

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("", summary="创建用户", status_code=201)
async def create_user(
    body: dict,
    request: Request,
    handler: CreateUserHandler = Depends(get_create_user_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
):
    """创建用户接口。"""
    command = CreateUserCommand(**body)
    result = handler.handle(command)
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
):
    """用户列表接口。"""
    query = SearchUsersQuery(keyword=keyword, status=status, page=page, page_size=page_size)
    result = handler.handle(query)
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
):
    """查询单个用户接口。"""
    result = handler.handle(GetUserQuery(user_id=user_id))
    return success_response(vars(result), request)


@router.post("/{user_id}/update", summary="更新用户")
async def update_user(
    user_id: int,
    body: dict,
    request: Request,
    handler: UpdateUserHandler = Depends(get_update_user_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
):
    """更新用户接口。"""
    command = UpdateUserCommand(user_id=user_id, **body)
    result = handler.handle(command)
    return success_response(
        {"id": result.id, "username": result.username, "email": result.email.value},
        request,
    )


@router.post("/{user_id}/delete", summary="删除用户")
async def delete_user(
    user_id: int,
    request: Request,
    handler: DeleteUserHandler = Depends(get_delete_user_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
):
    """删除用户接口（软删除）。"""
    handler.handle(DeleteUserCommand(user_id=user_id))
    return success_response({"message": "用户删除成功"}, request)
