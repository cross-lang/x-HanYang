"""角色管理 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.application.role.handlers import (
    CreateRoleCommand, CreateRoleHandler, UpdateRoleCommand, UpdateRoleHandler,
    DeleteRoleCommand, DeleteRoleHandler, GetRoleQuery, GetRoleHandler,
    SearchRolesQuery, SearchRolesHandler,
)
from src.application.auth.handlers import CurrentUserDTO
from src.constants.messages import MSG_ROLE_DELETED
from src.api.http.dependencies import (
    get_create_role_handler,
    get_update_role_handler,
    get_delete_role_handler,
    get_get_role_handler,
    get_search_roles_handler,
    get_current_user_dep,
)
from src.api.http.schemas.role import CreateRoleRequest, UpdateRoleRequest
from src.api.http.response import success_response

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("", summary="创建角色", status_code=201)
async def create_role(
    body: CreateRoleRequest,
    request: Request,
    handler: CreateRoleHandler = Depends(get_create_role_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """创建角色接口。"""
    command = CreateRoleCommand(
        role_name=body.role_name, role_code=body.role_code,
        description=body.description, role_type=body.role_type,
    )
    result = await handler.handle(command)
    return success_response({"id": result.id, "role_name": result.role_name, "role_code": result.role_code}, request, code=201)


@router.get("", summary="角色列表")
async def list_roles(
    request: Request,
    keyword: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    handler: SearchRolesHandler = Depends(get_search_roles_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """角色列表接口。"""
    query = SearchRolesQuery(keyword=keyword, status=status, page=page, page_size=page_size)
    result = await handler.handle(query)
    return success_response(
        {"items": [vars(item) for item in result.items], "total": result.total,
         "page": result.page, "page_size": result.page_size, "total_pages": result.total_pages},
        request,
    )


@router.get("/{role_id}", summary="查询角色")
async def get_role(
    role_id: int,
    request: Request,
    handler: GetRoleHandler = Depends(get_get_role_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """查询单个角色接口。"""
    result = await handler.handle(GetRoleQuery(role_id=role_id))
    return success_response(vars(result), request)


@router.put("/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    body: UpdateRoleRequest,
    request: Request,
    handler: UpdateRoleHandler = Depends(get_update_role_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """更新角色接口。"""
    command = UpdateRoleCommand(role_id=role_id, role_name=body.role_name, description=body.description, status=body.status)
    result = await handler.handle(command)
    return success_response({"id": result.id, "role_name": result.role_name, "role_code": result.role_code}, request)


@router.delete("/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    request: Request,
    handler: DeleteRoleHandler = Depends(get_delete_role_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """删除角色接口（软删除）。"""
    await handler.handle(DeleteRoleCommand(role_id=role_id))
    return success_response({"message": MSG_ROLE_DELETED}, request)
