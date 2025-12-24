from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json


class TranscriptEntry(BaseModel):
    """单个转录条目"""

    start: str = Field(description="开始时间，格式：HH:MM:SS")
    end: str = Field(description="结束时间，格式：HH:MM:SS")
    text: str = Field(description="转录文本内容")

    def get_duration_seconds(self) -> float:
        """获取该条目的持续时间（秒）"""
        start_parts = self.start.split(":")
        end_parts = self.end.split(":")

        start_seconds = (
            int(start_parts[0]) * 3600 + int(start_parts[1]) * 60 + int(start_parts[2])
        )
        end_seconds = (
            int(end_parts[0]) * 3600 + int(end_parts[1]) * 60 + int(end_parts[2])
        )

        return end_seconds - start_seconds


class LanguageCode(BaseModel):
    """语言代码信息"""

    code: str = Field(description="语言代码，如 'en_auto'")
    name: str = Field(description="语言名称，如 'English (auto-generated)'")


class VideoSummary(BaseModel):
    """视频摘要"""

    video_id: str = Field(description="视频ID")
    title: str = Field(description="视频标题")
    author: str = Field(description="视频作者")
    duration_seconds: float = Field(description="视频时长（秒）")
    duration_formatted: str = Field(description="视频时长（格式化字符串，如 '1:30'）")
    thumbnail_url: None | str = Field(description="视频缩略图URL")
    video_url: str = Field(description="视频播放URL")

    transcript_entries: int = Field(description="transcript 条目数")
    transcript_duration: float = Field(description="transcript 总时长（秒）")
    transcript_preview: str = Field(description="transcript 预览文本（前200字符）")


class VideoInfo(BaseModel):
    """视频基本信息"""

    name: str = Field(description="视频标题")
    # TODO "https://i.ytimg.com/vi/4KdvcQKNfbQ/maxresdefault.jpg" 国内不可用，如果要展示得通过 ddgs 搜索后获取
    thumbnailUrl: Dict[str, str] = Field(description="缩略图URL字典")
    embedUrl: str = Field(description="嵌入播放URL")
    duration: str = Field(description="视频时长（秒）")
    description: str = Field(description="视频描述")
    upload_date: str = Field(description="上传日期")
    genre: str = Field(description="视频分类")
    author: str = Field(description="作者/频道名")
    channel_id: str = Field(description="频道ID")

    def get_thumbnail_url(self, quality: str = "hqdefault") -> Optional[str]:
        """获取指定质量的缩略图URL"""
        return self.thumbnailUrl.get(quality)


class TranscriptData(BaseModel):
    """转录数据"""

    custom: List[TranscriptEntry] = Field(description="转录条目列表")

    def get_full_text(self) -> str:
        """获取完整的转录文本"""
        return " ".join([entry.text for entry in self.custom])

    def get_total_duration(self) -> float:
        """获取总转录时长"""
        if not self.custom:
            return 0.0
        return sum([entry.get_duration_seconds() for entry in self.custom])


class Transcripts(BaseModel):
    """转录数据容器"""

    en_auto: TranscriptData = Field(description="英文自动转录数据")


class VideoData(BaseModel):
    """视频数据"""

    videoId: str = Field(description="YouTube视频ID")
    videoInfo: VideoInfo = Field(description="视频基本信息")
    language_code: List[LanguageCode] = Field(description="可用语言列表")
    transcripts: Transcripts = Field(description="转录数据")

    def get_video_url(self) -> str:
        """获取YouTube视频URL"""
        return f"https://www.youtube.com/watch?v={self.videoId}"

    def get_duration_seconds(self) -> int:
        """获取视频时长（秒）"""
        return int(self.videoInfo.duration)


class YouTubeTranscriptResponse(BaseModel):
    """YouTube转录API响应"""

    code: int = Field(description="响应代码")
    message: str = Field(description="响应消息")
    data: VideoData = Field(description="视频数据")

    @classmethod
    def from_json(cls, json_data: str) -> "YouTubeTranscriptResponse":
        """从JSON字符串创建对象"""
        return cls(**json.loads(json_data))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "YouTubeTranscriptResponse":
        """从字典创建对象"""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()

    def is_success(self) -> bool:
        """检查响应是否成功"""
        return self.code == 100000

    def get_summary(self) -> VideoSummary:
        """获取视频摘要信息"""
        # if not self.is_success():
        #     return {"error": self.message}

        video_data = self.data
        return VideoSummary(
            video_id=video_data.videoId,
            title=video_data.videoInfo.name,
            author=video_data.videoInfo.author,
            duration_seconds=video_data.get_duration_seconds(),
            duration_formatted=f"{video_data.get_duration_seconds() // 60}:{video_data.get_duration_seconds() % 60:02d}",
            thumbnail_url=video_data.videoInfo.get_thumbnail_url(),
            video_url=video_data.get_video_url(),
            transcript_entries=len(video_data.transcripts.en_auto.custom),
            transcript_duration=video_data.transcripts.en_auto.get_total_duration(),
            transcript_preview=video_data.transcripts.en_auto.get_full_text()[:200]
            + "...",
        )


# 便利函数
def parse_youtube_transcript(
    json_data: str | Dict[str, Any],
) -> YouTubeTranscriptResponse:
    """
    解析YouTube转录JSON数据

    Args:
        json_data: JSON字符串或字典

    Returns:
        YouTubeTranscriptResponse: 解析后的对象
    """
    if isinstance(json_data, str):
        return YouTubeTranscriptResponse.from_json(json_data)
    else:
        return YouTubeTranscriptResponse.from_dict(json_data)


def get_transcript_summary(json_data: str | Dict[str, Any]) -> VideoSummary:
    """
    获取转录数据摘要

    Args:
        json_data: JSON字符串或字典

    Returns:
        Dict: 摘要信息字典
    """
    response = parse_youtube_transcript(json_data)
    return response.get_summary()


# 使用示例
if __name__ == "__main__":
    # 示例JSON数据
    example_json = """
    {
        "code": 1000001,
        "message": "success",
        "data": {
            "videoId": "4KdvcQKNfbQ",
            "videoInfo": {
                "name": "Programming Party Tricks",
                "thumbnailUrl": {
                    "hqdefault": "https://i.ytimg.com/vi/4KdvcQKNfbQ/hqdefault.jpg",
                    "maxresdefault": "https://i.ytimg.com/vi/4KdvcQKNfbQ/maxresdefault.jpg"
                },
                "embedUrl": "https://www.youtube.com/embed/4KdvcQKNfbQ",
                "duration": "1074",
                "description": "",
                "upload_date": "",
                "genre": "",
                "author": "Tsoding",
                "channel_id": "UCEbYhDd6c6vngsF5PQpFVWg"
            },
            "language_code": [
                {
                    "code": "en_auto",
                    "name": "English (auto-generated)"
                }
            ],
            "transcripts": {
                "en_auto": {
                    "custom": [
                        {
                            "start": "00:00:03",
                            "end": "00:01:10",
                            "text": "This is the most important property of exclusive or operation also known as zor."
                        },
                        {
                            "start": "00:17:31",
                            "end": "00:18:17",
                            "text": "But but I don't like this way of writing this property because it kind of hides the intent. It kind of hides the implications. If you write it like this, it tells you the implications very explicitly and I kind of like that. So do you know any other applications of this specific property of Zor? I'm pretty sure there's like an infinite of them. I only wish they start asking this in according interviews."
                        }
                    ]
                }
            }
        }
    }
    """

    # 使用便利函数
    summary = get_transcript_summary(example_json)
    print("视频摘要:")
    print(f"  视频ID: {summary.video_id}")
    print(f"  标题: {summary.title}")
    print(f"  作者: {summary.author}")
    print(f"  时长: {summary.duration_formatted}")
    print(f"  缩略图URL: {summary.thumbnail_url}")
    print(f"  视频URL: {summary.video_url}")
    print(f"  Transcript条目数: {summary.transcript_entries}")
    print(f"  Transcript总时长: {summary.transcript_duration:.1f} 秒")
    print(f"  Transcript预览: {summary.transcript_preview}")

    print("\n" + "=" * 50)

    # 使用完整对象
    response = parse_youtube_transcript(example_json)
    print(f"\n完整转录文本: {response.data.transcripts.en_auto.get_full_text()}")
    print(
        f"转录总时长: {response.data.transcripts.en_auto.get_total_duration():.1f} 秒"
    )
