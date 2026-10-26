# GrowLocal

**AI marketing strategy advisor for local businesses** — budget-first, free-first, Hindi + English.

> "I have ₹3,000. Who should I target, where, and exactly what do I do this month?" — answered in under 2 minutes.

| Part | Stack |
|---|---|
| `frontend/` | Next.js (App Router) + TypeScript + Tailwind + `next-intl` |
| `backend/` | Python + FastAPI + Pydantic v2 + `google-genai` + `firebase-admin` |
| Data | Firestore · Auth: Firebase Auth (Google / guest) |
| Hosting | Firebase Hosting (FE) · Cloud Run (BE) |

See `docs/` for PRD, TechSpecs, Schema, Appflow and Design specs. `Rule.md` governs how we work; `Tracker.md` tracks progress.

## Quick start (dev mode — no API keys needed)

```bash
# Backend
cd backend
python -m venv .venv            # first time only
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
copy .env.example .env          # dev switches: AUTH_DISABLED=true, GEMINI_MOCK=true, STORE_BACKEND=memory
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal, repo root)
cd frontend
npm install
copy .env.local.example .env.local
npm run dev                     # http://localhost:3000
```

In dev mode the backend runs with a fixed `dev-user`, a mocked Gemini response that always validates, and an in-memory store — no Firebase project or Gemini key required.

## Tests

```bash
cd backend && .venv\Scripts\activate && pytest -q
cd frontend && npm run lint && npm run build
```
