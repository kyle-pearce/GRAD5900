"""
Tier 2 approval gate — non-blocking design.

When EmailSkill produces a draft it:
  1. Stores the draft here under a UUID
  2. Emits an approval_required SSE event with that UUID
  3. Ends the generator (no blocking)

The frontend shows Save / Cancel. On user response:
  POST /api/approval/{id}/respond
  → retrieves the draft and writes it to disk if approved
"""

from enum import Enum

class ApprovalOutcome(str, Enum):
    APPROVED = "approved"
    CANCELLED = "cancelled"

# pending_drafts: approval_id → draft text
_pending_drafts: dict[str, str] = {}


def store_pending_draft(approval_id: str, draft: str) -> None:
    _pending_drafts[approval_id] = draft


def pop_pending_draft(approval_id: str) -> str | None:
    return _pending_drafts.pop(approval_id, None)
