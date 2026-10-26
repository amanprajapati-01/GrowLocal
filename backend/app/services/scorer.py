"""Rule-based channel scorer (TechSpecs.md SS5).

Rules decide, AI explains: this module deterministically picks and ranks
channels. Weights come from Settings so they are tunable for the demo.
"""

from typing import Any

from app.config import get_settings
from app.models.common import Audience, BusinessType, Goal
from app.services.catalog import channel_catalog

EFFORT_FIT: dict[str, float] = {"low": 1.0, "medium": 0.6, "high": 0.3}

MANDATORY_CHANNELS = ("google_business_profile", "whatsapp_business")
TOP_N = 5  # total selection size (4 when no budget can be spent)
PAID_FILL_MIN_BUDGET = 300  # below this, a free-only plan is returned


def _audience_fit(entry: dict[str, Any], audiences: list[str]) -> float:
    fits = [entry.get("audienceFit", {}).get(a, 0.0) for a in audiences]
    return sum(fits) / len(fits) if fits else 0.0


def _budget_fit(min_budget: int, monthly_budget: int) -> float:
    """1.0 when the budget comfortably covers the channel's minimum spend."""
    if min_budget == 0:
        return 1.0
    return min(1.0, monthly_budget / (min_budget * 2.0))


def _paid_slots(monthly_budget: int) -> int:
    """0 paid slots below ₹300; 1 up to ₹2k; 2 above (so money has a receiver)."""
    if monthly_budget < PAID_FILL_MIN_BUDGET:
        return 0
    if monthly_budget < 2000:
        return 1
    return 2


def score_channel(
    entry: dict[str, Any],
    goal: Goal,
    audiences: list[str],
    business_type: BusinessType,
    monthly_budget: int,
) -> float:
    """Weighted fit score for one channel, 0-100."""
    s = get_settings()
    goal_fit = float(entry.get("goalFit", {}).get(goal.value, 0.0))
    audience_score = _audience_fit(entry, audiences)
    type_fit = 1.0 if business_type.value in entry.get("bestFor", []) else 0.3
    budget_fit = _budget_fit(int(entry.get("minBudgetInr", 0)), monthly_budget)
    effort_fit = EFFORT_FIT.get(entry.get("effort", "medium"), 0.6)

    weighted = (
        s.w_goal_fit * goal_fit
        + s.w_audience_fit * audience_score
        + s.w_business_type_fit * type_fit
        + s.w_budget_fit * budget_fit
        + s.w_effort_fit * effort_fit
    )
    if entry.get("costType") == "free":
        weighted += s.free_bonus
    return min(100.0, round(weighted * 100))


def select_channels(
    goal: Goal | str,
    audiences: list[str],
    business_type: BusinessType | str,
    monthly_budget: int,
) -> list[dict[str, Any]]:
    """Filter, score, rank and return the top 4-5 channels as a portfolio.

    Google Business Profile and WhatsApp Business are always included when
    affordable. Free (time-based) channels build the base; when there is
    budget to spend (>= Rs 300) the best affordable non-free channels fill
    the remaining slots so the allocator always has money to place.
    Deterministic: same input, same output.
    """
    goal = Goal(goal)
    business_type = BusinessType(business_type)
    affordable = [
        e for e in channel_catalog.values() if int(e.get("minBudgetInr", 0)) <= monthly_budget
    ]
    scored = [
        {
            "channelId": e["id"],
            "score": score_channel(e, goal, audiences, business_type, monthly_budget),
            "entry": e,
        }
        for e in affordable
    ]
    scored.sort(key=lambda x: (-x["score"], x["channelId"]))

    selected_ids: set[str] = set()
    selection: list[dict[str, Any]] = []

    mandatory = [s for s in scored if s["channelId"] in MANDATORY_CHANNELS]
    for s in sorted(mandatory, key=lambda x: (-x["score"], x["channelId"])):
        selection.append(s)
        selected_ids.add(s["channelId"])

    paid_n = _paid_slots(monthly_budget)
    free_n = TOP_N - len(selection) - paid_n
    free_rest = [
        s
        for s in scored
        if s["entry"].get("costType") == "free" and s["channelId"] not in selected_ids
    ]
    for s in free_rest[:free_n]:
        selection.append(s)
        selected_ids.add(s["channelId"])

    if paid_n:
        paid_rest = [
            s
            for s in scored
            if s["entry"].get("costType") != "free" and s["channelId"] not in selected_ids
        ]
        for s in paid_rest[:paid_n]:
            selection.append(s)

    return [
        {
            "channelId": s["channelId"],
            "score": s["score"],
            "costType": s["entry"]["costType"],
            "minBudgetInr": s["entry"].get("minBudgetInr", 0),
        }
        for s in selection
    ]


def audiences_as_strings(audiences: list[Audience]) -> list[str]:
    return [a.value for a in audiences]
