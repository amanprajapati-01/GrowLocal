"""Vercel Python serverless entry for the GrowLocal FastAPI backend.

Deploy recipe (see README): Vercel project #2 with Root Directory = `backend/`.
The `api/index.py` file is served under `/api/*`; `requirements.txt` is
installed automatically. The frontend then points at this URL.

Path handling: Vercel strips the `/api` prefix before invoking the function,
while some rewrite setups preserve it. The wrapper below is deterministic for
BOTH cases — if the incoming path is not already `/api`-prefixed, we re-add it,
so the real app's `/api/*` routes always match.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app as growlocal_app  # noqa: E402


class ApiPrefixScopeRewriter:
    """Raw ASGI wrapper: makes any incoming path resolve as /api/* inside the app."""

    def __init__(self, inner) -> None:
        self.inner = inner

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            path = scope.get("path", "")
            if not path.startswith("/api"):
                new_path = "/api" + path
                scope = dict(scope)
                scope["path"] = new_path
                scope["raw_path"] = new_path.encode()
        await self.inner(scope, receive, send)


# Vercel's Python runtime detects `app` (ASGI) in this module.
app = ApiPrefixScopeRewriter(growlocal_app)
