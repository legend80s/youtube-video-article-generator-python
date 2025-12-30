from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import HTTPException, APIRouter

from app.core.database import SessionDep
from app.services.ai_generator import (
    Item,
    ItemWithTranscript,
    generate,
    generate_article_stream,
    to_vercel_ai_sdk_format,
    chat,
)
from app.models.articles import ArticleFromTranscript, ArticleFromYoutubeUrl

router = APIRouter(prefix="/youtube-articles", tags=["youtube-articles"])


@router.post("")
async def search_article(
    item: Item | ItemWithTranscript,
) -> ArticleFromTranscript | ArticleFromYoutubeUrl:
    return search_article(item)


@router.post("/generate")
async def generate_route(item: Item | ItemWithTranscript) -> dict:
    return {"article": await generate(item)}


@router.get("/chat")
async def chat_route(input: str):
    print(f"{input=}")
    stream = chat(input)

    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


@router.post("/generate_stream")
async def generate_stream_route(item: Item | ItemWithTranscript):
    print(f"{item=}")
    stream = await generate_article_stream(item)

    return StreamingResponse(
        to_vercel_ai_sdk_format(stream),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


# 为现有路由添加OPTIONS处理器
@router.options("/generate_stream")
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


# @router.get("/{id}")
# async def read_youtube_article(id: int, session: SessionDep) -> Hero:
#     hero = await session.get(Hero, id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Youtube Article not found")
#     return hero
