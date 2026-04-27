from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..approval import ApprovalOutcome, pop_pending_draft
from ..core.config import settings

router = APIRouter(prefix="/api/approval")


class ApprovalResponse(BaseModel):
    outcome: ApprovalOutcome  # "approved" or "cancelled"


@router.post("/{approval_id}/respond")
async def respond(approval_id: str, body: ApprovalResponse):
    draft = pop_pending_draft(approval_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Approval gate not found or already resolved")

    if body.outcome == ApprovalOutcome.APPROVED:
        draft_path = settings.handoffs_dir / "email-draft.md"
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(draft, encoding="utf-8")
        return {"status": "ok", "outcome": "approved", "saved_to": str(draft_path)}

    return {"status": "ok", "outcome": "cancelled"}
