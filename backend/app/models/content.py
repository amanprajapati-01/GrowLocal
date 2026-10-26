"""Content pack schemas (Schema.md SS3)."""

from typing import Annotated, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.common import CtaType, Language, clean_text


class ContentPackRequest(BaseModel):
    planId: Annotated[str, Field(min_length=4, max_length=64)]
    types: Annotated[list[str], Field(min_length=1, max_length=4)] = [
        "whatsapp",
        "instagram",
        "gbp_post",
        "offer",
    ]
    language: Language = Language.EN

    @model_validator(mode="after")
    def known_types(self) -> Self:
        allowed = {"whatsapp", "instagram", "gbp_post", "offer"}
        bad = set(self.types) - allowed
        if bad:
            raise ValueError(f"unknown content types: {sorted(bad)}")
        return self


class WhatsAppItem(BaseModel):
    label: Annotated[str, Field(min_length=3, max_length=80)]
    text: Annotated[str, Field(min_length=10, max_length=400)]

    @field_validator("label", "text")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:400]


class InstagramItem(BaseModel):
    caption: Annotated[str, Field(min_length=10, max_length=400)]
    hashtags: Annotated[list[str], Field(min_length=3, max_length=10)]
    reelIdea: Annotated[str, Field(min_length=8, max_length=300)]

    @field_validator("caption", "reelIdea")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:400]

    @field_validator("hashtags")
    @classmethod
    def clean_hashtags(cls, v: list[str]) -> list[str]:
        cleaned = [clean_text(h)[:30].replace(" ", "_") for h in v]
        return [h if h.startswith("#") else f"#{h}" for h in cleaned]


class GBPPost(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=80)]
    body: Annotated[str, Field(min_length=10, max_length=300)]
    ctaType: CtaType = CtaType.LEARN_MORE

    @field_validator("title", "body")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:300]


class OfferItem(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=80)]
    description: Annotated[str, Field(min_length=10, max_length=300)]
    validityDays: Annotated[int, Field(ge=1, le=90)] = 7

    @field_validator("name", "description")
    @classmethod
    def clean(cls, v: str) -> str:
        return clean_text(v)[:300]


class ContentPack(BaseModel):
    planId: str
    language: Language
    whatsapp: Annotated[list[WhatsAppItem], Field(min_length=1, max_length=4)] = []
    instagram: Annotated[list[InstagramItem], Field(min_length=1, max_length=3)] = []
    gbpPost: GBPPost | None = None
    offers: Annotated[list[OfferItem], Field(min_length=1, max_length=4)] = []
    createdAt: str = ""
    modelUsed: str = "rule_fallback"

    @model_validator(mode="after")
    def at_least_something(self) -> Self:
        if not any([self.whatsapp, self.instagram, self.gbpPost, self.offers]):
            raise ValueError("content pack must contain at least one item")
        return self
