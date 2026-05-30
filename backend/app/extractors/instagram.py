import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import requests
from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL

from app.extractors.apify_instagram import fetch_apify_reel_metadata
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def fetch_instagram_metadata(url: str) -> dict:
    info = _extract_info(url, download=False)
    creator_name = _first_text(info, "uploader", "channel", "uploader_id", "channel_id") or "Unknown"
    fallback_metadata = fetch_apify_reel_metadata(url, creator_name if creator_name != "Unknown" else None)
    follower_count = _extract_follower_count(info, creator_name)
    views = _extract_count(info, "view_count", "play_count", "video_view_count", "video_play_count", "reel_view_count")
    likes = _extract_count(info, "like_count", "likes", "edge_media_preview_like", "edge_liked_by")
    comments = _extract_count(info, "comment_count", "comments", "edge_media_preview_comment", "edge_media_to_comment")

    views = views if views is not None else fallback_metadata.get("views")
    likes = likes if likes is not None else fallback_metadata.get("likes")
    comments = comments if comments is not None else fallback_metadata.get("comments")
    follower_count = follower_count if follower_count is not None else fallback_metadata.get("follower_count")

    _log_missing_counts(url, views, likes, comments, follower_count)

    return {
        "title": _first_text(info, "title", "description") or fallback_metadata.get("title") or "Untitled Instagram Reel",
        "platform": "instagram",
        "url": url,
        "creator_name": creator_name if creator_name != "Unknown" else fallback_metadata.get("creator_name", creator_name),
        "follower_count": follower_count,
        "likes": likes,
        "comments": comments,
        "views": views,
        "upload_date": _format_timestamp(info) or fallback_metadata.get("upload_date"),
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
    if not Path(cookies_file).expanduser().exists():
        logger.warning("INSTAGRAM_COOKIES_FILE is set but the file does not exist: %s", cookies_file)
        return {}
    return {"cookiefile": cookies_file}


def _first_text(info: dict, *keys: str) -> str | None:
    for key in keys:
        value = info.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_count(info: dict, *keys: str) -> int | None:
    for key in keys:
        value = _to_optional_int(info.get(key))
        if value is not None:
            return value
    nested_value = _find_nested_count(info, keys)
    return _to_optional_int(nested_value)


def _extract_follower_count(info: dict, creator_name: str) -> int | None:
    count = _extract_count(info, "channel_follower_count", "follower_count", "followers")
    if count is not None:
        return count
    username = _profile_username(info, creator_name)
    if not username:
        return None
    return _fetch_profile_follower_count(username)


def _find_nested_count(value, keys: tuple[str, ...]):
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key in keys:
                return nested_value
            found = _find_nested_count(nested_value, keys)
            if found is not None:
                return found
    if isinstance(value, list):
        for item in value:
            found = _find_nested_count(item, keys)
            if found is not None:
                return found
    return None


def _profile_username(info: dict, creator_name: str) -> str | None:
    username = _first_text(info, "channel", "channel_id", "uploader")
    if username and not username.startswith("http"):
        return username.lstrip("@")
    if creator_name != "Unknown" and " " not in creator_name:
        return creator_name.lstrip("@")
    username = _first_text(info, "uploader_id")
    if username and not username.isdigit():
        return username.lstrip("@")
    return None


def _fetch_profile_follower_count(username: str) -> int | None:
    url = f"https://www.instagram.com/{username}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
    except requests.RequestException:
        logger.info("Instagram profile follower fallback failed for %s", username)
        return None

    match = re.search(r'property="og:description"\s+content="([^"]+)"', response.text)
    if not match:
        return None
    followers_text = match.group(1).split("Followers", 1)[0].split(",")[0].strip()
    return _parse_compact_count(followers_text)


def _parse_compact_count(value: str) -> int | None:
    compact = value.replace(",", "").strip().lower()
    match = re.match(r"([\d.]+)\s*([kmb])?", compact)
    if not match:
        return None
    number = float(match.group(1))
    multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(match.group(2), 1)
    return int(number * multiplier)


def _to_optional_int(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return _to_optional_int(value.get("count"))
    if isinstance(value, str):
        value = value.replace(",", "").strip()
        parsed = _parse_compact_count(value)
        if parsed is not None:
            return parsed
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _log_missing_counts(url: str, views: int | None, likes: int | None, comments: int | None, followers: int | None) -> None:
    missing = [
        name
        for name, value in {
            "views": views,
            "likes": likes,
            "comments": comments,
            "followers": followers,
        }.items()
        if value is None
    ]
    if missing:
        logger.warning("Instagram metadata missing %s for %s", ", ".join(missing), url)
