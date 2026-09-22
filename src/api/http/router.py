"""API 路由聚合。"""

from fastapi import APIRouter

from src.api.http.v1.user_router import router as user_router
from src.api.http.v1.auth_router import router as auth_router
from src.api.http.v1.health_router import router as health_router
from src.api.http.v1.file_router import router as file_router
from src.api.http.v1.audit_router import router as audit_router
from src.api.http.v1.role_router import router as role_router

api_router = APIRouter(prefix="/api/v1", tags=["API V1 路由"])

# 注册健康管理路由
api_router.include_router(health_router, tags=["健康检查"])

# 注册身份认证路由
api_router.include_router(auth_router, tags=["身份认证"])

# 注册用户管理路由
api_router.include_router(user_router, tags=["用户管理"])

# 注册角色管理路由
api_router.include_router(role_router, tags=["角色管理"])

# 注册文件管理路由
api_router.include_router(file_router, tags=["文件管理"])

# 注册审计日志路由
api_router.include_router(audit_router, tags=["审计日志"])
