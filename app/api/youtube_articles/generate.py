from typing import AsyncIterator

from langchain_core.messages import SystemMessage, AIMessageChunk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.runnables import Runnable
from langsmith import Client
from pydantic import BaseModel

from app.lib.models import chatModel

client = Client()


def enhance_prompt(
    original_prompt: PromptTemplate, custom_system_prompt: str
) -> ChatPromptTemplate:
    """增强原始提示词，添加自定义系统提示"""

    system_message = SystemMessage(content=custom_system_prompt)
    # 将原始 PromptTemplate 转换为 HumanMessage
    human_message = HumanMessagePromptTemplate.from_template(original_prompt.template)
    # 创建 ChatPromptTemplate
    chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    chat_prompt.input_variables = original_prompt.input_variables

    return chat_prompt


# https://smith.langchain.com/hub/muhsinbashir/youtube-transcript-to-article
# muhsinbashir/youtube-transcript-to-article：Convert any Youtube Video Transcript into an Article ( SEO friendly )
original_prompt: PromptTemplate = client.pull_prompt(
    "muhsinbashir/youtube-transcript-to-article", include_model=True
)


# 添加自定义系统提示词
custom_system_prompt = """
请根据提供的 YouTube 视频转录文本，创作一篇 Markdown 格式文章。需要：
1. 中文撰写
2. 使用恰当的 markdown 格式标题层级(#、## 等，# 不应该跟标题。错误示例：“# 标题：Exclusive Or Operation的重要特性”，正确例子：“# Exclusive Or Operation的重要特性”)
"""

chat_prompt = enhance_prompt(original_prompt, custom_system_prompt)

prompt = chat_prompt

chain: Runnable = prompt | chatModel


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
        str_chain: Runnable = chain | StrOutputParser()
        transcript = "\n" + item.transcript

        return await str_chain.ainvoke(input=transcript)

    return "not implemented 1"


def generate_stream(item: Item | ItemWithTranscript) -> AsyncIterator[AIMessageChunk]:
    print(f"Received 2 item: {item}")

    # print prompt

    if isinstance(item, ItemWithTranscript):
        transcript = "\n" + item.transcript
        # print(f"Prompt: {prompt.format(transcript=transcript)}")

        return chain.astream(input=transcript)

    return "not implemented 2"


__all__ = ["generate", "generate_stream"]
