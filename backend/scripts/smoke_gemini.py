"""Live Gemini smoke test. Run only when GEMINI_API_KEY is set.

Usage (backend venv):
    python scripts/smoke_gemini.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.services import gemini
from app.services.allocator import allocate
from app.services.scorer import select_channels

REQUEST = {
    "businessType": "bakery",
    "businessName": "Sharma Bakery",
    "city": "Kanpur",
    "locality": "Swaroop Nagar",
    "monthlyBudgetInr": 3000,
    "goal": "more_walk_ins",
    "targetAudience": ["students", "families"],
    "targetAudienceText": "",
    "language": "hi",
}


async def main() -> int:
    settings = get_settings()
    if settings.gemini_mock or not settings.gemini_api_key:
        print(
            "GEMINI_MOCK is on or GEMINI_API_KEY is empty — set GEMINI_MOCK=false and a key to smoke-test live."
        )
        return 1
    selected = select_channels(REQUEST["goal"], REQUEST["targetAudience"], "bakery", 3000)
    allocation = allocate(selected, 3000)
    plan = await gemini.generate_plan(REQUEST, selected, allocation, "hi")
    print("modelUsed:", plan.modelUsed)
    print("persona:", plan.persona.name)
    print("channels:", [(c.channelId, c.budgetInr) for c in plan.channels])
    print("weeks:", [(w.week, len(w.tasks)) for w in plan.actionPlan.weeks])
    print("festivals:", [(f.name, f.date) for f in plan.festivals])
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
