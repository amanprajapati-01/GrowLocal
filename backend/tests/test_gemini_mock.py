"""Gemini service tests under GEMINI_MOCK=true (no network)."""

import pytest
from app.services import gemini
from app.services.allocator import allocate
from app.services.planner import build_plan
from app.services.scorer import select_channels


@pytest.mark.asyncio
async def test_mock_plan_en(bakery_request):
    selected = select_channels(
        bakery_request["goal"], bakery_request["targetAudience"], "bakery", 3000
    )
    allocation = allocate(selected, 3000)
    plan = await gemini.generate_plan(bakery_request, selected, allocation, "en")
    assert plan.modelUsed == "gemini-mock"
    assert len(plan.actionPlan.weeks) == 4
    assert sum(c.budgetInr for c in plan.channels) <= 3000


@pytest.mark.asyncio
async def test_mock_plan_hi(salon_request):
    selected = select_channels(salon_request["goal"], salon_request["targetAudience"], "salon", 500)
    allocation = allocate(selected, 500)
    plan = await gemini.generate_plan(salon_request, selected, allocation, "hi")
    assert plan.modelUsed == "gemini-mock"
    has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in plan.persona.summary)
    assert has_devanagari


@pytest.mark.asyncio
async def test_mock_content_pack(bakery_request):

    selected = select_channels(
        bakery_request["goal"], bakery_request["targetAudience"], "bakery", 3000
    )
    allocation = allocate(selected, 3000)
    plan = build_plan(bakery_request, selected, allocation, "en")
    doc = {
        "planId": plan.planId,
        "input": bakery_request,
        "festivals": [f.model_dump() for f in plan.festivals],
        "persona": plan.persona.model_dump(),
        "channels": [c.model_dump() for c in plan.channels],
    }
    pack = await gemini.generate_content_pack(
        doc, "en", ["whatsapp", "instagram", "gbp_post", "offer"]
    )
    assert pack.whatsapp and len(pack.whatsapp[0].text) <= 400
    assert pack.instagram[0].hashtags
    assert pack.gbpPost and len(pack.gbpPost.body) <= 300
    assert pack.offers
