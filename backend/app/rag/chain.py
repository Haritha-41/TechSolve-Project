import logging

from app.models.schemas import ChatRequest
from app.rag.memory import get_memory

logger = logging.getLogger(__name__)


async def stream_rag_answer(request: ChatRequest):
    memory = get_memory(request.session_id)
    memory.chat_memory.add_user_message(request.message)
    logger.info("Streaming placeholder RAG response for session %s", request.session_id)

    response = "RAG pipeline placeholder. Analyze videos first, then wire retrieval and Gemini streaming here."
    for token in response.split(" "):
        yield {"event": "token", "data": f"{token} "}

    memory.chat_memory.add_ai_message(response)
    yield {"event": "done", "data": "[done]"}
