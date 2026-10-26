"""Rule-based plan builder: used as Gemini fallback and as the GEMINI_MOCK source.

Deterministic for identical inputs; produces a schema-valid PlanResponse in
English or Hindi from playbooks + scorer + allocator + festivals.
"""

import hashlib
from datetime import UTC, datetime
from typing import Any

from app.models.plan import PlanResponse
from app.services.catalog import channel_catalog
from app.services.festivals import upcoming_festivals
from app.services.templates import (
    CHANNEL_TEXT,
    DISCLAIMER,
    FESTIVAL_OFFER_WRAP,
    PERSONA_BY_AUDIENCE,
    PERSONA_RESPOND,
    PERSONA_TRIGGER,
    PERSONA_WHERE,
    QUICK_WINS,
    REVIEW_TASKS,
    SPEND_TASK,
    TYPE_LABELS,
    WEEK_THEMES,
)


def _fmt_amount(amount: int) -> str:
    """Plain thousands grouping for inline text, e.g. 1,500."""
    return f"₹{amount:,}"


def build_persona(request: dict[str, Any], language: str) -> dict[str, Any]:
    audiences = request.get("targetAudience") or ["families"]
    primary = audiences[0]
    persona_info = PERSONA_BY_AUDIENCE.get(primary, PERSONA_BY_AUDIENCE["families"])
    label = TYPE_LABELS.get(request["businessType"], TYPE_LABELS["other"])[language]
    name = persona_info["name"][language]
    if language == "en":
        summary = (
            f"{name} lives or works near {request['locality']}, {request['city']} and often "
            f"chooses a {label} like {request['businessName']} within 2 km. "
            f"They trust familiar faces and visible reviews."
        )
    else:
        summary = (
            f"{name} {request['locality']}, {request['city']} के आस-पास रहते या काम करते हैं और "
            f"2 किमी के अंदर {label} (जैसे {request['businessName']}) चुन लेते हैं। "
            f"पहचान और अच्छे रिव्यूज़ उनके फ़ैसले को बदल देते हैं।"
        )
    return {
        "name": name,
        "summary": summary,
        "ageRange": persona_info["ageRange"],
        "whereTheySpendTime": [PERSONA_WHERE[a][language] for a in audiences if a in PERSONA_WHERE],
        "whatTheyRespondTo": [
            PERSONA_RESPOND[a][language] for a in audiences if a in PERSONA_RESPOND
        ],
        "buyingTriggers": [PERSONA_TRIGGER[a][language] for a in audiences if a in PERSONA_TRIGGER],
    }


def build_channel_recommendations(
    selected: list[dict[str, Any]],
    allocation: dict[str, Any],
    request: dict[str, Any],
    language: str,
) -> list[dict[str, Any]]:
    """Channels with bilingual rationale/expected result/steps and allocator amounts."""
    labels = TYPE_LABELS.get(request["businessType"], TYPE_LABELS["other"])
    amount_map = {i["channelId"]: i["amountInr"] for i in allocation["items"]}
    out: list[dict[str, Any]] = []
    for ch in selected:
        cid = ch["channelId"]
        text = CHANNEL_TEXT[cid]
        amount = amount_map.get(cid, 0)
        out.append(
            {
                "channelId": cid,
                "score": ch["score"],
                "budgetInr": amount,
                "rationale": text["rationale"][language].format(
                    amount=_fmt_amount(amount), type_label=labels[language]
                ),
                "expectedResult": text["expected"][language],
                "howToStart": text["steps"][language][:3],
            }
        )
    # free (time-based) channels first, then by score
    out.sort(key=lambda c: (c["budgetInr"] > 0, -c["score"]))
    return out


def build_start_free(selected: list[dict[str, Any]], language: str) -> list[dict[str, Any]]:
    wins = []
    for ch in selected:
        if ch["costType"] != "free":
            continue
        win = QUICK_WINS.get(ch["channelId"])
        if win:
            wins.append(
                {"title": win[language], "minutes": win["minutes"], "channelId": ch["channelId"]}
            )
    wins.sort(key=lambda w: w["minutes"])
    return wins[:3]


def _channel_name(cid: str, language: str) -> str:
    entry = channel_catalog.get(cid, {})
    names = entry.get("name", {})
    return names.get(language) or names.get("en", cid)


def _make_task(cid: str, step_idx: int, language: str, cost: int = 0) -> dict[str, Any]:
    text = CHANNEL_TEXT[cid]
    return {
        "title": text["steps"][language][step_idx % 3],
        "channelId": cid,
        "minutes": text["minutes"][step_idx % 3],
        "costInr": cost,
    }


def _spend_task(cid: str, amount: int, language: str) -> dict[str, Any] | None:
    template = SPEND_TASK.get(cid)
    if not template or amount <= 0:
        return None
    return {
        "title": template[language].format(amount=_fmt_amount(amount)),
        "channelId": cid,
        "minutes": 30,
        "costInr": amount,
    }


def _review_task(cid: str, language: str) -> dict[str, Any]:
    return {
        "title": REVIEW_TASKS[language].format(channel=_channel_name(cid, language)),
        "channelId": cid,
        "minutes": 30,
        "costInr": 0,
    }


def build_weeks(
    selected: list[dict[str, Any]],
    allocation: dict[str, Any],
    request: dict[str, Any],
    language: str,
) -> dict[str, Any]:
    """4 weeks x 3-6 tasks each.

    Week 1 = setup steps of the top 3 channels; Week 2 = next steps + money task;
    Week 3 = remaining step + tie-up/partnership push; Week 4 = reviews.
    Deterministic; at least 3 tasks per week.
    """
    amount_map = {i["channelId"]: i["amountInr"] for i in allocation["items"]}
    channels = build_channel_recommendations(selected, allocation, request, language)
    top = [c["channelId"] for c in channels]

    spend_amounts = [(cid, amount_map.get(cid, 0)) for cid in top]
    money_tasks = [t for cid, amt in spend_amounts if (t := _spend_task(cid, amt, language))]

    week1 = [_make_task(cid, 0, language) for cid in top[:3]]
    week2 = [_make_task(top[0], 1, language), _make_task(top[1], 1, language) if len(top) > 1 else None]  # type: ignore[list-item]
    week2 = [t for t in (week2) if t is not None]
    week2 += [_make_task(top[2], 0, language) if len(top) > 2 else _make_task(top[0], 2, language)]
    week2 += money_tasks[:1]
    week3 = [
        _make_task(top[0], 2, language),
        _make_task(top[1], 2, language) if len(top) > 1 else None,
    ]
    week3 = [t for t in week3 if t is not None]
    week3 += [_make_task(top[2], 1, language) if len(top) > 2 else _make_task(top[0], 0, language)]
    week3 += money_tasks[1:2]
    week4 = [_review_task(cid, language) for cid in top[:3]]
    if len(week4) < 3:
        week4.append(_make_task(top[0], 1, language))

    raw_weeks = [
        {"week": 1, "theme": WEEK_THEMES[0][language], "tasks": week1},
        {"week": 2, "theme": WEEK_THEMES[1][language], "tasks": week2},
        {"week": 3, "theme": WEEK_THEMES[2][language], "tasks": week3},
        {"week": 4, "theme": WEEK_THEMES[3][language], "tasks": week4},
    ]
    for w in raw_weeks:
        seen: set[str] = set()
        unique = [t for t in w["tasks"] if not (t["title"] in seen or seen.add(t["title"]))]
        if len(unique) < 3:
            extra = _make_task(top[(w["week"]) % len(top)], w["week"] % 3, language)
            if extra["title"] not in seen:
                unique.append(extra)
        w["tasks"] = unique[:6]
    # ensure every week has >= 3 (validators require it)
    for w in raw_weeks:
        while len(w["tasks"]) < 3:
            filler = _make_task(top[0], len(w["tasks"]), language)
            w["tasks"].append(filler)
    return {"weeks": raw_weeks}


def build_festival_suggestions(
    festivals: list[dict[str, Any]], language: str
) -> list[dict[str, Any]]:
    out = []
    for f in festivals:
        offer = FESTIVAL_OFFER_WRAP[language].format(name=f["name"], idea=f["suggestedOffer"])
        out.append({"name": f["name"], "date": f["date"], "suggestedOffer": offer})
    return out


def build_plan(
    request: dict[str, Any],
    selected: list[dict[str, Any]],
    allocation: dict[str, Any],
    language: str,
    model_used: str = "rule_fallback",
    generation_ms: int = 0,
) -> PlanResponse:
    """Assemble the full rule-based plan and validate it through PlanResponse."""
    today = datetime.now(UTC).date()
    festivals_raw = upcoming_festivals(today, request["businessType"], language=language)
    weeks = build_weeks(selected, allocation, request, language)
    seed = hashlib.sha256(
        f"{request['businessName']}{request['city']}{request['monthlyBudgetInr']}".encode()
    ).hexdigest()
    return PlanResponse(
        planId=f"pln_{seed[:12]}",
        persona=build_persona(request, language),  # type: ignore[arg-type]
        channels=build_channel_recommendations(selected, allocation, request, language),  # type: ignore[arg-type]
        budgetAllocation=allocation,  # type: ignore[arg-type]
        startFreeToday=build_start_free(selected, language),  # type: ignore[arg-type]
        actionPlan=weeks,  # type: ignore[arg-type]
        festivals=build_festival_suggestions(festivals_raw, language),  # type: ignore[arg-type]
        disclaimer=DISCLAIMER[language],
        createdAt=datetime.now(UTC).isoformat(),
        modelUsed=model_used,
        generationMs=generation_ms,
        status="ready",
    )
