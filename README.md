# GrowLocal

**AI marketing strategy advisor for local businesses** — budget-first, free-first, Hindi + English.

> "I have ₹3,000. Who should I target, where, and exactly what do I do this month?" — answered in under 2 minutes.

| Part | Stack |
|---|---|
| `frontend/` | Next.js (App Router) + TypeScript + Tailwind + `next-intl` |
| `backend/` | Python + FastAPI + Pydantic v2 + `google-genai` + `firebase-admin` |
| Data | Firestore (per-user plans) · Auth: Firebase Auth (Google / guest) |
| Hosting | Firebase App Hosting (FE) · Cloud Run (BE) |

See `docs/` for PRD, TechSpecs, Schema, Appflow and Design specs. `Rule.md` governs how we work; `Tracker.md` tracks progress.

## Architecture

```
┌──────────────────────────────┐        HTTPS/JSON        ┌────────────────────────────┐
│  Next.js 16 web app (SSR)    │  ──────────────────────▶ │  FastAPI (Cloud Run)       │
│  Aurora-glass UI, hi/en      │                          │  validator → scorer        │
│  • /start wizard (5 steps)   │ ◀──────────────────────  │  → allocator → Gemini      │
│  • /generating (staged)      │        CORS allow        │    (JSON mode, retry)      │
│  • /plan/[id] 30-day board   │                          │  → rule-based fallback     │
│  • content studio, feedback  │                          │  MemoryStore / Firestore   │
└──────────────────────────────┘                          └──────────┬─────────────────┘
        │ cookie-locale (no URL routing)                             │ Admin SDK
        ▼                                                            ▼
  Firebase Auth (Google / guest)  ──────────────────────────▶  Firestore:
  (optional keys; auth no-ops to guest-mode)                  plans, tasks, content,
                                                              feedback, users/counters,
                                                              playbooks, festivals (read)
```

Client never writes Firestore directly (rules: read-own-only). The backend owns all writes; the browser only PATCHes task check-offs through the API, which then syncs Firestore.

## Repo layout

```
backend/        FastAPI app, prompts, seed data, tests, Dockerfile
frontend/       Next.js app, components, messages/{en,hi}.json, apphosting.yaml
docs/           PRD · TechSpecs · Schema.md · Appflow · Design docs
firestore.rules firestore.indexes.json  firebase.json  .firebaserc
Tracker.md      live progress log (update after every task)
```

## Quick start (dev mode — no API keys needed)

```bash
# Backend
cd backend
python -m venv .venv            # first time only
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
copy .env.example .env          # dev switches: AUTH_DISABLED=true, GEMINI_MOCK=true, STORE_BACKEND=memory
uvicorn app.main:app --port 8000

# Frontend (new terminal)
cd frontend
npm install
copy .env.example .env.local
npm run dev                     # http://localhost:3000
```

In dev mode the backend runs with a fixed `dev-user`, a mocked Gemini response that always validates, and an in-memory store — no Firebase project or Gemini key required.

## Tests

```bash
cd backend && .venv\Scripts\activate && pytest -q            # 44 tests
cd frontend && npm run lint && npm run build                  # eslint + next build
cd backend && .venv\Scripts\python.exe ..\backend\scripts\qa_matrix.py   # Step-12 matrix vs a live :8000
```

## Environment variables

### `backend/.env` (or Cloud Run env)
| Var | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | *(empty)* | real Gemini calls; keep empty in dev (`GEMINI_MOCK=true`) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | model id for plan/content JSON mode |
| `GOOGLE_PLACES_API_KEY` | *(empty)* | optional; `GET /api/places` returns `[] + note` without it |
| `FIREBASE_PROJECT_ID` | *(empty)* | enables Firestore/Auth Admin SDK |
| `AUTH_DISABLED` | `true` | skip token check and use `dev-user` (DEV ONLY) |
| `GEMINI_MOCK` | `true` | canned-valid plan/content (DEV ONLY) |
| `STORE_BACKEND` | `memory` | `memory` \| `firestore` |
| `PLANS_PER_USER_PER_DAY` | `10` | per-user daily plan cap (429 beyond) |
| `ALLOWED_ORIGIN` | `http://localhost:3000` | comma-separated CORS origins |

### `frontend/.env.local` (public)
| Var | Meaning |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | backend origin; default `http://localhost:8000` |
| `NEXT_PUBLIC_FIREBASE_*` (6 vars) | optional Firebase web config; sign-in no-ops to guest mode without them |

## Deploy

### Backend → Cloud Run (asia-south1, Enemy-official pattern: source deploy builds the Dockerfile)
```bash
gcloud auth login
gcloud run deploy growlocal-api \
  --source backend --region asia-south1 \
  --set-env-vars "AUTH_DISABLED=false,GEMINI_MOCK=false,STORE_BACKEND=firestore,ALLOWED_ORIGIN=https://<project>.apphosting.firebaseapp.com,GEMINI_API_KEY=<key>,GOOGLE_PLACES_API_KEY=<places-key>,FIREBASE_PROJECT_ID=<project-id>" \
  --min-instances 1
```

### Frontend → Firebase App Hosting (Next.js SSR; see `frontend/apphosting.yaml`)
Static export is not possible here: the app is server-rendered with dynamic `/plan/[id]` routes and cookie-based locale (next-intl), so the recommended App Hosting integration is used.
```bash
firebase login
firebase init apphosting           # pick this repo + frontend directory
# put the real NEXT_PUBLIC_* values in apphosting.yaml / console
firebase deploy --only apphosting
```

### Firestore config (rules + the one composite index)
```bash
firebase deploy --only firestore:rules,firestore:indexes
```

## Demo script (3 minutes)

1. **Landing** in हिंदी → hero, dual CTA (aurora-glass UI).
2. **/start wizard**: bakery ₹3,000, Indore, हिंदी → **Generating** stage animation.
3. **Plan dashboard**: persona (Devanagari), budget donut (₹0 demo alternative shows FREE-only), week-1 accordion, tick a task (PATCH round-trip).
4. **Content studio**: copy a WhatsApp blast → open wa.me deep link; regenerate tab.
5. **Feedback**: "worked" → next plan prompt receives the "what worked last time" summary (AI mode).
6. **Competitors** card: allow location → snapshot list (needs Places key; graceful empty otherwise).
7. Fallback demo if live AI flaky: `GEMINI_MOCK=true` produces identical UX deterministically.

## Known limitations

- Firebase/Gemini/Places keys are user-provided; without them the app runs in dev/mock mode and Places returns an honest empty state (see `Tracker.md` bugs).
- Rate limit is per fixed user in dev mode; per-Firebase-uid in production.
- Content regeneration reuses the server-side cache in MVP (no per-type fresh call yet).
- Rule-based plan fallback ignores feedback history (AI path receives it in the prompt).
- npm audit: 4 high findings chain through optional `@grpc/grpc-js` (Firebase web client, unused in guest mode); accepted and tracked.
