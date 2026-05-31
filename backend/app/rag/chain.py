import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.models.schemas import ChatRequest
from app.rag.memory import format_history, get_memory
from app.rag.vector_store import retrieve_chunks

logger = logging.getLogger(__name__)


async def stream_rag_answer(request: ChatRequest):
    try:
        memory = get_memory(request.session_id)
        memory.messages.append(("User", request.message))
        docs = retrieve_chunks(request.collection_name, request.message)
        prompt = _build_prompt(request.message, docs, format_history(memory))
        logger.info("Streaming RAG response for session %s", request.session_id)

        response = ""
        if not get_settings().gemini_api_key:
            response = _build_missing_key_response(docs)
            for token in response.split(" "):
                yield {"event": "token", "data": f"{token} "}
        else:
            async for token in _stream_gemini(prompt):
                response += token
                yield {"event": "token", "data": token}

        memory.messages.append(("Assistant", response))
        yield {"event": "done", "data": "[done]"}
    except Exception:
        logger.exception("RAG chat stream failed")
        yield {"event": "token", "data": "Chat failed while generating an answer. Check the backend logs for details."}
        yield {"event": "done", "data": "[done]"}


async def _stream_gemini(prompt: str):
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
    )
    async for chunk in llm.astream(prompt):
        content = chunk.content
        if isinstance(content, str):
            yield content


def _build_prompt(question: str, docs: list, history: str) -> str:
    context = "\n\n".join(_format_doc(doc) for doc in docs)
    return f"""
You are SocialSense RAG, an analyst for short-form video creators.
Answer only from the retrieved transcript chunks and available metadata.
Compare Video A and Video B when useful. Be specific and practical.
Every factual claim from transcripts must cite sources as [Video A, chunk A-1].
If context is insufficient, say what is missing.

Conversation history:
{history or "No previous conversation."}

Retrieved context:
{context or "No transcript chunks were retrieved."}

Available video metadata:
{_format_metadata_from_docs(docs)}

User question:
{question}
""".strip()


def _format_doc(doc) -> str:
    meta = doc.metadata
    if meta.get("document_type") == "metadata":
        return (
            f"[Video {meta.get('source_video')}, metadata] "
            f"Creator: {meta.get('creator_name')}. URL: {meta.get('video_url')}. "
            f"Views: {_display(meta.get('views'))}. Likes: {_display(meta.get('likes'))}. "
            f"Comments: {_display(meta.get('comments'))}. Engagement rate: {_display(meta.get('engagement_rate'))}.\n"
            f"{doc.page_content}"
        )
    return (
        f"[Video {meta.get('source_video')}, chunk {meta.get('chunk_id')}] "
        f"Creator: {meta.get('creator_name')}. URL: {meta.get('video_url')}. "
        f"Views: {_display(meta.get('views'))}. Likes: {_display(meta.get('likes'))}. "
        f"Comments: {_display(meta.get('comments'))}. Engagement rate: {_display(meta.get('engagement_rate'))}.\n"
        f"{doc.page_content}"
    )


def _format_metadata_from_docs(docs: list) -> str:
    by_video = {}
    for doc in docs:
        meta = doc.metadata
        source_video = meta.get("source_video")
        if source_video and source_video not in by_video:
            by_video[source_video] = meta
    if not by_video:
        return "No video metadata was retrieved."
    return "\n".join(
        (
            f"Video {source_video}: title={_display(meta.get('title'))}; "
            f"creator={_display(meta.get('creator_name'))}; views={_display(meta.get('views'))}; "
            f"likes={_display(meta.get('likes'))}; comments={_display(meta.get('comments'))}; "
            f"followers={_display(meta.get('follower_count'))}; "
            f"engagement_rate={_display(meta.get('engagement_rate'))}; url={_display(meta.get('video_url'))}"
        )
        for source_video, meta in sorted(by_video.items())
    )


def _display(value) -> str:
    return "unavailable" if value is None else str(value)


def _build_missing_key_response(docs: list) -> str:
    citations = ", ".join(
        f"[Video {doc.metadata.get('source_video')}, chunk {doc.metadata.get('chunk_id')}]"
        for doc in docs[:3]
    )
    return (
        "Gemini is not configured yet. Add GEMINI_API_KEY to backend/.env to enable full AI answers. "
        f"I retrieved relevant transcript context for this question: {citations or 'no matching chunks found'}."
    )
