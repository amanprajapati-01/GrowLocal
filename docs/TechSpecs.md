# TechSpecs — GrowLocal

## 1. Stack
| Layer | Choice | Notes |
|---|---|---|
| Frontend | Next.js (App Router) + React + TypeScript + Tailwind CSS | Mobile-first PWA-style UI |
| i18n | `next-intl` (or `react-i18next`) | `en`, `hi` |
| Hosting (FE) | Firebase Hosting (or Cloud Run if SSR is needed) | |
| Backend | Python 3.12 + FastAPI + Pydantic v2 | Deployed on Google Cloud Run |
| AI | Gemini API via `google-genai` SDK | Flash-class model for speed; check current model ID in AI Studio |
| Database | Firestore (Native mode) | |
| Auth | Firebase Auth (Google sign-in; anonymous allowed for demo) | |
| External data | Places API (New), Google Trends (optional), Maps JS API | P1 |
| Secrets | Google Secret Manager | No keys in repo |
| CI/CD | GitHub + Cloud Build or GitHub Actions | |

## 2. Architecture
```
Browser (Next.js, Firebase Auth SDK)
        │  HTTPS + Firebase ID token
        ▼
FastAPI on Cloud Run
   ├── /api/plan      → orchestrator
   │       1. validate input
   │       2. channel scorer (rules)         ← channels.json, playbooks
   │       3. budget allocator (code)
   │       4. Gemini: persona + explanations + 30-day plan (JSON mode)
   │       5. validate JSON → store → return
   ├── /api/content   → Gemini content pack (WhatsApp, IG, GBP, offer)
   ├── /api/places    → Places API competitor snapshot (P1)
   └── /api/feedback  → store feedback, flag for next plan
        │
        ▼
Firestore (users, businesses, plans, contentPacks, feedback, playbooks, festivals)
```

## 3. Core design decisions
1. **Hybrid AI + rules.** The scorer picks and ranks channels deterministically; Gemini personalizes and explains. This keeps output consistent, explainable, and safe from hallucinated channels.
2. **Structured output.** Gemini is called with a response schema (JSON mode); backend validates with Pydantic and retries once on failure.
3. **Budget math in code.** Allocation amounts are computed server-side; the model only writes rationale.
4. **Two-stage generation.** Stage 1 returns strategy (persona, channels, budget, plan). Stage 2 (content pack) is generated on demand to keep first response fast.
5. **Language.** `lang` is passed to every prompt; output text is generated natively in Hindi, not machine-translated afterwards.

## 4. API specification

### Auth
`Authorization: Bearer <Firebase ID token>`. Verified in FastAPI dependency using `firebase-admin`. Demo mode may allow anonymous sign-in.

### `POST /api/plan`
**Request**
```json
{
  "businessType": "bakery",
  "businessName": "Sharma Bakery",
  "city": "Kanpur",
  "locality": "Swaroop Nagar",
  "monthlyBudgetInr": 3000,
  "goal": "more_walk_ins",
  "targetAudience": "college students and families",
  "language": "hi"
}
```
**Response `200`**
```json
{
  "planId": "pln_123",
  "persona": { "...": "see Schema.md" },
  "channels": [ { "channelId": "google_business_profile", "score": 92, "budgetInr": 0, "rationale": "...", "expectedResult": "..." } ],
  "budgetAllocation": { "totalInr": 3000, "items": [ ] },
  "actionPlan": { "weeks": [ ] },
  "festivals": [ ],
  "createdAt": "2026-10-26T10:00:00Z"
}
```
**Errors:** `400` invalid input · `401` unauthenticated · `429` rate limited · `502` AI generation failed after retry.

### `POST /api/content`
Body: `{ "planId": "pln_123", "types": ["whatsapp","instagram","gbp_post","offer"], "language": "hi" }` → returns content pack.

### `GET /api/plans` · `GET /api/plans/{id}`
List and fetch the user's saved plans.

### `POST /api/feedback`
Body: `{ "planId", "channelId", "outcome": "worked|partial|didnt", "note" }`.

### `GET /api/places?lat=..&lng=..&type=..` (P1)
Returns nearby competitors with rating and review-count summary.

## 5. Channel scoring engine
`channels.json` catalog entries: `id`, `costType` (free/low/paid), `minBudgetInr`, `bestFor[]` (business types), `goalFit{}`, `audienceFit{}`, `effort`, `timeToResult`, `localReach`.

```
score = 0.35*goalFit + 0.25*audienceFit + 0.20*businessTypeFit
      + 0.10*budgetFit + 0.10*effortFit
      + freeBonus (if costType == free)
```
- Filter out channels where `minBudgetInr` > budget.
- Take top 4–5 channels. Always include Google Business Profile and WhatsApp Business when applicable.
- Weights live in config so they can be tuned during the demo.

**Budget allocation:** free channels get ₹0 but time-based tasks; remaining budget distributed proportionally to score among low/paid channels, rounded to ₹50, with 10% reserved as a "test and adjust" buffer.

## 6. AI integration
- SDK: `google-genai`. Model ID in env var `GEMINI_MODEL`.
- `temperature` 0.6 for plan, 0.8 for content.
- System prompt includes: role, language, tone (simple, friendly), the channel catalog result, budget constraints, festival list for next 60 days, and JSON schema.
- Optional: Search grounding for local trends/festivals (P1; adds latency).
- Guardrails: no income guarantees, no fake statistics, no platform-policy violations (e.g., spam bulk messaging).
- Retry once on schema validation failure; fall back to a templated plan from the rule engine if both attempts fail.

## 7. Performance & reliability
- Target: plan in ≤ 20s p95, content pack ≤ 10s.
- Cache identical requests (hash of inputs) for 24h.
- Cloud Run: min instances 0 (1 during demo to avoid cold start), concurrency 20, timeout 60s.
- Frontend shows staged progress ("Understanding your customers → Choosing channels → Building your plan").

## 8. Security & privacy
- Firebase ID token verification on all non-public routes.
- Firestore rules: users read/write only their own documents.
- Per-user rate limit (e.g., 10 plan generations/day).
- Secrets in Secret Manager; `.env.local` only for local dev and never committed.
- No sensitive personal data collected; business info only. Provide delete-my-data action (P2).
- CORS restricted to the frontend origin.
- Sanitize all model output before rendering (no raw HTML).

## 9. Observability
- Structured JSON logs (request id, user id hash, latency, model tokens).
- Cloud Run logs + Error Reporting.
- Simple counters: plans generated, failures, schema retries.

## 10. Environments & config
| Env | Purpose |
|---|---|
| local | Next dev + `uvicorn` + Firebase emulators |
| prod | Firebase project + Cloud Run service |

Env vars (backend): `GEMINI_API_KEY` (or Vertex project/location), `GEMINI_MODEL`, `GOOGLE_PLACES_API_KEY`, `FIREBASE_PROJECT_ID`, `ALLOWED_ORIGIN`.
Env vars (frontend): `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_FIREBASE_*`.

## 11. Repo structure
```
growlocal/
├── frontend/                 # Next.js app
│   ├── app/                  # routes
│   ├── components/
│   ├── lib/                  # api client, firebase, i18n
│   └── messages/             # en.json, hi.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/          # plan.py, content.py, feedback.py, places.py
│   │   ├── services/         # scorer.py, allocator.py, gemini.py, places.py
│   │   ├── models/           # pydantic schemas
│   │   ├── data/             # channels.json, playbooks/, festivals.json
│   │   └── prompts/
│   ├── tests/
│   └── Dockerfile
├── docs/                     # these .md files
└── firebase.json, firestore.rules
```

## 12. Testing
- Unit: scorer, allocator (budget sums), schema validation.
- Integration: `/api/plan` with mocked Gemini; one live test with real model.
- Manual: 3 business types × 2 languages × 3 budget levels (₹0, ₹3,000, ₹20,000).
- Mobile check on a real mid-range Android device.

## 13. Deployment
1. Create Firebase project; enable Auth (Google), Firestore, Hosting.
2. Build and deploy backend: `gcloud run deploy growlocal-api --source backend --region asia-south1`.
3. Set secrets; set `ALLOWED_ORIGIN`.
4. Deploy frontend: `firebase deploy --only hosting` (rewrite `/api/**` to Cloud Run optional).
5. Smoke-test with demo business.
