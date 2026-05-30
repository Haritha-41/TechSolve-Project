import logging
import re

from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)


def extract_youtube_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=", 1)[1].split("&", 1)[0]
    if "youtu.be/" in url:
        return url.rsplit("/", 1)[-1].split("?", 1)[0]
    raise ValueError("Unsupported YouTube URL format")


def fetch_youtube_metadata(url: str) -> dict:
    options = {"quiet": True, "skip_download": True}
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title") or "Untitled YouTube video",
        "platform": "youtube",
        "url": url,
        "creator_name": info.get("uploader") or info.get("channel") or "Unknown",
        "follower_count": info.get("channel_follower_count"),
        "likes": int(info.get("like_count") or 0),
        "comments": int(info.get("comment_count") or 0),
        "views": int(info.get("view_count") or 0),
        "upload_date": _format_upload_date(info.get("upload_date")),
        "duration_seconds": info.get("duration"),
        "hashtags": _extract_hashtags(info),
    }


def fetch_youtube_transcript(url: str) -> list[dict]:
    video_id = extract_youtube_id(url)
    logger.info("Fetching YouTube transcript for %s", video_id)
    transcript = YouTubeTranscriptApi().fetch(video_id)
    return [
        {"text": item.text, "start": item.start, "duration": item.duration}
        for item in transcript
    ]


def _format_upload_date(value: str | None) -> str | None:
    if not value or len(value) != 8:
        return value
    return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"


def _extract_hashtags(info: dict) -> list[str]:
    tags = [tag for tag in info.get("tags") or [] if str(tag).startswith("#")]
    description_tags = re.findall(r"#\w+", info.get("description") or "")
    return sorted(set(tags + description_tags))
