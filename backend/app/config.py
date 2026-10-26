"""Application settings loaded from environment / .env (pydantic-settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from env vars / .env at the backend root."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- AI ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # --- External data (P1) ---
    google_places_api_key: str = ""

    # --- Firebase ---
    firebase_project_id: str = ""

    # --- App ---
    allowed_origin: str = "http://localhost:3000"

    # --- Dev-mode switches (tooling only; production must run real behavior) ---
    auth_disabled: bool = True  # skip Firebase token check, use fixed dev-user
    gemini_mock: bool = True  # return canned valid response instead of calling Gemini
    store_backend: str = "memory"  # memory | firestore

    # --- Limits & tuning ---
    plans_per_user_per_day: int = 10
    plan_cache_ttl_hours: int = 24
    gemini_timeout_s: float = 30.0
    gemini_plan_temperature: float = 0.6
    gemini_content_temperature: float = 0.8

    # Scorer weights (TechSpecs.md SS5) — tunable for the demo
    w_goal_fit: float = 0.35
    w_audience_fit: float = 0.25
    w_business_type_fit: float = 0.20
    w_budget_fit: float = 0.10
    w_effort_fit: float = 0.10
    free_bonus: float = 0.05


@lru_cache
def get_settings() -> Settings:
    return Settings()
