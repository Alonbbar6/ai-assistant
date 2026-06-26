from collections import deque
from typing import Literal

MessageRole = Literal["user", "assistant"]


class ConversationMemory:
    """Sliding-window conversation history for the agent."""

    def __init__(self, max_turns: int = 20):
        self._messages: deque[dict] = deque(maxlen=max_turns * 2)

    def add(self, role: MessageRole, content: str | list) -> None:
        self._messages.append({"role": role, "content": content})

    def history(self) -> list[dict]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)
