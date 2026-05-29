from app.models.schemas import TranscriptChunk


def chunk_transcript(video_label: str, transcript: list[dict], chunk_size: int = 900) -> list[TranscriptChunk]:
    chunks: list[TranscriptChunk] = []
    buffer = ""
    chunk_index = 1

    for item in transcript:
        text = item.get("text", "").strip()
        if not text:
            continue
        if len(buffer) + len(text) > chunk_size and buffer:
            chunks.append(_build_chunk(video_label, chunk_index, buffer))
            chunk_index += 1
            buffer = ""
        buffer = f"{buffer} {text}".strip()

    if buffer:
        chunks.append(_build_chunk(video_label, chunk_index, buffer))
    return chunks


def _build_chunk(video_label: str, index: int, text: str) -> TranscriptChunk:
    return TranscriptChunk(chunk_id=f"{video_label.lower().replace(' ', '-')}-{index}", video_label=video_label, text=text)
