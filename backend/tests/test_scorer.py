"""Scorer tests: determinism, mandatory channels, budget filtering, portfolio."""

from app.services.scorer import select_channels


def _ids(selected):
    return [s["channelId"] for s in selected]


def test_mandatory_channels_always_present(salon_request):
    for budget in (0, 500, 3000, 20000):
        selected = select_channels(
            salon_request["goal"],
            salon_request["targetAudience"],
            salon_request["businessType"],
            budget,
        )
        ids = _ids(selected)
        assert "google_business_profile" in ids, budget
        assert "whatsapp_business" in ids, budget


def test_high_budget_channels_are_filtered_out():
    selected = select_channels("more_walk_ins", ["families"], "bakery", 0)
    for s in selected:
        assert s.get("minBudgetInr", 0) == 0


def test_paid_channels_selected_when_budget_allows():
    selected = select_channels("more_walk_ins", ["families"], "bakery", 3000)
    assert any(s["costType"] != "free" for s in selected)


def test_deterministic(salon_request):
    a = select_channels(salon_request["goal"], salon_request["targetAudience"], "salon", 500)
    b = select_channels(salon_request["goal"], salon_request["targetAudience"], "salon", 500)
    assert a == b


def test_two_to_five_channels():
    for budget in (0, 250, 500, 3000, 20000, 100000):
        selected = select_channels("brand_awareness", ["tourists"], "restaurant", budget)
        assert 2 <= len(selected) <= 5, budget
