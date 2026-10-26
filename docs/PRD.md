# PRD — GrowLocal (working name)
**AI marketing strategy advisor for local businesses** · Google Hackfest · Track: Digital Marketing

---

## 1. Problem
Local businesses (kirana stores, salons, bakeries, restaurants, coaching centers, clinics) struggle to reach the right customers on a small marketing budget. They lack marketing expertise, can't afford agencies, and generic online advice doesn't fit their business type, city, or budget.

## 2. Vision
Give any local shop owner a clear answer to: **"I have ₹X. Who should I target, where, and exactly what do I do this month?"** — in their own language, in under 2 minutes, for free.

## 3. Target users
| Persona | Description | Needs |
|---|---|---|
| **Primary: Shop owner** | 25–55, runs a small local business, phone-first, may prefer Hindi/Hinglish, limited tech skill | Simple input, plain-language plan, ready-to-send content |
| **Secondary: Marketing helper** | Family member/employee handling promotion | Copyable content, task checklist |
| **Tertiary: MSME program mentors** | Incubators, local business associations | Shareable plans for many businesses |

## 4. Goals & non-goals
**Goals (hackathon MVP)**
- G1. Generate a personalized, budget-aware marketing strategy from a short form.
- G2. Recommend and rank channels with explainable reasoning.
- G3. Produce a 30-day week-by-week action plan.
- G4. Generate ready-to-use content (WhatsApp, Instagram, Google Business post, offer idea).
- G5. Support English + Hindi.

**Non-goals (MVP)**
- Running or buying ads on the user's behalf.
- Posting directly to social platforms.
- Payments, subscriptions, multi-user team accounts.
- Real campaign analytics integrations (feedback is manual in MVP).

## 5. Key features & priority
| ID | Feature | Priority |
|---|---|---|
| F1 | Onboarding form (business type, locality, budget, goal, audience) | P0 |
| F2 | Audience persona generation (Gemini) | P0 |
| F3 | Rule-based channel scoring | P0 |
| F4 | Budget allocation, free channels first | P0 |
| F5 | 30-day action plan | P0 |
| F6 | One-click content generation | P0 |
| F7 | Hindi / English toggle | P0 |
| F8 | Google sign-in + saved plans | P1 |
| F9 | Places API competitor snapshot | P1 |
| F10 | Festival/season awareness (curated calendar + Search grounding) | P1 |
| F11 | Expected-result ranges per channel | P1 |
| F12 | Feedback loop ("what worked") feeding next plan | P1 |
| F13 | Voice input for the form | P2 |
| F14 | Share plan as link / PDF / WhatsApp message | P2 |

## 6. User stories
- As a bakery owner with ₹3,000/month, I want to know exactly how to split my budget so I don't waste money.
- As a salon owner, I want a ready-to-send WhatsApp message for my regulars so I don't have to write it.
- As a non-English speaker, I want the whole plan in Hindi so I can understand and act on it.
- As an owner, I want to see which free actions to do first so I can start today at zero cost.
- As a returning user, I want to tell the app what worked so next month's plan improves.

## 7. Functional requirements (summary)
1. Form validates inputs; budget range ₹0–₹1,00,000/month.
2. Plan generation completes in ≤ 20s (p95) with a visible progress state.
3. Output is structured JSON validated against a schema (see Schema.md) before rendering.
4. Channel recommendations must come from the rule-based scorer; Gemini explains and personalizes but does not invent channels outside the catalog.
5. Budget allocations must sum to ≤ the user's budget (enforced in code, not by the model).
6. Every content item is copyable with one tap.
7. UI language switch applies to both interface and generated output.

## 8. Success metrics
**Hackathon demo:** full plan generated live for a real local business in < 30s; 3 distinct business types tested; judges can understand the value in 60 seconds.
**Post-launch (aspirational):** plan completion rate, % of plans with ≥ 1 task checked, return usage after 30 days, self-reported results.

## 9. Differentiators
- Budget-first ("You have ₹3,000 — here is exactly how to spend it").
- Free-first strategy (Google Business Profile + WhatsApp before paid ads).
- Local language + simple UX for non-technical owners.
- Explainable, rule-backed recommendations plus AI personalization.
- Festival and seasonal awareness.

## 10. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Generic/hallucinated advice | Rule-based channel catalog, playbooks in prompt/RAG, JSON schema validation |
| Slow generation | Split calls (persona → plan → content lazily), streaming/progress UI, Flash-class model |
| Hindi quality | Test with native speakers, prompt-level style guide, fallback to English |
| API quota/cost | Cache plans, limit regenerations, use free tiers |
| Places/Trends API setup delays | Treat as P1; demo works without them |
| Unrealistic result estimates | Show ranges + "estimates" label, never promise outcomes |

## 11. Assumptions
- Users have a smartphone and internet.
- Gemini API and Firebase free tiers are enough for the demo.
- Owners can answer 5–6 simple questions.

## 12. Open questions
- Final product name and branding?
- Which 3 business types for the demo?
- Hindi only, or Hinglish toggle too?
