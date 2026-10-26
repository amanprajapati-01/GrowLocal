# Rule.md — Project rules for AI coding assistants and contributors

Read this file fully before writing or changing any code. Also read `PRD.md`, `TechSpecs.md`, `Schema.md`, `Design.md`, and `Appflow.md` when relevant.

## 1. Mission & scope
- Build **GrowLocal**: an AI marketing strategy advisor for local businesses (budget-first, free-first, Hindi + English).
- Build **only what is in `PRD.md` and `Implementationplan.md`**. Do not add features, pages, or dependencies that aren't listed. If something seems missing, ask or note it in `Tracker.md` under Decisions.
- P0 before P1 before P2. Never start P2 work while a P0 task is open.

## 2. Workflow
1. Pick the next unchecked task from `Tracker.md`.
2. Make a short plan (3–5 bullets) before coding.
3. Implement the smallest working version, then run it.
4. Update `Tracker.md` (status + progress log) after each completed task.
5. Commit with a clear message: `feat(plan): add budget allocator`.
- Work on one task at a time. Keep diffs small and focused.
- Do not refactor unrelated code.

## 3. Tech stack (fixed)
- Frontend: Next.js (App Router), TypeScript (strict), Tailwind CSS, `next-intl`.
- Backend: Python 3.12, FastAPI, Pydantic v2, `google-genai`, `firebase-admin`.
- DB/Auth: Firestore, Firebase Auth. Hosting: Firebase Hosting (FE), Cloud Run (BE).
- Do not swap frameworks or add heavy libraries without approval. Prefer built-ins and small, well-known packages.

## 4. Architecture rules
- **Rules decide, AI explains.** Channel selection and budget amounts are computed in code (`scorer.py`, `allocator.py`). Gemini never decides amounts or invents channels outside the catalog.
- All AI responses must be **JSON validated by Pydantic** before use. Retry once; then use the rule-based fallback plan.
- Frontend never calls Gemini directly. All AI goes through the backend.
- Keep business logic in `services/`, HTTP in `routers/`, schemas in `models/`. No logic inside route handlers beyond orchestration.

## 5. Security rules (non-negotiable)
- **Never** hardcode or commit API keys, tokens, or service-account files. Use env vars / Secret Manager. Add `.env*` to `.gitignore`.
- Verify the Firebase ID token on every protected route.
- Firestore: users access only their own data; plans are written by the backend only.
- Never render model output as raw HTML. Escape/strip it.
- Validate and bound all user input (length, ranges, enums). Budget: 0–100000.
- Rate-limit plan generation per user.

## 6. Code style
**General:** clear names, small functions (< 40 lines), early returns, no dead code, no commented-out blocks, no `TODO` without a Tracker entry.
**TypeScript:** `strict: true`, no `any`, functional components + hooks, props typed, one component per file, server components by default and `"use client"` only when needed.
**Python:** type hints everywhere, `ruff` + `black` formatting, Pydantic models for all I/O, `async` for I/O-bound routes, no bare `except`.
**Errors:** return structured errors `{ "error": { "code", "message" } }`; log details server-side, show friendly messages client-side.
**Tests:** unit tests for scorer, allocator, and schema validation are required. Budget sum invariant must be tested.

## 7. UI rules
- Follow `Design.md` tokens (colors, type, spacing). Do not invent new colors/fonts.
- **Mobile-first** (360px base). Touch targets ≥ 48px. Body text ≥ 16px.
- **All user-facing strings go in `messages/en.json` and `messages/hi.json`.** No hardcoded text in components.
- Every async view needs loading, empty, and error states.
- Currency always formatted as `₹` with Indian grouping (`₹1,00,000`).
- Accessibility: labels on inputs, visible focus, no color-only meaning.

## 8. AI / prompt rules
- Prompts live in `backend/app/prompts/` as versioned files, not inline strings.
- Always pass: business info, language, budget, scorer output, upcoming festivals, JSON schema.
- Tone: simple, friendly, no jargon. Hindi output must be natural Hindi/Hinglish, not literal translation.
- Never promise results. Expected outcomes are **ranges labeled as estimates**.
- Do not generate spammy tactics (unsolicited bulk messaging, fake reviews, misleading claims). Recommend compliant practices only (e.g., WhatsApp messages to opted-in customers).
- Do not fabricate statistics, competitor data, or sources.

## 9. Data rules
- Follow `Schema.md` exactly. Schema changes require updating `Schema.md` first, then code.
- Don't store sensitive personal data. Business info and plans only.
- Seed data (`channels.json`, `playbooks`, `festivals`) is the source of truth for recommendations; keep it reviewed and small.

## 10. Git & delivery
- Branches: `feat/<name>`, `fix/<name>`. Merge to `main` only when the app runs.
- Never commit `node_modules`, build output, or secrets.
- Keep a working `main` at all times after Hour 24 of the hackathon.
- README must contain: setup, env vars, run commands, deploy steps, architecture diagram.

## 11. When unsure
- Prefer the simplest approach that satisfies the PRD.
- If requirements conflict, priority order: **PRD.md → Schema.md → TechSpecs.md → Design.md → Appflow.md**.
- If a task would take more than ~2 hours, split it in `Tracker.md`.
- Ask before: adding dependencies, changing the schema, or changing the architecture.

## 12. Definition of done (per task)
- [ ] Works locally and matches the spec.
- [ ] Types/lint pass; relevant tests pass.
- [ ] No secrets, no console errors.
- [ ] Works on mobile viewport in English and Hindi (UI tasks).
- [ ] `Tracker.md` updated.
