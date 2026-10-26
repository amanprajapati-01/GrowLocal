"""Shared fixtures: env switches + standard request payloads."""

import pytest
from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def _dev_switches(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("GEMINI_MOCK", "true")
    monkeypatch.setenv("STORE_BACKEND", "memory")
    get_settings.cache_clear()
    app.dependency_overrides.clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def bakery_request() -> dict:
    return {
        "businessType": "bakery",
        "businessName": "Sharma Bakery",
        "city": "Kanpur",
        "locality": "Swaroop Nagar",
        "monthlyBudgetInr": 3000,
        "goal": "more_walk_ins",
        "targetAudience": ["students", "families"],
        "targetAudienceText": "",
        "language": "en",
    }


@pytest.fixture
def salon_request() -> dict:
    return {
        "businessType": "salon",
        "businessName": "Glamour Ladies Salon",
        "city": "Kanpur",
        "locality": "Civil Lines",
        "monthlyBudgetInr": 500,
        "goal": "repeat_customers",
        "targetAudience": ["women"],
        "targetAudienceText": "brides and office-goers",
        "language": "hi",
    }
