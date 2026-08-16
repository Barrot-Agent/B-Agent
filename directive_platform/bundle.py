"""Portable export, merge, and import support for local agent sessions."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .models import CollaborationSession

BUNDLE_VERSION = 1


def export_sessions(sessions_dir: Path | str, output: Path | str) -> dict[str, Any]:
    source = Path(sessions_dir)
    sessions = []
    for path in sorted(source.glob("*.json")):
        try:
            sessions.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    bundle = {
        "version": BUNDLE_VERSION,
        "exported_at": time.time(),
        "source": str(source),
        "sessions": sessions,
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return bundle


def merge_sessions(
    sessions_dir: Path | str, bundle_path: Path | str, report_path: Path | str | None = None
) -> dict[str, Any]:
    destination = Path(sessions_dir)
    destination.mkdir(parents=True, exist_ok=True)
    bundle = json.loads(Path(bundle_path).read_text(encoding="utf-8"))
    imported = {item["session_id"]: item for item in bundle.get("sessions", [])}
    conflicts: list[dict[str, Any]] = []
    merged = 0
    for session_id, incoming in imported.items():
        path = destination / f"{session_id}.json"
        if path.exists():
            try:
                current = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                current = {}
            current_messages = {m["message_id"]: m for m in current.get("messages", [])}
            for message in incoming.get("messages", []):
                previous = current_messages.get(message["message_id"])
                if previous is None:
                    current_messages[message["message_id"]] = message
                elif previous != message:
                    conflicts.append({"session_id": session_id, "message_id": message["message_id"]})
            current["messages"] = sorted(
                current_messages.values(), key=lambda message: message.get("timestamp", 0)
            )
            for key in ("repository", "branch", "agent", "source_session_id"):
                if current.get(key) is None:
                    current[key] = incoming.get(key)
            if current.get("status") != incoming.get("status"):
                conflicts.append({"session_id": session_id, "field": "status"})
            path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(json.dumps(incoming, indent=2) + "\n", encoding="utf-8")
        merged += 1
    report = {"imported": merged, "conflicts": conflicts, "bundle": str(bundle_path)}
    if report_path:
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
