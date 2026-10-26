"""Places API (New) nearby search — P1 competitor snapshot.

Returns [] + a note when no key is configured so the demo works without it.
"""

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("growlocal.places")

PLACES_URL = "https://places.googleapis.com/v1/places:searchNearby"
FIELD_MASK = "places.displayName,places.rating,places.userRatingCount,places.formattedAddress"


async def nearby_competitors(
    lat: float, lng: float, radius_m: int = 2500, place_type: str = ""
) -> tuple[list[dict[str, Any]], str]:
    """Return (competitors, note). No key -> ([], explanation)."""
    key = get_settings().google_places_api_key
    if not key:
        return [], "Places API key not configured — competitor snapshot unavailable."

    body: dict[str, Any] = {
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": max(100.0, float(min(radius_m, 50000))),
            }
        },
    }
    if place_type:
        body["includedTypes"] = [place_type]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                PLACES_URL,
                json=body,
                headers={
                    "X-Goog-Api-Key": key,
                    "X-Goog-FieldMask": FIELD_MASK,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("places search failed: %s", exc)
        return [], "Competitor snapshot temporarily unavailable."

    competitors = [
        {
            "name": p.get("displayName", {}).get("text", ""),
            "rating": p.get("rating", 0.0),
            "reviewCount": p.get("userRatingCount", 0),
            "address": p.get("formattedAddress", ""),
        }
        for p in data.get("places", [])
    ]
    return competitors, ""
