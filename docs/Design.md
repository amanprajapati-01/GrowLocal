# Design — GrowLocal

## 1. Design principles
1. **Owner-first simplicity** — one question per screen, plain words, no marketing jargon.
2. **Budget-first clarity** — the rupee amount is always visible and prominent.
3. **Action over information** — every screen ends with something to tap, copy, or do.
4. **Mobile-first** — designed at 360px width, enhanced for desktop.
5. **Trust** — show reasoning ("why this channel") and label estimates honestly.

## 2. Brand & tone
- Friendly, encouraging, local. Speaks like a helpful neighbor who knows marketing.
- Avoid: "ROI", "funnel", "KPI" without a plain explanation.
- Hindi copy uses simple everyday words (Hinglish terms like "WhatsApp", "Instagram", "offer" are fine).

## 3. Color palette
| Token | Hex | Use |
|---|---|---|
| `primary` | `#1A73E8` | Primary buttons, links (Google-blue feel) |
| `primary-dark` | `#1557B0` | Hover/pressed |
| `accent` | `#F9A825` | Highlights, festival chips, "Free" emphasis |
| `success` | `#188038` | Free badge, completed tasks |
| `danger` | `#D93025` | Errors |
| `bg` | `#F8FAFC` | Page background |
| `surface` | `#FFFFFF` | Cards |
| `text` | `#1F2937` | Body text |
| `muted` | `#6B7280` | Secondary text |
| `border` | `#E5E7EB` | Dividers |

Contrast: all text/background pairs meet WCAG AA (4.5:1).

## 4. Typography
- Latin: **Inter** (fallback system-ui).
- Devanagari: **Noto Sans Devanagari**.
- Scale (mobile): H1 28/34 · H2 22/28 · H3 18/24 · Body 16/24 · Small 14/20 · Caption 12/16.
- Minimum body size 16px; line-height ≥ 1.5 for Hindi.

## 5. Layout & spacing
- 4px base unit; spacing scale 4 / 8 / 12 / 16 / 24 / 32 / 48.
- Mobile padding 16px; max content width 720px (plan pages), 1100px (landing).
- Cards: radius 16px, 1px border, soft shadow `0 1px 3px rgba(0,0,0,.08)`.
- Touch targets ≥ 48×48px.

## 6. Components
| Component | Notes |
|---|---|
| **Button** | Primary (filled), Secondary (outline), Ghost; full-width on mobile; loading state |
| **Choice card** | Icon + label, selected state with primary border + check |
| **Budget slider** | Large ₹ value, preset chips below |
| **Chip** | Multi-select audience tags |
| **Progress stepper** | Top bar for onboarding; staged list for generation |
| **Channel card** | Icon, name, FREE/₹ badge, budget amount, 1-line why, expected-result range, expand for details |
| **Budget chart** | Donut or stacked bar; legend lists amounts |
| **Task item** | Checkbox + task + time estimate; strikethrough when done |
| **Week accordion** | Week title, progress count (3/6) |
| **Content card** | Text block, Copy / Regenerate / Share buttons |
| **Festival chip** | Date + name + suggested offer |
| **Language toggle** | EN / हिं segmented control, always in header |
| **Toast** | "Copied!" feedback |
| **Empty/Error state** | Friendly illustration + retry action |

## 7. Key screen wireframes (text)

**Landing (mobile)**
```
[Logo]                 [EN|हिं]
Your marketing plan
in 2 minutes.
"₹3,000 budget? We'll show you exactly
 how to spend it."
[ Get my free plan ]
(3 trust bullets: Free-first · Hindi · Ready messages)
```

**Plan dashboard (mobile)**
```
₹3,000 plan · Sharma Bakery
Goal: More walk-ins
─────────────────────────
Your customers   [persona card]
─────────────────────────
Where to spend
 ◉ Google Business   FREE
 ◉ WhatsApp          FREE
 ◉ Instagram Reels   ₹1,200
 ◉ Local flyers      ₹1,500
─────────────────────────
Start free today  ▸ 3 tasks
30-day plan       ▸ Week 1…4
Festivals         ▸ Diwali…
[Generate content] [Share]
```

## 8. Iconography & imagery
- Icon set: Lucide (consistent stroke). Channel icons: WhatsApp, Instagram, Google Maps pin, Facebook group, flyer/paper, handshake (collab).
- Minimal illustrations; avoid stock-photo clutter. Business-type cards use simple icons.

## 9. Motion
- 150–250ms ease-out transitions; skeleton loaders on plan sections.
- Generation screen: animated step checklist.
- Respect `prefers-reduced-motion`.

## 10. Accessibility
- Semantic HTML, labels on all inputs, focus rings visible.
- Color never the only indicator (badges include text).
- Screen-reader labels for charts; tables/lists as fallback.
- Works at 200% zoom; supports system dark mode (P2).

## 11. Localization notes
- All strings in `messages/en.json` and `messages/hi.json`; no hardcoded text.
- Allow ~30% text expansion in layouts.
- Currency format: `₹3,000` (Indian digit grouping, e.g., `₹1,00,000`).
- Dates: `26 Oct 2026` / Hindi month names in hi locale.

## 12. Performance targets
- Largest Contentful Paint < 2.5s on 4G mid-range Android.
- Initial JS < 200KB gzipped for landing + form.
- Lazy-load charts and Maps.
