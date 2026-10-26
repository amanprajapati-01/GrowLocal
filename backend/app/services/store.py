"""Persistence layer: MemoryStore (dev) and FirestoreStore, selected by STORE_BACKEND.

Interface (Schema.md SS1): users, businesses, plans (+tasks, contentPacks), feedback,
plus plan input-hash cache and per-user daily plan counters.
"""

import logging
import re
from datetime import UTC, timedelta
from typing import Any, Protocol

from app.config import get_settings

logger = logging.getLogger("growlocal.store")


class Store(Protocol):
    def save_plan(self, doc: dict[str, Any]) -> None: ...
    def get_plan(self, plan_id: str) -> dict[str, Any] | None: ...
    def list_plans(self, owner_uid: str) -> list[dict[str, Any]]: ...
    def update_task(self, plan_id: str, task_id: str, done: bool) -> dict[str, Any] | None: ...
    def save_business(self, owner_uid: str, biz: dict[str, Any]) -> str: ...
    def save_content_pack(self, plan_id: str, language: str, pack: dict[str, Any]) -> None: ...
    def get_content_pack(self, plan_id: str, language: str) -> dict[str, Any] | None: ...
    def save_feedback(self, owner_uid: str, doc: dict[str, Any]) -> str: ...
    def list_feedback(self, owner_uid: str) -> list[dict[str, Any]]: ...
    def plans_today(self, owner_uid: str, day: str) -> int: ...
    def increment_plan_count(self, owner_uid: str, day: str) -> None: ...
    def get_cached_plan(
        self, owner_uid: str, input_hash: str, ttl_hours: int
    ) -> dict[str, Any] | None: ...
    def put_cached_plan(self, owner_uid: str, input_hash: str, doc: dict[str, Any]) -> None: ...


def get_store() -> Store:
    settings = get_settings()
    if settings.store_backend == "firestore":
        return _firestore_store()
    return MemoryStore.get_instance()


class MemoryStore:
    """In-memory store (dev/demo). Singleton so reloads inside a process share data."""

    _instance: "MemoryStore | None" = None

    @classmethod
    def get_instance(cls) -> "MemoryStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.plans: dict[str, dict[str, Any]] = {}
        self.businesses: dict[str, dict[str, Any]] = {}
        self.content_packs: dict[tuple[str, str], dict[str, Any]] = {}
        self.feedback: list[dict[str, Any]] = []
        self.users: dict[tuple[str, str], int] = {}
        self.cache: dict[tuple[str, str], dict[str, Any]] = {}

    def save_plan(self, doc: dict[str, Any]) -> None:
        self.plans[doc["planId"]] = doc

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        return self.plans.get(plan_id)

    def list_plans(self, owner_uid: str) -> list[dict[str, Any]]:
        docs = [d for d in self.plans.values() if d.get("ownerUid") == owner_uid]
        docs.sort(key=lambda d: d.get("createdAt", ""), reverse=True)
        return docs

    def update_task(self, plan_id: str, task_id: str, done: bool) -> dict[str, Any] | None:
        doc = self.plans.get(plan_id)
        if not doc:
            return None
        parsed = parse_task_id(task_id)
        if not parsed:
            return None
        week_no, index = parsed
        for week in doc.get("actionPlan", {}).get("weeks", []):
            if week.get("week") != week_no:
                continue
            tasks = week.get("tasks", [])
            if 0 <= index < len(tasks):
                tasks[index]["done"] = done
                return {"taskId": task_id, "week": week_no, "done": done}
        return None

    def save_business(self, owner_uid: str, biz: dict[str, Any]) -> str:
        biz_id = f"biz_{len(self.businesses) + 1:06d}"
        doc = {**biz, "ownerUid": owner_uid, "businessId": biz_id}
        self.businesses[biz_id] = doc
        return biz_id

    def save_content_pack(self, plan_id: str, language: str, pack: dict[str, Any]) -> None:
        self.content_packs[(plan_id, language)] = pack

    def get_content_pack(self, plan_id: str, language: str) -> dict[str, Any] | None:
        return self.content_packs.get((plan_id, language))

    def save_feedback(self, owner_uid: str, doc: dict[str, Any]) -> str:
        feedback_id = f"fb_{len(self.feedback) + 1:06d}"
        self.feedback.append({**doc, "ownerUid": owner_uid, "feedbackId": feedback_id})
        return feedback_id

    def list_feedback(self, owner_uid: str) -> list[dict[str, Any]]:
        return [f for f in self.feedback if f.get("ownerUid") == owner_uid]

    def plans_today(self, owner_uid: str, day: str) -> int:
        return self.users.get((owner_uid, day), 0)

    def increment_plan_count(self, owner_uid: str, day: str) -> None:
        self.users[(owner_uid, day)] = self.users.get((owner_uid, day), 0) + 1

    def get_cached_plan(
        self, owner_uid: str, input_hash: str, ttl_hours: int
    ) -> dict[str, Any] | None:
        from datetime import datetime

        entry = self.cache.get((owner_uid, input_hash))
        if not entry:
            return None
        age = datetime.now(UTC) - datetime.fromisoformat(entry["cachedAt"])
        if age > timedelta(hours=ttl_hours):
            self.cache.pop((owner_uid, input_hash), None)
            return None
        return entry["doc"]

    def put_cached_plan(self, owner_uid: str, input_hash: str, doc: dict[str, Any]) -> None:
        from datetime import datetime

        self.cache[(owner_uid, input_hash)] = {
            "doc": doc,
            "cachedAt": datetime.now(UTC).isoformat(),
        }


_firestore_store_instance: "FirestoreStore | None" = None


def task_id(week: int, index: int) -> str:
    """Stable positional task id, e.g. t_w1_n0 (matches Firestore task doc ids)."""
    return f"t_w{week}_n{index}"


def parse_task_id(task_id_str: str) -> tuple[int, int] | None:
    """Parse 't_w<n>_m<i>' into (week, index)."""
    match = re.fullmatch(r"t_w(\d)_n(\d+)", task_id_str)
    return (int(match.group(1)), int(match.group(2))) if match else None


class FirestoreStore:
    """Firestore implementation; field names follow Schema.md SS1."""

    def __init__(self) -> None:
        self.db = None

    def _client(self) -> Any:
        if self.db is None:
            from firebase_admin import firestore

            self.db = firestore.client()
        return self.db

    def save_plan(self, doc: dict[str, Any]) -> None:
        db = self._client()
        db.collection("plans").document(doc["planId"]).set(doc)
        for week in doc.get("actionPlan", {}).get("weeks", []):
            for idx, task in enumerate(week.get("tasks", [])):
                db.collection("plans").document(doc["planId"]).collection("tasks").document(
                    f"t_w{week['week']}_n{idx}"
                ).set(
                    {
                        "week": week["week"],
                        "title": task["title"],
                        "channelId": task["channelId"],
                        "done": task.get("done", False),
                    }
                )

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        snapshot = self._client().collection("plans").document(plan_id).get()
        return snapshot.to_dict() if snapshot.exists else None

    def list_plans(self, owner_uid: str) -> list[dict[str, Any]]:
        docs = (
            self._client()
            .collection("plans")
            .where("ownerUid", "==", owner_uid)
            .order_by("createdAt", direction="DESCENDING")
            .limit(50)
            .stream()
        )
        return [d.to_dict() for d in docs]

    def update_task(self, plan_id: str, task_id: str, done: bool) -> dict[str, Any] | None:
        db = self._client()
        snapshot = (
            db.collection("plans").document(plan_id).collection("tasks").document(task_id).get()
        )
        if not snapshot.exists:
            return None
        task_doc = snapshot.to_dict()
        snapshot_ref = (
            db.collection("plans").document(plan_id).collection("tasks").document(task_id)
        )
        from datetime import datetime

        snapshot_ref.update({"done": done, "doneAt": datetime.now(UTC)})
        # keep the inline actionPlan copy in sync (it is what the response reads)
        plan_doc = self.get_plan(plan_id)
        if plan_doc:
            for week in plan_doc.get("actionPlan", {}).get("weeks", []):
                if week.get("week") == task_doc.get("week"):
                    for idx, task in enumerate(week.get("tasks", [])):
                        if f"t_w{week['week']}_n{idx}" == task_id:
                            task["done"] = done
            db.collection("plans").document(plan_id).update({"actionPlan": plan_doc["actionPlan"]})
            return {"taskId": task_id, "week": task_doc.get("week"), "done": done}
        return None

    def save_business(self, owner_uid: str, biz: dict[str, Any]) -> str:
        ref = self._client().collection("businesses").document()
        ref.set({**biz, "ownerUid": owner_uid})
        return ref.id

    def save_content_pack(self, plan_id: str, language: str, pack: dict[str, Any]) -> None:
        self._client().collection("plans").document(plan_id).collection("contentPacks").document(
            language
        ).set(pack)

    def get_content_pack(self, plan_id: str, language: str) -> dict[str, Any] | None:
        snapshot = (
            self._client()
            .collection("plans")
            .document(plan_id)
            .collection("contentPacks")
            .document(language)
            .get()
        )
        return snapshot.to_dict() if snapshot.exists else None

    def save_feedback(self, owner_uid: str, doc: dict[str, Any]) -> str:
        from datetime import datetime

        ref = self._client().collection("feedback").document()
        ref.set({**doc, "ownerUid": owner_uid, "createdAt": datetime.now(UTC).isoformat()})
        return ref.id

    def list_feedback(self, owner_uid: str) -> list[dict[str, Any]]:
        docs = (
            self._client()
            .collection("feedback")
            .where("ownerUid", "==", owner_uid)
            .limit(100)
            .stream()
        )
        return [d.to_dict() for d in docs]

    def plans_today(self, owner_uid: str, day: str) -> int:
        snapshot = self._client().collection("users").document(owner_uid).get()
        data = snapshot.to_dict() or {}
        return data.get("planCountToday", 0) if data.get("lastPlanDate") == day else 0

    def increment_plan_count(self, owner_uid: str, day: str) -> None:
        from firebase_admin import firestore

        db = self._client()
        ref = db.collection("users").document(owner_uid)
        ref.set(
            {
                "planCountToday": firestore.Increment(1),
                "lastPlanDate": day,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )

    def get_cached_plan(
        self, owner_uid: str, input_hash: str, ttl_hours: int
    ) -> dict[str, Any] | None:
        snapshot = (
            self._client()
            .collection("plans")
            .where("inputHash", "==", input_hash)
            .where("ownerUid", "==", owner_uid)
            .limit(1)
            .stream()
        )
        from datetime import datetime, timedelta

        for doc in snapshot:
            data = doc.to_dict()
            created = data.get("createdAt", "")
            try:
                created_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if datetime.now(UTC) - created_at <= timedelta(hours=ttl_hours):
                    return data
            except ValueError:
                continue
        return None

    def put_cached_plan(self, owner_uid: str, input_hash: str, doc: dict[str, Any]) -> None:
        # Firestore caching piggybacks on the saved plan document's inputHash.
        return None


def _firestore_store() -> FirestoreStore:
    global _firestore_store_instance
    if _firestore_store_instance is None:
        _firestore_store_instance = FirestoreStore()
        logger.info("store backend: firestore")
    return _firestore_store_instance
