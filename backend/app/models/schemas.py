from pydantic import BaseModel, Field, HttpUrl


class VideoInput(BaseModel):
    label: str = Field(..., examples=["Video A"])
    url: HttpUrl


class AnalyzeVideosRequest(BaseModel):
    video_a: VideoInput
    video_b: VideoInput


class VideoMetadata(BaseModel):
    title: str = "Unavailable"
    platform: str
    url: str
    likes: int = 0
    comments: int = 0
    views: int = 0
    engagement_rate: float = 0.0


class TranscriptChunk(BaseModel):
    chunk_id: str
    video_label: str
    text: str
    start_seconds: float | None = None
    end_seconds: float | None = None


class VideoAnalysis(BaseModel):
    metadata: VideoMetadata
    transcript_preview: str = ""
    chunks: list[TranscriptChunk] = []


class AnalyzeVideosResponse(BaseModel):
    videos: list[VideoAnalysis]
    collection_name: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    collection_name: str
    session_id: str = "default"
