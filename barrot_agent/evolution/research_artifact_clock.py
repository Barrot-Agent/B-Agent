"""Deterministic research-artifact capture/commit chronology checks."""
from __future__ import annotations

from datetime import datetime, timezone


class ResearchArtifactClockError(ValueError):
    """Artifact capture time is invalid or later than its introducing commit."""


def _parse_utc(value: str, field: str) -> tuple[datetime, str]:
    if not isinstance(value, str) or not value.strip():
        raise ResearchArtifactClockError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ResearchArtifactClockError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ResearchArtifactClockError(f"{field} must include a timezone")
    normalized = parsed.astimezone(timezone.utc)
    return normalized, normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")


def validate_capture_before_commit(captured_at_utc: str, commit_created_at_utc: str) -> dict[str, str]:
    """Require the capture to predate or equal the commit that first records it.

    GitHub's server-side commit creation time is a minimum chronology check.
    It does not independently authenticate the source observation.
    """
    captured, captured_s = _parse_utc(captured_at_utc, "captured_at_utc")
    committed, committed_s = _parse_utc(commit_created_at_utc, "commit_created_at_utc")
    if captured > committed:
        raise ResearchArtifactClockError(
            "captured_at_utc cannot be later than the commit that introduces the artifact"
        )
    return {
        "captured_at_utc": captured_s,
        "commit_created_at_utc": committed_s,
        "chronology": "valid",
    }
