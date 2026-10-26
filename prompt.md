# prompt.md — Build GrowLocal end to end

You are an autonomous senior full-stack engineer working inside this repository. Your job is to **build the entire GrowLocal MVP** (AI marketing strategy advisor for local businesses) by following the steps below **in order**, without waiting for confirmation between steps.

---

## 0. Operating rules (read first)

1. **Source of truth.** Before writing any code, locate and read these files (they may be in the repo root or `docs/`): `Rule.md`, `PRD.md`, `TechSpecs.md`, `Schema.md`, `Appflow.md`, `Design.md`, `Implementationplan.md`, `Tracker.md`. If one is missing, say so and continue with the others. If they conflict, priority is: **PRD → Schema → TechSpecs → Design → Appflow**. `Rule.md` always governs how you work.
2. **Be autonomous about setup.** If a directory, file, tool, or library is missing, **create or install it yourself** and continue. Specifically:
   - Create any missing folders and files from the repo structure in `TechSpecs.md`.
   - Install any missing **project-level** dependencies with `npm install` / `pip install` (inside the project and the Python virtual environment only).
   - If a **system-level** tool is missing (Node.js, Python, Git, gcloud CLI), first try the OS's standard installer if you have permission; if you can't, stop, tell me exactly what to install, and continue with every step that doesn't need it.
   - Never use `sudo`, delete files outside this repo, or change global system settings without telling me.
3. **Never commit secrets.** Create `.env.example` files with placeholder values; real keys go in `.env` / `.env.local`, which must be in `.gitignore`.
4. **Work step by step.** After finishing each step: run the verification commands, fix failures, update `Tracker.md` (mark tasks `[x]`, add a progress-log line), and commit with a clear message (e.g. `feat(backend): add channel scorer`). Then go straight to the next step.
5. **Stay in scope.** Build only what's in the docs. P0 first, then P1. Do P2 only if everything else is done and working.
6. **Detect the OS** (Windows / macOS / Linux) and use matching commands (e.g. `.venv\Scripts\activate` on Windows, `source .venv/bin/activate` elsewhere).
7. **Don't get stuck.** If a command fails, read the error, fix it, retry. If the same problem fails 3 times, apply the simplest workaround, log it in the `Tracker.md` Decisions log, and move on.
8. **Keep the app runnable.** After Step 6, the backend must always start; after Step 11, the frontend must always build. Never leave `main` broken.

### Dev-mode switches (tooling only, so the app runs without any keys)
Add these environment flags in the backend config. They exist so we can develop and demo even before real credentials are ready:
- `AUTH_DISABLED=true` → skip Firebase token verification and use a fixed dev user (`dev-user`).
- `GEMINI_MOCK=true` → skip the real Gemini call and return a realistic canned response that passes schema validation (in English and Hindi).
- `STORE_BACKEND=memory|firestore` → use an in-memory store (default in dev) or Firestore.

Production must run with all three switched to real behavior.

### Questions you may ask me (only these, and only when needed)
- Gemini API key · Firebase project config/credentials · Google Places API key · `gcloud` login for deployment.
Everything else: decide yourself using the docs.

---

## Step 1 — Environment check

Run and record versions:

```bash
node -v && npm -v
python --version        # or python3 --version
git --version
```

Requirements: Node.js ≥ 20, Python ≥ 3.11, Git. If `git` isn't initialized here, run `git init`.

Then check optional tools (don't block on them): `gcloud --version`, `firebase --version`. If `firebase` is missing, use `npx firebase-tools@latest <command>` when needed rather than installing globally.

**Verify:** you can print all versions. Log them in `Tracker.md`.

---

## Step 2 — Scaffold the repository

Create this structure (skip anything that already exists):

```
growlocal/               # repo root (use the current directory if it is already the repo)
├── frontend/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models/
│   │   ├── data/
│   │   │   └── playbooks/
│   │   └── prompts/
│   └── tests/
├── docs/                # move PRD, TechSpecs, Appflow, Design, Schema, Implementationplan here (keep Rule.md, Tracker.md, prompt.md in root)
├── .gitignore
└── README.md
```

`.gitignore` must include: `node_modules/`, `.next/`, `.venv/`, `__pycache__/`, `.env`, `.env.*` (except `.env.example`), `*.pem`, `serviceAccount*.json`, `.firebase/`, `.DS_Store`.

**Verify:** `git status` shows the structure; commit `chore: scaffold repo`.

---

## Step 3 — Backend project setup

```bash
cd backend
python -m venv .venv
# activate the venv (OS-specific, see rule 6)
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv \
            google-genai firebase-admin httpx pytest pytest-asyncio ruff black
pip freeze > requirements.txt
```

Create:
- `app/main.py` — FastAPI app, CORS (origin from `ALLOWED_ORIGIN`), `/health` endpoint returning `{"status":"ok"}`.
- `app/config.py` — `pydantic-settings` class loading: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GOOGLE_PLACES_API_KEY`, `FIREBASE_PROJECT_ID`, `ALLOWED_ORIGIN`, `AUTH_DISABLED`, `GEMINI_MOCK`, `STORE_BACKEND`.
- `.env.example` with all keys and safe placeholders (`GEMINI_MOCK=true`, `AUTH_DISABLED=true`, `STORE_BACKEND=memory`).
- `pyproject.toml` (or `ruff.toml`) with ruff + black config, line length 100.

**Verify:**
```bash
uvicorn app.main:app --reload --port 8000
# in another terminal:
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`. Commit `feat(backend): fastapi skeleton`.

---

## Step 4 — Seed data

Create in `backend/app/data/` following `Schema.md` §4:

1. `channels.json` — 10–12 channels: `google_business_profile`, `whatsapp_business`, `instagram_organic`, `instagram_reels`, `facebook_local_groups`, `meta_local_ads`, `flyers_local`, `influencer_micro`, `referral_offer`, `google_reviews_drive`, `tie_ups_local`. Each has: `id`, bilingual `name`, `costType`, `minBudgetInr`, `effort`, `timeToResult`, `bestFor[]`, `goalFit{}`, `audienceFit{}`.
2. `playbooks/<businessType>.json` for: `kirana`, `bakery`, `restaurant`, `salon`, `coaching`, `clinic`, `retail`, `other` — each with `tips[]`, `bestChannels[]`, `commonMistakes[]`, `exampleOffers[]` (practical, India-specific, no made-up statistics).
3. `festivals.json` — upcoming Indian festivals and seasons for the next ~6 months from today's date (Diwali, Dhanteras, Chhath, Christmas/New Year, Republic Day, Holi, wedding season, board-exam season, etc.) with English + Hindi names, `date` or `recurringRule`, `regions`, `relevantTypes`, `offerIdeas[]`. Mark dates as approximate where unsure and add a `"verify": true` flag.

**Verify:** write a small test that loads all three and validates required keys. Commit `feat(data): channels, playbooks, festivals`.

---

## Step 5 — Models (Pydantic)

In `app/models/`, implement from `Schema.md` §2–3:
- `PlanRequest` (validated: budget 0–100000, enums for `businessType`, `goal`, `language`; string length limits).
- `Persona`, `ChannelRecommendation`, `StartFreeAction`, `Week`, `Task`, `FestivalSuggestion`, `PlanResponse`.
- `ContentPackRequest`, `ContentPack` (+ sub-models).
- `FeedbackRequest`.
- Validators: `channelId` ∈ catalog; exactly 4 weeks with 3–6 tasks each; strip HTML from all text fields.

**Verify:** `pytest` passes with tests for valid and invalid payloads. Commit `feat(models): pydantic schemas`.

---

## Step 6 — Scoring engine and budget allocator (the core logic)

1. `services/scorer.py` — implement the formula in `TechSpecs.md` §5:
   - Filter by `minBudgetInr`, score, sort, return top 4–5.
   - Always include `google_business_profile` and `whatsapp_business` where applicable.
   - Weights come from config/constants so they're tunable.
2. `services/allocator.py`:
   - Free channels = ₹0 budget (time-based tasks).
   - Distribute the remainder proportionally to score among non-free channels; round to ₹50; keep a 10% "test and adjust" buffer.
   - **Invariant:** `sum(items) + buffer ≤ monthlyBudgetInr`. Handle budget = 0 (free-only plan).
3. Tests (`tests/test_scorer.py`, `tests/test_allocator.py`): budgets ₹0, ₹500, ₹3,000, ₹20,000 across 3+ business types; assert the invariant, that free channels appear first for small budgets, and that outputs are deterministic.

**Verify:** `pytest -q` all green. Commit `feat(core): channel scorer and budget allocator`.

---

## Step 7 — Gemini service, prompts, and fallback

1. `app/prompts/plan_prompt.md` (versioned): system + user template. It must pass in: business info, language, budget, the **scorer + allocator output** (already decided), matching playbook, upcoming festivals (next 60 days), and the JSON schema. Instructions to the model:
   - Write persona, per-channel rationale, expected-result **ranges labeled as estimates**, `startFreeToday`, a 4-week action plan, festival offers.
   - Do **not** change channels or amounts; do not invent channels; no guarantees; no fake statistics; no spam tactics.
   - Tone: simple, friendly, jargon-free; if `language=hi`, write natural Hindi/Hinglish (not literal translation), keeping brand names (WhatsApp, Instagram, Google) in English.
2. `app/prompts/content_prompt.md`: WhatsApp broadcast texts (≤ 400 chars, for opted-in customers), Instagram captions + hashtags + reel idea, Google Business post (≤ 300 chars + CTA), 2–3 offer ideas. Same tone rules.
3. `services/gemini.py`:
   - Use the `google-genai` SDK with JSON/structured output and `GEMINI_MODEL` from env (default to a current Flash-class model; I will confirm the exact ID in AI Studio).
   - Validate with Pydantic; **retry once** on failure; if it still fails, build a **rule-based fallback plan** from playbooks and scorer output (templated text in EN/HI).
   - If `GEMINI_MOCK=true`, return a realistic canned response in both languages that passes validation.
   - Timeout 30s; log latency.

**Verify:** tests with the mock; if `GEMINI_API_KEY` is set, run one live smoke test script (`scripts/smoke_gemini.py`) and print the result. Commit `feat(ai): gemini service with fallback`.

---

## Step 8 — API routes, auth, persistence

1. `services/auth.py` — FastAPI dependency: verify Firebase ID token via `firebase-admin`; if `AUTH_DISABLED=true`, return `dev-user`.
2. `services/store.py` — interface with two implementations: `MemoryStore` and `FirestoreStore` (collections per `Schema.md`; plans written by backend only). Selected by `STORE_BACKEND`.
3. Routers:
   - `POST /api/plan` — validate → scorer → allocator → Gemini (or fallback) → overwrite budget amounts with allocator values → save → return. Include input-hash caching (24h) and a per-user daily limit (default 10).
   - `GET /api/plans`, `GET /api/plans/{id}`, `PATCH /api/plans/{id}/tasks/{taskId}` (toggle done).
   - `POST /api/content` — generate and store a content pack for a plan.
   - `POST /api/feedback` — store feedback.
   - `GET /api/places` — **P1**: Places API (New) nearby search; return `[]` with a note if no key.
4. Consistent errors: `{"error": {"code": "...", "message": "..."}}` with correct HTTP codes (400, 401, 404, 429, 502).

**Verify:** with the dev switches on, run the server and test with `curl` (or a `tests/test_api.py` using `httpx`/`TestClient`): create a plan in English and Hindi, fetch it, toggle a task, generate content, post feedback. Commit `feat(api): plan, content, feedback endpoints`.

---

## Step 9 — Frontend project setup

```bash
cd ../
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --use-npm --import-alias "@/*" --no-src-dir
cd frontend
npm install next-intl firebase lucide-react recharts clsx
```

(Accept defaults for any remaining prompts. If the CLI asks about Turbopack or React Compiler, choose the default.)

Then:
- Configure Tailwind theme tokens from `Design.md` §3–5 (colors, radius, spacing, fonts). Load **Inter** and **Noto Sans Devanagari** via `next/font`.
- Set up `next-intl` with locales `en` and `hi`, `messages/en.json`, `messages/hi.json`, and a language toggle component.
- `lib/api.ts` — typed API client using `NEXT_PUBLIC_API_BASE_URL`; attaches the Firebase ID token when present.
- `lib/firebase.ts` — initialize from `NEXT_PUBLIC_FIREBASE_*` env vars; if they're missing, run in **guest mode** without crashing.
- `lib/format.ts` — `formatInr()` with Indian grouping.
- `.env.local.example` with placeholders.

**Verify:** `npm run dev` loads at `http://localhost:3000`; `npm run build` succeeds. Commit `feat(frontend): next.js setup with i18n and theme`.

---

## Step 10 — UI components

Build reusable components in `components/` per `Design.md` §6, mobile-first, typed props, no hardcoded strings (use i18n keys): `Button`, `Card`, `ChoiceCard`, `Chip`, `BudgetSlider`, `StepperProgress`, `ChannelCard`, `BudgetChart` (Recharts donut/bar with text legend), `TaskItem`, `WeekAccordion`, `ContentCard` (copy, regenerate, WhatsApp deep link), `FestivalChip`, `LanguageToggle`, `Toast`, `Skeleton`, `ErrorState`.

**Verify:** `npm run lint` and `npm run build` pass. Commit `feat(ui): base components`.

---

## Step 11 — Pages and flows (follow `Appflow.md`)

Implement in this order, wiring to the real backend:

1. `/` Landing — value prop, language toggle, CTA.
2. `/start` Onboarding wizard — 5 steps, one question per screen, validation, back keeps answers, progress bar.
3. `/generating` — staged progress while calling `POST /api/plan`; handle errors and retry.
4. `/plan/[id]` Plan dashboard — summary, persona, budget split + channel cards, "Start free today", 30-day plan with checkable tasks (persisted via PATCH), festivals, CTA bar.
5. `/plan/[id]/content` Content studio — tabs, copy, regenerate, WhatsApp link, language switch.
6. `/plans` My Plans list.
7. `/login` Google sign-in + "Continue as guest" (**P1**; guest works without Firebase config).
8. `/plan/[id]/feedback` Feedback screen (**P1**).

Every view needs loading, empty, and error states. Currency in `₹` with Indian grouping. All strings in both `en.json` and `hi.json`.

**Verify:** with both servers running (`AUTH_DISABLED=true`, `GEMINI_MOCK=true`), complete the full happy path in the browser at a 360px-wide viewport in **both languages**, using budgets ₹0, ₹3,000, and ₹20,000. Fix anything broken. Commit per page.

---

## Step 12 — End-to-end verification

1. Run backend tests (`pytest -q`) and frontend checks (`npm run lint && npm run build`).
2. Test matrix: 3 business types (e.g., bakery, salon, coaching) × 2 languages × 3 budgets. Check: budgets always sum correctly; no raw JSON or HTML on screen; no console errors; Hindi text renders correctly.
3. If `GEMINI_API_KEY` is available, switch `GEMINI_MOCK=false` and repeat a few runs; tune prompts if JSON validation fails often or text is generic.
4. Write results to `Tracker.md` (and open bugs in the Bugs table).

---

## Step 13 — P1 features (only after Steps 1–12 pass)

In this order, each with tests/verification and a Tracker update:
1. Firebase Auth (Google) + saving plans per user.
2. Festival awareness polish (show the right festivals per business type and region).
3. Places API competitor snapshot (needs key; otherwise leave behind a graceful empty state).
4. Feedback loop: store feedback and include a short "what worked last time" summary in the next plan's prompt.
5. Rate limit messaging in the UI.

P2 (only if time remains): voice input (Web Speech API, `hi-IN`), share plan (WhatsApp text/PDF).

---

## Step 14 — Deployment preparation

Create (don't run anything that needs my credentials without asking):
- `backend/Dockerfile` (Python slim, non-root user, `uvicorn` on `$PORT`).
- `firebase.json`, `.firebaserc` (placeholder project ID), `firestore.rules` (from `Schema.md` §5), `firestore.indexes.json`.
- Frontend deployment config for Firebase Hosting (static export or the recommended Next.js hosting integration — pick the simplest that works with our routes and tell me why).
- `README.md`: overview, architecture diagram, prerequisites, env vars table, local run steps, test commands, deploy steps (`gcloud run deploy growlocal-api --source backend --region asia-south1`, `firebase deploy`), demo script, known limitations.

Then ask me for: Firebase project ID, Gemini key, and `gcloud auth login` confirmation — and run the deploy only after I confirm.

---

## Step 15 — Final checklist

Confirm each item and report any that fail:

- [ ] Backend tests pass; frontend lint and build pass.
- [ ] Full flow works on mobile viewport in English and Hindi.
- [ ] Budget allocation always ≤ user's budget.
- [ ] Gemini failure falls back to a rule-based plan without crashing.
- [ ] No secrets in the repo (`git grep -i "api_key\|secret"` shows only placeholders).
- [ ] `.env.example` files are complete; README setup works from a clean clone.
- [ ] `Tracker.md` is up to date, with remaining work listed.

---

## Reporting format (after every step)

```
STEP N — <name>: DONE | PARTIAL | BLOCKED
Did: <1–3 bullets>
Verified: <commands run + result>
Installed/created: <new packages, folders, files>
Next: <next step>
Needs from me: <only if blocked>
```

## Start now

Begin at **Step 1**. Do not ask for confirmation to start. Proceed through the steps in order, report after each one, and stop only when you finish Step 15 or need something from the "Questions you may ask me" list.
