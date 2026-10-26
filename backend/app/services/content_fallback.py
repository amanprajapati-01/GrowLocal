"""Rule-based content pack builder (fallback + mock source for content generation).

Produces a valid ContentPack in EN/HI from playbook offers + festival context.
"""

from datetime import UTC, datetime
from typing import Any

from app.models.content import ContentPack
from app.services.templates import TYPE_LABELS

HASHTAGS: dict[str, list[str]] = {
    "kirana": ["#KiranaStore", "#GroceryRun", "#LocaliPurji", "#DailyNeeds"],
    "bakery": ["#FreshBakes", "#CakeLovers", "#TeaTime", "#SweetCraving"],
    "restaurant": ["#FoodNearMe", "#LunchSpecial", "#DesiTaste", "#FamilyDinner"],
    "salon": ["#GlowUp", "#HairAndCare", "#SalonDeals", "#SelfCareDay"],
    "coaching": ["#StudySmart", "#ExamReady", "#DoubtSolved", "#TuitionNearMe"],
    "clinic": ["#HealthFirst", "#BookSlot", "#FamilyCare", "#CheckupReminder"],
    "retail": ["#NewArrivals", "#ShoppingMood", "#DealOfTheWeek", "#VisitUs"],
    "other": ["#ShopLocal", "#LocalFavourite", "#NearMe", "#SupportLocal"],
}

HOOKS: dict[str, dict[str, str]] = {
    "kirana": {
        "en": "Everything for your daily needs, one call away",
        "hi": "घर की हर ज़रूरत, नज़दीक ही",
    },
    "bakery": {
        "en": "Fresh out of the oven, every single evening",
        "hi": "हर शाम, ताज़ा बेक किया हुआ",
    },
    "restaurant": {"en": "Ghar jaisa taste, ghar ke paas", "hi": "घर जैसा स्वाद, घर के पास"},
    "salon": {"en": "Walk in tired, walk out glowing", "hi": "थके जाएँ, चमकते हुए जाएँ"},
    "coaching": {"en": "Doubt clear karo, marks improve karo", "hi": "डाउट क्लियर करो, नंबर बढ़ाओ"},
    "clinic": {"en": "Your neighbourhood health partner", "hi": "आपका मोहल्ले का हेल्थ पार्टनर"},
    "retail": {
        "en": "New collection, old prices, familiar faces",
        "hi": "नया कलेक्शन, उसी कीमत पर, पुराने चेहरे",
    },
    "other": {"en": "Made for our neighbourhood", "hi": "मोहल्ले के लिए ही बनाया गया"},
}

WHATSAPP_MAIN: dict[str, str] = {
    "en": "Namaste! 🙏 It's {name} here. This week's special just for our regulars: {offer}. Reply with a YES and we will keep it ready for you.",
    "hi": "नमस्ते! 🙏 {name} यहाँ से। इस हफ़्ते हमारे रेगुलर ग्राहकों के लिए ख़ास ऑफ़र: {offer}। 'हाँ' लिखकर रिप्लाई करें, हम आपके लिए तैयार रख देंगे।",
}

WHATSAPP_STATUS: dict[str, str] = {
    "en": "This {days}-day only: {short_offer}. 📍 {locality}, {city}",
    "hi": "सिर्फ़ {days} दिन के लिए: {short_offer}। 📍 {locality}, {city}",
}

IG_CAPTION: dict[str, str] = {
    "en": "{hook} ✨ {offer_line} Walk in or send us a WhatsApp message to order. Find us: {locality}, {city}.",
    "hi": "{hook} ✨ {offer_line} दुकान पर आइए या WhatsApp पर मैसेज कीजिए। स्पट: {locality}, {city}।",
}

GBP_TITLE: dict[str, str] = {
    "en": "{name} — {short_offer}",
    "hi": "{name} — {short_offer}",
}

GBP_BODY: dict[str, str] = {
    "en": "{offer_line} Visit us at {locality}, {city}. Call or come by during shop hours — we would love to see you!",
    "hi": "{offer_line} हमें {locality}, {city} में देखें। दुकान के टाइम में कॉल कीजिए या पधारें — इंतज़ार रहेगा!",
}

CTA_BY_GOAL: dict[str, Any] = {
    "more_walk_ins": "CALL",
    "online_orders": "ORDER",
    "repeat_customers": "CALL",
    "brand_awareness": "LEARN_MORE",
}


def _city_hashtag(city: str) -> str:
    cleaned = "".join(ch for ch in city.title() if ch.isalpha())
    return f"#{cleaned}Local" if cleaned else "#LocalFinds"


def _offer_lines(context: dict[str, Any]) -> tuple[str, str]:
    offers = [context.get("festivalOffer") or "", *(context.get("offers") or [])]
    main = next((o for o in offers if o), "Visit us this week for something special")
    return main, main.split(".")[0][:60]


def build_content_pack(
    context: dict[str, Any],
    language: str,
    types: list[str] | None = None,
    model_used: str = "rule_fallback",
) -> ContentPack:
    """Build a deterministic ContentPack for the given business context."""
    labels = TYPE_LABELS.get(context["businessType"], TYPE_LABELS["other"])
    hook = HOOKS.get(context["businessType"], HOOKS["other"])
    main_offer, short_offer = _offer_lines(context)
    ctx_offers = [o for o in (context.get("offers") or []) if o]
    hashtags = [
        *HASHTAGS.get(context["businessType"], HASHTAGS["other"])[:4],
        _city_hashtag(context["city"]),
        "#GrowLocal",
    ]

    include = types if types is not None else ["whatsapp", "instagram", "gbp_post", "offer"]
    whatsapp_txt = WHATSAPP_MAIN[language].format(name=context["businessName"], offer=main_offer)
    status_txt = WHATSAPP_STATUS[language].format(
        days="3", short_offer=short_offer, locality=context["locality"], city=context["city"]
    )
    caption_txt = IG_CAPTION[language].format(
        hook=hook[language],
        offer_line=main_offer,
        locality=context["locality"],
        city=context["city"],
    )
    reel_txt = (
        f"15-sec phone reel: show your bestseller at the {labels[language]} and end with the offer '{short_offer}'"
        if language == "en"
        else f"15 सेकंड की फोन-रील: बेस्टसेलर दिखाएँ और अंत में ऑफ़र बोलें — '{short_offer}'"
    )
    second_offer = ctx_offers[0] if ctx_offers else main_offer
    offers_list = [
        {
            "name": (
                f"{context['businessName']} special"
                if language == "en"
                else f"{context['businessName']} तय ऑफ़र"
            ),
            "description": main_offer[:150],
            "validityDays": 7,
        },
        {
            "name": "Festival/season pick" if language == "en" else "त्योहार/सीज़न पिक",
            "description": second_offer[:150],
            "validityDays": 15,
        },
    ]
    return ContentPack(
        planId=context.get("planId", ""),
        language=language,  # type: ignore[arg-type]
        whatsapp=(
            [
                {
                    "label": (
                        "Regulars broadcast" if language == "en" else "रेगुलर ग्राहकों को मैसेज"
                    ),
                    "text": whatsapp_txt,
                },
                {
                    "label": "Status update" if language == "en" else "स्टेटस अपडेट",
                    "text": status_txt,
                },
            ]
            if "whatsapp" in include
            else []
        ),
        instagram=(
            [{"caption": caption_txt, "hashtags": hashtags, "reelIdea": reel_txt}]
            if "instagram" in include
            else []
        ),
        gbpPost=(
            {
                "title": GBP_TITLE[language].format(
                    name=context["businessName"], short_offer=short_offer
                ),
                "body": GBP_BODY[language].format(
                    offer_line=main_offer, locality=context["locality"], city=context["city"]
                ),
                "ctaType": CTA_BY_GOAL.get(context.get("goal", ""), "LEARN_MORE"),
            }
            if "gbp_post" in include
            else None
        ),
        offers=offers_list if "offer" in include else [],
        createdAt=datetime.now(UTC).isoformat(),
        modelUsed=model_used,
    )
