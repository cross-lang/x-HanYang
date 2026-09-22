"""API 路由聚合。"""

from fastapi import APIRouter

from src.interfaces.http.v1.user_router import router as user_router
from src.interfaces.http.v1.auth_router import router as auth_router
from src.interfaces.http.v1.health_router import router as health_router
from src.interfaces.http.v1.file_router import router as file_router
from src.interfaces.http.v1.audit_router import router as audit_router
from src.interfaces.http.v1.role_router import router as role_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(file_router)
api_router.include_router(audit_router)
