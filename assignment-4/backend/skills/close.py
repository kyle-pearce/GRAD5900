"""
Close skill — generates a session summary from chat history, writes it to disk,
and auto-ingests it into ChromaDB.

Triggered by the "Close Session" button in the UI sidebar.
"""

import datetime
from typing import Generator

from .base import BaseSkill
from ..core.config import settings
from ..core.ollama_client import stream_chat
from ..knowledge.ingest import ingest_single


CLOSE_SYSTEM = """You are writing a session summary from a conversation history.

Produce a structured handoff document in this format:

# Session Handoff — [date]

## What Was Worked On
[Summary of the session content]

## Goal Alignment
[One sentence: did the work reflect stated priorities?]

## Decisions Made
- [bullet list or "none"]

## Carry-Forward / Open Items
- [bullet list or "none"]

## Next Session Starting Point
[One sentence: where to pick up next time]

Be factual and concise. Use the user's own words where possible.
Do not add commentary or filler."""


class CloseSkill(BaseSkill):
    REQUIRED_CONTEXT = []

    def stream(self, history: list[dict], user_message: str = "") -> Generator[dict, None, None]:
        today = datetime.date.today().isoformat()

        # Summarize the full session history
        history_text = "\n\n".join(
            f"**{m['role'].title()}:** {m['content']}" for m in history
        )
        messages = [
            {"role": "system", "content": CLOSE_SYSTEM.replace("[date]", today)},
            {"role": "user", "content": f"Here is the session conversation:\n\n{history_text}"},
        ]

        summary_tokens: list[str] = []
        for token in stream_chat(messages):
            summary_tokens.append(token)
            yield {"event": "token", "data": token}

        summary = "".join(summary_tokens)

        # Write to handoffs/session-handoff.md
        handoff_path = settings.handoffs_dir / "session-handoff.md"
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        handoff_path.write_text(summary, encoding="utf-8")

        # Auto-ingest into ChromaDB (Tier 1 — no approval needed)
        chunk_count = ingest_single(str(handoff_path))

        yield {
            "event": "token",
            "data": f"\n\n_Session closed. Handoff written and ingested ({chunk_count} chunks)._",
        }
        yield {"event": "done", "data": ""}
