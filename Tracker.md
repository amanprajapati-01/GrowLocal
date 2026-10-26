# Tracker — GrowLocal

**How to use:** update this file after every completed task. Mark `[x]` when done, `[~]` when in progress, `[!]` when blocked. Add a one-line note in the Log at the bottom.

**Legend:** P0 must · P1 nice · P2 stretch · Owner = A (Frontend) / B (Backend) / C (AI/Content) / D (Pitch/QA)

**Status snapshot:** Phase: 0 · Overall: 0% · Blockers: none · Last updated: ____

---

## Setup
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-001 | Create repo + branches | P0 | |
| [ ] | T-002 | Firebase project (Auth, Firestore, Hosting) | P0 | |
| [ ] | T-003 | Gemini API key + test call | P0 | |
| [ ] | T-004 | Scaffold Next.js + Tailwind | P0 | |
| [ ] | T-005 | Scaffold FastAPI + Dockerfile | P0 | |
| [ ] | T-006 | Add Rule.md to repo root | P0 | |
| [ ] | T-007 | Pick name + 3 demo businesses | P0 | |

## Data & prompts
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-010 | `channels.json` (10–12 channels) | P0 | |
| [ ] | T-011 | Playbooks for 8 business types | P0 | |
| [ ] | T-012 | `festivals.json` (6 months) | P1 | |
| [ ] | T-013 | Plan prompt + JSON schema validated in AI Studio | P0 | |
| [ ] | T-014 | Content prompt (WhatsApp/IG/GBP/offer) | P0 | |
| [ ] | T-015 | Hindi prompt/style guide + native review | P0 | |

## Backend
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-020 | Pydantic models | P0 | |
| [ ] | T-021 | Channel scorer + tests | P0 | |
| [ ] | T-022 | Budget allocator + tests | P0 | |
| [ ] | T-023 | Gemini service (JSON mode, retry, fallback) | P0 | |
| [ ] | T-024 | `POST /api/plan` | P0 | |
| [ ] | T-025 | Firebase token auth dependency | P0 | |
| [ ] | T-026 | Firestore persistence | P0 | |
| [ ] | T-027 | `POST /api/content` | P0 | |
| [ ] | T-028 | `POST /api/feedback` | P1 | |
| [ ] | T-029 | Rate limit + input-hash cache | P1 | |
| [ ] | T-030 | Places API endpoint | P1 | |

## Frontend
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-040 | Design tokens + base components | P0 | |
| [ ] | T-041 | i18n (en/hi) + language toggle | P0 | |
| [ ] | T-042 | Landing page | P0 | |
| [ ] | T-043 | Onboarding wizard (5 steps) | P0 | |
| [ ] | T-044 | Generating screen | P0 | |
| [ ] | T-045 | Plan dashboard (persona, channels, budget chart) | P0 | |
| [ ] | T-046 | 30-day plan with checkable tasks | P0 | |
| [ ] | T-047 | Content studio (copy + WhatsApp link) | P0 | |
| [ ] | T-048 | Google sign-in + guest mode | P1 | |
| [ ] | T-049 | My Plans page | P1 | |
| [ ] | T-050 | Festivals + competitors sections | P1 | |
| [ ] | T-051 | Feedback screen | P1 | |
| [ ] | T-052 | Voice input (hi-IN) | P2 | |
| [ ] | T-053 | Share plan | P2 | |

## Deploy & QA
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-060 | Deploy backend to Cloud Run | P0 | |
| [ ] | T-061 | Deploy frontend to Firebase Hosting | P0 | |
| [ ] | T-062 | CORS, Firestore rules, indexes | P0 | |
| [ ] | T-063 | Test matrix (3 types × 2 langs × 3 budgets) | P0 | |
| [ ] | T-064 | Real-phone test on mobile data | P0 | |
| [ ] | T-065 | Cloud Run min-instances = 1 for demo | P1 | |

## Pitch
| Status | ID | Task | Pri | Owner |
|---|---|---|---|---|
| [ ] | T-070 | Demo data from real local business | P0 | |
| [ ] | T-071 | Backup demo video | P0 | |
| [ ] | T-072 | Pitch deck (5–6 slides) | P0 | |
| [ ] | T-073 | Rehearse 3-minute pitch ×2 | P0 | |
| [ ] | T-074 | README with setup + architecture | P1 | |

---

## Bugs & issues
| ID | Description | Severity | Status | Owner |
|---|---|---|---|---|
| B-001 | | | | |

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| | | |

## Progress log
- _YYYY-MM-DD HH:MM — what changed, who._
