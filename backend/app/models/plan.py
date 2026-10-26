"""Request/response schemas for the AI plan (Schema.md SS2)."""

import re
from datetime import date
from typing import Annotated, Any, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.common import (
    Audience,
    BusinessType,
    Goal,
    Language,
    clean_text,
)
from app.services.catalog import is_valid_channel

RANGE_RE = re.compile(r"\d+\s*[-\u2013\u2014]|\d+\s*to\s*\d+")


def has_range(text: str) -> bool:
    """Expected results must carry an honest numeric range or an 'estimate' label — never a guarantee."""
    lowered = text.lower()
    return (
        bool(RANGE_RE.search(text))
        or "estimate" in lowered
        or "\u0905\u0928\u0941\u092e\u093e\u0928" in lowered
    )


class PlanRequest(BaseModel):
    businessType: BusinessType
    businessName: Annotated[str, Field(min_length=2, max_length=60)]
    city: Annotated[str, Field(min_length=2, max_length=40)]
    locality: Annotated[str, Field(min_length=2, max_length=40)]
    monthlyBudgetInr: Annotated[int, Field(ge=0, le=100000)]
    goal: Goal
    targetAudience: Annotated[list[Audience], Field(min_length=1, max_length=6)] = []
    targetAudienceText: Annotated[str, Field(max_length=200)] = ""
    language: Language = Language.EN

    @field_validator("businessName", "city", "locality", "targetAudienceText")
    @classmethod
    def no_html(cls, v: str) -> str:
        if "<" in v or ">" in v:
            raise ValueError("HTML is not allowed in text fields")
        return clean_text(v)


class Persona(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=80)]
    summary: Annotated[str, Field(min_length=10, max_length=600)]
    ageRange: Annotated[str, Field(min_length=2, max_length=30)]
    whereTheySpendTime: Annotated[list[str], Field(min_length=1, max_length=6)]
    whatTheyRespondTo: Annotated[list[str], Field(min_length=1, max_length=6)]
    buyingTriggers: Annotated[list[str], Field(min_length=1, max_length=6)]

    @field_validator("*")
    @classmethod
    def clean(cls, v: Any) -> Any:
        if isinstance(v, str):
            return clean_text(v)
        if isinstance(v, list):
            return [clean_text(i)[:120] for i in v]
        return v


class ChannelRecommendation(BaseModel):
    channelId: str
    score: Annotated[int, Field(ge=0, le=100)]
    budgetInr: Annotated[int, Field(ge=0, le=100000)] = 0
    rationale: Annotated[str, Field(min_length=8, max_length=240)]
    expectedResult: Annotated[str, Field(min_length=8, max_length=240)]
    howToStart: Annotated[list[str], Field(min_length=1, max_length=3)]

    @field_validator("channelId")
    @classmethod
    def channel_in_catalog(cls, v: str) -> str:
        if not is_valid_channel(v):
            raise ValueError(f"channelId '{v}' is not in the catalog")
        return v

    @field_validator("expectedResult")
    @classmethod
    def result_is_a_range(cls, v: str) -> str:
        text = clean_text(v)[:240]
        if not has_range(text):
            raise ValueError("expectedResult must be an honest range labelled as an estimate")
        return text

    @field_validator("rationale")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:240]

    @field_validator("howToStart")
    @classmethod
    def clean_steps(cls, v: list[str]) -> list[str]:
        return [clean_text(s)[:160] for s in v]


class StartFreeAction(BaseModel):
    title: Annotated[str, Field(min_length=4, max_length=160)]
    minutes: Annotated[int, Field(ge=5, le=180)]
    channelId: str

    @field_validator("channelId")
    @classmethod
    def channel_in_catalog(cls, v: str) -> str:
        if not is_valid_channel(v):
            raise ValueError(f"channelId '{v}' is not in the catalog")
        return v

    @field_validator("title")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:160]


class Task(BaseModel):
    title: Annotated[str, Field(min_length=4, max_length=160)]
    channelId: str
    minutes: Annotated[int, Field(ge=5, le=480)]
    costInr: Annotated[int, Field(ge=0, le=100000)] = 0
    done: bool = False

    @field_validator("channelId")
    @classmethod
    def channel_in_catalog(cls, v: str) -> str:
        if not is_valid_channel(v):
            raise ValueError(f"channelId '{v}' is not in the catalog")
        return v

    @field_validator("title")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:160]


class Week(BaseModel):
    week: Annotated[int, Field(ge=1, le=4)]
    theme: Annotated[str, Field(min_length=4, max_length=120)]
    tasks: Annotated[list[Task], Field(min_length=3, max_length=6)]

    @field_validator("theme")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:120]


class ActionPlan(BaseModel):
    weeks: Annotated[list[Week], Field(min_length=4, max_length=4)]

    @model_validator(mode="after")
    def weeks_are_four_in_order(self) -> Self:
        numbers = [w.week for w in self.weeks]
        if numbers != [1, 2, 3, 4]:
            raise ValueError("actionPlan must contain exactly weeks 1, 2, 3, 4 in order")
        return self


class FestivalSuggestion(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=80)]
    date: Annotated[str, Field(min_length=10, max_length=10)]
    suggestedOffer: Annotated[str, Field(min_length=10, max_length=300)]

    @field_validator("date")
    @classmethod
    def valid_date(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError as e:
            raise ValueError("date must be YYYY-MM-DD") from e
        return v

    @field_validator("suggestedOffer")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:300]


class BudgetItem(BaseModel):
    channelId: str
    amountInr: Annotated[int, Field(ge=0, le=100000)]


class BudgetAllocation(BaseModel):
    totalInr: Annotated[int, Field(ge=0, le=100000)]
    bufferInr: Annotated[int, Field(ge=0, le=10000)] = 0
    items: Annotated[list[BudgetItem], Field(max_length=12)] = []

    @model_validator(mode="after")
    def within_budget(self) -> Self:
        if sum(i.amountInr for i in self.items) + self.bufferInr > self.totalInr:
            raise ValueError("budget items + buffer exceed the total budget")
        return self


class PlanResponse(BaseModel):
    planId: str
    persona: Persona
    channels: Annotated[list[ChannelRecommendation], Field(min_length=2, max_length=6)]
    budgetAllocation: BudgetAllocation
    startFreeToday: Annotated[list[StartFreeAction], Field(min_length=0, max_length=5)] = []
    actionPlan: ActionPlan
    festivals: Annotated[list[FestivalSuggestion], Field(min_length=0, max_length=6)] = []
    disclaimer: Annotated[str, Field(min_length=20, max_length=400)]
    createdAt: str = ""
    modelUsed: str = "rule_fallback"
    generationMs: int = 0
    status: str = "ready"

    @field_validator("disclaimer")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:400]
