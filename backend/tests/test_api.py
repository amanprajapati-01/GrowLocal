"""API tests: full happy path against the FastAPI app with dev switches on."""

import json

import pytest
from app.main import app
from app.services.store import MemoryStore
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    MemoryStore._instance = None  # fresh store per test
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_channels_metadata(client):
    response = client.get("/api/channels")
    assert response.status_code == 200
    channels = response.json()["channels"]
    ids = {c["id"] for c in channels}
    assert "google_business_profile" in ids
    assert all(set(c["name"].keys()) >= {"en", "hi"} for c in channels)


def test_full_flow_en_then_task_toggle_then_content_then_feedback(client, bakery_request):
    plan = client.post("/api/plan", json=bakery_request).json()
    plan_id = plan["planId"]
    assert plan_id.startswith("pln_")
    assert (
        sum(i["amountInr"] for i in plan["budgetAllocation"]["items"])
        + plan["budgetAllocation"]["bufferInr"]
        <= 3000
    )
    assert "<" not in json.dumps(plan)

    task_id = f"t_w{plan['actionPlan']['weeks'][0]['week']}_n0"
    toggled = client.patch(f"/api/plans/{plan_id}/tasks/{task_id}", json={"done": True})
    assert toggled.status_code == 200

    content = client.post("/api/content", json={"planId": plan_id, "language": "en"})
    assert content.status_code == 200
    assert content.json()["whatsapp"]

    feedback = client.post(
        "/api/feedback",
        json={
            "planId": plan_id,
            "channelId": plan["channels"][0]["channelId"],
            "outcome": "worked",
            "note": "",
        },
    )
    assert feedback.status_code == 200

    plans = client.get("/api/plans").json()["plans"]
    assert len(plans) == 1
    assert plans[0]["planId"] == plan_id


def test_create_plan_hi(client, salon_request):
    salon_request["language"] = "hi"
    plan = client.post("/api/plan", json=salon_request).json()
    summary = json.dumps(plan["persona"]["summary"], ensure_ascii=False)
    assert any("\u0900" <= ch <= "\u097f" for ch in summary)


def test_plan_validation_error(client, bakery_request):
    bakery_request["monthlyBudgetInr"] = 100001
    response = client.post("/api/plan", json=bakery_request)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_plan_cache_returns_same(client, bakery_request):
    first = client.post("/api/plan", json=bakery_request).json()
    second = client.post("/api/plan", json=bakery_request).json()
    assert first["planId"] == second["planId"]


def test_unknown_plan_404(client):
    response = client.get("/api/plans/pln_missing0000")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_feedback_summary_surfaces_correctly(client, bakery_request):
    """P1: what worked / didn't must reach the next plan's prompt summary."""
    from app.services.plan_service import _summarize_feedback
    from app.services.store import get_store

    plan = client.post("/api/plan", json=bakery_request).json()
    worked_channel = plan["channels"][0]["channelId"]

    # reject the old UI values — contract per docs/Schema.md is worked|partial|didnt
    assert (
        client.post(
            "/api/feedback",
            json={"planId": plan["planId"], "channelId": worked_channel, "outcome": "neutral"},
        ).status_code
        == 422
    )

    for outcome, channel in (("worked", worked_channel), ("didnt", "instagram_organic")):
        response = client.post(
            "/api/feedback",
            json={"planId": plan["planId"], "channelId": channel, "outcome": outcome, "note": ""},
        )
        assert response.status_code == 200

    summary = _summarize_feedback(get_store(), "dev-user")
    assert "worked" in summary.lower() and worked_channel in summary
    assert "DID NOT WORK" in summary and "instagram_organic" in summary



def test_bad_task_patch_400(client, bakery_request):
    plan = client.post("/api/plan", json=bakery_request).json()
    response = client.patch(f'/api/plans/{plan["planId"]}/tasks/bogus', json={"done": True})
    assert response.status_code == 400
