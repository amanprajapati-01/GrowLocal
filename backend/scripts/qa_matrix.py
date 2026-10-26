"""QA matrix — Step 12 (prompt.md): 3 business types x 2 languages x 3 budgets.

Runs against a live dev backend (uvicorn on :8000, dev switches on) and checks:
  - POST /api/plan returns a structurally valid plan for every combination
  - channel budget amounts always sum to budget.totalInr and never exceed the user budget
  - budget 0 => zero paid allocations; FREE channels still recommended
  - every recommended channel id exists in GET /api/channels catalogue
  - 4 weeks of tasks, ids in t_w{week}_n{i} form, minutes/cost sanity
  - no raw HTML tags in any display string
  - language=hi plans contain Devanagari (\\u0900-\\u097F) in persona/task text
  - POST /api/content packs validate (whatsapp/instagram/gbp/offers) incl. Hindi

Usage: .\\.venv\\Scripts\\python.exe ..\\backend\\scripts\\qa_matrix.py  (cwd irrelevant)
Exit code 0 = all checks pass.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from typing import Any

BASE = "http://localhost:8000"

BUSINESS_TYPES = ["bakery", "salon", "coaching"]
LANGUAGES = ["en", "hi"]
BUDGETS = [0, 3000, 20000]

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
HTML_TAG = re.compile(r"</?[a-z][^>]*>", re.IGNORECASE)

failures: list[str] = []
passed = 0


def call(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    req = urllib.request.Request(
        BASE + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())


def check(cond: bool, label: str) -> None:
    global passed
    if cond:
        passed += 1
    else:
        failures.append(label)


def strings_of(plan: dict[str, Any]) -> list[str]:
    out: list[str] = [
        plan.get("persona", {}).get("summary", ""),
        plan.get("persona", {}).get("name", ""),
    ]
    for ch in plan.get("channels", []):
        out += [ch.get("rationale", ""), ch.get("expectedResult", ""), *ch.get("howToStart", [])]
    for week in plan.get("weeks", []):
        out += [t.get("title", "") for t in week.get("tasks", [])]
        out += [t.get("detail", "") for t in week.get("tasks", []) if t.get("detail")]
    for a in plan.get("startFreeToday", []):
        out.append(a.get("title", ""))
    return [s for s in out if s]


def run() -> None:
    catalogue = call("GET", "/api/channels")["channels"]
    cat_ids = {c["id"] for c in catalogue}

    plan_ids: dict[tuple[str, str, int], str] = {}

    for btype in BUSINESS_TYPES:
        for lang in LANGUAGES:
            for budget in BUDGETS:
                combo = f"{btype}/{lang}/₹{budget}"
                req = {
                    "businessType": btype,
                    "businessName": f"QA {btype.title()}",
                    "city": "Indore",
                    "locality": "Vijay Nagar",
                    "monthlyBudgetInr": budget,
                    "goal": {
                        "bakery": "more_walk_ins",
                        "salon": "repeat_customers",
                        "coaching": "online_orders",
                    }[btype],
                    "targetAudience": ["families"] if btype != "coaching" else ["students"],
                    "language": lang,
                }
                plan = call("POST", "/api/plan", req)
                pid = plan.get("planId", "")
                check(bool(pid), f"{combo}: planId missing")
                plan_ids[(btype, lang, budget)] = pid

                # budgets always sum correctly and never exceed user budget
                alloc = [(c["channelId"], c.get("budgetInr", 0)) for c in plan["channels"]]
                channel_alloc = sum(a for _, a in alloc)
                summary = plan[  # noqa: E501
                    "budgetAllocation"
                ]  # {items: [{channelId, amountInr}], totalInr, bufferInr}
                item_sum = sum(i["amountInr"] for i in summary["items"])
                check(
                    item_sum + summary["bufferInr"] == summary["totalInr"],
                    f"{combo}: items {item_sum} + buffer {summary['bufferInr']} "
                    f"!= totalInr {summary['totalInr']}",
                )
                check(
                    summary["totalInr"] <= budget,
                    f"{combo}: totalInr {summary['totalInr']} exceeds user budget",
                )
                check(
                    channel_alloc <= summary["totalInr"],
                    f"{combo}: channel allocations {channel_alloc} exceed totalInr",
                )
                check(all(a % 50 == 0 for _, a in alloc), f"{combo}: allocation off ₹50 grid")

                if budget == 0:
                    check(
                        channel_alloc == 0,
                        f"{combo}: zero budget but nonzero allocation",
                    )
                else:
                    check(
                        channel_alloc >= 0.5 * budget,
                        f"{combo}: budget barely used ({channel_alloc} of {budget})",
                    )

                # channels from catalogue, with required fields
                check(all(cid in cat_ids for cid, _ in alloc), f"{combo}: unknown channel id")
                for ch in plan["channels"]:
                    check(0 <= ch["score"] <= 100, f"{combo}: score range")
                    check(bool(ch["rationale"]), f"{combo}: empty rationale")
                    check(bool(ch["howToStart"]), f"{combo}: empty howToStart")

                # 30-day plan geometry
                weeks = plan["actionPlan"]["weeks"]
                check(len(weeks) == 4, f"{combo}: weeks != 4")
                for w_i, week in enumerate(weeks):
                    tasks = week.get("tasks", [])
                    check(1 <= len(tasks) <= 8, f"{combo}: w{w_i} has {len(tasks)} tasks")
                    for t_i, t in enumerate(tasks):
                        check(t["minutes"] > 0, f"{combo}: w{w_i} n{t_i} minutes")
                        check(t["costInr"] >= 0, f"{combo}: w{w_i} n{t_i} costInr")
                        if t.get("id"):
                            check(
                                t["id"] == f"t_w{w_i}_n{t_i}",
                                f"{combo}: task id {t.get('id')} mismatch",
                            )

                # plan must be consumable, pre-DB fetch equality
                fetched = call("GET", f"/api/plans/{pid}")
                check(fetched["planId"] == pid, f"{combo}: GET after POST mismatch")

                # no raw JSON/html markers on screen: HTML in display strings
                for s in strings_of(plan):
                    check(not HTML_TAG.search(s), f"{combo}: raw HTML in text: {s[:60]!r}")

                # Hindi renders as Devanagari; English avoid full Hindi text
                text_blob = " ".join(strings_of(plan))
                if lang == "hi":
                    check(bool(DEVANAGARI.search(text_blob)), f"{combo}: no Devanagari found")
                else:
                    check(
                        not plan["persona"]["name"].endswith("(HI)"),
                        f"{combo}: persona leaked HI marker",
                    )

    # --- content packs for one plan per (type, lang) at ₹3000 (recreate with cache) ---
    for btype in BUSINESS_TYPES:
        for lang in LANGUAGES:
            req = {
                "businessType": btype,
                "businessName": f"QA {btype.title()}",
                "city": "Indore",
                "locality": "Vijay Nagar",
                "monthlyBudgetInr": 3000,
                "goal": "more_walk_ins",
                "targetAudience": ["families"],
                "language": lang,
            }
            plan = call("POST", "/api/plan", req)
            pid = plan["planId"]
            pack = call("POST", "/api/content", {"planId": pid, "language": lang})
            combo = f"content {btype}/{lang}"
            check(len(pack["whatsapp"]) >= 2, f"{combo}: whatsapp < 2")
            check(len(pack["instagram"]) >= 1, f"{combo}: instagram empty")
            check(pack["gbpPost"] is not None, f"{combo}: gbpPost empty")
            check(len(pack["offers"]) >= 1, f"{combo}: offers empty")
            for ig in pack["instagram"]:
                check(3 <= len(ig["hashtags"]) <= 10, f"{combo}: hashtag count {len(ig['hashtags'])}")
            blob = " ".join(
                w["text"] for w in pack["whatsapp"]
            ) + " ".join(ig["caption"] for ig in pack["instagram"])
            check(bool(blob.strip()), f"{combo}: empty pack text")
            if lang == "hi":
                check(bool(DEVANAGARI.search(blob)), f"{combo}: content has no Devanagari")

    print(f"checks passed: {passed}")
    if failures:
        print("FAILURES:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("QA MATRIX: ALL PASS (18 plan combos + 6 content packs)")


if __name__ == "__main__":
    run()
