"""Model validation tests: good payloads pass, bad ones fail with useful errors."""

import pytest
from app.models.content import ContentPack
from app.models.feedback import FeedbackRequest
from app.models.plan import PlanRequest, PlanResponse
from pydantic import ValidationError


def test_valid_plan_request(bakery_request):
    req = PlanRequest(**bakery_request)
    assert req.monthlyBudgetInr == 3000
    assert req.language.value == "en"


@pytest.mark.parametrize(
    "field,value",
    [
        ("monthlyBudgetInr", -1),
        ("monthlyBudgetInr", 100001),
        ("businessName", "S"),
        ("city", "K<i>anpur</i>"),
        ("locality", ""),
    ],
)
def test_invalid_plan_request(bakery_request, field, value):
    bakery_request[field] = value
    with pytest.raises(ValidationError):
        PlanRequest(**bakery_request)


def _plan_like(**overrides):
    channels = [
        {
            "channelId": "google_business_profile",
            "score": 90,
            "budgetInr": 0,
            "rationale": "Complete listing so locals find you on Google Maps quickly.",
            "expectedResult": "Estimate: 10-30 calls within 1-4 weeks.",
            "howToStart": ["Claim listing", "Add hours", "Add photos"],
        },
        {
            "channelId": "whatsapp_business",
            "score": 85,
            "budgetInr": 800,
            "rationale": "Broadcast to regulars who already bought from you.",
            "expectedResult": "Estimate: 2-10 repeat orders in 1-2 weeks.",
            "howToStart": ["Install app", "Make list", "Send note"],
        },
        {
            "channelId": "flyers_local",
            "score": 70,
            "budgetInr": 1500,
            "rationale": "Print flyers for the 1-2 km nobody sees online.",
            "expectedResult": "Estimate: 5-20 responses per 200 flyers.",
            "howToStart": ["One offer", "Print 200", "Distribute"],
        },
    ]
    weeks = [
        {
            "week": w,
            "theme": f"Week {w} theme",
            "tasks": [
                {
                    "title": f"Task {w}.{i}",
                    "channelId": "google_business_profile",
                    "minutes": 20,
                    "costInr": 0,
                }
                for i in range(3)
            ],
        }
        for w in range(1, 5)
    ]
    base = {
        "planId": "pln_abc123",
        "persona": {
            "name": "Weekend Family Planner Sunita",
            "summary": "She lives near the shop and picks family treats on weekends. She trusts reviews.",
            "ageRange": "28-45",
            "whereTheySpendTime": ["WhatsApp groups"],
            "whatTheyRespondTo": ["family bundles"],
            "buyingTriggers": ["festivals ahead"],
        },
        "channels": channels,
        "budgetAllocation": {
            "totalInr": 3000,
            "bufferInr": 300,
            "items": [
                {"channelId": "whatsapp_business", "amountInr": 800},
                {"channelId": "flyers_local", "amountInr": 1500},
            ],
        },
        "startFreeToday": [
            {
                "title": "Complete your Google listing",
                "minutes": 20,
                "channelId": "google_business_profile",
            }
        ],
        "actionPlan": {"weeks": weeks},
        "festivals": [
            {
                "name": "Diwali",
                "date": "2026-11-08",
                "suggestedOffer": "Gift hamper with pre-order discount",
            }
        ],
        "disclaimer": "Estimates are not guarantees; check platform policies.",
    }
    base.update(overrides)
    return PlanResponse(**base)


def test_valid_plan_response(bakery_request):
    plan = _plan_like()
    assert plan.budgetAllocation.bufferInr == 300


def test_plan_budget_overflow_rejected():
    with pytest.raises(ValidationError):
        _plan_like(
            budgetAllocation={
                "totalInr": 1000,
                "bufferInr": 0,
                "items": [
                    {"channelId": "flyers_local", "amountInr": 1500},
                ],
            }
        )


def test_unknown_channel_rejected():
    bad = _plan_like().model_dump()
    bad["channels"][0]["channelId"] = "not_a_channel"
    bad["channels"][0]["expectedResult"] = "Estimate: 10-30 calls within 1-4 weeks."
    with pytest.raises(ValidationError):
        PlanResponse(**bad)


def test_expected_result_must_be_range():
    bad = _plan_like().model_dump()
    bad["channels"][0]["expectedResult"] = "Guaranteed 50 orders immediately."
    with pytest.raises(ValidationError):
        PlanResponse(**bad)


def test_weeks_must_be_four():
    bad = _plan_like().model_dump()
    bad["actionPlan"]["weeks"] = bad["actionPlan"]["weeks"][:3]
    with pytest.raises(ValidationError):
        PlanResponse(**bad)


def test_each_week_needs_3_to_6_tasks():
    bad = _plan_like().model_dump()
    bad["actionPlan"]["weeks"][0]["tasks"] = bad["actionPlan"]["weeks"][0]["tasks"][:2]
    with pytest.raises(ValidationError):
        PlanResponse(**bad)


def test_html_is_stripped():
    bad = _plan_like().model_dump()
    bad["disclaimer"] = "<script>alert(1)</script>Estimates only, no promises."
    plan = PlanResponse(**bad)
    assert "<script>" not in plan.disclaimer
    assert "</script>" not in plan.disclaimer


def test_feedback_validation():
    ok = FeedbackRequest(
        planId="pln_abc", channelId="instagram_reels", outcome="worked", note="nice"
    )
    assert ok.outcome == "worked"
    with pytest.raises(ValidationError):
        FeedbackRequest(planId="pln_abc", channelId="instagram_reels", outcome="meh")


def test_content_pack_validation():
    pack = ContentPack(
        planId="pln_abc",
        language="en",
        whatsapp=[{"label": "Regulars", "text": "Hi! Family combo this week."}],
        instagram=[
            {
                "caption": "Fresh bread every evening!",
                "hashtags": ["#Fresh", "#KanpurLocal", "#Bakery"],
                "reelIdea": "Oven shot",
            }
        ],
        gbpPost={
            "title": "New offer",
            "body": "Combo this week at Sharma Bakery.",
            "ctaType": "CALL",
        },
        offers=[{"name": "Combo", "description": "Bread + cake combo", "validityDays": 7}],
    )
    assert pack.whatsapp[0].text.startswith("Hi!")
    assert pack.instagram[0].hashtags[0].startswith("#")
