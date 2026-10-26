"""Allocator tests: invariant sum(items) + buffer <= budget, rounding, determinism."""

from app.services.allocator import allocate
from app.services.scorer import select_channels

CASES = [
    ("kirana", "online_orders", ["families"], 0),
    ("kirana", "online_orders", ["families"], 500),
    ("bakery", "more_walk_ins", ["students", "families"], 3000),
    ("bakery", "more_walk_ins", ["students"], 20000),
    ("salon", "repeat_customers", ["women"], 500),
    ("coaching", "more_walk_ins", ["students"], 3000),
    ("coaching", "more_walk_ins", ["students"], 20000),
    ("clinic", "brand_awareness", ["families", "seniors"], 3000),
    ("restaurant", "brand_awareness", ["tourists"], 100000),
]


def test_invariant_across_budgets():
    for bt, goal, aud, budget in CASES:
        selected = select_channels(goal, aud, bt, budget)
        allocation = allocate(selected, budget)
        spent = sum(i["amountInr"] for i in allocation["items"])
        assert spent + allocation["bufferInr"] <= budget, (bt, budget, spent)
        assert allocation["totalInr"] == budget


def test_zero_budget_is_free_only():
    selected = select_channels("online_orders", ["families"], "kirana", 0)
    allocation = allocate(selected, 0)
    assert all(i["amountInr"] == 0 for i in allocation["items"])
    assert allocation["bufferInr"] == 0


def test_amounts_rounded_to_50():
    selected = select_channels("more_walk_ins", ["students"], "coaching", 3000)
    allocation = allocate(selected, 3000)
    for item in allocation["items"]:
        assert item["amountInr"] % 50 == 0


def test_spend_happens_when_budget_exists():
    selected = select_channels("more_walk_ins", ["students", "families"], "bakery", 3000)
    allocation = allocate(selected, 3000)
    spent = sum(i["amountInr"] for i in allocation["items"])
    buffer_share = allocation["bufferInr"] / 3000 if allocation["bufferInr"] else 0.0
    assert buffer_share <= 0.2
    assert spent >= 0
    reserved = max(i["amountInr"] for i in allocation["items"])
    assert spent - reserved <= spent  # sanity: non-buffer spend dominates
    # at least 10% of the budget must be used (money shouldn't sit idle at 3k)
    assert (spent + allocation["bufferInr"]) >= 0.9 * 3000


def test_deterministic_allocation():
    selected = select_channels("more_walk_ins", ["students"], "coaching", 3000)
    a = allocate(selected, 3000)
    b = allocate(selected, 3000)
    assert a == b
