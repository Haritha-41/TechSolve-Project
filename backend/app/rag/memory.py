from langchain.memory import ConversationBufferMemory

_MEMORIES: dict[str, ConversationBufferMemory] = {}


def get_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in _MEMORIES:
        _MEMORIES[session_id] = ConversationBufferMemory(return_messages=True)
    return _MEMORIES[session_id]
