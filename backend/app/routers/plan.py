"""Plan endpoints: create, list, fetch, task toggles, and channels metadata."""

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.models.plan import PlanRequest, PlanResponse
from app.services import plan_service
from app.services.auth import get_current_user
from app.services.catalog import channel_catalog
from app.services.store import get_store

router = APIRouter(prefix="/api", tags=["plan"])

SAFE_ID = re.compile(r"^[\w\-]{4,64}$")
TASK_ID_RE = re.compile(r"t_w[1-4]_n\d+")


def _compact(doc: dict[str, Any]) -> dict[str, Any]:
    inp = doc.get("input", {})
    alloc = doc.get("budgetAllocation", {})
    return {
        "planId": doc.get("planId", ""),
        "businessName": inp.get("businessName", ""),
        "businessType": inp.get("businessType", ""),
        "city": inp.get("city", ""),
        "locality": inp.get("locality", ""),
        "goal": inp.get("goal", ""),
        "language": inp.get("language", "en"),
        "monthlyBudgetInr": inp.get("monthlyBudgetInr", 0),
        "allocatedInr": sum(i.get("amountInr", 0) for i in alloc.get("items", [])),
        "bufferInr": alloc.get("bufferInr", 0),
        "status": doc.get("status", ""),
        "createdAt": doc.get("createdAt", ""),
    }


def _response_from_doc(doc: dict[str, Any]) -> PlanResponse:
    data = {k: v for k, v in doc.items() if k in PlanResponse.model_fields}
    return PlanResponse(**data)


@router.get("/channels")
async def channels_metadata() -> dict[str, Any]:
    """Bilingual channel catalog for UI labels (single source of truth)."""
    channels = [
        {
            "id": ch["id"],
            "name": ch["name"],
            "costType": ch.get("costType", "free"),
            "effort": ch.get("effort", ""),
            "timeToResult": ch.get("timeToResult", ""),
        }
        for ch in channel_catalog.values()
    ]
    return {"channels": channels}


@router.post("/plan", response_model=PlanResponse)
async def create_plan(req: PlanRequest, user: str = Depends(get_current_user)) -> PlanResponse:
    return await plan_service.create_plan(user, req)


@router.get("/plans")
async def list_plans(user: str = Depends(get_current_user)) -> dict[str, Any]:
    docs = get_store().list_plans(user)
    return {"plans": [_compact(d) for d in docs]}


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str, user: str = Depends(get_current_user)) -> PlanResponse:
    doc = get_store().get_plan(plan_id)
    if not doc or doc.get("ownerUid") != user:
        raise HTTPException(status_code=404, detail="Plan not found.")
    return _response_from_doc(doc)


@router.patch("/plans/{plan_id}/tasks/{task_id}")
async def toggle_task(
    plan_id: str, task_id: str, body: dict[str, bool], user: str = Depends(get_current_user)
) -> dict[str, Any]:
    if not SAFE_ID.match(plan_id) or not TASK_ID_RE.fullmatch(task_id):
        raise HTTPException(status_code=400, detail="Invalid plan or task id.")
    if "done" not in body or not isinstance(body["done"], bool):
        raise HTTPException(status_code=400, detail='Body must be {"done": true|false}.')
    store = get_store()
    doc = store.get_plan(plan_id)
    if not doc or doc.get("ownerUid") != user:
        raise HTTPException(status_code=404, detail="Plan not found.")
    updated = store.update_task(plan_id, task_id, body["done"])
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found.")
    return updated
