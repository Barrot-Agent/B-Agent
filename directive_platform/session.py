"""
SessionManager — creates and manages collaboration sessions.

Each session is a bounded working context in which multiple agents
exchange messages to fulfil a directive.  Sessions are persisted as
JSON files under ``.directive_platform/sessions/``.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

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
        *,
        repository: str | None = None,
        branch: str | None = None,
        agent: str | None = None,
    ) -> CollaborationSession:
        """Start a new collaboration session for *directive_id*."""
        session = CollaborationSession(
            directive_id=directive_id,
            participant_ids=participant_ids,
            status="active",
            repository=repository or self._git_config("remote.origin.url"),
            branch=branch or self._git_current_branch(),
            agent=agent or os.environ.get("BARROT_AGENT"),
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

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _persist(self, session: CollaborationSession) -> None:
        dest = self._dir / f"{session.session_id}.json"
        dest.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def _git_current_branch() -> str | None:
        return SessionManager._run_git(["git", "branch", "--show-current"])

    @staticmethod
    def _git_config(key: str) -> str | None:
        return SessionManager._run_git(["git", "config", "--get", key])

    @staticmethod
    def _run_git(command: list[str]) -> str | None:
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError:
            return None
        return result.stdout.strip() or None
