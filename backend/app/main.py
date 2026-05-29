import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.extractors.instagram import fetch_instagram_metadata
from app.extractors.youtube import fetch_youtube_metadata
from app.models.schemas import AnalyzeVideosRequest, AnalyzeVideosResponse, ChatRequest, VideoAnalysis
from app.rag.chain import stream_rag_answer
from app.rag.chunker import chunk_transcript
from app.rag.vector_store import add_chunks
from app.services.metadata_service import build_metadata
from app.services.transcript_service import fetch_transcript, transcript_to_text

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/videos/analyze", response_model=AnalyzeVideosResponse)
def analyze_videos(payload: AnalyzeVideosRequest) -> AnalyzeVideosResponse:
    try:
        collection_name = f"socialsense-{uuid4().hex[:12]}"
        analyses = [
            _analyze_video(str(payload.video_a.url), payload.video_a.label, "youtube", collection_name),
            _analyze_video(str(payload.video_b.url), payload.video_b.label, "instagram", collection_name),
        ]
        return AnalyzeVideosResponse(videos=analyses, collection_name=collection_name)
    except Exception as exc:
        logger.exception("Video analysis failed")
        raise HTTPException(status_code=500, detail="Video analysis failed") from exc


@app.post("/api/chat/stream")
async def chat_stream(payload: ChatRequest) -> EventSourceResponse:
    return EventSourceResponse(stream_rag_answer(payload))


def _analyze_video(url: str, label: str, platform: str, collection_name: str) -> VideoAnalysis:
    raw_metadata = fetch_youtube_metadata(url) if platform == "youtube" else fetch_instagram_metadata(url)
    metadata = build_metadata(raw_metadata)
    transcript = fetch_transcript(url, platform)
    chunks = chunk_transcript(label, transcript)
    add_chunks(collection_name, chunks)
    return VideoAnalysis(
        metadata=metadata,
        transcript_preview=transcript_to_text(transcript)[:500],
        chunks=chunks,
    )
