"""
BaseSkill: the interface every skill implements.

Each skill declares:
  - REQUIRED_CONTEXT: which context files to load
  - system_prompt: the instruction block prepended to every conversation

Skills communicate with the frontend via a generator that yields SSE event dicts.
"""

from typing import Generator
from ..core.context import load_context
from ..core.ollama_client import stream_chat


class BaseSkill:
    REQUIRED_CONTEXT: list[str] = []
    system_prompt: str = ""

    def _build_system(self) -> str:
        ctx = load_context(self.REQUIRED_CONTEXT)
        if not ctx:
            return self.system_prompt
        context_block = "\n\n".join(
            f"## {stem.replace('-', ' ').replace('_', ' ').title()}\n{content}"
            for stem, content in ctx.items()
            if content
        )
        return f"{self.system_prompt}\n\n---\n\n{context_block}" if context_block else self.system_prompt

    def stream(
        self,
        history: list[dict],
        user_message: str,
    ) -> Generator[dict, None, None]:
        """
        Yield SSE-ready event dicts for this skill turn.

        history: prior [{"role": "user"|"assistant", "content": "..."}] pairs
        user_message: the latest user input (empty string for skill-initiated flows)
        """
        messages = [{"role": "system", "content": self._build_system()}]
        messages.extend(history)
        if user_message:
            messages.append({"role": "user", "content": user_message})

        for token in stream_chat(messages):
            yield {"event": "token", "data": token}

        yield {"event": "done", "data": ""}
