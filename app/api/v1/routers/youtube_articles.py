from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import HTTPException, APIRouter

from app.core.database import SessionDep
from app.api.youtube_articles.generate import (
    Item,
    ItemWithTranscript,
    generate,
    to_vercel_ai_sdk_generator,
)
from app.lib.models.articles import ArticleFromTranscript, ArticleFromYoutubeUrl

router = APIRouter(prefix="/youtube-articles", tags=["youtube-articles"])


@router.post("/api/youtube-articles")
async def search_article(
    item: Item | ItemWithTranscript,
) -> ArticleFromTranscript | ArticleFromYoutubeUrl:
    return search_article(item)


@router.post("/api/youtube-articles/generate")
async def generate_route(item: Item | ItemWithTranscript) -> dict:
    return {"article": await generate(item)}


@router.post("/api/youtube-articles/generate_stream")
async def generate_stream_route(item: Item | ItemWithTranscript):
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
@router.options("/api/youtube-articles/generate_stream")
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


# @router.get("/api/youtube-articles/{id}")
# async def read_youtube_article(id: int, session: SessionDep) -> Hero:
#     hero = await session.get(Hero, id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Youtube Article not found")
#     return hero
