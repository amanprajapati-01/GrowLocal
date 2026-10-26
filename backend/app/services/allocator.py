"""Budget allocator: free channels get tasks, money goes to paid/low channels.

Invariant (tested): sum(items) + buffer <= monthlyBudgetInr, budget = 0 gives a
free-only plan.
"""

from typing import Any

GRID = 50  # all amounts are multiples of ₹50
RESERVE_RATIO = 0.10  # "test and adjust" buffer
SINGLE_CHANNEL_CAP = 0.60  # no single channel takes more than 60% of distributable


def _round_down_50(amount: float) -> int:
    return int(amount // GRID) * GRID


def allocate(
    selected: list[dict[str, Any]],
    monthly_budget: int,
) -> dict[str, Any]:
    """Distribute the remainder among non-free channels proportionally to score.

    Rules: amounts on a ₹50 grid, 10% reserve buffer, no single channel takes
    more than 60% of the distributable amount (excess is redistributed by
    score). selected: scorer output. Returns deterministic allocation dict.
    """
    free = [c for c in selected if c["costType"] == "free"]
    paid_pool = [c for c in selected if c["costType"] != "free"]
    buffer = 0
    items: dict[str, int] = {c["channelId"]: 0 for c in free}

    if monthly_budget > 0 and paid_pool:
        buffer = _round_down_50(RESERVE_RATIO * monthly_budget)
        distributable = monthly_budget - buffer
        weight_sum = sum(c["score"] for c in paid_pool)

        if weight_sum > 0 and distributable >= GRID:
            raw_shares = {
                c["channelId"]: distributable * c["score"] / weight_sum for c in paid_pool
            }
            for cid, share in raw_shares.items():
                items[cid] = _round_down_50(min(share, SINGLE_CHANNEL_CAP * distributable))
            items.update(_redistribute_excess(items, distributable, paid_pool))
            leftover = distributable - sum(items.values())
            for c in sorted(paid_pool, key=lambda x: (-x["score"], x["channelId"])):
                while leftover >= GRID and c["channelId"] in items:
                    items[c["channelId"]] += GRID
                    leftover -= GRID

    result_items = [{"channelId": cid, "amountInr": amt} for cid, amt in items.items()]
    allocated = sum(i["amountInr"] for i in result_items) + buffer
    result_items = _safety_clamp(result_items, monthly_budget, allocated)
    return {
        "totalInr": monthly_budget,
        "bufferInr": buffer,
        "items": result_items,
    }


def _redistribute_excess(
    items: dict[str, int], distributable: int, paid_pool: list[dict[str, Any]]
) -> dict[str, int]:
    """When the 60% cap bites, move freed money to the next channels by score."""
    updated = dict(items)
    freed = distributable - sum(updated.values())
    for c in sorted(paid_pool, key=lambda x: (-x["score"], x["channelId"])):
        cid = c["channelId"]
        share_left = SINGLE_CHANNEL_CAP * distributable - updated.get(cid, 0)
        while freed >= GRID and share_left >= GRID:
            updated[cid] = updated.get(cid, 0) + GRID
            freed -= GRID
            share_left -= GRID
        if freed < GRID:
            break
    return updated


def _safety_clamp(
    result_items: list[dict[str, Any]], monthly_budget: int, allocated: int
) -> list[dict[str, Any]]:
    """Absolute invariant guard (should never trigger)."""
    while allocated > monthly_budget and result_items:
        result_items.sort(key=lambda i: i["amountInr"])
        reduce_by = min(GRID, result_items[0]["amountInr"])
        result_items[0]["amountInr"] -= reduce_by
        allocated -= reduce_by
        if result_items[0]["amountInr"] == 0 and len(result_items) > 1:
            result_items.pop(0)
    return result_items


def attach_amounts(channels: list[dict[str, Any]], allocation: dict[str, Any]) -> None:
    """Copy allocated amounts into channel recommendation dicts in place."""
    amounts = {i["channelId"]: i["amountInr"] for i in allocation["items"]}
    for ch in channels:
        ch["budgetInr"] = amounts.get(ch["channelId"], 0)
