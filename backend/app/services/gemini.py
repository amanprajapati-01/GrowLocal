"""Gemini integration (google-genai SDK): JSON mode, validate + retry, rule-based fallback.

Chat/completions never leave the backend; the frontend never calls Gemini.
"""

import asyncio
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.models.content import ContentPack
from app.models.plan import PlanResponse
from app.services import content_fallback, planner
from app.services.catalog import playbook_catalog
from app.services.festivals import upcoming_festivals

logger = logging.getLogger("growlocal.gemini")

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _apply_template(template_name: str, tokens: dict[str, str]) -> str:
    text = (PROMPTS_DIR / template_name).read_text(encoding="utf-8")
    for key, value in tokens.items():
        text = text.replace(f"[[{key}]]", value)
    return text


def _extract_json(raw: str) -> str:
    fenced = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    return fenced.strip()


def build_plan_tokens(
    request: dict[str, Any],
    selected: list[dict[str, Any]],
    allocation: dict[str, Any],
    language: str,
    feedback_summary: str = "",
) -> dict[str, str]:
    """Fill plan_prompt.md tokens from the rule engine output."""
    today = datetime.now(UTC).date()
    festivals = upcoming_festivals(today, request["businessType"], language=language)
    playbook = playbook_catalog.get(request["businessType"], playbook_catalog["other"])
    channels_scored = [
        {"channelId": c["channelId"], "score": c["score"], "costType": c["costType"]}
        for c in selected
    ]
    return {
        "BUSINESS_NAME": request["businessName"],
        "BUSINESS_TYPE": request["businessType"],
        "LOCALITY": request["locality"],
        "CITY": request["city"],
        "BUDGET": str(request["monthlyBudgetInr"]),
        "GOAL": request["goal"],
        "AUDIENCES": ", ".join(request.get("targetAudience", []) or ["families"]),
        "AUDIENCE_TEXT": request.get("targetAudienceText", "") or "-",
        "LANGUAGE": "English" if language == "en" else "Hindi (natural, Hinglish-friendly)",
        "CHANNELS_SCORED": str(channels_scored),
        "BUDGET_ALLOCATION": str(
            {
                "totalInr": allocation["totalInr"],
                "bufferInr": allocation["bufferInr"],
                "items": allocation["items"],
            }
        ),
        "PLAYBOOK": str(playbook),
        "FESTIVALS": str(
            [
                {"name": f["name"], "date": f["date"], "offerIdea": f["suggestedOffer"]}
                for f in festivals
            ]
        ),
        "SCHEMA": '{"persona": {...}, "channels": [...], "startFreeToday": [...], "actionPlan": {"weeks": [...]}, "festivals": [...], "disclaimer": "..."} — full field shape: persona{name,summary,ageRange,whereTheySpendTime[],whatTheyRespondTo[],buyingTriggers[]}, channels[]{channelId,score,budgetInr,rationale,expectedResult,howToStart[<=3]}, startFreeToday[]{title,minutes,channelId}, weeks[4] each {week,theme,tasks[]{title,channelId,minutes,costInr}}, festivals[]{name,date,suggestedOffer}',
        "FEEDBACK": feedback_summary or "-",
    }


def _fallback_plan(
    request: dict[str, Any],
    selected: list[dict[str, Any]],
    allocation: dict[str, Any],
    language: str,
    model_used: str,
    generation_ms: int,
) -> PlanResponse:
    return planner.build_plan(request, selected, allocation, language, model_used, generation_ms)


def _live_client() -> Any:
    from google import genai  # imported lazily so GEMINI_MOCK dev never needs it
    from google.genai import types as genai_types

    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    return client, genai_types


async def _call_model(prompt: str, system: str, temperature: float) -> str:
    """One JSON-mode Gemini call, waiting max 30s."""
    settings = get_settings()
    client, genai_types = _live_client()
    config = genai_types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=temperature,
        system_instruction=system,
    )

    async def _run() -> str:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=config,
            ),
        )
        return response.text or ""

    return await asyncio.wait_for(_run(), timeout=settings.gemini_timeout_s)


def _split_prompt(full_text: str) -> tuple[str, str]:
    """plan_prompt.md is '# System' + '# User turn'; content template likewise."""
    marker = "\n# User turn\n"
    if marker not in full_text:
        return full_text, ""
    system, user = full_text.split(marker, 1)
    return system.replace("# System", "").strip(), user.strip()


async def generate_plan(
    request: dict[str, Any],
    selected: list[dict[str, Any]],
    allocation: dict[str, Any],
    language: str,
    feedback_summary: str = "",
) -> PlanResponse:
    """Try Gemini twice (JSON + schema validation), else rule-based fallback.

    With GEMINI_MOCK=true a deterministic, validated canned plan is returned.
    """
    settings = get_settings()
    start = time.perf_counter()

    if settings.gemini_mock or not settings.gemini_api_key:
        await asyncio.sleep(0)
        ms = int((time.perf_counter() - start) * 1000)
        return _fallback_plan(request, selected, allocation, language, "gemini-mock", ms)

    prompt_text = _apply_template(
        "plan_prompt.md",
        build_plan_tokens(request, selected, allocation, language, feedback_summary),
    )
    system_text, user_text = _split_prompt(prompt_text)
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            raw = await _call_model(
                (
                    user_text
                    if attempt == 0
                    else user_text + "\n\nREMINDER: return ONLY valid JSON in the exact shape."
                ),
                system_text,
                settings.gemini_plan_temperature,
            )
            parsed = json.loads(_extract_json(raw))
            plan = PlanResponse(**parsed)
            plan.planId = ""
            plan.modelUsed = settings.gemini_model
            plan.generationMs = int((time.perf_counter() - start) * 1000)
            plan.status = "ready"
            return plan
        except Exception as exc:  # noqa: BLE001 — any failure falls to retry/fallback
            last_error = exc
            logger.warning("gemini plan attempt %d failed: %s", attempt + 1, exc)
    ms = int((time.perf_counter() - start) * 1000)
    logger.error("gemini plan failed after retry (%s); using rule fallback", last_error)
    return _fallback_plan(request, selected, allocation, language, "rule_fallback", ms)


def build_content_tokens(plan_doc: dict[str, Any], language: str) -> dict[str, str]:
    return {
        "BUSINESS_NAME": plan_doc["input"].get("businessName", ""),
        "BUSINESS_TYPE": plan_doc["input"].get("businessType", "other"),
        "LOCALITY": plan_doc["input"].get("locality", ""),
        "CITY": plan_doc["input"].get("city", ""),
        "GOAL": plan_doc["input"].get("goal", ""),
        "BUDGET": str(plan_doc["input"].get("monthlyBudgetInr", 0)),
        "LANGUAGE": "English" if language == "en" else "Hindi (natural, Hinglish-friendly)",
        "PLAN_CONTEXT": str(
            {
                "festival": (plan_doc.get("festivals") or [None])[0],
                "persona": (plan_doc.get("persona") or {}).get("name", ""),
                "channels": [c.get("channelId") for c in (plan_doc.get("channels") or [])],
            }
        ),
        "SCHEMA": 'content pack JSON: {"whatsapp": [{label, text<=400}], "instagram": [{caption, hashtags[], reelIdea}], "gbpPost": {title, body<=300, ctaType CALL|ORDER|LEARN_MORE}, "offers": [{name, description, validityDays}]}',
    }


async def generate_content_pack(
    plan_doc: dict[str, Any],
    language: str,
    types: list[str],
) -> ContentPack:
    """Content pack from Gemini; falls back to templated pack on any failure."""
    settings = get_settings()

    def _fallback(model_used: str) -> ContentPack:
        context = {
            "businessName": plan_doc["input"].get("businessName", ""),
            "businessType": plan_doc["input"].get("businessType", "other"),
            "locality": plan_doc["input"].get("locality", ""),
            "city": plan_doc["input"].get("city", ""),
            "goal": plan_doc["input"].get("goal", ""),
            "festivalOffer": (
                (plan_doc.get("festivals") or [{}])[0].get("suggestedOffer")
                if plan_doc.get("festivals")
                else None
            ),
            "offers": playbook_catalog.get(plan_doc["input"].get("businessType", "other"), {}).get(
                "exampleOffers", []
            ),
        }
        return content_fallback.build_content_pack(context, language, types, model_used)

    if settings.gemini_mock or not settings.gemini_api_key:
        return _fallback("gemini-mock")

    prompt_text = _apply_template("content_prompt.md", build_content_tokens(plan_doc, language))
    system_text, user_text = _split_prompt(prompt_text)
    for attempt in range(2):
        try:
            raw = await _call_model(
                user_text if attempt == 0 else user_text + "\n\nREMINDER: ONLY valid JSON.",
                system_text,
                settings.gemini_content_temperature,
            )
            parsed = json.loads(_extract_json(raw))
            parsed["planId"] = plan_doc["planId"]
            parsed["language"] = language
            pack = ContentPack(**{k: v for k, v in parsed.items() if k in ContentPack.model_fields})
            pack.modelUsed = settings.gemini_model
            pack.createdAt = datetime.now(UTC).isoformat()
            return pack
        except Exception as exc:  # noqa: BLE001
            logger.warning("gemini content attempt %d failed: %s", attempt + 1, exc)
    return _fallback("rule_fallback")
