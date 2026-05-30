import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def fetch_instagram_metadata(url: str) -> dict:
    info = _extract_info(url, download=False)

    return {
        "title": _first_text(info, "title", "description") or "Untitled Instagram Reel",
        "platform": "instagram",
        "url": url,
        "creator_name": _first_text(info, "uploader", "channel", "uploader_id", "channel_id") or "Unknown",
        "follower_count": _to_int(info.get("channel_follower_count")),
        "likes": _to_int(info.get("like_count")),
        "comments": _to_int(info.get("comment_count")),
        "views": _to_int(info.get("view_count") or info.get("play_count")),
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
    options.update(_cookie_options())
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
    if timestamp:
        return datetime.fromtimestamp(timestamp, tz=UTC).date().isoformat()
    return None


def _extract_hashtags(info: dict) -> list[str]:
    tags = [tag for tag in info.get("tags") or [] if str(tag).startswith("#")]
    description_tags = re.findall(r"#\w+", info.get("description") or "")
    return sorted(set(tags + description_tags))


def _extract_info(url: str, download: bool) -> dict:
    options = {
        "quiet": True,
        "skip_download": not download,
        "noplaylist": True,
        "ignore_no_formats_error": True,
    }
    options.update(_cookie_options())
    try:
        with YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=download)
    except DownloadError as exc:
        logger.exception("Instagram metadata extraction failed")
        raise ValueError(
            "Instagram metadata could not be extracted. If the reel is public but still fails, "
            "set INSTAGRAM_COOKIES_FILE in backend/.env to a Netscape cookies.txt export."
        ) from exc


def _cookie_options() -> dict:
    cookies_file = get_settings().instagram_cookies_file
    if not cookies_file:
        return {}
    return {"cookiefile": cookies_file}


def _first_text(info: dict, *keys: str) -> str | None:
    for key in keys:
        value = info.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _to_int(value) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0
