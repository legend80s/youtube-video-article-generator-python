# from typing import Union

# AsyncGenerator


import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from langserve import add_routes

from app.core.database import create_db_and_tables
from app.api.v1 import api_v1_router
from app.core.exceptions import validation_exception_handler
from .lib.llms import chatModel

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s - %(asctime)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


# # from langchain import promt
# # Create a LANGSMITH_API_KEY in Settings > API Keys


async def lifespan(app: FastAPI):
    logger.info("[lifespan] Starting up...")
    await create_db_and_tables()
    yield
    logger.info("[lifespan] Shutting down...")


def create_application() -> FastAPI:
    """创建 FastAPI 应用"""

    # app = FastAPI(title="YouTube Articles API")
    app = FastAPI(title="YouTube Articles API", lifespan=lifespan)

    # 注册异常处理器
    @app.exception_handler(RequestValidationError)
    def _(request: Request, exc: RequestValidationError):
        return validation_exception_handler(request, exc)

    # app.exception_handler(RequestValidationError)(
    #     lambda request, exc: validation_exception_handler(request, exc)
    # )

    # 注册路由
    app.include_router(api_v1_router)

    # Edit this to add the chain you want to add
    add_routes(
        app,
        chatModel,
        path="/openai",
    )

    return app


# 创建应用实例 -Error loading ASGI app. Attribute "app" not found in module "app.server".
app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        # log_level="debug",  # 或 "debug" 查看更详细信息
        # access_log=True,
    )
