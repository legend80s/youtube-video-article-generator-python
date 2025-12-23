from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from .lib.models import chatModel

app = FastAPI()


@app.get("/docs")
async def redirect_root_to_docs() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/echo")
async def echo() -> dict:
    return {"message": "Hello world!"}


# Edit this to add the chain you want to add
add_routes(
    app,
    chatModel,
    path="/openai",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
