"""
SessionManager — creates and manages collaboration sessions.

Each session is a bounded working context in which multiple agents
exchange messages to fulfil a directive.  Sessions are persisted as
JSON files under ``.directive_platform/sessions/``.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Iterable, Any

from .models import CollaborationSession, Message

_DEFAULT_SESSIONS_DIR = Path(".directive_platform") / "sessions"


class SessionManager:
    """
    Create and manage multi-agent collaboration sessions.

    Parameters
    ----------
    sessions_dir:
        Directory where session JSON files are persisted.
    """

    def __init__(self, sessions_dir: Path | str | None = None) -> None:
        self._dir = Path(sessions_dir) if sessions_dir else _DEFAULT_SESSIONS_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_session(
        self,
        directive_id: str,
        participant_ids: list[str],
    ) -> CollaborationSession:
        """Start a new collaboration session for *directive_id*."""
        session = CollaborationSession(
            directive_id=directive_id,
            participant_ids=participant_ids,
            status="active",
        )
        self._persist(session)
        return session

    def get_session(self, session_id: str) -> CollaborationSession | None:
        """Return the session with the given ID, or ``None``."""
        path = self._dir / f"{session_id}.json"
        if not path.exists():
            return None
        try:
            return CollaborationSession.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, KeyError):
            return None

    def list_sessions(self, directive_id: str | None = None) -> list[CollaborationSession]:
        """
        Return all sessions, optionally filtered by *directive_id*.
        Sorted newest-first.
        """
        sessions: list[CollaborationSession] = []
        for fp in self._dir.glob("*.json"):
            try:
                s = CollaborationSession.from_dict(json.loads(fp.read_text(encoding="utf-8")))
                if directive_id is None or s.directive_id == directive_id:
                    sessions.append(s)
            except (json.JSONDecodeError, KeyError):
                pass
        return sorted(sessions, key=lambda s: s.started_at, reverse=True)

    def add_message(self, session_id: str, message: Message) -> bool:
        """
        Append *message* to a session.
        Returns ``True`` if the session was found and updated.
        """
        session = self.get_session(session_id)
        if session is None:
            return False
        session.messages.append(message)
        self._persist(session)
        return True

    def close_session(self, session_id: str, status: str = "completed") -> bool:
        """
        Mark a session as finished.
        Returns ``True`` if the session was found and updated.
        """
        session = self.get_session(session_id)
        if session is None:
            return False
        session.status = status
        session.ended_at = time.time()
        self._persist(session)
        return True

    def update_session(self, session: CollaborationSession) -> None:
        """Persist the current state of *session* to disk."""
        self._persist(session)

    def delete(self, session_id: str) -> bool:
        """Delete a session. Returns ``True`` if it existed."""
        path = self._dir / f"{session_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def import_transcript(
        self,
        source: Path | str,
        *,
        source_kind: str = "external",
        directive_id: str = "imported",
        participant_ids: list[str] | None = None,
    ) -> CollaborationSession:
        """Import a local JSON, JSONL, Markdown, or text transcript.

        The source is read explicitly by the caller; no network access or
        repository-wide scanning is performed.  Imported messages retain a
        ``source_kind`` marker so downstream consumers can distinguish them
        from native platform messages.
        """
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError("Transcript exceeds the 5 MiB import limit.")

        records = self._read_transcript(path)
        session = CollaborationSession(
            directive_id=directive_id,
            participant_ids=participant_ids or [],
        )
        for record in records:
            content = str(record.get("content", "")).strip()
            if not content:
                continue
            session.messages.append(
                Message(
                    session_id=session.session_id,
                    sender_id=str(record.get("sender_id") or "external"),
                    sender_name=str(record.get("sender_name") or "External"),
                    content=content,
                    message_type=str(record.get("message_type", "response")),
                    timestamp=self._timestamp(record.get("timestamp")),
                    source_session_id=str(
                        record.get("source_session_id") or path.stem
                    ),
                    source_kind=source_kind,
                )
            )
        self._persist(session)
        return session

    def merge_sessions(
        self,
        session_ids: Iterable[str],
        *,
        directive_id: str | None = None,
        participant_ids: list[str] | None = None,
    ) -> CollaborationSession:
        """Create a new chronological, de-duplicated session from sessions.

        Original sessions are never modified or deleted.  Each copied message
        receives ``source_session_id`` when it did not already have one.
        """
        source_sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session is None:
                raise ValueError(f"Session {session_id!r} not found.")
            source_sessions.append(session)
        if not source_sessions:
            raise ValueError("At least one session is required.")

        merged = CollaborationSession(
            directive_id=directive_id or source_sessions[0].directive_id,
            participant_ids=participant_ids
            if participant_ids is not None
            else sorted({pid for s in source_sessions for pid in s.participant_ids}),
        )
        seen: set[tuple[str, str, str, float]] = set()
        candidates = []
        for source in source_sessions:
            for message in source.messages:
                source_id = message.source_session_id or source.session_id
                key = (source_id, message.sender_id, message.content, message.timestamp)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append((message.timestamp, source.session_id, message))

        for _, source_session_id, message in sorted(
            candidates, key=lambda item: (item[0], item[1], item[2].message_id)
        ):
            merged.messages.append(
                Message(
                    session_id=merged.session_id,
                    sender_id=message.sender_id,
                    sender_name=message.sender_name,
                    content=message.content,
                    message_type=message.message_type,
                    timestamp=message.timestamp,
                    source_session_id=message.source_session_id or source_session_id,
                    source_kind=message.source_kind or "session",
                )
            )
        self._persist(merged)
        return merged

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _persist(self, session: CollaborationSession) -> None:
        dest = self._dir / f"{session.session_id}.json"
        dest.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def _timestamp(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _read_transcript(cls, path: Path) -> list[dict[str, Any]]:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            payload = json.loads(text)
            if isinstance(payload, dict):
                payload = payload.get("messages", [payload])
            if not isinstance(payload, list):
                raise ValueError("JSON transcript must contain a message list.")
            return [item for item in payload if isinstance(item, dict)]
        if path.suffix.lower() == ".jsonl":
            records = []
            for line in text.splitlines():
                if line.strip():
                    item = json.loads(line)
                    if isinstance(item, dict):
                        records.append(item)
            return records

        records = []
        pattern = re.compile(
            r"^\s*(?P<sender>[A-Za-z][\w -]{0,39})\s*:\s*(?P<content>.+?)\s*$"
        )
        for line in text.splitlines():
            match = pattern.match(line)
            if match:
                sender = match.group("sender").strip()
                records.append(
                    {
                        "sender_id": sender.lower().replace(" ", "_"),
                        "sender_name": sender,
                        "content": match.group("content"),
                    }
                )
        if not records and text.strip():
            records.append({"sender_id": "external", "sender_name": "External", "content": text})
        return records
