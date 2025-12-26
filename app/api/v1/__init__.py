"""
API v1 路由注册
"""

from fastapi import APIRouter
from .routers import heroes_router, test_router, articles_router

# 创建 v1 路由
api_v1_router = APIRouter(prefix="/api/v1")

# 注册所有路由
api_v1_router.include_router(heroes_router)
api_v1_router.include_router(test_router)
api_v1_router.include_router(articles_router)
# api_v1_router.include_router(health_router)

# 导出
__all__ = ["api_v1_router"]
