from typing import Generator
from .base import BaseSkill
from ..knowledge.retriever import query_knowledge


class OneOnOneSkill(BaseSkill):
    REQUIRED_CONTEXT = ["goals.md", "projects.md", "mental-model.md"]

    system_prompt = """You are helping the user prepare for a 1:1 meeting.

First ask: "Who is this 1:1 with?"

Then produce a prep sheet covering:
- Context to recall about this person and your relationship
- Agenda topics based on current projects and goals
- Open items from past meetings (if any surface from memory)
- Your asks or decisions that need to come out of this meeting
- Coaching note: anything from the user's mental model relevant to this 1:1

Format the output as:

## 1:1 Prep — [person name]
**Context:** [relationship and standing context]
**Agenda topics:**
- [topic]
**Open items from last time:** [items or "none"]
**Your asks:** [what you need from this meeting]
**Watch-out:** [coaching note if relevant]

Be specific. Use the projects and goals context to make this prep actionable."""

    def stream(self, history: list[dict], user_message: str) -> Generator[dict, None, None]:
        # If the user has named a person, query knowledge for past meeting context
        person = self._extract_person(history, user_message)
        if person:
            result = query_knowledge(f"past meetings with {person} action items open decisions")
            retrieved = result["chunks"]
            if retrieved:
                retrieved_block = "\n\n---\n\n".join(retrieved[:3])
                history = [
                    *history,
                    {
                        "role": "system",
                        "content": f"Retrieved past context for {person}:\n\n{retrieved_block}",
                    },
                ]
        yield from super().stream(history, user_message)

    def _extract_person(self, history: list[dict], user_message: str) -> str | None:
        """Look for a person's name in recent history or current message."""
        for msg in reversed(history[-4:]):
            content = msg.get("content", "")
            if "with" in content.lower():
                parts = content.lower().split("with")
                if len(parts) > 1:
                    candidate = parts[-1].strip().split()[0].rstrip(".,!?")
                    if candidate:
                        return candidate.title()
        return None
