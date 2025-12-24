import os
import re

import httpx
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from app.lib.youtube_models import YouTubeTranscriptResponse

load_dotenv()


YAG_VERBOSE = os.getenv("YAG_VERBOSE")

verbose = YAG_VERBOSE == "True"


class YouTubeId(BaseModel):
    """YouTube视频ID"""

    id: str = Field(description="YouTube视频ID")

    @field_validator("id")
    def validate_id(cls, value: str) -> str:
        """Validate YouTube video ID"""
        if not re.match(r"^[a-zA-Z0-9_-]{11}$", value):
            raise ValueError(f"Invalid YouTube video ID: {value}")
        return value

    @staticmethod
    def of(id: str) -> "YouTubeId":
        return YouTubeId(id=id)


class YouTubeURL(BaseModel):
    """YouTube视频URL"""

    url: str = Field(description="YouTube视频URL")

    @staticmethod
    def of(url: str) -> "YouTubeURL":
        return YouTubeURL(url=url)

    @property
    def video_id(self) -> str:
        """
        # Extract video ID from YouTube URL

        ## example
        ### 标准YouTube链接
        ```py
        >>> url1 = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        'dQw4w9WgXcQ'
        ```

        ### 短链接
        ```py
        >>> url2 = "https://youtu.be/dQw4w9WgXcQ"
        'dQw4w9WgXcQ'
        ```

        Args:
            youtube_url (str): _description_

        Raises:
            ValueError: _description_

        Returns:
            str: _description_
        """

        video_id_match = re.search(
            r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", self.url
        )
        if not video_id_match:
            raise ValueError(f"Invalid YouTube URL: {self.url}")

        return video_id_match.group(1)


async def fetch_video_info_using_notegpt_api(
    video_id_instance: YouTubeId,
) -> YouTubeTranscriptResponse:
    """Fetch YouTube transcript using NoteGPT API"""

    video_id: str = video_id_instance.id

    # Headers from the cURL command
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i",
        "referer": f"https://notegpt.io/detail/{video_id}?type=1&utm_source=youtube-transcript-generator&epl=1",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    }

    cookie_str = os.getenv("NOTE_GPT_COOKIES")

    # Cookies from the cURL command
    cookies = {}
    if cookie_str:
        cookies = dict(
            item.split("=") for item in cookie_str.split("; ") if "=" in item
        )

    # Make the API request
    url = f"https://notegpt.io/api/v2/video-transcript?platform=youtube&video_id={video_id}"

    if verbose:
        print(f"\nfetch {url=}")
        print(f"{cookies=}")

    async with httpx.AsyncClient(
        timeout=10.0, headers=headers, cookies=cookies
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

        resp = response.json()

        # Extract transcript from response
        if resp.get("data"):
            return YouTubeTranscriptResponse.from_dict(resp)
        else:
            invalid_format_msg = f"Unexpected response format: {resp}"
            if not cookie_str:
                raise ValueError(
                    f"NOTE_GPT_COOKIES environment variable is not set. {invalid_format_msg}"
                )

            raise ValueError(invalid_format_msg)


async def fetch_transcript_using_notegpt_api(
    youtube_id_or_youtube_url: YouTubeId | YouTubeURL,
) -> str:
    """Fetch YouTube transcript using NoteGPT API"""

    # Extract video ID from YouTube URL
    # Since YouTubeId is a NewType of str, we check if it's a valid video ID or a URL

    # Check if input looks like a YouTube video ID (11 characters with allowed chars)
    video_id: YouTubeId
    if isinstance(youtube_id_or_youtube_url, YouTubeId):
        # It's a video ID
        video_id = youtube_id_or_youtube_url
    else:
        # It's a URL, extract video ID
        video_id = YouTubeId.of(youtube_id_or_youtube_url.video_id)

    return (
        await fetch_video_info_using_notegpt_api(video_id)
    ).data.transcripts.en_auto.get_full_text()


async def fetch_transcript(
    youtube_id_or_youtube_url: YouTubeURL | YouTubeId,
) -> str:
    """Fetch YouTube transcript"""
    return await fetch_transcript_using_notegpt_api(youtube_id_or_youtube_url)


__all__ = ["fetch_transcript", "YouTubeId", "YouTubeURL"]
