import time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlmodel import JSON, SQLModel
from sqlmodel import Field as SQLField

from app.utils.youtube_models import VideoSummary


class ArticleBaseFields(BaseModel):
    """文章基础字段模型 - 所有文章都需要的字段"""

    model_config = ConfigDict(from_attributes=True)

    # 共享字段定义 - 使用 Pydantic Field
    id: str = Field(description="文章ID")
    source: Literal["from_transcript", "from_youtube_url"] = Field(
        description="文章生成来源"
    )
    style: Literal["professional", "casual", "academic"] = Field(
        description="文章风格", default="professional"
    )
    title: str = Field(description="文章标题")
    content: str = Field(description="文章内容 - AI 生成")
    transcript: str = Field(description="视频转录文本")
    gmt_created: int = Field(
        description="文章创建时间（GMT 时间戳）",
        default_factory=lambda: int(time.time()),
    )
    gmt_modified: int = Field(
        description="文章最后修改时间（GMT 时间戳）",
        default_factory=lambda: int(time.time()),
    )


class ArticleDB(ArticleBaseFields, SQLModel, table=True):
    """SQLModel 文章模型 - 继承基础字段并重写数据库特定字段"""

    # 重写主键ID - 使用 int 类型作为数据库主键
    id: int = SQLField(description="文章ID", primary_key=True)

    # 重写 source 和 style - 使用 str 类型而非 Literal
    source: str = SQLField(description="文章生成来源", index=True)
    style: str = SQLField(description="文章风格", default="professional")

    # YouTube视频ID - 数据库特有字段
    youtube_video_id: str | None = SQLField(
        default=None, description="YouTube视频ID", index=True
    )

    # 视频摘要信息 - 使用 JSON 类型存储
    video_info: dict[str, Any] | None = SQLField(
        default=None, sa_type=JSON, description="视频摘要信息"
    )


class ArticleFromTranscript(ArticleBaseFields):
    """文章模型 - 从视频转录文本生成"""

    """文章生成来源"""
    source: Literal["from_transcript"] = "from_transcript"

    # 必须提供 transcript
    transcript: str = Field(description="视频转录文本")

    # 验证器
    @field_validator("transcript")
    @classmethod
    def validate_transcript_length(cls, v: str) -> str:
        if len(v) < 50:
            raise ValueError("转录文本至少需要50个字符")
        return v


class ArticleFromYoutubeUrl(ArticleBaseFields):
    """文章模型 - 从 YouTube 视频 URL 生成"""

    source: Literal["from_youtube_url"] = "from_youtube_url"
    youtube_video_id: str = Field(description="YouTube 视频ID")
    """视频摘要信息 - 从 API 获取"""
    video_info: VideoSummary = Field(description="视频信息")

    # 自动从 video_info 提取标题（如果未提供）
    @model_validator(mode="before")
    @classmethod
    def set_title_from_video_info(cls, data: dict) -> dict:
        print(f"set_title_from_video_info: {data}, type of data {type(data)}")

        if "title" not in data and "video_info" in data:
            video_info = data.get("video_info")
            print(
                f"video_info: {video_info}, type of video_info {type(video_info)}, title: {video_info.title}"
            )
            if video_info and hasattr(video_info, "title"):
                data["title"] = video_info.title

        return data
