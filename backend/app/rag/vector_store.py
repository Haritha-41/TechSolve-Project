from app.core.config import get_settings
from app.models.schemas import TranscriptChunk
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


def retrieve_chunks(collection_name: str, query: str):
    store = get_vector_store(collection_name)
    return store.similarity_search(query, k=get_settings().retrieval_k)


def _metadata_for_chroma(chunk: TranscriptChunk) -> dict:
    return {
        key: value
        for key, value in chunk.model_dump(exclude={"text"}).items()
        if value is not None
    }
