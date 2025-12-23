from langsmith import Client
from pydantic import BaseModel
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from app.lib.models import chatModel

client = Client()
# https://smith.langchain.com/hub/muhsinbashir/youtube-transcript-to-article
# muhsinbashir/youtube-transcript-to-article：Convert any Youtube Video Transcript into an Article ( SEO friendly )
prompt = client.pull_prompt(
    "muhsinbashir/youtube-transcript-to-article", include_model=True
)

chain: Runnable = prompt | chatModel | StrOutputParser()


class ItemWithTranscript(BaseModel):
    prompt: str | None = None
    transcript: str
    mode: str | None = None


class Item(BaseModel):
    prompt: str | None = None
    youtube_url: str
    mode: str | None = None


async def generate(item: Item | ItemWithTranscript) -> str:
    print(f"Received 1 item: {item}")
    if isinstance(item, ItemWithTranscript):
        return chain.invoke(input=item.transcript)

    return "Hello world 2!"


__all__ = ["generate"]
