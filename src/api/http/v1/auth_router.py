"""认证 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.application.auth.commands.login import LoginCommand, LoginHandler
from src.application.auth.commands.refresh_token import RefreshTokenCommand, RefreshTokenHandler
from src.application.auth.commands.logout import LogoutCommand, LogoutHandler
from src.application.auth.dto.auth_dto import CurrentUserDTO
from src.constants.messages import MSG_LOGOUT_SUCCESS
from src.api.http.dependencies import (
    get_login_handler,
    get_refresh_token_handler,
    get_logout_handler,
    get_current_user_dep,
)
from src.api.http.schemas.auth import LoginRequest, RefreshTokenRequest
from src.api.shared.response import success_response
from src.utils.helpers import get_client_ip

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", summary="用户登录")
async def login(
    body: LoginRequest,
    request: Request,
    handler: LoginHandler = Depends(get_login_handler),
) -> dict:
    """登录接口。

    Args:
        body: 登录请求体
        request: HTTP 请求
        handler: 登录处理器

    Returns:
        dict: 包含令牌对的响应
    """
    command = LoginCommand(
        account=body.account,
        password=body.password,
        ip_address=get_client_ip(request),
    )
    result = await handler.handle(command)
    return success_response(vars(result), request)


@router.post("/refresh", summary="刷新令牌")
async def refresh_token(
    body: RefreshTokenRequest,
    request: Request,
    handler: RefreshTokenHandler = Depends(get_refresh_token_handler),
) -> dict:
    """刷新令牌接口。

    Args:
        body: 刷新令牌请求体
        request: HTTP 请求
        handler: 刷新令牌处理器

    Returns:
        dict: 包含新令牌对的响应
    """
    command = RefreshTokenCommand(refresh_token=body.refresh_token)
    result = await handler.handle(command)
    return success_response(vars(result), request)


@router.post("/logout", summary="退出登录")
async def logout(
    request: Request,
    handler: LogoutHandler = Depends(get_logout_handler),
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """退出登录接口。

    Args:
        request: HTTP 请求
        handler: 退出登录处理器
        current_user: 当前用户

    Returns:
        dict: 退出成功响应
    """
    await handler.handle(LogoutCommand(user_id=current_user.id))
    return success_response({"message": MSG_LOGOUT_SUCCESS}, request)


@router.get("/me", summary="当前用户信息")
async def get_me(
    request: Request,
    current_user: CurrentUserDTO = Depends(get_current_user_dep),
) -> dict:
    """获取当前登录用户信息。

    Args:
        request: HTTP 请求
        current_user: 当前用户

    Returns:
        dict: 当前用户信息响应
    """
    return success_response(vars(current_user), request)
