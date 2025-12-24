from typing import Union

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, StreamingResponse, JSONResponse
from langserve import add_routes

from .api.youtube_articles.generate import (
    Item,
    ItemWithTranscript,
    generate,
    to_vercel_ai_sdk_generator,
)
from .lib.models import chatModel

# from langchain import promt
# Create a LANGSMITH_API_KEY in Settings > API Keys

app = FastAPI()


@app.get("/docs")
async def redirect_root_to_docs() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/echo")
async def echo() -> dict:
    return {"message": "Hello world!"}


@app.post("/echo")
async def echo_post() -> dict:
    return {"message": "Hello world!"}


@app.post("/api/youtube-articles/generate")
async def generate_route(item: Union[Item, ItemWithTranscript]) -> dict:
    return {"article": await generate(item)}


@app.post("/api/youtube-articles/generate_stream")
async def generate_stream_route(item: Union[Item, ItemWithTranscript]):
    print(f"{item=}")
    return StreamingResponse(
        to_vercel_ai_sdk_generator(item),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


# INFO:     127.0.0.1:53070 - "OPTIONS /api/youtube-articles/generate_stream HTTP/1.1" 405 Method Not Allowed
# 为现有路由添加OPTIONS处理器
@app.options("/api/youtube-articles/generate_stream")
async def handle_options():
    """处理OPTIONS预检请求"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Origin": "*",  # 生产环境请指定具体域名
            "Access-Control-Max-Age": "86400",  # 24小时缓存
        },
    )


# Edit this to add the chain you want to add
add_routes(
    app,
    chatModel,
    path="/openai",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
