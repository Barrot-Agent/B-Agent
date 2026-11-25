"""Portable, conflict-preserving project state for long-horizon Barrot work.

Uses AutonomousTaskStore for atomic local persistence. Cross-workspace transfer is
explicit: export a hash-verified JSON bundle, move it through an authorized channel,
then reconcile it. No network sync, credentials, or silent conflict resolution.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .autonomous_state import AutonomousTaskStore

SCHEMA = "barrot.project-state.v1"
TASK_ID = "barrot_project_state_ledger"
MAX_RECORDS = 5000
MAX_BUNDLE_BYTES = 5 * 1024 * 1024
RECORD_TYPES = {
    "objective", "priority", "constraint", "decision", "architecture", "dependency",
    "task", "blocker", "evidence", "rejected_approach", "question", "lesson",
    "forecast", "outcome", "capability", "mission",
}
STATUSES = {"active", "hypothesis", "unverified", "open", "blocked", "complete", "rejected"}
CONFLICT_STATUSES = {"unresolved", "resolved", "superseded"}
HEX = set("0123456789abcdef")


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    raw = value.strip()
    try:
        parsed = datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
    except ValueError as exc:
        raise ValueError(f"{field} must be a timezone-aware ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in HEX for c in value.lower()):
        raise ValueError(f"{field} must be a SHA-256 hex digest")
    return value.lower()


def _strings(value: Any, field: str, *, hashes: bool = False) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    items = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field} entries must be non-empty strings")
        item = _digest(item, field) if hashes else item.strip()
        if item not in items:
            items.append(item)
    return sorted(items)


def _record(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValueError("project-state record must be an object")
    kind, key, status = raw.get("record_type"), raw.get("key"), raw.get("status", "active")
    if not isinstance(kind, str) or kind not in RECORD_TYPES:
        raise ValueError("unsupported project-state record_type")
    if not isinstance(key, str) or not key.strip() or len(key.strip()) > 256:
        raise ValueError("record key must be 1-256 characters")
    if not isinstance(status, str) or status not in STATUSES:
        raise ValueError("unsupported project-state record status")
    provenance = raw.get("provenance")
    if not isinstance(provenance, Mapping):
        raise ValueError("record provenance is required")
    source_type, source_ref = provenance.get("source_type"), provenance.get("source_ref")
    if not isinstance(source_type, str) or not source_type.strip() or not isinstance(source_ref, str) or not source_ref.strip():
        raise ValueError("provenance.source_type and provenance.source_ref are required")
    source_hash = provenance.get("source_sha256")
    if source_hash is not None:
        source_hash = _digest(source_hash, "provenance.source_sha256")
    confidence = raw.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")
    value = json.loads(_json(raw.get("value")))
    if kind == "task":
        if not isinstance(value, dict) or type(value.get("priority", 100)) is not int or value.get("priority", 100) < 1:
            raise ValueError("task records require an object value and positive integer priority")
    stale_after = raw.get("stale_after_seconds")
    if stale_after is not None and (type(stale_after) is not int or stale_after < 1):
        raise ValueError("stale_after_seconds must be a positive integer")
    valid_until = raw.get("valid_until_utc")
    normalized = {
        "record_type": kind,
        "key": key.strip(),
        "value": value,
        "status": status,
        "observed_at_utc": _timestamp(raw.get("observed_at_utc"), "observed_at_utc"),
        "recorded_at_utc": _timestamp(raw.get("recorded_at_utc", _now()), "recorded_at_utc"),
        "confidence": float(confidence),
        "provenance": {"source_type": source_type.strip(), "source_ref": source_ref.strip(), "source_sha256": source_hash},
        "supersedes": _strings(raw.get("supersedes", []), "supersedes", hashes=True),
        "depends_on": _strings(raw.get("depends_on", []), "depends_on"),
        "stale_after_seconds": stale_after,
        "valid_until_utc": _timestamp(valid_until, "valid_until_utc") if valid_until is not None else None,
    }
    if kind == "task" and key.strip() in normalized["depends_on"]:
        raise ValueError("a task cannot depend on itself")
    calculated = _hash(normalized)
    if raw.get("record_id") is not None and _digest(raw["record_id"], "record_id") != calculated:
        raise ValueError("record_id does not match canonical record content")
    normalized["record_id"] = calculated
    return normalized


def _validate_conflict_history(records: list[dict[str, Any]], history: Any, conflicts: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(history, list) or not isinstance(conflicts, list):
        raise ValueError("project-state conflict records must be lists")
    by_id = {item["record_id"]: item for item in records}
    normalized = []
    for raw in history:
        if not isinstance(raw, Mapping):
            raise ValueError("project-state conflict history entry must be an object")
        kind, key, status = raw.get("record_type"), raw.get("key"), raw.get("status")
        ids = _strings(raw.get("record_ids"), "conflict.record_ids", hashes=True)
        if not isinstance(kind, str) or kind not in RECORD_TYPES or not isinstance(key, str) or not key.strip():
            raise ValueError("project-state conflict identity is invalid")
        if not isinstance(status, str) or status not in CONFLICT_STATUSES or len(ids) < 2 or any(rid not in by_id for rid in ids):
            raise ValueError("project-state conflict references are invalid")
        if any(by_id[rid]["record_type"] != kind or by_id[rid]["key"] != key for rid in ids):
            raise ValueError("project-state conflict references a different logical record")
        cid = _hash({"record_type": kind, "key": key, "record_ids": ids})
        if _digest(raw.get("conflict_id"), "conflict_id") != cid:
            raise ValueError("project-state conflict id is invalid")
        item = dict(raw)
        item["record_ids"] = ids
        item["created_at_utc"] = _timestamp(raw.get("created_at_utc"), "conflict.created_at_utc")
        if status == "resolved":
            resolution = _digest(raw.get("resolution_record_id"), "resolution_record_id")
            if resolution not in by_id or not set(ids).issubset(by_id[resolution]["supersedes"]):
                raise ValueError("conflict resolution lacks a matching supersession record")
            item["resolution_record_id"] = resolution
            item["resolved_at_utc"] = _timestamp(raw.get("resolved_at_utc"), "conflict.resolved_at_utc")
        elif status == "superseded":
            item["superseded_by_conflict_id"] = _digest(raw.get("superseded_by_conflict_id"), "superseded_by_conflict_id")
            item["resolved_at_utc"] = _timestamp(raw.get("resolved_at_utc"), "conflict.resolved_at_utc")
        elif raw.get("resolution_record_id") is not None or raw.get("resolved_at_utc") is not None or raw.get("superseded_by_conflict_id") is not None:
            raise ValueError("unresolved conflict cannot contain resolution metadata")
        normalized.append(item)
    if len({item["conflict_id"] for item in normalized}) != len(normalized):
        raise ValueError("project-state conflict history contains duplicate ids")
    unresolved = [item for item in normalized if item["status"] == "unresolved"]
    current_ids = []
    for raw in conflicts:
        if not isinstance(raw, Mapping):
            raise ValueError("current project-state conflict must be an object")
        current_ids.append(_digest(raw.get("conflict_id"), "conflict_id"))
    if sorted(current_ids) != sorted(item["conflict_id"] for item in unresolved):
        raise ValueError("project-state unresolved conflict index is inconsistent")
    history_ids = {item["conflict_id"] for item in normalized}
    if any(item.get("superseded_by_conflict_id") not in history_ids for item in normalized if item["status"] == "superseded"):
        raise ValueError("superseded conflict references a missing successor")
    return normalized, unresolved


def _revision_payload(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "project_id": state["project_id"],
        "parent_revisions": sorted(set(state.get("parent_revisions", []))),
        "records": sorted(state.get("records", []), key=lambda item: item["record_id"]),
        "conflicts": sorted(state.get("conflicts", []), key=lambda item: item["conflict_id"]),
        "conflict_history": sorted(state.get("conflict_history", []), key=lambda item: item["conflict_id"]),
    }


def _revision(state: Mapping[str, Any]) -> str:
    return _hash(_revision_payload(state))


class ProjectStateLedger:
    """Versioned project ledger with explicit export/import and no silent overwrites."""

    def __init__(self, workspace: str | Path, project_id: str = "barrot") -> None:
        if not isinstance(project_id, str) or not project_id.strip() or len(project_id) > 128:
            raise ValueError("project_id must be 1-128 characters")
        self.project_id = project_id.strip()
        self.store = AutonomousTaskStore(workspace)

    def _empty(self) -> dict[str, Any]:
        state = {
            "project_schema": SCHEMA, "project_id": self.project_id, "parent_revisions": [],
            "records": [], "conflicts": [], "conflict_history": [], "history": [],
            "history_archive_receipts": [],
        }
        state["revision"] = _revision(state)
        return state

    def load(self) -> dict[str, Any]:
        state = self.store.load(TASK_ID)
        if state is None:
            return self._empty()
        if state.get("project_schema") != SCHEMA or state.get("project_id") != self.project_id:
            raise ValueError("project-state schema or identity mismatch")
        records = [_record(item) for item in state.get("records", [])]
        if records != state.get("records") or len(records) > MAX_RECORDS:
            raise ValueError("stored project-state records are non-canonical or exceed the limit")
        by_id = {item["record_id"]: item for item in records}
        if len(by_id) != len(records):
            raise ValueError("stored project-state contains duplicate record ids")
        for item in records:
            if not set(item["supersedes"]).issubset(by_id):
                raise ValueError("stored project-state has a missing supersedes reference")
            if any(by_id[target]["record_type"] != item["record_type"] or by_id[target]["key"] != item["key"] for target in item["supersedes"]):
                raise ValueError("stored project-state supersedes a different logical record")
        history, conflicts = _validate_conflict_history(records, state.get("conflict_history", []), state.get("conflicts", []))
        if history != state.get("conflict_history") or conflicts != state.get("conflicts"):
            raise ValueError("stored project-state conflict history is non-canonical")
        parents = _strings(state.get("parent_revisions", []), "parent_revisions", hashes=True)
        if parents != state.get("parent_revisions", []):
            raise ValueError("stored project-state lineage is non-canonical")
        if state.get("revision") != _revision(state):
            raise ValueError("stored project-state revision hash mismatch")
        return state

    def _history(self, state: dict[str, Any], action: str, detail: Mapping[str, Any]) -> None:
        event = {"action": action, "detail": json.loads(_json(detail)), "at_utc": _now()}
        event["event_id"] = _hash(event)
        state.setdefault("history", []).append(event)

    def _refresh_conflicts(self, state: dict[str, Any]) -> None:
        records = state["records"]
        superseded = {rid for item in records for rid in item["supersedes"]}
        active = [item for item in records if item["record_id"] not in superseded and item["status"] != "rejected"]
        groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for item in active:
            groups.setdefault((item["record_type"], item["key"]), []).append(item)
        history = {item["conflict_id"]: item for item in state.get("conflict_history", [])}
        current = []
        for (kind, key), candidates in groups.items():
            values = {_hash({"value": item["value"], "status": item["status"]}) for item in candidates}
            if len(values) < 2:
                continue
            ids = sorted(item["record_id"] for item in candidates)
            cid = _hash({"record_type": kind, "key": key, "record_ids": ids})
            conflict = history.get(cid)
            if conflict is None:
                conflict = {"conflict_id": cid, "record_type": kind, "key": key, "record_ids": ids,
                            "status": "unresolved", "created_at_utc": _now(), "resolved_at_utc": None,
                            "resolution_record_id": None}
                state.setdefault("conflict_history", []).append(conflict)
                history[cid] = conflict
            if conflict["status"] == "unresolved":
                current.append(conflict)
        current_by_key = {(item["record_type"], item["key"]): item for item in current}
        for conflict in state.get("conflict_history", []):
            if conflict["status"] != "unresolved" or any(item["conflict_id"] == conflict["conflict_id"] for item in current):
                continue
            same_key = [item for item in records if item["record_type"] == conflict["record_type"] and item["key"] == conflict["key"]]
            resolution = next((item for item in reversed(same_key) if set(conflict["record_ids"]).issubset(item["supersedes"])), None)
            expanded = current_by_key.get((conflict["record_type"], conflict["key"]))
            if resolution is not None:
                conflict.update(status="resolved", resolved_at_utc=_now(), resolution_record_id=resolution["record_id"])
            elif expanded is not None and set(conflict["record_ids"]).issubset(expanded["record_ids"]):
                conflict.update(status="superseded", resolved_at_utc=_now(), superseded_by_conflict_id=expanded["conflict_id"])
        state["conflicts"] = current

    def add_record(self, raw: Mapping[str, Any], *, expected_revision: str | None = None) -> dict[str, Any]:
        state = self.load()
        if expected_revision is not None and expected_revision != state["revision"]:
            raise RuntimeError("project-state revision changed since it was loaded")
        item = _record(raw)
        existing = {record["record_id"]: record for record in state["records"]}
        prior = existing.get(item["record_id"])
        if prior is not None:
            if prior != item:
                raise ValueError("project-state record id collision")
            return prior
        if set(item["supersedes"]) - set(existing):
            raise ValueError("supersedes references must identify existing records")
        if any(existing[rid]["record_type"] != item["record_type"] or existing[rid]["key"] != item["key"] for rid in item["supersedes"]):
            raise ValueError("supersedes may only target the same record type and key")
        if len(state["records"]) >= MAX_RECORDS:
            raise ValueError("project-state record limit reached")
        state["records"].append(item)
        self._refresh_conflicts(state)
        self._history(state, "record_added", {"record_id": item["record_id"]})
        state["revision"] = _revision(state)
        self.store.save(TASK_ID, state)
        return item

    def export_bundle(self) -> dict[str, Any]:
        state = self.load()
        receipts = list(state.get("history_archive_receipts", []))
        digest, count = state.get("history_archive_digest"), state.get("history_archived_count", 0)
        if isinstance(digest, str) and len(digest) == 64 and isinstance(count, int) and count > 0:
            receipt = {"digest": digest, "count": count}
            if receipt not in receipts:
                receipts.append(receipt)
        bundle = {
            "schema": SCHEMA, "project_id": self.project_id, "revision": state["revision"],
            "parent_revisions": state.get("parent_revisions", []), "records": state["records"],
            "conflicts": state.get("conflicts", []), "conflict_history": state.get("conflict_history", []),
            "history": state.get("history", []), "history_archive_receipts": receipts, "exported_at_utc": _now(),
        }
        bundle["bundle_sha256"] = _hash(bundle)
        if len(_json(bundle).encode("utf-8")) > MAX_BUNDLE_BYTES:
            raise ValueError("project-state bundle exceeds the size limit")
        return bundle

    def _validate_bundle(self, bundle: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(bundle, Mapping) or bundle.get("schema") != SCHEMA or bundle.get("project_id") != self.project_id:
            raise ValueError("project-state bundle schema or identity mismatch")
        if len(_json(bundle).encode("utf-8")) > MAX_BUNDLE_BYTES:
            raise ValueError("project-state bundle exceeds the size limit")
        digest = _digest(bundle.get("bundle_sha256"), "bundle_sha256")
        unsigned = {key: value for key, value in bundle.items() if key != "bundle_sha256"}
        if digest != _hash(unsigned):
            raise ValueError("project-state bundle digest mismatch")
        records = [_record(item) for item in bundle.get("records", [])]
        if len(records) > MAX_RECORDS:
            raise ValueError("project-state bundle exceeds the record limit")
        by_id = {item["record_id"]: item for item in records}
        if len(by_id) != len(records):
            raise ValueError("project-state bundle contains duplicate record ids")
        for item in records:
            if not set(item["supersedes"]).issubset(by_id):
                raise ValueError("bundle contains an unresolved supersedes reference")
            if any(by_id[rid]["record_type"] != item["record_type"] or by_id[rid]["key"] != item["key"] for rid in item["supersedes"]):
                raise ValueError("bundle supersedes a different logical record")
        state = {"project_id": self.project_id,
                 "parent_revisions": _strings(bundle.get("parent_revisions", []), "parent_revisions", hashes=True),
                 "records": records, "conflicts": bundle.get("conflicts", []),
                 "conflict_history": bundle.get("conflict_history", [])}
        history, conflicts = _validate_conflict_history(records, state["conflict_history"], state["conflicts"])
        state["conflict_history"], state["conflicts"] = history, conflicts
        if bundle.get("revision") != _revision(state):
            raise ValueError("project-state bundle revision mismatch")
        events = bundle.get("history", [])
        if not isinstance(events, list) or any(not isinstance(item, Mapping) or not isinstance(item.get("event_id"), str) for item in events):
            raise ValueError("project-state bundle history is malformed")
        receipts = bundle.get("history_archive_receipts", [])
        if not isinstance(receipts, list) or any(not isinstance(item, Mapping) or not isinstance(item.get("digest"), str) or type(item.get("count")) is not int or item["count"] < 1 for item in receipts):
            raise ValueError("project-state bundle archive receipts are malformed")
        return {**state, "revision": bundle["revision"], "bundle_sha256": digest,
                "history": events, "history_archive_receipts": receipts}

    def reconcile_bundle(self, bundle: Mapping[str, Any], *, expected_revision: str | None = None) -> dict[str, Any]:
        remote = self._validate_bundle(bundle)
        local = self.load()
        if expected_revision is not None and expected_revision != local["revision"]:
            raise RuntimeError("project-state revision changed since it was loaded")
        local_by_id = {item["record_id"]: item for item in local["records"]}
        if remote["revision"] == local["revision"] or remote["revision"] in local.get("parent_revisions", []):
            if all(local_by_id.get(item["record_id"]) == item for item in remote["records"]):
                return local
        merged = dict(local_by_id)
        for item in remote["records"]:
            if item["record_id"] in merged and merged[item["record_id"]] != item:
                raise ValueError("same record id has different content")
            merged[item["record_id"]] = item
        if len(merged) > MAX_RECORDS:
            raise ValueError("reconciled project-state exceeds the record limit")
        parents = set(local.get("parent_revisions", [])) | set(remote.get("parent_revisions", []))
        if local["revision"] != remote["revision"]:
            parents.update({local["revision"], remote["revision"]})
        conflict_map = {}
        for conflict in [*local.get("conflict_history", []), *remote.get("conflict_history", [])]:
            prior = conflict_map.get(conflict["conflict_id"])
            if prior is None or prior == conflict:
                conflict_map[conflict["conflict_id"]] = conflict
            elif prior["status"] == conflict["status"] == "unresolved":
                chosen = dict(prior)
                chosen["created_at_utc"] = min(prior["created_at_utc"], conflict["created_at_utc"])
                conflict_map[conflict["conflict_id"]] = chosen
            elif prior["status"] == "resolved" or conflict["status"] == "resolved":
                chosen = prior if prior["status"] == "resolved" else conflict
                rid = chosen.get("resolution_record_id")
                by_id = {item["record_id"]: item for item in merged.values()}
                if rid not in by_id or not set(chosen["record_ids"]).issubset(by_id[rid]["supersedes"]):
                    raise ValueError("conflict resolution cannot be verified across workspaces")
                if prior.get("status") == conflict.get("status") == "resolved" and prior.get("resolution_record_id") != conflict.get("resolution_record_id"):
                    raise ValueError("workspaces contain competing conflict resolutions")
                conflict_map[conflict["conflict_id"]] = chosen
            elif prior["status"] == "superseded" or conflict["status"] == "superseded":
                chosen = prior if prior["status"] == "superseded" else conflict
                successor = chosen.get("superseded_by_conflict_id")
                if successor not in {item["conflict_id"] for item in [*local.get("conflict_history", []), *remote.get("conflict_history", [])]}:
                    raise ValueError("superseded conflict successor is missing")
                conflict_map[conflict["conflict_id"]] = chosen
            else:
                raise ValueError("conflicting project-state history requires explicit reconciliation")
        state = {
            "project_schema": SCHEMA, "project_id": self.project_id, "parent_revisions": sorted(parents),
            "records": sorted(merged.values(), key=lambda item: (item["recorded_at_utc"], item["record_id"])),
            "conflicts": [], "conflict_history": list(conflict_map.values()), "history": [],
            "history_archive_receipts": list(local.get("history_archive_receipts", [])),
            "history_archive_digest": local.get("history_archive_digest") or "",
            "history_archived_count": local.get("history_archived_count") or 0,
            "updated_at": local.get("updated_at"),
        }
        events = {item.get("event_id"): item for item in [*local.get("history", []), *remote.get("history", [])] if item.get("event_id")}
        state["history"] = sorted(events.values(), key=lambda item: (item.get("at_utc", ""), item["event_id"]))[-50:]
        receipts = {(item.get("digest"), item.get("count")) for item in [*local.get("history_archive_receipts", []), *remote.get("history_archive_receipts", [])]}
        state["history_archive_receipts"] = [{"digest": d, "count": n} for d, n in sorted(receipts) if isinstance(d, str) and isinstance(n, int)]
        self._refresh_conflicts(state)
        self._history(state, "bundle_reconciled", {"local_revision": local["revision"], "remote_revision": remote["revision"]})
        state["revision"] = _revision(state)
        self.store.save(TASK_ID, state)
        return state

    def stale_record_ids(self, *, now_utc: str | None = None) -> list[str]:
        now = datetime.fromisoformat(_timestamp(now_utc or _now(), "now_utc").replace("Z", "+00:00"))
        state = self.load()
        superseded = {rid for item in state["records"] for rid in item["supersedes"]}
        stale = []
        for item in state["records"]:
            if item["record_id"] in superseded or item["status"] == "rejected":
                continue
            expired = item["valid_until_utc"] and now > datetime.fromisoformat(item["valid_until_utc"].replace("Z", "+00:00"))
            age = (now - datetime.fromisoformat(item["observed_at_utc"].replace("Z", "+00:00"))).total_seconds()
            if expired or (item["stale_after_seconds"] is not None and age > item["stale_after_seconds"]):
                stale.append(item["record_id"])
        return sorted(stale)

    def select_ready_tasks(self, *, now_utc: str | None = None) -> list[dict[str, Any]]:
        state = self.load()
        stale = set(self.stale_record_ids(now_utc=now_utc))
        superseded = {rid for item in state["records"] for rid in item["supersedes"]}
        active = {item["key"]: item for item in state["records"]
                  if item["record_type"] == "task" and item["record_id"] not in superseded and item["status"] != "rejected"}
        conflicted = {(item["record_type"], item["key"]) for item in state["conflicts"]}
        ready = []
        for item in active.values():
            if item["status"] != "open" or item["record_id"] in stale or ("task", item["key"]) in conflicted:
                continue
            if all(active.get(key) and active[key]["status"] == "complete" and active[key]["record_id"] not in stale
                   and ("task", key) not in conflicted for key in item["depends_on"]):
                ready.append(item)
        return sorted(ready, key=lambda item: (item["value"].get("priority", 100), item["recorded_at_utc"], item["record_id"]))

    def summary(self, *, now_utc: str | None = None) -> dict[str, Any]:
        state = self.load()
        return {"project_id": self.project_id, "revision": state["revision"],
                "record_count": len(state["records"]), "unresolved_conflict_count": len(state["conflicts"]),
                "stale_record_ids": self.stale_record_ids(now_utc=now_utc),
                "ready_task_ids": [item["record_id"] for item in self.select_ready_tasks(now_utc=now_utc)],
                "parent_revisions": state.get("parent_revisions", [])}
