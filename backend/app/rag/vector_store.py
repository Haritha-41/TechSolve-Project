from app.core.config import get_settings
from app.models.schemas import TranscriptChunk, VideoMetadata
from app.rag.embeddings import get_embedding_model


def get_vector_store(collection_name: str):
    from langchain_chroma import Chroma

    settings = get_settings()
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embedding_model(),
        persist_directory=settings.chroma_persist_dir,
    )


def add_chunks(collection_name: str, chunks: list[TranscriptChunk]) -> None:
    store = get_vector_store(collection_name)
    texts = [chunk.text for chunk in chunks]
    metadatas = [_metadata_for_chroma(chunk) for chunk in chunks]
    ids = [chunk.chunk_id for chunk in chunks]
    if texts:
        store.add_texts(texts=texts, metadatas=metadatas, ids=ids)


def add_video_metadata(collection_name: str, label: str, metadata: VideoMetadata) -> None:
    store = get_vector_store(collection_name)
    source_video = "A" if "A" in label else "B"
    text = (
        f"Video {source_video} metadata. Title: {metadata.title}. Creator: {metadata.creator_name}. "
        f"Platform: {metadata.platform}. Views: {_display(metadata.views)}. Likes: {_display(metadata.likes)}. "
        f"Comments: {_display(metadata.comments)}. Followers: {_display(metadata.follower_count)}. "
        f"Engagement rate: {_display(metadata.engagement_rate)}. URL: {metadata.url}."
    )
    store.add_texts(
        texts=[text],
        metadatas=[
            {
                key: value
                for key, value in {
                    "chunk_id": f"{source_video}-metadata",
                    "video_label": label,
                    "source_video": source_video,
                    "creator_name": metadata.creator_name,
                    "video_url": metadata.url,
                    "title": metadata.title,
                    "platform": metadata.platform,
                    "views": metadata.views,
                    "likes": metadata.likes,
                    "comments": metadata.comments,
                    "follower_count": metadata.follower_count,
                    "engagement_rate": metadata.engagement_rate,
                    "document_type": "metadata",
                }.items()
                if value is not None
            }
        ],
        ids=[f"{source_video}-metadata"],
    )


def retrieve_chunks(collection_name: str, query: str):
    store = get_vector_store(collection_name)
    return store.similarity_search(query, k=get_settings().retrieval_k)


def _metadata_for_chroma(chunk: TranscriptChunk) -> dict:
    return {
        key: value
        for key, value in chunk.model_dump(exclude={"text"}).items()
        if value is not None
    }


def _display(value) -> str:
    return "unavailable" if value is None else str(value)
