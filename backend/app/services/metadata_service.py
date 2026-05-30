from app.models.schemas import VideoMetadata


def calculate_engagement_rate(likes: int, comments: int, views: int) -> float:
    if views <= 0:
        return 0.0
    return round(((likes + comments) / views) * 100, 2)


def build_metadata(raw: dict) -> VideoMetadata:
    engagement_rate = calculate_engagement_rate(
        raw.get("likes", 0),
        raw.get("comments", 0),
        raw.get("views", 0),
    )
    return VideoMetadata(**raw, engagement_rate=engagement_rate)


def detect_platform(url: str) -> str:
    lowered_url = url.lower()
    if "youtube.com" in lowered_url or "youtu.be" in lowered_url:
        return "youtube"
    if "instagram.com" in lowered_url:
        return "instagram"
    raise ValueError("URL must be from YouTube or Instagram")
