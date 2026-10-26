"""FastAPI application entrypoint for GrowLocal."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import content, feedback, places, plan

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("growlocal")

settings = get_settings()

app = FastAPI(
    title="GrowLocal API",
    version="0.1.0",
    description="AI marketing strategy advisor for local businesses.",
)

allow_origins = [o.strip() for o in settings.allowed_origin.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # exact origins via ALLOWED_ORIGIN (comma list)
    # demo-friendly: any *.vercel.app preview/production URL works without env tweaks
    allow_origin_regex=r"https://[a-z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", include_in_schema=False)
async def api_health() -> dict[str, str]:
    """Same check as /health, under /api so it works identically on Vercel."""
    return {"status": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """All errors use a consistent envelope: {"error": {"code", "message"}}."""
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": _code_for_status(exc.status_code), "message": detail}},
    )


def _code_for_status(status: int) -> str:
    return {
        400: "invalid_input",
        401: "unauthenticated",
        403: "forbidden",
        404: "not_found",
        422: "validation_error",
        429: "rate_limited",
        502: "upstream_error",
    }.get(status, "error")


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Pydantic/FastAPI validation failures use the same error envelope."""
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(p) for p in first.get("loc", []) if p != "body")
    message = f"Invalid {field}" if field else "Invalid input"
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": message}},
    )


app.include_router(plan.router)
app.include_router(content.router)
app.include_router(feedback.router)
app.include_router(places.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
