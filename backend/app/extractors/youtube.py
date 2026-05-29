import logging

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
        "likes": int(info.get("like_count") or 0),
        "comments": int(info.get("comment_count") or 0),
        "views": int(info.get("view_count") or 0),
    }


def fetch_youtube_transcript(url: str) -> list[dict]:
    video_id = extract_youtube_id(url)
    logger.info("Fetching YouTube transcript for %s", video_id)
    return YouTubeTranscriptApi.get_transcript(video_id)
