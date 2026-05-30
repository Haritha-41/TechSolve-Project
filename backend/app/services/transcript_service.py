import logging
import re
from html import unescape

from app.extractors.instagram import fetch_instagram_transcript
from app.extractors.youtube import fetch_youtube_transcript

logger = logging.getLogger(__name__)


def fetch_transcript(url: str, platform: str) -> list[dict]:
    try:
        if platform == "youtube":
            return fetch_youtube_transcript(url)
        if platform == "instagram":
            return fetch_instagram_transcript(url)
    except Exception:
        logger.exception("Transcript extraction failed for %s", url)
        return []

    raise ValueError(f"Unsupported platform: {platform}")


def transcript_to_text(transcript: list[dict]) -> str:
    return normalize_transcript(" ".join(item.get("text", "") for item in transcript))


def normalize_transcript(text: str) -> str:
    cleaned = unescape(text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()
