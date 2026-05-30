import logging
import re
from pathlib import Path
from uuid import uuid4

from yt_dlp import YoutubeDL

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def fetch_instagram_metadata(url: str) -> dict:
    options = {"quiet": True, "skip_download": True}
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title") or "Untitled Instagram Reel",
        "platform": "instagram",
        "url": url,
        "creator_name": info.get("uploader") or info.get("channel") or "Unknown",
        "follower_count": info.get("channel_follower_count"),
        "likes": int(info.get("like_count") or 0),
        "comments": int(info.get("comment_count") or 0),
        "views": int(info.get("view_count") or 0),
        "upload_date": _format_timestamp(info),
        "duration_seconds": info.get("duration"),
        "hashtags": _extract_hashtags(info),
    }


def fetch_instagram_transcript(url: str) -> list[dict]:
    logger.info("Transcribing Instagram Reel with local Whisper fallback")
    audio_path = _download_audio(url)
    try:
        return _transcribe_audio(audio_path)
    finally:
        audio_path.unlink(missing_ok=True)


def _download_audio(url: str) -> Path:
    output_template = f"data/instagram-{uuid4().hex}.%(ext)s"
    options = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
    }
    with YoutubeDL(options) as ydl:
        ydl.extract_info(url, download=True)
    return Path(output_template.replace("%(ext)s", "wav"))


def _transcribe_audio(audio_path: Path) -> list[dict]:
    from faster_whisper import WhisperModel

    model = WhisperModel(get_settings().whisper_model, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path))
    return [
        {"text": segment.text.strip(), "start": segment.start, "duration": segment.end - segment.start}
        for segment in segments
        if segment.text.strip()
    ]


def _format_timestamp(info: dict) -> str | None:
    upload_date = info.get("upload_date")
    if upload_date and len(upload_date) == 8:
        return f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    timestamp = info.get("timestamp")
    return str(timestamp) if timestamp else None


def _extract_hashtags(info: dict) -> list[str]:
    tags = [tag for tag in info.get("tags") or [] if str(tag).startswith("#")]
    description_tags = re.findall(r"#\w+", info.get("description") or "")
    return sorted(set(tags + description_tags))
