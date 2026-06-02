from app.models.schemas import TranscriptChunk, VideoMetadata
from app.services.transcript_service import normalize_transcript


def chunk_transcript(
    video_label: str,
    transcript: list[dict],
    metadata: VideoMetadata,
    chunk_size: int = 900,
) -> list[TranscriptChunk]:
    chunks: list[TranscriptChunk] = []
    buffer = ""
    start_seconds: float | None = None
    end_seconds: float | None = None
    chunk_index = 1

    for item in transcript:
        text = normalize_transcript(item.get("text", ""))
        if not text:
            continue
        if start_seconds is None:
            start_seconds = item.get("start")
        end_seconds = _segment_end(item)
        if len(buffer) + len(text) > chunk_size and buffer:
            chunks.append(_build_chunk(video_label, chunk_index, metadata, buffer, start_seconds, end_seconds))
            chunk_index += 1
            buffer = ""
            start_seconds = item.get("start")
        buffer = f"{buffer} {text}".strip()

    if buffer:
        chunks.append(_build_chunk(video_label, chunk_index, metadata, buffer, start_seconds, end_seconds))
    return chunks


def _build_chunk(
    video_label: str,
    index: int,
    metadata: VideoMetadata,
    text: str,
    start_seconds: float | None,
    end_seconds: float | None,
) -> TranscriptChunk:
    source_video = "A" if "A" in video_label else "B"
    return TranscriptChunk(
        chunk_id=f"{source_video}-{index}",
        video_label=video_label,
        source_video=source_video,
        creator_name=metadata.creator_name,
        video_url=metadata.url,
        text=text,
        start_seconds=start_seconds,
        end_seconds=end_seconds,
        title=metadata.title,
        platform=metadata.platform,
        views=metadata.views,
        likes=metadata.likes,
        comments=metadata.comments,
        follower_count=metadata.follower_count,
        engagement_rate=metadata.engagement_rate,
    )


def _segment_end(item: dict) -> float | None:
    start = item.get("start")
    duration = item.get("duration")
    if start is None or duration is None:
        return None
    return start + duration
