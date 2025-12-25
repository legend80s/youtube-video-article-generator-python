from sqlalchemy import alias
import os
import json
import uuid
from typing import AsyncIterator, Union

from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.runnables import Runnable
from langsmith import Client
from pydantic import BaseModel, ConfigDict, Field

from app.lib.models import chatModel
from app.lib.tools.youtube_info import fetch_transcript, YouTubeURL

client = Client()

load_dotenv()

verbose = os.getenv("YAG_VERBOSE") == "True"


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
    youtube_url: str = Field(description="YouTube视频URL")
    # youtube_url: str = Field(description="YouTube视频URL", alias="youtubeUrl")
    mode: str | None = None

    model_config = ConfigDict(
        # 关键配置
        # populate_by_name=True,  # 允许通过字段名或别名设置值
        # use_enum_values=True,  # 使用枚举值
        # extra="ignore",  # 忽略未定义的字段
        json_schema_extra={  # OpenAPI 文档示例
            "example": {
                "youtubeUrl": "https://youtube.com/watch?v=abc123",
            }
        },
    )


async def generate(item: Item | ItemWithTranscript) -> str:
    print(f"Received 1 item: {item}")
    if isinstance(item, ItemWithTranscript):
        str_chain: Runnable = chain | StrOutputParser()
        transcript = "\n" + item.transcript

        return await str_chain.ainvoke(input=transcript)

    return "not implemented 1"


async def generate_stream(
    item: Item | ItemWithTranscript,
) -> AsyncIterator[AIMessageChunk]:
    verbose and print(f"[generate_stream] item: {item}")

    # print prompt

    if isinstance(item, ItemWithTranscript):
        verbose and print("[generate_stream] ItemWithTranscript")

        transcript = "\n" + item.transcript
        # print(f"Prompt: {prompt.format(transcript=transcript)}")
        return chain.astream(input=transcript)
    else:
        url: str = item.youtube_url
        verbose and print(f"[generate_stream] only url: {url}")

        # fetch transcript by url
        try:
            transcript = await fetch_transcript(YouTubeURL.of(url))
            return chain.astream(input="\n" + transcript)
        except Exception as exception:
            verbose and print(f"💥 [generate_stream] Exception: {exception}")

            # Return error as async generator
            async def error_generator(error_msg: str):
                yield AIMessageChunk(content=f"Error fetching transcript: {error_msg}")

            return error_generator(str(exception))

    # Final fallback for any unhandled case
    async def not_implemented_generator():
        yield AIMessageChunk(content="not implemented")

    return not_implemented_generator()


async def to_vercel_ai_sdk_generator(item: Union[Item, ItemWithTranscript]):
    """生成SSE格式的流式响应"""
    try:
        # 获取流式输出
        stream = await generate_stream(item)

        # 如果是字符串类型（错误信息），直接返回
        if isinstance(stream, str):
            yield f"data: {stream}\n\n"
            return

        # 初始化id

        id: str = str(uuid.uuid4())
        yield f"data: {json.dumps({'id': id, 'type': 'text-start'})}\n\n"

        # 流式输出内容
        async for chunk in stream:
            if not id:
                assert chunk.id, "chunk.id should not be None"
                id = chunk.id
            # 将每个数据块包装为SSE格式
            # 转成 vercel ai sdk 格式 id, type: "text-delta", delta: chunk.content
            chunk = {"id": id, "type": "text-delta", "delta": chunk.content}
            # yield f"data: {chunk}\n\n"
            # json dump
            chunk = json.dumps(chunk)
            # yield f"data: {chunk}\n\n"
            yield f"data: {chunk}\n\n"

        # 发送结束信号 id, type: "text-end"
        yield f"data: {json.dumps({'id': id, 'type': 'text-end'})}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        # 错误处理
        yield f"data: Error: {str(e)}\n\n"


__all__ = ["generate", "to_vercel_ai_sdk_generator"]
