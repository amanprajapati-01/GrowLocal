"""Shared enums and text-cleaning helpers for models."""

import re
from enum import Enum

HTML_TAG_RE = re.compile(r"<[^>]*>")


class BusinessType(str, Enum):
    KIRANA = "kirana"
    BAKERY = "bakery"
    RESTAURANT = "restaurant"
    SALON = "salon"
    COACHING = "coaching"
    CLINIC = "clinic"
    RETAIL = "retail"
    OTHER = "other"


class Goal(str, Enum):
    MORE_WALK_INS = "more_walk_ins"
    ONLINE_ORDERS = "online_orders"
    REPEAT_CUSTOMERS = "repeat_customers"
    BRAND_AWARENESS = "brand_awareness"


class Language(str, Enum):
    EN = "en"
    HI = "hi"


class Audience(str, Enum):
    STUDENTS = "students"
    FAMILIES = "families"
    PROFESSIONALS = "professionals"
    WOMEN = "women"
    SENIORS = "seniors"
    TOURISTS = "tourists"


class CtaType(str, Enum):
    CALL = "CALL"
    ORDER = "ORDER"
    LEARN_MORE = "LEARN_MORE"


def clean_text(value: str) -> str:
    """Strip HTML tags (never render model output raw) and trim whitespace."""
    cleaned = HTML_TAG_RE.sub("", value).replace("\n\n\n", "\n\n")
    return re.sub(r"[ \t]+", " ", cleaned).strip()
