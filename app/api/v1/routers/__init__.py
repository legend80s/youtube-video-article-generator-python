"""
聚合所有路由
"""

from .heroes import router as heroes_router
from .test import router as test_router
from .youtube_articles import router as articles_router
# from .health import router as health_router

# 导出所有路由
__all__ = ["heroes_router", "test_router", "articles_router"]
