# Appflow — GrowLocal

## 1. Screen inventory
| # | Screen | Route | Purpose |
|---|---|---|---|
| S1 | Landing | `/` | Value prop, language toggle, "Get my plan" CTA |
| S2 | Sign in (optional) | `/login` | Google sign-in or "Continue as guest" |
| S3 | Onboarding wizard | `/start` | 5-step form |
| S4 | Generating | `/generating` | Staged progress |
| S5 | Plan dashboard | `/plan/[id]` | Persona, channels, budget, 30-day plan |
| S6 | Content studio | `/plan/[id]/content` | Generated WhatsApp/IG/GBP/offer content |
| S7 | My plans | `/plans` | Saved plans list |
| S8 | Feedback | `/plan/[id]/feedback` | What worked / didn't |

## 2. Main user flow
```
Landing ──► (Sign in / Guest) ──► Onboarding (5 steps) ──► Generating
                                                              │
                                                              ▼
                                                        Plan dashboard
                                          ┌───────────────┼───────────────┐
                                          ▼               ▼               ▼
                                   Content studio    Mark tasks done   Share / Save
                                                              │
                                                              ▼
                                                         Feedback ──► Next plan (improved)
```

## 3. Onboarding steps (S3)
1. **Business type** — tappable cards: Kirana, Bakery/Café, Restaurant, Salon/Beauty, Coaching/Education, Clinic, Clothing/Retail, Other (free text).
2. **Location** — city + locality (autocomplete; "use my location" optional).
3. **Monthly budget** — slider with presets (₹0, ₹1,000, ₹3,000, ₹5,000, ₹10,000+) and custom input.
4. **Main goal** — more walk-ins / more online or phone orders / more repeat customers / brand awareness.
5. **Target customers** — chips (students, families, working professionals, women, seniors, tourists…) + optional free-text.

Rules: one question per screen on mobile; back button preserves answers; voice input mic on text fields (P2); progress bar at top.

## 4. Generation flow (S4)
States: `queued → analyzing audience → selecting channels → allocating budget → writing plan → done`.
- On success → redirect to S5.
- On failure → friendly message + "Try again" + fallback plan from rules if available.

## 5. Plan dashboard sections (S5), in order
1. **Summary header** — "₹3,000 plan for Sharma Bakery · Goal: more walk-ins".
2. **Your customers** — persona card (who, where they are, what they respond to).
3. **Where to spend (budget split)** — donut/bar + per-channel cards (free badge, amount, why, expected result range).
4. **Start free today** — top 3 zero-cost actions.
5. **30-day plan** — Week 1–4 accordion with checkable tasks.
6. **Upcoming festivals/seasons** — dates + suggested offers.
7. **Nearby competitors** (P1) — small list with rating gaps.
8. **CTA bar** — "Generate content", "Share plan", "Give feedback".

## 6. Content studio flow (S6)
- Tabs: WhatsApp · Instagram · Google Business post · Offer ideas.
- Each item: text, regenerate button, copy button, "Open in WhatsApp" deep link (`https://wa.me/?text=`).
- Language toggle regenerates in the other language.

## 7. Feedback loop (S8)
- After 2+ weeks (or manually): for each channel → 👍 worked / 😐 partial / 👎 didn't + optional note.
- Submit → "Create next month's plan" pre-filled with learnings.

## 8. Edge cases & states
| Case | Behavior |
|---|---|
| Budget = ₹0 | Free-channels-only plan, banner "Great plans don't need a budget" |
| Unknown business type | Falls back to "Other" prompt asking for a one-line description |
| Gemini timeout/fail | Retry once, then rule-based fallback plan with notice |
| Offline | Show cached last plan if available; disable generation |
| Hindi selected | All UI + generated text in Hindi; numbers in standard digits and ₹ |
| Guest user | Plan stored locally/anonymous; prompt to sign in to save |
| Rate limit hit | Friendly message with reset time |

## 9. Navigation
- Top bar: logo, language toggle (EN/हिं), profile/sign-in.
- Bottom nav on mobile (signed-in): Home · My Plans · New Plan.
- Deep links to `/plan/[id]` work for owner only (shareable read-only link is P2).

## 10. Demo flow (3 minutes)
1. Landing → switch to Hindi (10s).
2. Fill form for a real Kanpur business (40s).
3. Watch generation → plan dashboard; walk through budget split and "Start free today" (60s).
4. Generate WhatsApp + Instagram content; copy and open WhatsApp (40s).
5. Show feedback loop concept and festival awareness (30s).
