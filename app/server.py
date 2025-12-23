from typing import Union

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from .api.youtube_articles.generate import Item, ItemWithTranscript, generate
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


# @app.post("/api/youtube-articles/generate_stream")
# async def generate_route(item: Union[Item, ItemWithTranscript]) -> dict:
#     return {"article": await generate(item)}


# Edit this to add the chain you want to add
add_routes(
    app,
    chatModel,
    path="/openai",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
