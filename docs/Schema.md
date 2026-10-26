# Schema — GrowLocal

Covers (1) Firestore data model, (2) the AI plan JSON schema, (3) the channel catalog, (4) security rules.

---

## 1. Firestore collections

### `users/{uid}`
| Field | Type | Notes |
|---|---|---|
| `displayName` | string | From Google profile |
| `email` | string | |
| `preferredLanguage` | `"en"` \| `"hi"` | |
| `isAnonymous` | bool | Guest sessions |
| `createdAt` | timestamp | |
| `planCountToday` | number | For rate limiting |
| `lastPlanDate` | string `YYYY-MM-DD` | Reset counter daily |

### `businesses/{businessId}`
| Field | Type | Notes |
|---|---|---|
| `ownerUid` | string | Index |
| `name` | string | |
| `type` | enum | `kirana, bakery, restaurant, salon, coaching, clinic, retail, other` |
| `typeOtherText` | string? | When `other` |
| `city` | string | |
| `locality` | string | |
| `geo` | geopoint? | Optional, for Places |
| `createdAt`, `updatedAt` | timestamp | |

### `plans/{planId}`
| Field | Type | Notes |
|---|---|---|
| `ownerUid` | string | Index |
| `businessId` | string | |
| `input` | map | `{monthlyBudgetInr, goal, targetAudience[], targetAudienceText, language}` |
| `inputHash` | string | For caching |
| `persona` | map | See AI schema |
| `channels` | array<map> | Ranked, scored |
| `budgetAllocation` | map | `{totalInr, bufferInr, items[]}` |
| `actionPlan` | map | `{weeks[]}` |
| `festivals` | array<map> | |
| `competitors` | array<map>? | P1 |
| `status` | enum | `generating, ready, failed` |
| `modelUsed` | string | |
| `generationMs` | number | |
| `createdAt` | timestamp | |

### `plans/{planId}/tasks/{taskId}` (subcollection)
| Field | Type |
|---|---|
| `week` | number (1–4) |
| `title` | string |
| `channelId` | string |
| `done` | bool |
| `doneAt` | timestamp? |

### `plans/{planId}/contentPacks/{packId}`
| Field | Type | Notes |
|---|---|---|
| `language` | string | |
| `whatsapp` | array<map> | `{label, text}` |
| `instagram` | array<map> | `{caption, hashtags[], reelIdea}` |
| `gbpPost` | map | `{title, body, ctaType}` |
| `offers` | array<map> | `{name, description, validityDays}` |
| `createdAt` | timestamp | |

### `feedback/{feedbackId}`
| Field | Type | Notes |
|---|---|---|
| `ownerUid`, `planId`, `channelId` | string | |
| `outcome` | enum | `worked, partial, didnt` |
| `note` | string? | |
| `createdAt` | timestamp | |

### `playbooks/{businessType}` (read-only, seeded)
| Field | Type |
|---|---|
| `businessType` | string |
| `tips` | array<string> |
| `bestChannels` | array<string> |
| `commonMistakes` | array<string> |
| `exampleOffers` | array<string> |

### `festivals/{id}` (read-only, seeded)
| Field | Type |
|---|---|
| `name`, `nameHi` | string |
| `date` | string `YYYY-MM-DD` (or `recurringRule`) |
| `regions` | array<string> (`all`, `north`, …) |
| `relevantTypes` | array<string> |
| `offerIdeas` | array<string> |

### Indexes
- `plans`: `ownerUid ASC, createdAt DESC`
- `plans`: `inputHash ASC, ownerUid ASC`
- `feedback`: `planId ASC, createdAt DESC`
- `businesses`: `ownerUid ASC, createdAt DESC`

---

## 2. AI plan JSON schema (Gemini response + stored in `plans`)

```json
{
  "persona": {
    "name": "string (e.g. 'Campus Foodie Rhea')",
    "summary": "string, 2 sentences",
    "ageRange": "string",
    "whereTheySpendTime": ["string"],
    "whatTheyRespondTo": ["string"],
    "buyingTriggers": ["string"]
  },
  "channels": [
    {
      "channelId": "string (must exist in catalog)",
      "score": 0,
      "budgetInr": 0,
      "rationale": "string, <= 30 words",
      "expectedResult": "string (range + 'estimate' wording)",
      "howToStart": ["string (max 3 steps)"]
    }
  ],
  "startFreeToday": [
    { "title": "string", "minutes": 0, "channelId": "string" }
  ],
  "actionPlan": {
    "weeks": [
      {
        "week": 1,
        "theme": "string",
        "tasks": [
          { "title": "string", "channelId": "string", "minutes": 0, "costInr": 0 }
        ]
      }
    ]
  },
  "festivals": [
    { "name": "string", "date": "YYYY-MM-DD", "suggestedOffer": "string" }
  ],
  "disclaimer": "string"
}
```

**Pydantic validation rules**
- `channels[].channelId` ∈ catalog IDs.
- `sum(channels[].budgetInr)` + buffer ≤ `monthlyBudgetInr` (budget values are overwritten by backend allocator, not trusted from the model).
- `weeks.length == 4`; each week has 3–6 tasks.
- Text fields have max lengths; strip HTML.
- `expectedResult` must contain a range, not a single guarantee.

## 3. Content pack JSON schema

```json
{
  "whatsapp": [ { "label": "Regulars broadcast", "text": "string <= 400 chars" } ],
  "instagram": [ { "caption": "string", "hashtags": ["string"], "reelIdea": "string" } ],
  "gbpPost": { "title": "string", "body": "string <= 300 chars", "ctaType": "CALL|ORDER|LEARN_MORE" },
  "offers": [ { "name": "string", "description": "string", "validityDays": 7 } ]
}
```

## 4. Channel catalog (`backend/app/data/channels.json`)

```json
{
  "id": "google_business_profile",
  "name": { "en": "Google Business Profile", "hi": "गूगल बिज़नेस प्रोफ़ाइल" },
  "costType": "free",
  "minBudgetInr": 0,
  "effort": "low",
  "timeToResult": "1-4 weeks",
  "bestFor": ["bakery","restaurant","salon","clinic","retail","kirana","coaching"],
  "goalFit": { "more_walk_ins": 1.0, "online_orders": 0.5, "repeat_customers": 0.4, "brand_awareness": 0.6 },
  "audienceFit": { "students": 0.7, "families": 0.9, "professionals": 0.8, "seniors": 0.6 }
}
```
**Starter channel IDs:** `google_business_profile`, `whatsapp_business`, `instagram_organic`, `instagram_reels`, `facebook_local_groups`, `meta_local_ads`, `flyers_local`, `influencer_micro`, `referral_offer`, `google_reviews_drive`, `tie_ups_local` (collabs with nearby businesses).

## 5. Firestore security rules (sketch)

```
rules_version = '2';
service cloud.firestore {
  match /databases/{db}/documents {
    function isOwner(uid) { return request.auth != null && request.auth.uid == uid; }

    match /users/{uid} { allow read, write: if isOwner(uid); }

    match /businesses/{id} {
      allow read, write: if request.auth != null &&
        (resource == null ? request.resource.data.ownerUid == request.auth.uid
                          : resource.data.ownerUid == request.auth.uid);
    }

    match /plans/{planId} {
      allow read: if request.auth != null && resource.data.ownerUid == request.auth.uid;
      allow write: if false;               // written by backend (Admin SDK) only
      match /tasks/{t} { allow read, update: if request.auth != null &&
        get(/databases/$(db)/documents/plans/$(planId)).data.ownerUid == request.auth.uid; }
      match /contentPacks/{c} { allow read: if request.auth != null &&
        get(/databases/$(db)/documents/plans/$(planId)).data.ownerUid == request.auth.uid; }
    }

    match /feedback/{id} { allow create: if request.auth != null &&
        request.resource.data.ownerUid == request.auth.uid; allow read: if false; }

    match /playbooks/{id} { allow read: if true; allow write: if false; }
    match /festivals/{id} { allow read: if true; allow write: if false; }
  }
}
```
