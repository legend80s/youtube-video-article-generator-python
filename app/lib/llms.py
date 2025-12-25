import os

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv

# 加载 .env 文件中的所有变量
load_dotenv()

api_key = os.getenv("ARK_API_KEY")
base_url = os.getenv("ARK_BASE_URL")

if api_key and base_url:
    print(f"{SecretStr(api_key)=}")
    print(f"{base_url=}")

    print("API Key 已成功加载")
else:
    print("API Key 未找到，请检查设置")
    # throw error
    raise ValueError("API Key or base_url 未找到，请检查设置")


model_with_function_calling: ChatOpenAI = ChatOpenAI(
    api_key=SecretStr(api_key),
    model="doubao-seed-1-6-lite-251015",
    base_url=base_url,
    # configuration: {
    #   baseURL: ,
    #   // logLevel: "debug",
    # },
    # // temperature: 0,
    # // timeout: 10,
    # // maxTokens: 1000,
)
"""支持函数调用的模型实例。
- 模型：doubao-seed-1-6-lite-251015
- 用途：适合需要工具/函数调用的场景
"""
# model_with_function_calling = 1


# 标准对话模型
chatModel: ChatOpenAI = ChatOpenAI(
    api_key=SecretStr(api_key),
    model="doubao-lite-32k-character-250228",
    base_url=base_url,
    # configuration: {
    #   baseURL: "https://ark.cn-beijing.volces.com/api/v3",
    #   // logLevel: "debug",
    # },
    temperature=0.2,
    # // timeout: 10,
    # // maxTokens: 1000,
)
"""标准对话模型实例。
- 模型：doubao-lite-32k-character-250228
- 温度：0.2（略有创造性）
- 上下文长度：32K
- 用途：通用对话、文本生成任务
"""


# 可选：按需导出特定模型
__all__ = ["model_with_function_calling", "chatModel"]
