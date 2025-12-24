import unittest
import json
from youtube_models import (
    YouTubeTranscriptResponse,
    parse_youtube_transcript,
    get_transcript_summary,
    VideoSummary,
    TranscriptEntry,
    VideoData,
)


class TestYouTubeModels(unittest.TestCase):
    """YouTube转录模型测试类"""

    def setUp(self):
        """设置测试数据"""
        self.example_json = """
        {
            "code": 100000,
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

    def test_transcript_entry_duration(self):
        """测试转录条目时长计算"""
        entry = TranscriptEntry(start="00:00:03", end="00:01:10", text="Test text")
        expected_duration = 67.0  # 1分10秒 - 3秒 = 67秒
        self.assertAlmostEqual(
            entry.get_duration_seconds(), expected_duration, places=1
        )

    def test_transcript_entry_empty_text(self):
        """测试转录条目空文本"""
        entry = TranscriptEntry(start="00:00:00", end="00:00:10", text="")
        self.assertEqual(entry.text, "")
        self.assertEqual(entry.get_duration_seconds(), 10.0)

    def test_parse_youtube_transcript_from_string(self):
        """测试从JSON字符串解析转录数据"""
        response = parse_youtube_transcript(self.example_json)

        self.assertIsInstance(response, YouTubeTranscriptResponse)
        self.assertEqual(response.code, 100000)
        self.assertEqual(response.message, "success")
        self.assertIsInstance(response.data, VideoData)

    def test_parse_youtube_transcript_from_dict(self):
        """测试从字典解析转录数据"""
        data_dict = json.loads(self.example_json)
        response = parse_youtube_transcript(data_dict)

        self.assertIsInstance(response, YouTubeTranscriptResponse)
        self.assertEqual(response.code, 100000)

    def test_response_success_status(self):
        """测试响应成功状态检查"""
        response = parse_youtube_transcript(self.example_json)
        self.assertTrue(response.is_success())

    def test_response_video_data(self):
        """测试视频数据访问"""
        response = parse_youtube_transcript(self.example_json)
        video_data = response.data

        self.assertEqual(video_data.videoId, "4KdvcQKNfbQ")
        self.assertEqual(video_data.videoInfo.name, "Programming Party Tricks")
        self.assertEqual(video_data.videoInfo.author, "Tsoding")
        self.assertEqual(video_data.get_duration_seconds(), 1074)

    def test_video_url_generation(self):
        """测试视频URL生成"""
        response = parse_youtube_transcript(self.example_json)
        expected_url = "https://www.youtube.com/watch?v=4KdvcQKNfbQ"
        self.assertEqual(response.data.get_video_url(), expected_url)

    def test_thumbnail_url_getter(self):
        """测试缩略图URL获取"""
        response = parse_youtube_transcript(self.example_json)

        hq_url = response.data.videoInfo.get_thumbnail_url("hqdefault")
        self.assertEqual(hq_url, "https://i.ytimg.com/vi/4KdvcQKNfbQ/hqdefault.jpg")

        maxres_url = response.data.videoInfo.get_thumbnail_url("maxresdefault")
        self.assertEqual(
            maxres_url, "https://i.ytimg.com/vi/4KdvcQKNfbQ/maxresdefault.jpg"
        )

        # 测试不存在的质量
        none_url = response.data.videoInfo.get_thumbnail_url("nonexistent")
        self.assertIsNone(none_url)

    def test_transcript_full_text(self):
        """测试完整转录文本获取"""
        response = parse_youtube_transcript(self.example_json)
        full_text = response.data.transcripts.en_auto.get_full_text()

        self.assertIn("This is the most important property", full_text)
        self.assertIn("exclusive or operation", full_text)
        self.assertIn("according interviews", full_text)

    def test_transcript_total_duration(self):
        """测试转录总时长计算"""
        response = parse_youtube_transcript(self.example_json)
        total_duration = response.data.transcripts.en_auto.get_total_duration()

        # 第一个条目: 00:01:10 - 00:00:03 = 67秒
        # 第二个条目: 00:18:17 - 00:17:31 = 46秒
        # 总计: 113秒
        self.assertAlmostEqual(total_duration, 113.0, places=1)

    def test_video_summary_generation(self):
        """测试视频摘要生成"""
        response = parse_youtube_transcript(self.example_json)
        summary = response.get_summary()

        self.assertIsInstance(summary, VideoSummary)
        self.assertEqual(summary.video_id, "4KdvcQKNfbQ")
        self.assertEqual(summary.title, "Programming Party Tricks")
        self.assertEqual(summary.author, "Tsoding")
        self.assertEqual(summary.duration_seconds, 1074)
        self.assertEqual(summary.duration_formatted, "17:54")
        self.assertEqual(summary.transcript_entries, 2)
        self.assertAlmostEqual(summary.transcript_duration, 113.0, places=1)
        self.assertIn("This is the most important property", summary.transcript_preview)

    def test_convenience_functions(self):
        """测试便利函数"""
        # 测试从字符串获取摘要
        summary = get_transcript_summary(self.example_json)
        self.assertIsInstance(summary, VideoSummary)
        self.assertEqual(summary.video_id, "4KdvcQKNfbQ")

        # 测试从对象获取摘要
        response = parse_youtube_transcript(self.example_json)
        summary2 = get_transcript_summary(response)
        self.assertEqual(summary.video_id, summary2.video_id)

    def test_empty_transcript_duration(self):
        """测试空转录的时长"""
        empty_data = {
            "code": 100000,
            "message": "success",
            "data": {
                "videoId": "test123",
                "videoInfo": {
                    "name": "Test Video",
                    "thumbnailUrl": {},
                    "embedUrl": "https://www.youtube.com/embed/test123",
                    "duration": "60",
                    "description": "",
                    "upload_date": "",
                    "genre": "",
                    "author": "Test Author",
                    "channel_id": "test_channel",
                },
                "language_code": [],
                "transcripts": {"en_auto": {"custom": []}},
            },
        }

        response = YouTubeTranscriptResponse.from_dict(empty_data)
        self.assertEqual(response.data.transcripts.en_auto.get_total_duration(), 0.0)
        self.assertEqual(response.data.transcripts.en_auto.get_full_text(), "")

    def test_invalid_json_handling(self):
        """测试无效JSON处理"""
        invalid_json = "{ invalid json }"

        with self.assertRaises(json.JSONDecodeError):
            parse_youtube_transcript(invalid_json)

    def test_response_conversion_methods(self):
        """测试响应对象转换方法"""
        response = parse_youtube_transcript(self.example_json)

        # 测试转换为字典
        response_dict = response.to_dict()
        self.assertIsInstance(response_dict, dict)
        self.assertIn("code", response_dict)
        self.assertIn("data", response_dict)

        # 测试从字典重新创建
        response2 = YouTubeTranscriptResponse.from_dict(response_dict)
        self.assertEqual(response.code, response2.code)
        self.assertEqual(response.data.videoId, response2.data.videoId)


class TestTranscriptEntryEdgeCases(unittest.TestCase):
    """转录条目边界情况测试"""

    def test_zero_duration_entry(self):
        """测试零时长条目"""
        entry = TranscriptEntry(start="00:00:00", end="00:00:00", text="Zero duration")
        self.assertEqual(entry.get_duration_seconds(), 0.0)

    def test_long_duration_entry(self):
        """测试长时长条目"""
        entry = TranscriptEntry(start="00:00:00", end="01:30:45", text="Long duration")
        self.assertAlmostEqual(entry.get_duration_seconds(), 5445.0, places=1)

    def test_hour_boundary_duration(self):
        """测试跨小时边界时长"""
        entry = TranscriptEntry(start="00:59:59", end="01:00:01", text="Hour boundary")
        self.assertAlmostEqual(entry.get_duration_seconds(), 2.0, places=1)


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)
