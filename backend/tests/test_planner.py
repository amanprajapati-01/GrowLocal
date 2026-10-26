"""Rule-based planner tests: mock/fallback plans validate in EN and HI."""

from app.services.allocator import allocate
from app.services.planner import build_plan
from app.services.scorer import select_channels


def _run(req, language):
    selected = select_channels(
        req["goal"], req["targetAudience"], req["businessType"], req["monthlyBudgetInr"]
    )
    allocation = allocate(selected, req["monthlyBudgetInr"])
    return build_plan(req, selected, allocation, language)


def test_fallback_plan_en(bakery_request):
    plan = _run(bakery_request, "en")
    assert plan.modelUsed == "rule_fallback"
    assert plan.persona.summary
    assert (
        "estimate" in plan.channels[0].expectedResult.lower()
        or "-" in plan.channels[0].expectedResult
    )
    assert len(plan.actionPlan.weeks) == 4
    assert plan.startFreeToday


def test_fallback_plan_hi(salon_request):
    plan = _run(salon_request, "hi")
    assert plan.modelUsed == "rule_fallback"
    # Hindi output should be Devanagari-ish, not the English template
    has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in plan.persona.summary)
    assert has_devanagari


def test_fallback_plan_deterministic(bakery_request):
    a = _run(bakery_request, "en")
    b = _run(bakery_request, "en")
    a.createdAt = b.createdAt = ""
    a.generationMs = b.generationMs = 0
    assert a == b


def test_all_business_types_valid(bakery_request):
    for bt in ["kirana", "bakery", "restaurant", "salon", "coaching", "clinic", "retail", "other"]:
        req = {**bakery_request, "businessType": bt, "monthlyBudgetInr": 3000}
        plan = _run(req, "hi")
        assert len(plan.actionPlan.weeks) == 4
        assert len(plan.startFreeToday) >= 3
