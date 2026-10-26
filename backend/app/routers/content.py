"""Content pack endpoint: generate + store + return for a saved plan."""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.content import ContentPack, ContentPackRequest
from app.services import gemini
from app.services.auth import get_current_user
from app.services.store import get_store

router = APIRouter(prefix="/api", tags=["content"])


class ContentCreate(BaseModel):
    planId: str
    types: list[str] = ["whatsapp", "instagram", "gbp_post", "offer"]
    language: str = "en"


@router.post("/content", response_model=ContentPack)
async def create_content(req: ContentCreate, user: str = Depends(get_current_user)) -> ContentPack:
    body = ContentPackRequest(planId=req.planId, types=req.types)
    store = get_store()
    plan_doc = store.get_plan(body.planId)
    if not plan_doc or plan_doc.get("ownerUid") != user:
        raise HTTPException(status_code=404, detail="Plan not found.")
    if body.language not in ("en", "hi"):
        raise HTTPException(status_code=400, detail="language must be en or hi.")

    cached = store.get_content_pack(body.planId, body.language)
    if cached:
        return ContentPack(**json.loads(json.dumps(cached)))

    pack = await gemini.generate_content_pack(plan_doc, body.language, list(body.types))
    store.save_content_pack(body.planId, body.language, pack.model_dump())
    return pack


@router.get("/content/{plan_id}")
async def get_content(
    plan_id: str, language: str = "en", user: str = Depends(get_current_user)
) -> dict[str, Any]:
    store = get_store()
    plan_doc = store.get_plan(plan_id)
    if not plan_doc or plan_doc.get("ownerUid") != user:
        raise HTTPException(status_code=404, detail="Plan not found.")
    pack = store.get_content_pack(plan_id, language)
    if not pack:
        return {"pack": None}
    return {"pack": pack}
