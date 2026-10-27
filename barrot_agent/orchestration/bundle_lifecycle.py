"""Durable, append-only evidence store for Barrot's work-bundle lifecycle."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BundleLifecycleStore:
    """Persist bundle versions and execution evidence without unsafe path interpolation."""

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        self.root = self.workspace / ".git" / "barrot_repair" / "bundles"

    @staticmethod
    def _key(work_id: str) -> str:
        value = str(work_id).strip()
        if not value:
            raise ValueError("work_id must be non-empty")
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]

    def _directory(self, work_id: str) -> Path:
        target = (self.root / self._key(work_id)).resolve()
        if self.root.resolve() not in target.parents:
            raise ValueError("bundle path escaped lifecycle store")
        return target

    @staticmethod
    def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".bundle-", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        except Exception:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise

    def save_plan(self, work_id: str, result: Any) -> Path:
        """Persist exact plan, deterministic review, revision attempts, and current state."""
        directory = self._directory(work_id)
        path = directory / "lifecycle.json"
        bundle = getattr(result, "bundle", None)
        fingerprint = None
        if isinstance(bundle, dict):
            canonical = json.dumps(bundle, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            fingerprint = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        previous = None
        if path.is_file():
            try:
                candidate = json.loads(path.read_text(encoding="utf-8"))
                if candidate.get("work_id") == work_id and candidate.get("bundle_fingerprint") == fingerprint:
                    previous = candidate
            except (OSError, ValueError, TypeError):
                previous = None
        payload = {
            "schema_version": "1.0",
            "work_id": work_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": getattr(result, "status", "UNKNOWN"),
            "bundle": bundle,
            "bundle_fingerprint": fingerprint,
            "review": result.review.to_dict() if getattr(result, "review", None) else None,
            "attempts": list(getattr(result, "attempts", []) or []),
            "execution_evidence": list((previous or {}).get("execution_evidence", [])),
            "task_states": dict((previous or {}).get("task_states", {})),
        }
        self._atomic_json(path, payload)
        return path

    def record_task_execution(self, work_id: str, task_id: str, evidence: dict[str, Any]) -> Path:
        """Append task-level evidence while retaining the latest state for interruption resume."""
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id must be non-empty")
        path = self._directory(work_id) / "lifecycle.json"
        if not path.is_file():
            raise FileNotFoundError("bundle lifecycle must be initialized before task execution")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("work_id") != work_id:
            raise ValueError("bundle lifecycle work_id mismatch")
        task_states = payload.setdefault("task_states", {})
        if not isinstance(task_states, dict):
            raise ValueError("task_states must be an object")
        history = task_states.setdefault(task_id, [])
        if not isinstance(history, list):
            raise ValueError("task state history must be a list")
        record = {"recorded_at": datetime.now(timezone.utc).isoformat(), **evidence}
        history.append(record)
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._atomic_json(path, payload)
        return path

    def latest_task_states(self, work_id: str) -> dict[str, dict[str, Any]]:
        """Return the latest durable record per task; incomplete histories fail closed."""
        payload = self.load(work_id)
        if payload is None:
            return {}
        states = payload.get("task_states", {})
        if not isinstance(states, dict):
            raise ValueError("task_states must be an object")
        latest: dict[str, dict[str, Any]] = {}
        for task_id, history in states.items():
            if not isinstance(history, list) or not history:
                continue
            if isinstance(history[-1], dict):
                latest[str(task_id)] = history[-1]
        return latest

    def record_execution(self, work_id: str, evidence: dict[str, Any]) -> Path:
        """Append execution evidence to the durable lifecycle record."""
        path = self._directory(work_id) / "lifecycle.json"
        if not path.is_file():
            raise FileNotFoundError("bundle lifecycle must be initialized before execution")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("work_id") != work_id:
            raise ValueError("bundle lifecycle work_id mismatch")
        history = payload.setdefault("execution_evidence", [])
        if not isinstance(history, list):
            raise ValueError("execution evidence must be a list")
        history.append({
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            **evidence,
        })
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        payload["execution_status"] = evidence.get("status", "UNKNOWN")
        self._atomic_json(path, payload)
        return path

    def load(self, work_id: str) -> dict[str, Any] | None:
        path = self._directory(work_id) / "lifecycle.json"
        if not path.is_file():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("work_id") != work_id:
            raise ValueError("bundle lifecycle work_id mismatch")
        return payload



def dispatch_bundle_tasks(
    *,
    store: BundleLifecycleStore,
    work_id: str,
    bundle: dict[str, Any],
    execute_task: Any,
) -> dict[str, Any]:
    """Execute ready bundle tasks through the caller's existing queue and resume from evidence.

    The dispatcher never interprets a model assertion as completion. A task is reusable
    on resume only when its latest durable record contains all queue and verification gates.
    """
    if not isinstance(bundle, dict) or not isinstance(bundle.get("tasks"), list) or not bundle["tasks"]:
        raise ValueError("bundle must contain a non-empty tasks list")
    if not callable(execute_task):
        raise ValueError("execute_task must be callable")

    tasks = bundle["tasks"]
    task_by_id: dict[str, dict[str, Any]] = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not task["id"].strip():
            raise ValueError("every bundle task must have a non-empty id")
        if task["id"] in task_by_id:
            raise ValueError(f"duplicate bundle task id: {task['id']}")
        task_by_id[task["id"]] = task

    for task in tasks:
        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or any(dep not in task_by_id for dep in deps):
            raise ValueError(f"invalid dependencies for task {task['id']}")

    def is_complete(record: dict[str, Any] | None) -> bool:
        return bool(
            record
            and record.get("status") == "complete"
            and record.get("queue_advanced") is True
            and record.get("local_validation_passed") is True
            and record.get("remote_verified") is True
            and record.get("resolution_verified") is True
        )

    latest = store.latest_task_states(work_id)
    completed = {task_id for task_id, record in latest.items() if is_complete(record)}
    last_result: Any = next((latest[task_id].get("result") for task_id in reversed(list(task_by_id)) if task_id in completed and latest[task_id].get("result") is not None), None)
    executed: list[str] = []
    blocked: dict[str, str] = {}
    remaining = {task["id"] for task in tasks} - completed

    # Iterate until no more dependency-ready work can be advanced.
    while remaining:
        progressed = False
        for task in tasks:
            task_id = task["id"]
            if task_id not in remaining:
                continue
            dependencies = task.get("depends_on", [])
            failed_dependencies = [
                dep for dep in dependencies
                if dep in blocked or (dep not in completed and dep not in remaining)
            ]
            if failed_dependencies:
                reason = "dependency blocked: " + ", ".join(failed_dependencies)
                blocked[task_id] = reason
                store.record_task_execution(work_id, task_id, {
                    "status": "blocked",
                    "reason": reason,
                    "depends_on": dependencies,
                })
                remaining.remove(task_id)
                progressed = True
                continue
            if any(dep not in completed for dep in dependencies):
                continue

            store.record_task_execution(work_id, task_id, {
                "status": "running",
                "depends_on": dependencies,
                "attempt": len(store.latest_task_states(work_id).get(task_id, {}).get("attempt", [])) + 1
                if isinstance(store.latest_task_states(work_id).get(task_id, {}).get("attempt"), list) else 1,
            })
            try:
                result = execute_task(task)
                last_result = result
                raw = result if isinstance(result, dict) else result.to_dict()
                cycle = raw.get("repair_cycle", raw)
                if not isinstance(cycle, dict):
                    cycle = {}
                commit = cycle.get("commit") or {}
                evidence = {
                    "status": cycle.get("status", raw.get("status", "UNKNOWN")),
                    "cycle_id": cycle.get("cycle_id"),
                    "queue_advanced": raw.get("queue_advanced") is True,
                    "local_validation_passed": cycle.get("local_validation_passed") is True,
                    "remote_verified": commit.get("remote_verified") is True,
                    "resolution_verified": cycle.get("resolution_verified") is True,
                    "commit_sha": commit.get("sha", ""),
                    "failure": cycle.get("failure"),
                    "depends_on": dependencies,
                    "result": raw,
                }
                store.record_task_execution(work_id, task_id, evidence)
                if is_complete(evidence):
                    completed.add(task_id)
                else:
                    blocked[task_id] = str(evidence.get("failure") or evidence["status"])
                remaining.remove(task_id)
                executed.append(task_id)
                progressed = True
            except Exception as exc:
                reason = f"{type(exc).__name__}: {str(exc)[:800]}"
                store.record_task_execution(work_id, task_id, {
                    "status": "failed",
                    "reason": reason,
                    "depends_on": dependencies,
                })
                blocked[task_id] = reason
                remaining.remove(task_id)
                executed.append(task_id)
                progressed = True
        if not progressed:
            # Any remaining node is dependency-blocked or part of a malformed graph.
            for task_id in sorted(remaining):
                reason = "dependencies are not complete; safe to resume after prerequisites pass"
                blocked[task_id] = reason
                store.record_task_execution(work_id, task_id, {
                    "status": "blocked",
                    "reason": reason,
                    "depends_on": task_by_id[task_id].get("depends_on", []),
                })
            remaining.clear()

    return {
        "complete": len(completed.intersection(task_by_id)) == len(task_by_id),
        "completed_task_ids": sorted(completed.intersection(task_by_id)),
        "executed_task_ids": executed,
        "blocked_tasks": blocked,
        "last_result": last_result,
    }
