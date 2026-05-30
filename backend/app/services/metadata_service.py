from app.models.schemas import VideoMetadata


def calculate_engagement_rate(likes: int | None, comments: int | None, views: int | None) -> float | None:
    if not views or views <= 0:
        return None
    return round((((likes or 0) + (comments or 0)) / views) * 100, 2)


def build_metadata(raw: dict) -> VideoMetadata:
    engagement_rate = calculate_engagement_rate(
        raw.get("likes"),
        raw.get("comments"),
        raw.get("views"),
    )
    return VideoMetadata(**raw, engagement_rate=engagement_rate)


def detect_platform(url: str) -> str:
    lowered_url = url.lower()
    if "youtube.com" in lowered_url or "youtu.be" in lowered_url:
        return "youtube"
    if "instagram.com" in lowered_url:
        return "instagram"
    raise ValueError("URL must be from YouTube or Instagram")
