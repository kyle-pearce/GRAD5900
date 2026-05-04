"""
Email draft skill (Tier 2 — requires approval before saving to disk).

The user pastes an email thread; this skill drafts a reply in their voice.
The draft is stored in the approval module. Writing to disk only happens
after the user explicitly clicks Save Draft in the UI.
"""

import uuid
from typing import Generator

from .base import BaseSkill
from ..core.ollama_client import stream_chat
from ..core.context import load_context
from ..approval import store_pending_draft


class EmailSkill(BaseSkill):
    REQUIRED_CONTEXT = ["writing-style.md", "email-goals.md"]
    TRIGGER_MESSAGE = "I need to draft an email."

    system_prompt = """You are drafting an email reply for the user.

Ask the user to paste the email thread they want to reply to, or describe the situation
if they do not have the thread.

Then draft a reply that:
- Matches their writing style and communication preferences exactly
- Is direct and appropriately concise
- Addresses every point that needs a response
- Ends with a clear next step or ask

Present the draft clearly between --- markers so it is easy to copy.
Flag any sentence you are uncertain about in tone with a brief note."""

    def stream(self, history: list[dict], user_message: str) -> Generator[dict, None, None]:
        ctx = load_context(self.REQUIRED_CONTEXT)
        context_block = "\n\n".join(
            f"## {stem.replace('-', ' ').title()}\n{content}"
            for stem, content in ctx.items()
            if content
        )
        system = (
            f"{self.system_prompt}\n\n---\n\n{context_block}"
            if context_block
            else self.system_prompt
        )

        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message or self.TRIGGER_MESSAGE})

        # Stream the draft
        draft_tokens: list[str] = []
        for token in stream_chat(messages):
            draft_tokens.append(token)
            yield {"event": "token", "data": token}

        draft = "".join(draft_tokens)

        # Store the draft and request approval (non-blocking)
        approval_id = str(uuid.uuid4())
        store_pending_draft(approval_id, draft)

        yield {
            "event": "approval_required",
            "data": {
                "id": approval_id,
                "tier": 2,
                "action": "save_email_draft",
                "description": "Save this email draft to disk?",
            },
        }

        yield {"event": "done", "data": ""}
