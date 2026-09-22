"""API 路由聚合。"""

from fastapi import APIRouter

from src.interfaces.http.v1.user_router import router as user_router
from src.interfaces.http.v1.auth_router import router as auth_router
from src.interfaces.http.v1.health_router import router as health_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_router)
api_router.include_router(auth_router)
api_router.include_router(health_router)
