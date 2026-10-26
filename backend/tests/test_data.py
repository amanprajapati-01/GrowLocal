"""Seed data integrity: channels, playbooks, festivals load and validate."""

import json
from datetime import date
from pathlib import Path

from app.services.catalog import channel_catalog, festival_catalog, playbook_catalog

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"

BTS = {"kirana", "bakery", "restaurant", "salon", "coaching", "clinic", "retail", "other"}
GOALS = {"more_walk_ins", "online_orders", "repeat_customers", "brand_awareness"}


def test_channels_load_and_validate():

    raw = json.loads((DATA_DIR / "channels.json").read_text(encoding="utf-8"))
    assert len(raw) >= 10
    required = {
        "id",
        "name",
        "costType",
        "minBudgetInr",
        "effort",
        "timeToResult",
        "bestFor",
        "goalFit",
        "audienceFit",
    }
    for ch in raw:
        assert required <= set(ch.keys()), ch["id"]
        assert ch["name"]["en"] and ch["name"]["hi"]
        assert ch["costType"] in {"free", "low", "paid"}
        assert set(ch["goalFit"].keys()) <= GOALS
        assert all(ch["bestFor"]) and set(ch["bestFor"]) <= BTS
        assert 0 <= ch["minBudgetInr"] <= 100000
    assert "google_business_profile" in channel_catalog
    assert "whatsapp_business" in channel_catalog


def test_playbooks_load():
    assert set(playbook_catalog.keys()) == BTS
    for _name, pb in playbook_catalog.items():
        assert pb["tips"] and len(pb["tips"]) >= 3
        assert pb["bestChannels"] and all(c in channel_catalog for c in pb["bestChannels"])
        assert pb["commonMistakes"] and pb["exampleOffers"]


def test_festivals_load():
    assert len(festival_catalog) >= 10
    for fest in festival_catalog:
        if fest.get("date"):
            date.fromisoformat(fest["date"])
        else:
            assert fest.get("recurringRule")
        assert fest["name"] or fest.get("nameHi")
        assert fest["regions"] and fest["relevantTypes"] and fest["offerIdeas"]
