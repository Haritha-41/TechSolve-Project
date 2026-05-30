import logging
from typing import Any

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


COUNT_KEYS = {
    "views": (
        "views",
        "viewCount",
        "viewsCount",
        "views_count",
        "playCount",
        "play_count",
        "plays",
        "videoViewCount",
        "video_view_count",
    ),
    "likes": ("likes", "likeCount", "likesCount", "like_count", "likes_count"),
    "comments": ("comments", "commentCount", "commentsCount", "comment_count", "comments_count"),
    "follower_count": ("followers", "followerCount", "followersCount", "follower_count", "followers_count"),
}

TEXT_KEYS = {
    "title": ("caption", "description", "title"),
    "creator_name": ("ownerUsername", "authorUsername", "author_username", "username", "userName"),
    "upload_date": ("timestamp", "postedAt", "posted_at", "takenAt", "taken_at", "date"),
}


def fetch_apify_reel_metadata(url: str, username: str | None = None) -> dict:
    settings = get_settings()
    if settings.instagram_view_provider.lower() != "apify" or not settings.apify_token:
        return {}

    actor_id = _format_actor_id(settings.apify_reel_actor_id)
    endpoint = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    response = _run_actor(endpoint, settings.apify_token, settings.apify_timeout_seconds, _direct_url_input(url))
    if response is None and username:
        response = _run_actor(endpoint, settings.apify_token, settings.apify_timeout_seconds, _username_input(username))
    if response is None:
        return {}

    try:
        items = response.json()
    except ValueError:
        logger.warning("Apify Instagram Reel fallback returned non-JSON response")
        return {}

    if not isinstance(items, list) or not items:
        logger.warning("Apify Instagram Reel fallback returned no dataset items")
        return {}

    item = _best_item(items, url)
    metadata = {
        key: _extract_count(item, *count_keys)
        for key, count_keys in COUNT_KEYS.items()
    }
    metadata.update(
        {
            key: _extract_text(item, *text_keys)
            for key, text_keys in TEXT_KEYS.items()
        }
    )
    return {key: value for key, value in metadata.items() if value not in (None, "")}


def _run_actor(endpoint: str, token: str, timeout_seconds: int, payload: dict) -> requests.Response | None:
    try:
        response = requests.post(
            endpoint,
            params={"token": token, "timeout": timeout_seconds},
            json=payload,
            timeout=timeout_seconds + 15,
        )
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        response_text = exc.response.text[:500] if exc.response is not None else ""
        logger.warning("Apify Instagram Reel fallback failed with status %s: %s", status_code, response_text)
        return None


def _direct_url_input(url: str) -> dict:
    return {
        "urls": [url],
        "directUrls": [url],
        "startUrls": [{"url": url}],
        "maxItems": 1,
        "maxReels": 1,
        "maxReelsPerProfile": 1,
        "limit": 1,
        "resultsLimit": 1,
        "commentsPerReel": 0,
        "proxyConfiguration": _proxy_configuration(),
    }


def _username_input(username: str) -> dict:
    return {
        "username": [username.lstrip("@")],
        "usernames": [username.lstrip("@")],
        "urls": [username.lstrip("@")],
        "maxItems": 1,
        "maxReels": 1,
        "maxReelsPerProfile": 1,
        "limit": 1,
        "resultsLimit": 1,
        "commentsPerReel": 0,
        "proxyConfiguration": _proxy_configuration(),
    }


def _proxy_configuration() -> dict:
    return {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"],
    }


def _format_actor_id(actor_id: str) -> str:
    return actor_id.replace("/", "~")


def _best_item(items: list[Any], url: str) -> dict:
    shortcode = _shortcode(url)
    for item in items:
        if isinstance(item, dict) and shortcode and shortcode in str(item):
            return item
    return next((item for item in items if isinstance(item, dict)), {})


def _shortcode(url: str) -> str:
    parts = [part for part in url.rstrip("/").split("/") if part]
    if not parts:
        return ""
    return parts[-1]


def _extract_count(value: Any, *keys: str) -> int | None:
    found = _find_key(value, set(keys))
    if found is None:
        return None
    if isinstance(found, dict):
        found = found.get("count")
    if isinstance(found, str):
        found = found.replace(",", "").strip().lower()
        multiplier = 1
        if found.endswith("k"):
            multiplier = 1_000
            found = found[:-1]
        elif found.endswith("m"):
            multiplier = 1_000_000
            found = found[:-1]
        elif found.endswith("b"):
            multiplier = 1_000_000_000
            found = found[:-1]
        try:
            return int(float(found) * multiplier)
        except ValueError:
            return None
    try:
        return int(float(found))
    except (TypeError, ValueError):
        return None


def _extract_text(value: Any, *keys: str) -> str | None:
    found = _find_key(value, set(keys))
    if isinstance(found, str) and found.strip():
        return found.strip()
    return None


def _find_key(value: Any, keys: set[str]) -> Any:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key in keys:
                return nested_value
        for nested_value in value.values():
            found = _find_key(nested_value, keys)
            if found is not None:
                return found
    if isinstance(value, list):
        for item in value:
            found = _find_key(item, keys)
            if found is not None:
                return found
    return None
