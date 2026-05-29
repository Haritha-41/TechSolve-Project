import logging

from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)


def fetch_instagram_metadata(url: str) -> dict:
    options = {"quiet": True, "skip_download": True}
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title") or "Untitled Instagram Reel",
        "platform": "instagram",
        "url": url,
        "likes": int(info.get("like_count") or 0),
        "comments": int(info.get("comment_count") or 0),
        "views": int(info.get("view_count") or 0),
    }


def fetch_instagram_transcript(url: str) -> list[dict]:
    logger.info("Instagram transcript extraction is a placeholder for local Whisper fallback")
    return [{"text": "Instagram transcription placeholder.", "start": 0.0, "duration": 0.0}]
