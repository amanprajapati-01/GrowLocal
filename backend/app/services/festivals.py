"""Festival/season selection for a window from today (seed data from festivals.json)."""

from datetime import date, timedelta
from typing import Any

from app.services.catalog import festival_catalog

WINDOW_DAYS = 60


def _parse_rule(rule: str) -> tuple[tuple[int, int], tuple[int, int] | None]:
    """'MM-DD' -> (start, None). 'MM-DD:MM-DD' -> (start, end)."""
    start_s, _, end_s = rule.partition(":")
    sm, sd = (int(p) for p in start_s.split("-"))
    if end_s:
        em, ed = (int(p) for p in end_s.split("-"))
        return (sm, sd), (em, ed)
    return (sm, sd), None


def _match_window(fest: dict[str, Any], today: date, days: int) -> date | None:
    """Return the festival/range start date if it begins within `days` of today."""
    if fest.get("date"):
        try:
            fixed = date.fromisoformat(str(fest["date"]))
        except ValueError:
            return None
        return fixed if today <= fixed <= today + timedelta(days=days) else None

    rule = str(fest.get("recurringRule", ""))
    if not rule:
        return None
    (sm, sd), _end = _parse_rule(rule)
    for year in (today.year, today.year + 1):
        try:
            candidate = date(year, sm, sd)
        except ValueError:
            continue
        if today <= candidate <= today + timedelta(days=days):
            return candidate
    return None


def upcoming_festivals(
    today: date,
    business_type: str | None = None,
    days: int = WINDOW_DAYS,
    language: str = "en",
) -> list[dict[str, Any]]:
    """Festivals starting within `days`, targeted at the business type, sorted by date."""
    results: list[dict[str, Any]] = []
    for fest in festival_catalog:
        regions = fest.get("regions", [])
        # MVP has no reliable region resolution; keep only all-India festivals.
        if regions != ["all"]:
            continue
        if business_type and business_type not in fest.get("relevantTypes", []):
            continue
        start = _match_window(fest, today, days)
        if not start:
            continue
        name = str(fest["nameHi"] if language == "hi" and fest.get("nameHi") else fest["name"])
        ideas = fest.get("offerIdeas", [])
        results.append(
            {
                "id": fest["id"],
                "name": name,
                "officialName": fest["name"],
                "nameHi": fest.get("nameHi", ""),
                "date": start.isoformat(),
                "suggestedOffer": ideas[0] if ideas else "",
                "verify": bool(fest.get("verify", False)),
            }
        )
    results.sort(key=lambda f: f["date"])
    return results[:4]
