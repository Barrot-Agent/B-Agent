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
from typing import Any, Iterable

from .models import CollaborationSession, Message, SessionAnalysis, UnifiedReport

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
        self._reports_dir = self._dir.parent / "reports"
        self._reports_dir.mkdir(parents=True, exist_ok=True)

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

    def analyze_session(self, session_id: str) -> SessionAnalysis:
        """Extract structured, provenance-linked findings from a session."""
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id!r} not found.")
        analysis = SessionAnalysis(session_id=session.session_id, directive_id=session.directive_id)
        buckets = {
            "directive": "objectives", "query": "objectives", "insight": "decisions",
            "response": "actions", "result": "outputs", "handoff": "dependencies",
        }
        markers = {
            "decision": "decisions", "decided": "decisions",
            "assume": "assumptions", "assumption": "assumptions",
            "depend": "dependencies", "requires": "dependencies",
            "conflict": "conflicts", "contradict": "conflicts", "disagree": "conflicts",
            "unresolved": "unresolved_items", "open question": "unresolved_items",
            "todo": "actions",
        }
        for message in session.messages:
            content = " ".join(message.content.split())
            if not content:
                continue
            evidence = {
                "claim": content,
                "source_session_id": message.source_session_id or session.session_id,
                "timestamp": message.timestamp,
                "author": message.sender_name,
                "confidence": "high" if message.source_kind is None else "medium",
                "message_id": message.message_id,
            }
            bucket = buckets.get(message.message_type, "outputs")
            getattr(analysis, bucket).append(evidence)
            lowered = content.casefold()
            for marker, marker_bucket in markers.items():
                if marker in lowered and evidence not in getattr(analysis, marker_bucket):
                    getattr(analysis, marker_bucket).append(dict(evidence))
            analysis.normalized_terms[content.casefold()] = content
        self._persist_analysis(analysis)
        return analysis

    def unify_sessions(self, session_ids: Iterable[str] | None = None) -> UnifiedReport:
        """Corroborate sessions into a versioned report without hiding conflicts."""
        ids = list(session_ids) if session_ids is not None else [
            session.session_id for session in self.list_sessions()
        ]
        analyses = [self.analyze_session(session_id) for session_id in ids]
        evidence: list[dict[str, Any]] = []
        for analysis in analyses:
            for field in SessionAnalysis._FIELDS:
                evidence.extend(getattr(analysis, field))

        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in evidence:
            grouped.setdefault(item["claim"].casefold(), []).append(item)
        agreements = [
            {"claim": items[0]["claim"], "evidence": items}
            for items in grouped.values() if len(items) > 1
        ]
        conflicts = [
            item for analysis in analyses for item in analysis.conflicts
        ]
        dependencies = [
            item for analysis in analyses for item in analysis.dependencies
        ]
        gaps = [
            item for analysis in analyses for item in analysis.unresolved_items
        ]
        previous = self.get_latest_report()
        version = previous.version + 1 if previous else 1
        changes = self._report_changes(previous, agreements, conflicts, gaps)
        report = UnifiedReport(
            version=version, session_ids=ids,
            executive_summary=(
                f"Synthesized {len(analyses)} session(s), preserving "
                f"{len(evidence)} provenance-linked findings."
            ),
            knowledge_model={
                "sessions": ids,
                "facts": len(evidence),
                "confirmed_agreements": len(agreements),
                "unresolved_questions": len(gaps),
            },
            agreements=agreements, conflicts=conflicts, dependencies=dependencies,
            gaps_and_risks=gaps,
            recommendations=[
                {"action": "Review unresolved items and conflicts", "evidence_count": len(gaps) + len(conflicts)}
            ] if gaps or conflicts else [],
            evidence_index=evidence,
            changes=changes,
            analyses=[analysis.to_dict() for analysis in analyses],
        )
        self._persist_report(report)
        return report

    def get_latest_report(self) -> UnifiedReport | None:
        path = self._reports_dir / "unified.json"
        if not path.exists():
            return None
        try:
            return UnifiedReport.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def list_reports(self) -> list[UnifiedReport]:
        reports = []
        for path in (self._reports_dir / "history").glob("*.json"):
            try:
                reports.append(UnifiedReport.from_dict(json.loads(path.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        latest = self.get_latest_report()
        if latest:
            reports.append(latest)
        return sorted(reports, key=lambda report: report.version)

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
        size = path.stat().st_size
        if size > 5 * 1024 * 1024:
            raise ValueError(f"Transcript exceeds the 5 MiB import limit ({size} bytes).")

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
                    source_session_id=str(record.get("source_session_id") or path.stem),
                    source_kind=source_kind,
                )
            )
        session.source_session_ids = sorted(
            {message.source_session_id for message in session.messages if message.source_session_id}
        ) or [path.stem]
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
            source_session_ids=[
                source_id
                for source in source_sessions
                for source_id in (source.source_session_ids or [source.session_id])
            ],
        )
        seen: set[tuple[str, str, float | None]] = set()
        candidates = []
        for source in source_sessions:
            for message in source.messages:
                source_id = message.source_session_id or source.session_id
                key = (message.sender_id, message.content, message.timestamp)
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

    def _persist_analysis(self, analysis: SessionAnalysis) -> None:
        dest = self._reports_dir / f"{analysis.session_id}.json"
        dest.write_text(json.dumps(analysis.to_dict(), indent=2), encoding="utf-8")

    def _persist_report(self, report: UnifiedReport) -> None:
        history = self._reports_dir / "history"
        history.mkdir(parents=True, exist_ok=True)
        if report.version > 1:
            previous = history / f"v{report.version - 1}.json"
            latest = self._reports_dir / "unified.json"
            if latest.exists() and not previous.exists():
                previous.write_text(latest.read_text(encoding="utf-8"), encoding="utf-8")
        (self._reports_dir / "unified.json").write_text(
            json.dumps(report.to_dict(), indent=2), encoding="utf-8"
        )

    @staticmethod
    def _report_changes(
        previous: UnifiedReport | None,
        agreements: list[dict[str, Any]],
        conflicts: list[dict[str, Any]],
        gaps: list[dict[str, Any]],
    ) -> list[str]:
        if previous is None:
            return ["Initial synthesis created."]
        changes = []
        if len(agreements) != len(previous.agreements):
            changes.append(f"Agreements changed from {len(previous.agreements)} to {len(agreements)}.")
        if len(conflicts) != len(previous.conflicts):
            changes.append(f"Conflicts changed from {len(previous.conflicts)} to {len(conflicts)}.")
        if len(gaps) != len(previous.gaps_and_risks):
            changes.append(f"Unresolved items changed from {len(previous.gaps_and_risks)} to {len(gaps)}.")
        return changes or ["No material finding-count changes."]

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
                source_session_id = payload.get("session_id") or path.stem
                payload = payload.get("messages", [payload])
                if isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict):
                            item.setdefault("source_session_id", source_session_id)
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
        pattern = re.compile(r"^\s*(?P<sender>[^:\n]{1,40}?)\s*:\s*(?P<content>.+?)\s*$")
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
