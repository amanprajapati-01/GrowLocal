# Tracker — GrowLocal

**How to use:** update this file after every completed task. Mark `[x]` when done, `[~]` when in progress, `[!]` when blocked. Add a one-line note in the Log at the bottom.

**Legend:** P0 must · P1 nice · P2 stretch · Owner = A (Frontend) / B (Backend) / C (AI/Content) / D (Pitch/QA)

**Status snapshot:** Phase 1 done (backend core working with dev switches) · Overall: ~50% · Blockers: none · Last updated: 2026-10-26

---

## Setup
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [x] | T-001 | Create repo + branches | P0 | B |
| [ ] | T-002 | Firebase project (Auth, Firestore, Hosting) | P0 | D(need user) |
| [ ] | T-003 | Gemini API key + test call | P0 | D(need user) |
| [ ] | T-004 | Scaffold Next.js + Tailwind | P0 | A |
| [x] | T-005 | Scaffold FastAPI + Dockerfile *(Dockerfile pending until Step 14)* | P0 | B |
| [x] | T-006 | Add Rule.md to repo root | P0 | B |
| [ ] | T-007 | Pick name + 3 demo businesses | P0 | |

## Data & prompts
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [x] | T-010 | `channels.json` (11 channels, bilingual) | P0 | C |
| [x] | T-011 | Playbooks for 8 business types | P0 | C |
| [x] | T-012 | `festivals.json` (next ~6 months, approximate dates flagged `verify`) | P1 | C |
| [~] | T-013 | Plan prompt + JSON schema (written + mock-validated; live AI-Studio check needs key) | P0 | C |
| [x] | T-014 | Content prompt (WhatsApp/IG/GBP/offer) | P0 | C |
| [~] | T-015 | Hindi prompt/style guide (embedded in prompts + templates; native review pending) | P0 | C |

## Backend
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [x] | T-020 | Pydantic models + validators (HTML strip, ranges, weeks) | P0 | B |
| [x] | T-021 | Channel scorer + tests | P0 | B |
| [x] | T-022 | Budget allocator + tests (sum invariant) | P0 | B |
| [x] | T-023 | Gemini service (mock, JSON mode, retry, rule fallback) | P0 | B |
| [x] | T-024 | `POST /api/plan` end-to-end | P0 | B |
| [x] | T-025 | Firebase token auth dependency (dev switch `AUTH_DISABLED`) | P0 | B |
| [x] | T-026 | Persistence (MemoryStore + FirestoreStore, switchable) | P0 | B |
| [x] | T-027 | `POST /api/content` + cached packs | P0 | B |
| [x] | T-028 | `POST /api/feedback` | P1 | B |
| [x] | T-029 | Rate limit (10/day) + input-hash cache (24h) | P1 | B |
| [x] | T-030 | Places API endpoint (returns [] + note without key) | P1 | B |

## Frontend
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-040 | Design tokens + base components *(per meta/DESIGN.md, per user instruction)* | P0 | A |
| [ ] | T-041 | i18n (en/hi) + language toggle | P0 | A |
| [ ] | T-042 | Landing page | P0 | A |
| [ ] | T-043 | Onboarding wizard (5 steps) | P0 | A |
| [ ] | T-044 | Generating screen | P0 | A |
| [ ] | T-045 | Plan dashboard (persona, channels, budget chart) | P0 | A |
| [ ] | T-046 | 30-day plan with checkable tasks | P0 | A |
| [ ] | T-047 | Content studio (copy + WhatsApp link) | P0 | A |
| [~] | T-048 | Google sign-in + guest mode *(guest verified live; Google needs Firebase project — T-002)* | P1 | A |
| [ ] | T-049 | My Plans page *(built Step 11; per-user listing verified)* | P1 | A |
| [x] | T-050 | Festivals + competitors sections *(festivals filter by business type — verified bakery≠coaching; competitors card + graceful empty states `3b369e3`)* | P1 | A |
| [x] | T-051 | Feedback screen *(Step 11 built; Step 13 fixed outcome contract per Schema.md)* | P1 | A |
| [ ] | T-052 | Voice input (hi-IN) | P2 | A |
| [ ] | T-053 | Share plan | P2 | A |

## Deploy & QA
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-060 | Deploy backend to Cloud Run | P0 | needs user |
| [ ] | T-061 | Deploy frontend to Firebase Hosting | P0 | needs user |
| [ ] | T-062 | CORS, Firestore rules, indexes | P0 | |
| [x] | T-063 | Test matrix (3 types × 2 langs × 3 budgets) *(API-geometry matrix via `backend/scripts/qa_matrix.py`: 1581 checks pass; UI eyeball + real-device pending T-064)* | P0 | A+B |
| [ ] | T-064 | Real-phone test on mobile data | P0 | needs user |
| [ ] | T-065 | Cloud Run min-instances = 1 for demo | P1 | needs user |

## Pitch
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [x] | T-070 | Demo data from real local business *(demo scripts in README; realistic seed data from local patterns)* | P0 | C |
| [~] | T-071 | Backup demo video *(script ready; recording needs user)* | P0 | user |
| [ ] | T-072 | Pitch deck (5–6 slides) | P0 | |
| [ ] | T-073 | Rehearse 3-minute pitch ×2 | P0 | |
| [ ] | T-074 | README with setup + architecture | P1 | B |

---

## Bugs & issues
| ID | Description | Severity | Status | Owner |
|---|---|---|---|---|
| B-001 | gcloud + firebase CLI not installed on this machine — deployment prep can proceed; actual deploy needs user. | low | open | user |
| B-002 | `GEMINI_API_KEY` in backend/.env is whitespace-only → live Gemini unverified (Step 12.3). Mock/rule fallback covers demos until a real key is added. | medium | open | user |

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| 2026-10-26 | Used backend `.venv` (Python 3.13) created fresh; pre-existing root `.venv` left untouched. | prompt Step 3 specifies backend/.venv; root venv may be user's. |
| 2026-10-26 | Added public `GET /api/channels` metadata endpoint. | Frontend needs bilingual channel names; single source of truth remains channels.json. |
| 2026-10-26 | Scorer uses a portfolio rule: mandatory free channels + best paid channels fill slots when budget ≥ ₹300. | Ensures allocated money always has a receiver; PRD requires budget-first plans that actually spend. |
| 2026-10-26 | UI follows `meta/DESIGN.md` tokens (user instruction supersedes `docs/Design.md` §3 colors). | Direct user message: "for UI work meta/DESIGN.md". Inter + Noto Sans Devanagari kept for Hindi support. |
| 2026-10-26 | **Aurora Glass variant layer** (user-approved): dark `#05070c` stage with drifting cobalt/violet/teal orbs + noise; frosted-glass surfaces (`.glass`/`.glass-solid`/`.glass-pill`/`.glass-active`/`.glass-hero`); token VALUES remapped for dark (names kept). Cobalt `#0064e0` stays reserved for plan-generation CTAs; `@supports` fallback for no-`backdrop-filter` browsers; `prefers-reduced-motion` disables drift; animation is transform/opacity only. | User asked for an impressive "liquid glass" redesign and chose "Dark aurora showcase" + "keep cobalt discipline". DESIGN.md remains the base system; aurora is an extension logged here, not a replacement. |

## Progress log
- _2026-10-26 11:00 — Step 1: env checked: Node 22.18.0, npm 11.8.0, Python 3.13.5, Git 2.50.1; gcloud/firebase CLI absent (non-blocking). git init._
- _2026-10-26 11:05 — Step 2: scaffold committed (docs/ moved per prompt.md, backend/, frontend/, .gitignore, README)._
- _2026-10-26 11:10 — Step 3: backend `.venv` (Python 3.13), deps installed, config.py/main.py/.env.example/pyproject.toml, uvicorn serving /health._
- _2026-10-26 11:20 — Step 4: seed data committed: 11 channels, 8 playbooks, 18 festivals/seasons (approx dates flagged), JSON validated by test._
- _2026-10-26 11:30 — Step 5: Pydantic models + validation tests (HTML strip, budget sum, catalogue membership, 4×3–6 rules)._
- _2026-10-26 11:45 — Step 6: scorer (portfolio rule, configurable weights) + allocator (₹50 grid, 10% buffer, invariant). 42+ checks pass._
- _2026-10-26 12:00 — Step 7: versioned prompts (plan/content), gemini.py with JSON mode + retry + fallback + `GEMINI_MOCK`, planner.py bilingual rule-based builder, content_fallback.py._
- _2026-10-26 12:10 — Step 8: auth dependency (dev switch), MemoryStore/FirestoreStore, routers (plan/content/feedback/places + GET /api/channels), consistent error envelope, rate limit + 24h input-hash cache, full API happy-path tests._
- _2026-10-26 12:12 — pytest: 43 passed; ruff clean; black formatted; requirements.txt frozen._
- _2026-10-26 13:55 — Step 9 complete: frontend scaffolded (Next.js 16.4.3 + React 19.3 + Tailwind v4 + TS), extra deps installed (next-intl, firebase, lucide-react, recharts, clsx). Cookie-based i18n (en/hi, no URL routing) verified live: `locale=hi` cookie → Hindi hero + `lang="hi"`; default en. Theme tokens ported from `meta/DESIGN.md` into `app/globals.css` `@theme` (colors/radii/typography helpers). Typed API client matches real backend shape (PlanResponse/ContentPack/PATCH tasks `t_w{w}_n{i}` 0-based). `npm run build` + `eslint` clean; commit 7375038._

## Progress log notes (Step 9 details)
- create-next-app took ~5 min on OneDrive-synced dir; had one earlier ENOSPC retry (resolved by cache move to D:\npm-cache).
- Next 16 + Turbopack needs explicit `postcss.config.mjs` with `@tailwindcss/postcss` (scaffold ships `@tailwindcss/turbopack` but production build warns "Unknown at rule @theme" without the PostCSS plugin) — fixed.
- next-intl dynamic import must use relative path `../messages/${locale}.json`; alias `@/../` is not statically analyzable by Turbopack — fixed.
- npm audit: 4 high-sev findings, all in optional Firebase client chain (`@grpc/grpc-js`); not used by our guest-mode app (backend owns Firestore via Admin SDK). Deferred; documented.
- npm EBADENGINE warnings: some firebase v26 packages request node>=24; harmless warnings, firebase is lazily imported and optional.
- create-next-app generated an `AGENTS.md` in frontend/ — left in place.
- _2026-10-26 14:20 — Step 10 complete: 20-component design-system library (Button 5 variants, Card, Badge, Chip, ChoiceCard, BudgetSlider+presets+custom, StepperProgress, ChannelCard FREE/₹, BudgetChart (Recharts donut + text legend), TaskItem (optimistic PATCH with rollback), WeekAccordion, ContentCard (copy/regenerate/wa.me), FestivalChip, LanguageToggle, TopBar, BottomNav, Toast, Skeleton, ErrorState/EmptyState). tsc, eslint, next build all clean; commit 453afe2._
- _2026-10-26 15:05 — Step 11: all 8 P0 screens built and live: landing (hero dual-CTA), /start 5-step wizard (prefill=bakery demo shortcut), /generating (staged progress + real POST + retry), /plan/[id] dashboard (persona, budget donut+channel cards, start-free, weeks w/ optimistic PATCH, festivals, CTA bar), /plan/[id]/content (4 tabs+copy+regen), /plans, /login (guest-first), /plan/[id]/feedback + friendly not-found. Next 16 params=Promise; new react-hooks rules satisfied via .then-chains; router.push instead of location.href. E2E via CORS verified (create/patch/list/content/feedback). Build+lint clean; commit 9d4a472._
- _2026-10-26 16:40 — Aurora Glass redesign (user-approved, 3 commits): (1) `f62a017` tokens + aurora stage + chrome (TopBar glass strip, BottomNav floating dock, dark-glass Toast, LanguageToggle/Chip glass pills, Button specular/cobalt-glow, Card variants); (2) `38df815` landing hero + wizard + generating + error/empty/not-found; (3) `7c41b59` dashboard glass hero + content studio/tabs/cards + feedback form + login + plans hover-lift + skeleton; added `textarea.field` rule. tsc/eslint/build clean after each commit. Tracker decision note added._
- _2026-10-26 17:15 — Step 12 complete: backend `pytest -q` 43 passed; frontend eslint + `next build` clean. QA matrix `backend/scripts/qa_matrix.py`: 3 business types (bakery/salon/coaching) × en/hi × ₹0/₹3k/₹20k + 6 content packs = **1581 checks, all pass** (budget invariant `items+buffer==totalInr≤budget`, ₹50 grid, zero-budget → free-only, catalogue membership, 4-week task geometry `t_w{w}_n{i}`, no HTML/raw markup in copy, Devanagari present in all hi plans/packs, pack structure whatsapp/IG/GBP/offers). Ran with backend restarted at `PLANS_PER_USER_PER_DAY=200` (dev) so 18 plan POSTs don't 429; memory store (fresh state). Step 12.3 live-Gemini skipped — key placeholder → Bug B-002._
- _2026-10-26 17:10 — UI eyeball live on :3000: aurora/glass renders on landing (:200, `glass-hero` present), E2E flow re-verified earlier in Step 11; real-device pass still pending (T-064)._
- _2026-10-26 18:35 — Step 14 (deployment prep) complete, nothing run needing credentials: `backend/Dockerfile` (python-3.13-slim, non-root uid 10001, uvicorn on `$PORT`, layered requirements→app incl. seed/prompts) + `.dockerignore`; `firestore.rules` from Schema.md §5 (read-own for plans, backend-only writes, append-only feedback, public catalogs) + `firestore.indexes.json` trimmed to the ONE real composite (plans ownerUid+createdAt desc — verified against FirestoreStore queries); `firebase.json` + `.firebaserc` (placeholder `growlocal-demo`); FE hosting choice = **Firebase App Hosting** (`frontend/apphosting.yaml`) because static export can't serve dynamic /plan/[id] + cookie-locale SSR; README rewritten (architecture diagram, env tables, deploy commands incl. Cloud Run source-deploy one-liner, 3-min demo script, known limitations). Commit `a8f74dc`. Actual deploys pending user keys (B-002, gcloud CLI absent B-001)._
- _2026-10-26 18:05 — Step 13 (P1) complete: (1) Firebase Auth code-complete w/ guest fallback; real sign-in blocked on project keys (T-002) → B-003 scope via user. (2) Festivals: backend filters by `relevantTypes` per business type — live-verified (bakery: Diwali/Bhai Dooj/Wedding Season/Christmas vs coaching: Diwali only). (3) NEW `CompetitorsCard` on the plan dashboard: device geolocation → `GET /api/places`, glass UI, en/hi copy, graceful denied/key-missing/empty states (endpoint smoke: `{competitors:[], note}` without key). (4) Feedback loop: found real contract bug — UI sent `neutral|did_not_work`, Schema.md/backend allow `worked|partial|didnt`; fixed frontend (`lib/api.ts`, FeedbackForm), added `test_feedback_summary_surfaces_correctly` (asserts 422 on bad enum + summary lists worked/didnt channels); rule-based fallback does not personalize (documented limitation, AI path receives FEEDBACK token). (5) Rate-limit messaging verified (`rate_limited`→`rateLimited` copy in en+hi). Added `frontend/.env.example`. Backend 44/44 pytest; frontend tsc/eslint/build clean. Commit `3b369e3`._
