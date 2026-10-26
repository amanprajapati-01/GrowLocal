"""Auth dependency: Firebase ID token verification, with a dev-mode switch."""

import logging
from typing import Any

from fastapi import Header, HTTPException

from app.config import get_settings

logger = logging.getLogger("growlocal.auth")

_firebase_app: Any = None
_firebase_init_error: str | None = None


def _init_firebase() -> Any:
    """Initialise firebase-admin once (Application Default Credentials)."""
    global _firebase_app, _firebase_init_error
    if _firebase_app is None and _firebase_init_error is None:
        try:
            import firebase_admin
            from firebase_admin import auth as fb_auth  # noqa: F401 (ensures import works)

            options = (
                {"projectId": get_settings().firebase_project_id}
                if get_settings().firebase_project_id
                else None
            )
            _firebase_app = firebase_admin.initialize_app(options=options)
        except Exception as exc:  # noqa: BLE001 — deployment in dev may lack creds
            _firebase_init_error = str(exc)
            logger.error("firebase-admin init failed: %s", exc)
    if _firebase_app is None:
        raise HTTPException(
            status_code=502,
            detail="Auth backend misconfigured (FIREBASE_PROJECT_ID / credentials missing).",
        )
    return _firebase_app


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    """Verify the Bearer Firebase ID token; dev mode returns a fixed user."""
    settings = get_settings()
    if settings.auth_disabled:
        return "dev-user"

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        _init_firebase()
        from firebase_admin import auth as fb_auth

        decoded: dict[str, Any] = fb_auth.verify_id_token(token, check_revoked=True)
        uid = decoded.get("uid")
        if not uid:
            raise ValueError("token without uid")
        return str(uid)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 — invalid/expired tokens
        logger.warning("token verification failed: %s", exc)
        raise HTTPException(
            status_code=401, detail="Session expired. Please sign in again."
        ) from exc
