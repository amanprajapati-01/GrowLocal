"""Catalog loading: channels, playbooks, festivals (JSON seed data)."""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

channel_catalog: dict[str, dict[str, Any]] = {}
playbook_catalog: dict[str, dict[str, Any]] = {}
festival_catalog: list[dict[str, Any]] = []


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_catalogs() -> None:
    """(Re)load all seed data from JSON files into in-memory dicts."""
    channel_catalog.clear()
    for ch in _load_json(DATA_DIR / "channels.json"):
        channel_catalog[ch["id"]] = ch

    playbook_catalog.clear()
    for pb_file in (DATA_DIR / "playbooks").glob("*.json"):
        pb = _load_json(pb_file)
        playbook_catalog[pb["businessType"]] = pb

    festival_catalog.clear()
    for fest in _load_json(DATA_DIR / "festivals.json")["festivals"]:
        festival_catalog.append(fest)


load_catalogs()


def channel_ids() -> list[str]:
    return list(channel_catalog.keys())


def is_valid_channel(channel_id: str) -> bool:
    return channel_id in channel_catalog
