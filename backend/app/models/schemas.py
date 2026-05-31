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
    creator_name: str = "Unknown"
    follower_count: int | None = None
    likes: int | None = None
    comments: int | None = None
    views: int | None = None
    upload_date: str | None = None
    duration_seconds: float | None = None
    hashtags: list[str] = []
    engagement_rate: float | None = None


class TranscriptChunk(BaseModel):
    chunk_id: str
    video_label: str
    source_video: str
    creator_name: str
    video_url: str
    text: str
    start_seconds: float | None = None
    end_seconds: float | None = None
    title: str | None = None
    platform: str | None = None
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    follower_count: int | None = None
    engagement_rate: float | None = None
    document_type: str = "transcript"


class VideoAnalysis(BaseModel):
    metadata: VideoMetadata
    transcript_preview: str = ""
    transcript: str = ""
    chunks: list[TranscriptChunk] = []


class AnalyzeVideosResponse(BaseModel):
    videos: list[VideoAnalysis]
    collection_name: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    collection_name: str
    session_id: str = "default"


class ErrorResponse(BaseModel):
    detail: str
