"""Admission boundary for ordinary agent requests.

``barrot_agent.inbound.transmutation`` is the protocol. This module is the
boundary an ordinary request crosses before the agent plans or executes
anything. It resolves the record directory, invokes the protocol exactly once,
and turns the persisted record into an admission decision.

The boundary adds one rule of its own: a request may continue only when the
protocol produced ``PROCEED_BOUNDED``, no stop reason, a gate verdict that
allowed it, and a read-only execution mode. Everything else fails closed,
including an unknown decision from a future protocol version.

Duplicates are refused at this boundary. The protocol already suppresses the
record and journals the duplicate; refusing here prevents the agent from
repeating work that is already recorded. A caller that is running an internal
repetition (for example an observation loop), rather than receiving a new
inbound request, must opt out explicitly at its own call site.

No network imports. No subprocess. No writes outside the record directory.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .gate import Source
from .transmutation import (
    EXECUTION_MODE,
    Budget,
    TransmutationError,
    transmute_request,
)

RECORD_DIR_ENV = "BARROT_TRANSMUTATION_DIR"
_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RECORD_DIR = _REPO_ROOT / "results" / "transmutation"

PROCEED = "PROCEED_BOUNDED"

ADMITTED = "ADMITTED"
BLOCKED = "BLOCKED"
DUPLICATE_SUPPRESSED = "DUPLICATE_SUPPRESSED"
INTAKE_ERROR = "INTAKE_ERROR"


@dataclass(frozen=True)
class Admission:
    """The result of passing one request through the intake boundary."""

    allowed: bool
    outcome: str
    request_id: str
    decision: str
    stop_reason: str | None
    reasons: tuple[str, ...]
    record_path: str
    duplicate: bool
    record: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        """Serialise the decision without the request body or the record body."""
        return {
            "allowed": self.allowed,
            "outcome": self.outcome,
            "request_id": self.request_id,
            "decision": self.decision,
            "stop_reason": self.stop_reason,
            "reasons": list(self.reasons),
            "record_path": self.record_path,
            "duplicate": self.duplicate,
        }

    def refusal(self) -> str:
        """A safe, human-readable refusal that never repeats the request body."""
        reason = self.stop_reason or self.outcome
        detail = "; ".join(self.reasons) if self.reasons else "no reason recorded"
        if self.record_path:
            return (
                f"Request {self.request_id} was not admitted ({reason}): {detail}. "
                f"Record: {self.record_path}"
            )
        return f"Request was not admitted ({reason}): {detail}."


def resolve_record_dir(record_dir: str | Path | None = None) -> Path:
    """Resolve an explicit directory, then the environment override, then the default."""
    if record_dir is not None:
        return Path(record_dir)
    override = os.environ.get(RECORD_DIR_ENV, "").strip()
    if override:
        return Path(override)
    return DEFAULT_RECORD_DIR


def _reasons(record: Mapping[str, Any]) -> tuple[str, ...]:
    constraints = record.get("constraints")
    if not isinstance(constraints, Mapping):
        return ()
    stop_reasons = constraints.get("stop_reasons")
    if isinstance(stop_reasons, (list, tuple)) and stop_reasons:
        return tuple(str(item) for item in stop_reasons)
    reasons = constraints.get("reasons")
    if isinstance(reasons, (list, tuple)):
        return tuple(str(item) for item in reasons)
    return ()


def _admission_from_record(
    record: Mapping[str, Any],
    *,
    record_path: Path,
    duplicate: bool,
    allow_duplicate: bool,
) -> Admission:
    decision = str(record.get("decision", "UNKNOWN"))
    stop_reason = record.get("stop_reason")
    constraints = record.get("constraints")
    if not isinstance(constraints, Mapping):
        constraints = {}
    allowed = (
        decision == PROCEED
        and stop_reason is None
        and constraints.get("allowed") is True
        and constraints.get("executed") is False
        and record.get("execution_mode") == EXECUTION_MODE
    )
    if duplicate and not allow_duplicate:
        allowed = False
        outcome = DUPLICATE_SUPPRESSED
        reasons = (
            "an identical request is already recorded; reload the record instead of "
            "re-planning or repeating the work",
        )
    elif allowed:
        outcome = ADMITTED
        reasons = _reasons(record)
    else:
        outcome = BLOCKED
        reasons = _reasons(record)
    return Admission(
        allowed=allowed,
        outcome=outcome,
        request_id=str(record.get("request_id", "")),
        decision=decision,
        stop_reason=stop_reason,
        reasons=reasons,
        record_path=str(record_path),
        duplicate=duplicate,
        record=record,
    )


def admit(
    text: str,
    *,
    source: Source = Source.OPERATOR,
    received_from: str = "",
    record_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
    budget: Budget | None = None,
    allow_duplicate: bool = False,
) -> Admission:
    """Transmute one ordinary request and decide whether it may continue.

    The original is preserved by the protocol before this function decides
    anything. A preservation or record-integrity failure is converted into a
    refused admission rather than an exception, so a caller cannot accidentally
    treat a broken record as authority to proceed.

    ``allow_duplicate`` is for a caller that owns its own durable resume and
    deduplication, such as the production task dispatcher. The protocol still
    detects and journals the duplicate; the caller decides whether its own
    recovery state makes continuation legitimate.
    """
    directory = resolve_record_dir(record_dir)
    try:
        result = transmute_request(
            text,
            source=source,
            received_from=received_from,
            record_dir=directory,
            repo_root=repo_root,
            budget=budget,
        )
    except (TransmutationError, OSError, json.JSONDecodeError) as exc:
        # The protocol never includes the request body in these messages.
        return Admission(
            allowed=False,
            outcome=INTAKE_ERROR,
            request_id="",
            decision=INTAKE_ERROR,
            stop_reason=INTAKE_ERROR,
            reasons=(str(exc),),
            record_path="",
            duplicate=False,
            record={},
        )
    return _admission_from_record(
        result.record,
        record_path=result.record_path,
        duplicate=result.duplicate,
        allow_duplicate=allow_duplicate,
    )
