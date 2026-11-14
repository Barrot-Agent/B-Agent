"""Crash-safe checkpoints for long-horizon Barrot autonomous tasks."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from datetime import datetime, timezone
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback is single-writer only
    fcntl = None


class AutonomousTaskStore:
    """Persist task state atomically under a workspace-owned directory."""

    SCHEMA_VERSION = 1
    MAX_HISTORY_ITEMS = 50
    MAX_CHECKPOINT_BYTES = 5 * 1024 * 1024
    _TASK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        state_parent = self.workspace / ".barrot"
        state_parent.mkdir(parents=True, exist_ok=True)
        resolved_parent = state_parent.resolve()
        try:
            resolved_parent.relative_to(self.workspace)
        except ValueError as exc:
            raise ValueError("autonomous task store path escapes workspace") from exc
        self.root = resolved_parent / "autonomous_tasks"
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, task_id: str) -> Path:
        if not isinstance(task_id, str) or not self._TASK_ID.fullmatch(task_id):
            raise ValueError("task_id must be 1-96 safe filename characters")
        path = (self.root / f"{task_id}.json").resolve()
        path.relative_to(self.root)
        return path

    def _lock_path_for(self, task_id: str) -> Path:
        lock_path = self.path_for(task_id).with_suffix(".lock")
        resolved = lock_path.resolve()
        resolved.relative_to(self.root)
        return resolved

    def load(self, task_id: str) -> dict[str, Any] | None:
        path = self.path_for(task_id)
        lock_path = self._lock_path_for(task_id)
        with lock_path.open("a+", encoding="utf-8") as lock:
            if fcntl is not None:
                fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
            try:
                if not path.exists():
                    return None
                if path.stat().st_size > self.MAX_CHECKPOINT_BYTES:
                    raise ValueError("autonomous task checkpoint exceeds the size limit")
                try:
                    state = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise ValueError("autonomous task checkpoint is unreadable") from exc
                if not isinstance(state, dict):
                    raise ValueError("autonomous task checkpoint must be an object")
                if state.get("schema_version") != self.SCHEMA_VERSION:
                    raise ValueError("unsupported autonomous task checkpoint schema")
                if state.get("task_id") != task_id:
                    raise ValueError("autonomous task checkpoint identity mismatch")
                if not isinstance(state.get("history"), list):
                    raise ValueError("autonomous task checkpoint history must be a list")
                return state
            finally:
                if fcntl is not None:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def save(self, task_id: str, state: dict[str, Any]) -> Path:
        path = self.path_for(task_id)
        if not isinstance(state, dict):
            raise TypeError("autonomous task state must be an object")
        payload = dict(state)
        payload["schema_version"] = self.SCHEMA_VERSION
        payload["task_id"] = task_id
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        if not isinstance(payload.get("history"), list):
            raise ValueError("autonomous task state history must be a list")
        history = payload["history"]
        if len(history) > self.MAX_HISTORY_ITEMS:
            archived = history[:-self.MAX_HISTORY_ITEMS]
            digest = str(payload.get("history_archive_digest", ""))
            for item in archived:
                canonical = json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                digest = hashlib.sha256((digest + canonical).encode("utf-8")).hexdigest()
            archived_count = int(payload.get("history_archived_count", 0)) + len(archived)
            payload["history_archive_digest"] = digest
            payload["history_archived_count"] = archived_count
            state["history_archive_digest"] = digest
            state["history_archived_count"] = archived_count
            del history[:-self.MAX_HISTORY_ITEMS]
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n"
        if len(serialized.encode("utf-8")) > self.MAX_CHECKPOINT_BYTES:
            raise ValueError("autonomous task checkpoint exceeds the size limit")

        lock_path = self._lock_path_for(task_id)
        with lock_path.open("a+", encoding="utf-8") as lock:
            if fcntl is not None:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            temporary: Path | None = None
            try:
                if path.exists():
                    current = json.loads(path.read_text(encoding="utf-8"))
                    if current.get("updated_at") != state.get("updated_at"):
                        raise RuntimeError("autonomous task checkpoint changed since it was loaded")
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.root,
                    prefix=f".{task_id}.",
                    suffix=".tmp",
                    delete=False,
                ) as handle:
                    temporary = Path(handle.name)
                    handle.write(serialized)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, path)
                temporary = None
                state["updated_at"] = payload["updated_at"]
                state["schema_version"] = self.SCHEMA_VERSION
                state["task_id"] = task_id
                if os.name != "nt":
                    directory_fd = os.open(self.root, os.O_RDONLY)
                    try:
                        os.fsync(directory_fd)
                    finally:
                        os.close(directory_fd)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
                if fcntl is not None:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        return path
