"""Plan generation orchestration: validate -> score -> allocate -> AI -> enforce -> save."""

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException

from app.config import get_settings
from app.models.plan import BudgetAllocation, BudgetItem, PlanRequest, PlanResponse
from app.services import gemini, planner
from app.services.allocator import allocate
from app.services.scorer import audiences_as_strings, select_channels
from app.services.store import Store, get_store

logger = logging.getLogger("growlocal.plan")


def _input_hash(req: PlanRequest) -> str:
    canonical = json.dumps(
        {
            "businessType": req.businessType.value,
            "businessName": req.businessName.lower(),
            "city": req.city.lower(),
            "locality": req.locality.lower(),
            "monthlyBudgetInr": req.monthlyBudgetInr,
            "goal": req.goal.value,
            "targetAudience": [a.value for a in req.targetAudience],
            "targetAudienceText": req.targetAudienceText.lower(),
            "language": req.language.value,
        },
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def _request_to_dict(req: PlanRequest) -> dict[str, Any]:
    return {
        "businessType": req.businessType.value,
        "businessName": req.businessName,
        "city": req.city,
        "locality": req.locality,
        "monthlyBudgetInr": req.monthlyBudgetInr,
        "goal": req.goal.value,
        "targetAudience": audiences_as_strings(req.targetAudience),
        "targetAudienceText": req.targetAudienceText,
        "language": req.language.value,
    }


def _summarize_feedback(store: Store, owner_uid: str) -> str:
    """Short 'what worked last time' summary fed into the next plan's prompt (P1)."""
    items = store.list_feedback(owner_uid)
    if not items:
        return ""
    worked = sorted({f.get("channelId", "?") for f in items if f.get("outcome") == "worked"})
    flopped = sorted({f.get("channelId", "?") for f in items if f.get("outcome") == "didnt"})
    parts = []
    if worked:
        parts.append(f"Previously WORKED for this owner: {', '.join(worked)}. Keep prioritised.")
    if flopped:
        parts.append(f"Previously DID NOT WORK: {', '.join(flopped)}. Deprioritise.")
    return " ".join(parts)


def _enforce_budgets(
    plan: PlanResponse, selected: list[dict[str, Any]], allocation: dict[str, Any]
) -> PlanResponse:
    """Budget amounts are decided in code — overwrite anything the model wrote."""
    for ch in plan.channels:
        if ch.channelId not in {s["channelId"] for s in selected}:
            raise ValueError(f"model returned channel '{ch.channelId}' that was not selected")
    plan.budgetAllocation = BudgetAllocation(
        totalInr=allocation["totalInr"],
        bufferInr=allocation["bufferInr"],
        items=[BudgetItem(**item) for item in allocation["items"]],
    )
    for ch in plan.channels:
        ch.budgetInr = next(
            (i["amountInr"] for i in allocation["items"] if i["channelId"] == ch.channelId), 0
        )
    return plan


async def create_plan(user_uid: str, req: PlanRequest) -> PlanResponse:
    settings = get_settings()
    store = get_store()
    today = datetime.now(UTC).date().isoformat()

    if store.plans_today(user_uid, today) >= settings.plans_per_user_per_day:
        raise HTTPException(
            status_code=429,
            detail=f"Plan limit ({settings.plans_per_user_per_day}/day) reached. Try again tomorrow.",
        )

    request_hash = _input_hash(req)
    cached = store.get_cached_plan(user_uid, request_hash, settings.plan_cache_ttl_hours)
    if cached:
        return PlanResponse(**cached)

    request = _request_to_dict(req)
    selected = select_channels(
        req.goal,
        request["targetAudience"],
        req.businessType,
        req.monthlyBudgetInr,
    )
    allocation = allocate(selected, req.monthlyBudgetInr)

    feedback_summary = _summarize_feedback(store, user_uid)
    plan = await gemini.generate_plan(
        request, selected, allocation, req.language.value, feedback_summary
    )
    try:
        plan = _enforce_budgets(plan, selected, allocation)
    except ValueError as exc:
        logger.warning("model channel mix rejected (%s); rebuilding from rules", exc)
        rule_plan = planner.build_plan(request, selected, allocation, req.language.value)
        plan = _enforce_budgets(rule_plan, selected, allocation)
    total = sum(i.amountInr for i in plan.budgetAllocation.items) + plan.budgetAllocation.bufferInr
    if total > req.monthlyBudgetInr:
        logger.warning("budget overflow after enforcement; rebuilding from rules")
        rule_plan = planner.build_plan(request, selected, allocation, req.language.value)
        plan = _enforce_budgets(rule_plan, selected, allocation)

    plan.planId = f"pln_{uuid.uuid4().hex[:12]}"
    plan.createdAt = datetime.now(UTC).isoformat()
    plan.status = "ready"

    doc = _to_doc(user_uid, plan, request, request_hash, allocation)
    business_id = store.save_business(
        user_uid,
        {
            "name": req.businessName,
            "type": req.businessType.value,
            "city": req.city,
            "locality": req.locality,
        },
    )
    doc["businessId"] = business_id
    store.save_plan(doc)
    store.put_cached_plan(user_uid, request_hash, doc)
    store.increment_plan_count(user_uid, today)
    return plan


async def _rebuild_with_allocator(
    request: dict[str, Any],
    selected: list[dict[str, Any]],
    allocation: dict[str, Any],
    language: str,
    plan: PlanResponse,
) -> PlanResponse:
    """Safety net: if totals still exceed budget, rebuild the whole plan from rules."""
    return planner.build_plan(request, selected, allocation, language, "rule_fallback")


def _to_doc(
    owner_uid: str,
    plan: PlanResponse,
    request: dict[str, Any],
    request_hash: str,
    allocation: dict[str, Any],
) -> dict[str, Any]:
    data = plan.model_dump()
    return {
        "planId": data["planId"],
        "ownerUid": owner_uid,
        "businessId": "",
        "input": request,
        "inputHash": request_hash,
        "persona": data["persona"],
        "channels": data["channels"],
        "budgetAllocation": allocation,
        "startFreeToday": data["startFreeToday"],
        "actionPlan": data["actionPlan"],
        "festivals": data["festivals"],
        "competitors": [],
        "status": data["status"],
        "modelUsed": data["modelUsed"],
        "generationMs": data["generationMs"],
        "disclaimer": data["disclaimer"],
        "createdAt": data["createdAt"],
    }
