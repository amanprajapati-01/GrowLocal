"""Bilingual (en/hi) text templates for rule-based plans and content packs.

All wording: simple, friendly, no jargon, no guarantees, ranges as estimates.
Brand names (WhatsApp, Instagram, Google) stay in English inside Hindi text.
"""

from typing import Any

# --- business type labels -----------------------------------------------------
TYPE_LABELS: dict[str, dict[str, str]] = {
    "kirana": {"en": "kirana store", "hi": "किराना स्टोर"},
    "bakery": {"en": "bakery", "hi": "बेकरी"},
    "restaurant": {"en": "restaurant", "hi": "रेस्टोरेंट"},
    "salon": {"en": "salon", "hi": "सैलून"},
    "coaching": {"en": "coaching centre", "hi": "कोचिंग सेंटर"},
    "clinic": {"en": "clinic", "hi": "क्लिनिक"},
    "retail": {"en": "shop", "hi": "दुकान"},
    "other": {"en": "local business", "hi": "लोकल बिज़नेस"},
}

# --- persona ------------------------------------------------------------------
PERSONA_BY_AUDIENCE: dict[str, dict[str, str]] = {
    "students": {
        "name": {"en": "Campus Foodie Rhea", "hi": "कॉलेज फ्रेंड रिया"},
        "ageRange": "18-26",
    },
    "families": {
        "name": {"en": "Weekend Family Planner Sunita", "hi": "वीकेंड फैमिली प्लानर सुनीता"},
        "ageRange": "28-45",
    },
    "professionals": {
        "name": {"en": "Desk-Hour Smart Buyer Arjun", "hi": "ऑफिस गोइंग स्मार्ट बायर अर्जुन"},
        "ageRange": "25-40",
    },
    "women": {
        "name": {"en": "Neighbourhood Regular Priya", "hi": "मोहल्ले की रेगुलर प्रिया"},
        "ageRange": "25-50",
    },
    "seniors": {
        "name": {"en": "Trusted Old Regular Mr. Khanna", "hi": "पुराने भरोसेमंद ग्राहक खन्ना जी"},
        "ageRange": "55+",
    },
    "tourists": {
        "name": {"en": "City Explorer Neha", "hi": "सिटी एक्सप्लोरर नेहा"},
        "ageRange": "any",
    },
}

PERSONA_WHERE: dict[str, str] = {
    "students": {
        "en": "Instagram Reels and campus WhatsApp groups",
        "hi": "इंस्टाग्राम रील्स और कॉलेज WhatsApp ग्रुप्स",
    },
    "families": {
        "en": "area WhatsApp groups and Google Maps near home",
        "hi": "इलाके के WhatsApp ग्रुप्स और घर के पास Google Maps",
    },
    "professionals": {
        "en": "Google Maps on the commute and Instagram at lunch",
        "hi": "ओफिस जाते-आते Google Maps और दोपहर में इंस्टाग्राम",
    },
    "women": {
        "en": "Instagram and neighbourhood women's WhatsApp groups",
        "hi": "इंस्टाग्राम और मोहल्ले की महिलाओं के WhatsApp ग्रुप्स",
    },
    "seniors": {
        "en": "word of mouth, local groups and Google reviews",
        "hi": "ज़ुबानी बातें, लोकल ग्रुप्स और Google रिव्यूज़",
    },
    "tourists": {
        "en": "Google Maps reviews and travel Instagram pages",
        "hi": "Google Maps रिव्यूज़ और ट्रैवल इंस्टाग्राम पेजेस",
    },
}

PERSONA_RESPOND: dict[str, str] = {
    "students": {
        "en": "short videos, clear prices, student-throwaway prices",
        "hi": "छोटे वीडियो, साफ़ कीमत, स्टूडेंट-फ्रेंडली रेट",
    },
    "families": {
        "en": "family bundles, festival offers, trust and reviews",
        "hi": "फैमिली कॉम्बो, फेस्टिव ऑफ़र, भरोसा और रिव्यू",
    },
    "professionals": {
        "en": "speed, convenience, online order or call option",
        "hi": "तेज़ी, सुविधा, ऑनलाइन ऑर्डर या कॉल करने का विकल्प",
    },
    "women": {
        "en": "honest photos of real work, before/after, referrals",
        "hi": "असली काम की साफ़ तस्वीरें, पहले-बाद के फोटो, किसी की सलाह",
    },
    "seniors": {
        "en": "familiar faces, simple language, phone number visible",
        "hi": "परिचित चेहरे, आसान भाषा, फ़ोन नंबर साफ़ दिखे",
    },
    "tourists": {
        "en": "strong Google rating, popular-item photos, location pin",
        "hi": "अच्छी Google रेटिंग, फेवरेट आइटम के फोटो, लोकेशन पिन",
    },
}

PERSONA_TRIGGER: dict[str, str] = {
    "students": {
        "en": "a friend tagging them, or a new-item drop on Reels",
        "hi": "कोई दोस्त टैग करे, या Reels पर नया आइटम दिख जाए",
    },
    "families": {
        "en": "a festival or occasion coming up in 1-2 weeks",
        "hi": "1-2 हफ़्ते में कोई फेस्टिवल या खास मौका आ रहा हो",
    },
    "professionals": {
        "en": "a limited-time weekday offer that saves time",
        "hi": "टाइम बचाने वाली वीकडे ऑफ़र, सिर्फ़ कुछ दिनों के लिए",
    },
    "women": {
        "en": "a trusted friend's recommendation or a visible result",
        "hi": "किसी भरोसेमंद दोस्त की सलाह या दिखने वाला नतीजा",
    },
    "seniors": {
        "en": "an old relationship plus good reviews on Google",
        "hi": "पुराना रिश्ता और Google पर अच्छे रिव्यू",
    },
    "tourists": {
        "en": "a rating above 4 stars and clear photos on Maps",
        "hi": "Maps पर 4+ रेटिंग और साफ़ फोटो",
    },
}

# --- channel text (rationale / expected result / steps) -----------------------
CHANNEL_TEXT = {
    "google_business_profile": {
        "rationale": {
            "en": "Customers near you search on Google first — a complete profile with photos makes your {type_label} show up there.",
            "hi": "आपके पास के लोग सबसे पहले Google पर खोजते हैं — पूरी प्रोफ़ाइल और फोटो होंगी तो आपकी {type_label} वहीं दिखेगी।",
        },
        "expected": {
            "en": "Estimate: more calls and direction requests within 1-4 weeks of completing the listing.",
            "hi": "अनुमान: लिस्टिंग पूरी करने के 1-4 हफ़्तों में कॉल और directions ज़्यादा आ सकती हैं।",
        },
        "steps": {
            "en": [
                "Open google.com/business and claim your listing",
                "Fill hours, phone, category and services",
                "Add 5 real photos of shop, staff and products",
            ],
            "hi": [
                "google.com/business खोलकर अपनी लिस्टिंग दावा करें",
                "टाइम, फ़ोन नंबर, कैटेगरी सब भरें",
                "दुकान, स्टाफ़ और प्रोडक्ट की 5 असली फोटो डालें",
            ],
        },
        "minutes": [30, 15, 15],
    },
    "whatsapp_business": {
        "rationale": {
            "en": "Your existing customers already trust you — WhatsApp Business turns them into repeat orders with one broadcast.",
            "hi": "आपके पुराने ग्राहक पहले से भरोसा करते हैं — WhatsApp Business से एक मैसेज में रिपीट ऑर्डर आते हैं।",
        },
        "expected": {
            "en": "Estimate: 10-25 messages per broadcast are opened immediately; expect extra daytime orders in 1-2 weeks (range varies).",
            "hi": "अनुमान: हर ब्रॉडकास्ट में 10-25 लोग तुरंत मैसेज खोलते हैं; 1-2 हफ़्तों में दिन के ऑर्डर बढ़ने की उम्मीद (हर दुकान का रेंज अलग है)।",
        },
        "steps": {
            "en": [
                "Download WhatsApp Business, set shop name and hours",
                "Add regulars' numbers into a broadcast list (only opted-in)",
                "Send a friendly save-my-number note with one offer",
            ],
            "hi": [
                "WhatsApp Business ऐप लगाएँ, दुकान का नाम और टाइम डालें",
                "रेगुलर ग्राहकों के नंबर ब्रॉडकास्ट लिस्ट में डालें (सिर्फ़ इजाज़त वाले)",
                "एक दोस्ताना मैसेज भेजें — नंबर सेव करने को कहें और एक ऑफ़र दें",
            ],
        },
        "minutes": [20, 25, 10],
    },
    "instagram_organic": {
        "rationale": {
            "en": "A clean profile grid works like a mini-catalogue — people will scroll it before visiting.",
            "hi": "साफ़-सुथरी इंस्टाग्राम प्रोफ़ाइल छोटे कैटलॉग जैसी काम करती है — लोग आने से पहले देखते हैं।",
        },
        "expected": {
            "en": "Estimate: profile visits from area hashtags in 2-8 weeks if you post consistently 3-4 times a week.",
            "hi": "अनुमान: हफ़्ते में 3-4 बार पोस्ट करेंगे तो 2-8 हफ़्तों में इलाके के लोग प्रोफ़ाइल देख सकते हैं।",
        },
        "steps": {
            "en": [
                "Switch to a Business account with locality in bio",
                "Post 6 good photos of your best work",
                "Add location + city on every post",
            ],
            "hi": [
                "बिज़नेस अकाउंट बनाएँ, bio में इलाका डालें",
                "अपने बेहतरीन काम की 6 फोटो पोस्ट करें",
                "हर पोस्ट पर लोकेशन + सिटी चुनें",
            ],
        },
        "minutes": [20, 25, 10],
    },
    "instagram_reels": {
        "rationale": {
            "en": "Reels push your {type_label} to nearby phone screens — simple behind-the-scenes clips work best.",
            "hi": "Reels आपकी {type_label} को पास के फोनों तक ले जाते हैं — सीधे-सादे behind-the-scenes क्लिप सबसे चलते हैं।",
        },
        "expected": {
            "en": "Estimate: 500-5,000 local views per Reel once you post 4-8 of them; ranges differ by city and item.",
            "hi": "अनुमान: 4-8 Reels डालने के बाद हर Reel पर 500-5,000 लोकल views मिल सकते हैं; रेंज शहर और आइटम पर निर्भर करती है।",
        },
        "steps": {
            "en": [
                "Record one 15-30s clip of your bestseller",
                "Add a trending-but-simple audio + location",
                "Post 2-3 Reels weekly at lunch or 7-9 PM",
            ],
            "hi": [
                "अपने बेस्टसेलर की 15-30 सेकंड की क्लिप बनाएँ",
                "सीधा ट्रेंडिंग ऑडियो + लोकेशन लगाएँ",
                "हफ़्ते में 2-3 Reels, दोपहर या 7-9 बजे डालें",
            ],
        },
        "minutes": [25, 10, 15],
    },
    "facebook_local_groups": {
        "rationale": {
            "en": "Your neighbourhood asks for recommendations in Facebook groups — being the helpful answer wins customers.",
            "hi": "मोहल्ले के लोग Facebook ग्रुप्स में सुझाव पूछते हैं — मददगार जवाब देने वाला ग्राहक जीतता है।",
        },
        "expected": {
            "en": "Estimate: 2-10 direct replies per genuine post in active area groups (varies by group).",
            "hi": "अनुमान: काम के ग्रुप्स में असली पोस्ट पर 2-10 लोग आगे बढ़कर पूछ सकते हैं (ग्रुप के हिसाब से)।",
        },
        "steps": {
            "en": [
                "Join 2-3 area groups (read their rules first)",
                "Introduce your shop with one good photo",
                "Answer local questions helpfully, not with ads",
            ],
            "hi": [
                "2-3 इलाके के ग्रुप जॉइन करें (पहले रूल्स पढ़ें)",
                "एक अच्छी फोटो के साथ दुकान की जान-पहचान कराएँ",
                "लोगों के सवाल दोस्ताना जवाब दें — ऐड-बाज़ी बिल्कुल नहीं",
            ],
        },
        "minutes": [15, 15, 10],
    },
    "google_reviews_drive": {
        "rationale": {
            "en": "New customers compare stars before walking in — a steady flow of honest reviews lifts all your other efforts.",
            "hi": "नए ग्राहक आने से पहले स्टार्स देखते हैं — सच्चे रिव्यू तेज़ी से बढ़ने से बाकी मेहनत भी मज़बूत होती है।",
        },
        "expected": {
            "en": "Estimate: 3-10 new reviews a month if you ask 2-3 happy customers daily (never pay or force).",
            "hi": "अनुमान: हफ़्ते में रोज़ 2-3 खुश ग्राहकों से कहेंगे तो हर महीने 3-10 नए रिव्यू (कभी पैसे या ज़बरदस्ती नहीं)।",
        },
        "steps": {
            "en": [
                "Print a small card with your review QR/link",
                "Ask 2-3 happy customers at peak happy moments",
                "Say thanks in one line to every review",
            ],
            "hi": [
                "रिव्यू के QR/लिंक वाला छोटा कार्ड बनवाएँ",
                "खुश लगने वाले 2-3 ग्राहकों से निवेदन करें",
                "हर रिव्यू पर एक-लाइन में शुक्रिया लिखें",
            ],
        },
        "minutes": [20, 15, 5],
    },
    "tie_ups_local": {
        "rationale": {
            "en": "Neighbouring shops, offices and societies share the same customers — one tie-up is free marketing all month.",
            "hi": "पास की दुकानें, ऑफिस और सोसाइटी वही ग्राहक देखते हैं — एक tie-up महीने भर की फ्री मार्केटिंग है।",
        },
        "expected": {
            "en": "Estimate: 5-15 walk-ins from each good tie-up in its first month (depends on partner footfall).",
            "hi": "अनुमान: अच्छे tie-up से पहले महीने में 5-15 नए ग्राहक (पार्टनर की फुटफ़ॉल पर निर्भर)।",
        },
        "steps": {
            "en": [
                "List 5 nearby shops/offices as partners",
                "Pitch a simple cross-promo (sample, combo, referral)",
                "Keep one poster/card at each partner's counter",
            ],
            "hi": [
                "पास के 5 दुकान/ऑफिस पार्टनर की लिस्ट बनाएँ",
                "आसान cross-promo पेश करें (सैंपल, कॉम्बो, रेफ़रल)",
                "हर पार्टनर के काउंटर पर एक पोस्टर/कार्ड रखें",
            ],
        },
        "minutes": [15, 30, 20],
    },
    "flyers_local": {
        "rationale": {
            "en": "₹{amount} of simple flyers around your locality reaches the 1-2 km who never saw your Instagram.",
            "hi": "₹{amount} के आसान परचे इलाके के वह 1-2 किमी तक पहुँचते हैं जहाँ इंस्टाग्राम तक नहीं पहुँचा।",
        },
        "expected": {
            "en": "Estimate: 5-20 responses from a 200-flyer drop when the offer is clear and dated.",
            "hi": "अनुमान: 200 परचों से 5-20 जवाब आ सकते हैं जब ऑफ़र साफ़ हो, तारीख के साथ।",
        },
        "steps": {
            "en": [
                "One offer, one date, one phone number on the flyer",
                "Print 200 copies",
                "Hand them at society gates and nearby crossings",
            ],
            "hi": [
                "परचे पर एक ऑफ़र, एक तारीख, एक नंबर",
                "200 कॉपियाँ छपवाएँ",
                "सोसाइटी गेट और चौक पर बाँटें",
            ],
        },
        "minutes": [30, 20, 60],
    },
    "referral_offer": {
        "rationale": {
            "en": "Happy customers already talk about you — ₹{amount} of referral discount turns talk into visits.",
            "hi": "खुश ग्राहक पहले से आपकी बात करते हैं — ₹{amount} का रेफ़रल डिस्काउंट बातों को नए ग्राहकों में बदलता है।",
        },
        "expected": {
            "en": "Estimate: 2-8 new customers a month once your regulars know the offer (simple rules work best).",
            "hi": "अनुमान: रेगुलर ग्राहकों को ऑफ़र पता चलने पर हर महीने 2-8 नए ग्राहक (सीधे नियम सबसे बेहतर)।",
        },
        "steps": {
            "en": [
                "Pick one simple offer (bring a friend = X off)",
                "Announce it to regulars on WhatsApp",
                "Thank both referee and referrer the same day",
            ],
            "hi": [
                "एक सीधा ऑफ़र चुनें (दोस्त लाओ = X की छूट)",
                "रेगुलर ग्राहकों को WhatsApp पर बताएँ",
                "दोनों (साथ लाने वाला और आने वाला) को उसी दिन शुक्रिया कहें",
            ],
        },
        "minutes": [15, 10, 10],
    },
    "influencer_micro": {
        "rationale": {
            "en": "A city creator with 5k-50k followers charges ₹1,500-3,000 per reel and their audience is exactly your street.",
            "hi": "शहर के 5k-50k फ़ॉलोवर वाले क्रिएटर की एक reel ₹1,500-3,000 में बनती है — उनका दर्शक आपके इलाके का ही है।",
        },
        "expected": {
            "en": "Estimate: 1-3 reels bring 200-2,000 nearby profile visits; ask for local-audience proof before paying.",
            "hi": "अनुमान: 1-3 reels से 200-2,000 पास के प्रोफ़ाइल विज़िट; पैसे देने से पहले लोकल ऑडियंस का सबूत माँगें।",
        },
        "steps": {
            "en": [
                "Shortlist 3 local creators whose audience is your city",
                "DM or visit with one clear paid-reel offer",
                "Fix: video, date, and what they must show",
            ],
            "hi": [
                "3 लोकल क्रिएटर चुनें जिनका दर्शक आपके शहर का हो",
                "DM या मिलकर एक साफ़ पेड-रील ऑफ़र करें",
                "तय करें: वीडियो, तारीख, क्या दिखाना है",
            ],
        },
        "minutes": [20, 25, 15],
    },
    "meta_local_ads": {
        "rationale": {
            "en": "For ₹{amount} a month you can serve your best photo to phone users within 2-3 km of the shop.",
            "hi": "₹{amount} महीने में आप अपनी बेहतरीन फोटो दुकान के 2-3 किमी के फोन पर दिखा सकते हैं।",
        },
        "expected": {
            "en": "Estimate: 1,000-6,000 views and 10-50 clicks per month at this budget; ranges vary by city and creative.",
            "hi": "अनुमान: इस बजट में 1,000-6,000 views और 10-50 क्लिक प्रति माह; रेंज शहर और क्रिएटिव पर निर्भर।",
        },
        "steps": {
            "en": [
                "Pick 'messages' or 'calls' objective, radius 2-3 km",
                "Use your single best photo + one clear offer",
                "Set the daily spend and run a 7-day test",
            ],
            "hi": [
                "'messages' या 'calls' ऑब्जेक्टिव चुनें, रेडियस 2-3 किमी",
                "अपनी सबसे अच्छी फोटो + एक साफ़ ऑफ़र लगाएँ",
                "रोज़ का बजट सेट करके 7 दिन का टेस्ट चलाएँ",
            ],
        },
        "minutes": [20, 30, 15],
    },
}

# --- start-free quick wins -------------------------------------------------------
QUICK_WINS: dict[str, dict[str, Any]] = {
    "google_business_profile": {
        "en": "Open/finish your Google Business Profile listing",
        "hi": "अपनी Google Business Profile लिस्टिंग आज पूरी करें",
        "minutes": 20,
    },
    "whatsapp_business": {
        "en": "Set up WhatsApp Business + broadcast list of regulars",
        "hi": "WhatsApp Business सेटअप करें और रेगुलर ग्राहकों की ब्रॉडकास्ट लिस्ट बनाएँ",
        "minutes": 20,
    },
    "google_reviews_drive": {
        "en": "Ask 3 happy customers for a Google review today",
        "hi": "आज 3 खुश ग्राहकों से Google रिव्यू माँगें",
        "minutes": 15,
    },
    "facebook_local_groups": {
        "en": "Join 2 area Facebook groups and say hello",
        "hi": "2 इलाके के Facebook ग्रुप्स जॉइन करके हेलो कहें",
        "minutes": 15,
    },
    "instagram_organic": {
        "en": "Post 3 good photos with your location",
        "hi": "लोकेशन के साथ 3 अच्छी फोटो पोस्ट करें",
        "minutes": 20,
    },
    "instagram_reels": {
        "en": "Record one Reel of your bestseller",
        "hi": "अपने बेस्टसेलर का एक Reel बनाएँ",
        "minutes": 25,
    },
    "tie_ups_local": {
        "en": "Message 2 nearby shops about a tie-up",
        "hi": "पास की 2 दुकानों को tie-up बात के लिए मैसेज करें",
        "minutes": 20,
    },
}

# --- weekly plan scaffolding -----------------------------------------------------
WEEK_THEMES: list[dict[str, str]] = [
    {
        "en": "Set your base: be findable on Google and WhatsApp",
        "hi": "आधार तैयार: Google और WhatsApp पर दिखना",
    },
    {"en": "First push: content and one clear offer", "hi": "पहला पुश: कंटेंट और एक साफ़ ऑफ़र"},
    {
        "en": "Reach more: partners, groups and paid test",
        "hi": "और दूर तक: पार्टनर्स, ग्रुप्स और पेड टेस्ट",
    },
    {"en": "Review what worked and double down", "hi": "जो काम आया उसे दोगुना करें"},
]

REVIEW_TASKS: dict[str, str] = {
    "en": "30-day check-in: what brought customers this month on {channel}? Keep, adjust or stop.",
    "hi": "30 दिन की समीक्षा: इस महीने {channel} से क्या ग्राहक लाया? रखें, सुधारें या रोकें।",
}

DISCLAIMER: dict[str, str] = {
    "en": "This plan uses simple rules and seed data; result ranges are estimates, not guarantees. Google, WhatsApp and Instagram are independent platforms with their own policies.",
    "hi": "यह प्लान सरल नियमों पर बना है; नतीजों की रेंज सिर्फ़ अनुमान हैं, कोई गारंटी नहीं। Google, WhatsApp और Instagram की अपनी पॉलिसी पर आपकी जानकारी देखें।",
}

FESTIVAL_OFFER_WRAP: dict[str, str] = {
    "en": "Run a {name} special this week — e.g. {idea}",
    "hi": "इस हफ़्ते {name} का खास ऑफ़र चलाएँ — जैसे: {idea}",
}

# verdict strings for task review when a channel brought nothing
NO_SPEND_NOTE: dict[str, str] = {
    "en": "Free channel — your effort is the only investment.",
    "hi": "फ्री चैनल — इसमें सिर्फ़ आपकी मेहनत लगती है।",
}

SPEND_TASK: dict[str, dict[str, str]] = {
    "flyers_local": {
        "en": "Print and distribute ₹{amount} worth of flyers near your locality",
        "hi": "₹{amount} के परचे छपवाकर इलाके में बाँटें",
    },
    "influencer_micro": {
        "en": "Book one local creator Reel for ₹{amount}",
        "hi": "₹{amount} में एक लोकल क्रिएटर की Reel बुक करें",
    },
    "meta_local_ads": {
        "en": "Run a ₹{amount} 7-day local ad test on Meta (best photo + search objective)",
        "hi": "Meta पर ₹{amount} का 7 दिन का लोकल ऐड टेस्ट चलाएँ (बेस्ट फोटो से)",
    },
    "referral_offer": {
        "en": "Keep ₹{amount} aside as referral-credit pool for loyal customers",
        "hi": "₹{amount} को रेफ़रल-छूट के लिए अलग रखें",
    },
}
