"""Places endpoint (P1): nearby competitor snapshot. Empty + note without a key."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.services.auth import get_current_user
from app.services.places import nearby_competitors

router = APIRouter(prefix="/api", tags=["places"])


def _validate(lat: float | None, lng: float | None) -> None:
    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="lat and lng are required.")
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(status_code=400, detail="lat/lng out of range.")


@router.get("/places")
async def places(
    lat: float | None = None,
    lng: float | None = None,
    radius: int = 2500,
    type: str = "",
    user: str = Depends(get_current_user),  # noqa: ARG001 — protected route
) -> dict[str, Any]:
    _validate(lat, lng)
    competitors, note = await nearby_competitors(
        lat=float(lat or 0.0), lng=float(lng or 0.0), radius_m=radius, place_type=type
    )
    return {"competitors": competitors, "note": note, "radiusMeters": min(radius, 50000)}
