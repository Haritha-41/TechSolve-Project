from dataclasses import dataclass, field


@dataclass
class ChatMemory:
    messages: list[tuple[str, str]] = field(default_factory=list)


_MEMORIES: dict[str, ChatMemory] = {}


def get_memory(session_id: str) -> ChatMemory:
    if session_id not in _MEMORIES:
        _MEMORIES[session_id] = ChatMemory()
    return _MEMORIES[session_id]


def format_history(memory: ChatMemory, max_messages: int = 6) -> str:
    recent = memory.messages[-max_messages:]
    return "\n".join(f"{role}: {content}" for role, content in recent)
