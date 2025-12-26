"""测试路由"""

from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/")
async def test() -> dict[str, str]:
    return {"message": "Hello World from /test"}


@router.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@router.get("/echo")
async def echo() -> dict:
    return {"message": "Hello world from GET!"}


@router.post("/echo")
async def echo_post() -> dict:
    return {"message": "Hello world from POST!"}
