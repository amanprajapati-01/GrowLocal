# Implementation Plan — GrowLocal

Timeline assumes a ~48-hour hackathon with 2–4 people. Scale hours if your event is longer. Scope tags: **[P0]** must ship · **[P1]** nice · **[P2]** stretch.

## Team roles (suggested)
| Role | Focus |
|---|---|
| **A — Frontend** | Next.js UI, i18n, plan/ content screens |
| **B — Backend** | FastAPI, scorer, Firestore, deploy |
| **C — AI/Content** | Prompts, schema, playbooks, Hindi quality, demo data |
| **D — Pitch/QA** (if available) | Deck, demo script, testing |

---

## Phase 0 — Setup (Hours 0–3)
- [ ] Create GitHub repo, branch strategy (`main` + feature branches).
- [ ] Create Firebase project; enable Auth (Google + Anonymous), Firestore, Hosting.
- [ ] Get Gemini API key (AI Studio); enable Places API (P1).
- [ ] Scaffold `frontend/` (Next.js + TS + Tailwind) and `backend/` (FastAPI).
- [ ] Add `Rule.md` to repo root and point your AI coding tool at it.
- [ ] Decide product name, logo placeholder, 3 demo businesses.

**Exit criteria:** both apps run locally; "hello" API call works from UI.

## Phase 1 — Prompts & data (Hours 3–8) *(parallel with Phase 2)*
- [ ] Write `channels.json` (10–12 channels) with fit scores.
- [ ] Write 6–8 `playbooks` (kirana, bakery, restaurant, salon, coaching, clinic, retail, other).
- [ ] Seed `festivals.json` (next 6 months + wedding/exam seasons).
- [ ] Prototype plan prompt + JSON schema in AI Studio; test 5 inputs in English and Hindi.
- [ ] Finalize Pydantic models matching `Schema.md`.

**Exit criteria:** a prompt reliably returns valid JSON for 3 business types.

## Phase 2 — Backend core (Hours 3–16)
- [ ] `models/` Pydantic schemas.
- [ ] `services/scorer.py` — channel scoring + unit tests. **[P0]**
- [ ] `services/allocator.py` — budget split, rounding, buffer, sum ≤ budget test. **[P0]**
- [ ] `services/gemini.py` — client, JSON mode, retry, fallback to rule-based plan. **[P0]**
- [ ] `routers/plan.py` — `POST /api/plan` end-to-end. **[P0]**
- [ ] Firebase token verification dependency. **[P0]**
- [ ] Firestore persistence (plans, tasks). **[P0]**
- [ ] `routers/content.py` — content packs. **[P0]**
- [ ] Rate limit + input-hash cache. **[P1]**

**Exit criteria:** `curl` returns a valid, saved plan in < 20s.

## Phase 3 — Frontend core (Hours 6–22)
- [ ] Tailwind theme tokens from `Design.md`; base components (Button, Card, Chip, Slider). **[P0]**
- [ ] i18n setup with `en.json`/`hi.json` and language toggle. **[P0]**
- [ ] Landing page. **[P0]**
- [ ] Onboarding wizard (5 steps) with validation. **[P0]**
- [ ] Generating screen with staged progress. **[P0]**
- [ ] Plan dashboard: persona, channel cards, budget chart, start-free, 30-day plan with checkable tasks. **[P0]**
- [ ] Content studio with copy + WhatsApp deep link. **[P0]**
- [ ] Firebase Auth (Google + guest). **[P1]**
- [ ] My Plans list. **[P1]**

**Exit criteria:** full happy path works locally against the real backend.

## Phase 4 — Integration & deploy (Hours 20–30)
- [ ] Deploy backend to Cloud Run (region `asia-south1`), set secrets.
- [ ] Deploy frontend to Firebase Hosting; set `NEXT_PUBLIC_API_BASE_URL`.
- [ ] Configure CORS, Firestore rules, indexes.
- [ ] Set Cloud Run min-instances = 1 for demo day.
- [ ] End-to-end test on a real phone.

**Exit criteria:** public URL works on mobile data.

## Phase 5 — Differentiators (Hours 28–40)
- [ ] Places API competitor snapshot. **[P1]**
- [ ] Festival awareness surfaced in plan. **[P1]**
- [ ] Expected-result ranges polished with honest labels. **[P1]**
- [ ] Feedback screen + store feedback. **[P1]**
- [ ] Voice input (Web Speech API, `hi-IN`). **[P2]**
- [ ] Share plan (WhatsApp message / PDF). **[P2]**

## Phase 6 — Polish & pitch (Hours 40–48)
- [ ] UI polish pass: loading skeletons, empty/error states, copy review in Hindi.
- [ ] Test matrix: 3 business types × 2 languages × budgets ₹0 / ₹3,000 / ₹20,000.
- [ ] Prepare demo data: 2–3 real local businesses (permission/ anonymized).
- [ ] Record a 60–90s backup demo video.
- [ ] Build 5–6 slide deck: problem, solution, live demo, tech (Google stack), impact, roadmap.
- [ ] Rehearse 3-minute pitch twice; assign Q&A topics.

---

## Dependencies & critical path
```
Prompts/schema ─┐
channels.json ──┼─► Scorer ─► /api/plan ─► Plan UI ─► Deploy ─► Polish/Demo
Firebase setup ─┘                     └─► Content API ─► Content UI
```
Critical path: **schema → /api/plan → plan dashboard → deploy.** Everything in P1/P2 is cut first if time slips.

## Cut list (if behind schedule)
1. Voice input → 2. Share/PDF → 3. Places competitors → 4. Auth (use guest only) → 5. Feedback screen UI (keep API).
Never cut: onboarding, plan with budget split, 30-day plan, content generation, Hindi toggle, live deploy.

## Risk checkpoints
| Hour | Check | If failing |
|---|---|---|
| 8 | Prompt returns valid JSON reliably | Simplify schema; split into 2 calls |
| 16 | `/api/plan` works end to end | Drop Firestore persistence temporarily; return plan only |
| 24 | Frontend happy path complete | Freeze features; polish only |
| 36 | Deployed and working on phone | Stop all new features |
| 44 | Demo rehearsed | Use backup video |

## Definition of done (MVP)
- Deployed public URL, works on mobile.
- Generates valid plan + content for 3 business types in EN and HI.
- Budget always sums correctly.
- No secrets in repo; README with setup steps.
- Demo script and backup video ready.
