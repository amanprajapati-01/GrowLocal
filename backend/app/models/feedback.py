"""Feedback schemas (Schema.md feedback collection)."""

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.models.common import clean_text


class FeedbackRequest(BaseModel):
    planId: Annotated[str, Field(min_length=4, max_length=64)]
    channelId: Annotated[str, Field(min_length=3, max_length=64)]
    outcome: str  # worked | partial | didnt — validated below
    note: Annotated[str, Field(max_length=300)] = ""

    @field_validator("outcome")
    @classmethod
    def known_outcome(cls, v: str) -> str:
        if v not in {"worked", "partial", "didnt"}:
            raise ValueError("outcome must be worked, partial or didnt")
        return v

    @field_validator("channelId", "note")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:300]
