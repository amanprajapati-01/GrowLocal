"""Feedback endpoint: store what worked / didn't for the next plan."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from app.models.feedback import FeedbackRequest
from app.services.auth import get_current_user
from app.services.store import get_store

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback")
async def create_feedback(
    req: FeedbackRequest, user: str = Depends(get_current_user)
) -> dict[str, object]:
    store = get_store()
    plan_doc = store.get_plan(req.planId)
    if not plan_doc or plan_doc.get("ownerUid") != user:
        raise HTTPException(status_code=404, detail="Plan not found.")
    doc = {
        "planId": req.planId,
        "channelId": req.channelId,
        "outcome": req.outcome,
        "note": req.note,
    }
    feedback_id = store.save_feedback(user, {**doc, "createdAt": datetime.now(UTC).isoformat()})
    return {"feedbackId": feedback_id, "status": "stored"}
