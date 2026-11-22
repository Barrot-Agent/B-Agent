"""Evidence-gated capability discovery and experiment cycle for Barrot V3.

This controller composes existing MMI, sandbox, verification, and promotion
adapters. It does not create a second ingestion, memory, task, or sandbox system.
All side-effecting behavior is supplied explicitly by the caller.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


class CapabilityCycleError(RuntimeError):
    """Raised when a capability cycle violates its evidence or safety contract."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CapabilityCycleResult:
    cycle_id: str
    status: str
    gaps_found: int
    experiments_run: int
    experiments_verified: int
    promoted: int
    ledger_path: str
    unresolved: list[str] = field(default_factory=list)


class CapabilityCycleLedger:
    """Append-only, hash-linked cycle events stored inside the workspace."""

    SCHEMA = "barrot.capability-cycle-event.v1"
    CYCLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        root = self.workspace / ".barrot" / "capability_cycles"
        root.mkdir(parents=True, exist_ok=True)
        self.root = root.resolve()
        self.root.relative_to(self.workspace)
        self.path = self.root / "events.jsonl"
        self.lock_path = self.root / "events.lock"

    def _read_unlocked(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events: list[dict[str, Any]] = []
        previous = "0" * 64
        with self.path.open("r", encoding="utf-8") as stream:
            for number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise CapabilityCycleError(f"ledger JSON is corrupt at line {number}") from exc
                if not isinstance(event, dict) or event.get("schema") != self.SCHEMA:
                    raise CapabilityCycleError(f"ledger schema is invalid at line {number}")
                if event.get("previous_hash") != previous:
                    raise CapabilityCycleError(f"ledger chain is broken at line {number}")
                claimed = event.get("event_hash")
                body = {key: value for key, value in event.items() if key != "event_hash"}
                actual = _sha256(_canonical(body))
                if claimed != actual:
                    raise CapabilityCycleError(f"ledger event hash mismatch at line {number}")
                previous = claimed
                events.append(event)
        return events

    def read_events(self) -> list[dict[str, Any]]:
        with self.lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
            try:
                return self._read_unlocked()
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def append(self, cycle_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(cycle_id, str) or not self.CYCLE_ID.fullmatch(cycle_id):
            raise ValueError("cycle_id must contain 1-96 safe filename characters")
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be non-empty")
        if not isinstance(payload, dict):
            raise TypeError("event payload must be an object")
        with self.lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                events = self._read_unlocked()
                previous = events[-1]["event_hash"] if events else "0" * 64
                sequence = len(events) + 1
                body = {
                    "schema": self.SCHEMA,
                    "sequence": sequence,
                    "cycle_id": cycle_id,
                    "event_type": event_type,
                    "recorded_at": datetime.now(timezone.utc).isoformat(),
                    "previous_hash": previous,
                    "payload": payload,
                }
                event = {**body, "event_hash": _sha256(_canonical(body))}
                with self.path.open("a", encoding="utf-8") as stream:
                    stream.write(_canonical(event) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                return event
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


class CapabilityCycleController:
    """Run one bounded MMI → gap → sandbox experiment → verification → promotion cycle.

    Adapters must bind to Barrot's existing MMI, sandbox, verifier, and approval
    systems. This controller deliberately contains no provider, network, shell,
    deployment, or repository-mutation implementation of its own.
    """

    def __init__(
        self,
        *,
        workspace: str | Path,
        mmi_ingest: Callable[[str], dict[str, Any]],
        gap_analyzer: Callable[[dict[str, Any]], list[dict[str, Any]]],
        experiment_planner: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
        sandbox_runner: Callable[[dict[str, Any]], dict[str, Any]],
        verifier: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
        promoter: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
        authorizer: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        max_experiments: int = 3,
        max_cost_units: float = 10.0,
    ):
        if isinstance(max_experiments, bool) or not isinstance(max_experiments, int) or max_experiments < 1:
            raise ValueError("max_experiments must be a positive integer")
        if isinstance(max_cost_units, bool) or not isinstance(max_cost_units, (int, float)) or max_cost_units <= 0:
            raise ValueError("max_cost_units must be positive")
        self.workspace = Path(workspace).resolve()
        self.ledger = CapabilityCycleLedger(self.workspace)
        self.mmi_ingest = mmi_ingest
        self.gap_analyzer = gap_analyzer
        self.experiment_planner = experiment_planner
        self.sandbox_runner = sandbox_runner
        self.verifier = verifier
        self.promoter = promoter
        self.authorizer = authorizer
        self.max_experiments = max_experiments
        self.max_cost_units = float(max_cost_units)

    @staticmethod
    def _require_mapping(value: Any, label: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise CapabilityCycleError(f"{label} must return an object")
        return value

    def run(self, request: str, *, cycle_id: str) -> CapabilityCycleResult:
        if not isinstance(request, str) or not request.strip():
            raise ValueError("request must be non-empty")
        prior = [event for event in self.ledger.read_events() if event["cycle_id"] == cycle_id]
        if prior:
            raise CapabilityCycleError(
                "cycle_id already exists; use the existing task/checkpoint recovery path rather than replaying side effects"
            )

        request_hash = _sha256(request)
        self.ledger.append(cycle_id, "cycle_started", {
            "request": request,
            "request_sha256": request_hash,
            "workspace": str(self.workspace),
            "limits": {
                "max_experiments": self.max_experiments,
                "max_cost_units": self.max_cost_units,
            },
        })
        gaps_found = experiments_run = verified = promoted = 0
        unresolved: list[str] = []
        spent = 0.0
        status = "incomplete"

        try:
            ingestion = self._require_mapping(self.mmi_ingest(request), "MMI adapter")
            source_refs = ingestion.get("source_refs")
            if not isinstance(source_refs, list) or not source_refs:
                raise CapabilityCycleError("MMI must return at least one canonical source reference")
            if ingestion.get("complete") is not True:
                raise CapabilityCycleError("MMI ingestion is partial or unverified; capability promotion is blocked")
            self.ledger.append(cycle_id, "mmi_ingested", ingestion)

            gaps = self.gap_analyzer(ingestion)
            if not isinstance(gaps, list):
                raise CapabilityCycleError("gap analyzer must return a list")
            if any(not isinstance(gap, dict) or not str(gap.get("gap_id", "")).strip() for gap in gaps):
                raise CapabilityCycleError("every gap must be an object with a stable gap_id")
            gaps_found = len(gaps)
            self.ledger.append(cycle_id, "gaps_identified", {"count": gaps_found, "gaps": gaps})

            if not gaps:
                status = "no_gap_found"
            for gap in gaps:
                if experiments_run >= self.max_experiments:
                    unresolved.append(str(gap["gap_id"]) + ": experiment_count_budget_exhausted")
                    continue
                plan = self._require_mapping(self.experiment_planner(gap, ingestion), "experiment planner")
                cost = plan.get("estimated_cost_units")
                if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
                    raise CapabilityCycleError("experiment plan must declare non-negative estimated_cost_units")
                if spent + float(cost) > self.max_cost_units:
                    unresolved.append(str(gap["gap_id"]) + ": resource_budget_exhausted")
                    self.ledger.append(cycle_id, "experiment_skipped_budget", {
                        "gap_id": gap["gap_id"], "estimated_cost_units": cost,
                        "remaining_cost_units": self.max_cost_units - spent,
                    })
                    continue
                if plan.get("acceptance_criteria") is None or not plan.get("hypothesis"):
                    raise CapabilityCycleError("experiment plan requires a hypothesis and acceptance_criteria")
                self.ledger.append(cycle_id, "experiment_planned", {"gap_id": gap["gap_id"], "plan": plan})

                execution = self._require_mapping(self.sandbox_runner(plan), "sandbox runner")
                if execution.get("sandboxed") is not True:
                    raise CapabilityCycleError("experiment execution lacks affirmative sandbox evidence")
                if not execution.get("baseline_hash") or not execution.get("artifact_refs"):
                    raise CapabilityCycleError("sandbox execution must identify immutable baseline and output artifacts")
                experiments_run += 1
                spent += float(cost)
                self.ledger.append(cycle_id, "experiment_executed", {
                    "gap_id": gap["gap_id"], "plan": plan, "execution": execution,
                    "cost_units": float(cost), "cumulative_cost_units": spent,
                })

                result = self._require_mapping(self.verifier(plan, execution), "verifier")
                evidence = result.get("evidence")
                passed = result.get("passed") is True and isinstance(evidence, list) and bool(evidence)
                self.ledger.append(cycle_id, "experiment_verified", {
                    "gap_id": gap["gap_id"], "passed": passed, "verification": result,
                })
                if not passed:
                    unresolved.append(str(gap["gap_id"]) + ": verification_failed")
                    continue
                verified += 1

                if self.promoter is None:
                    unresolved.append(str(gap["gap_id"]) + ": no_promotion_adapter")
                    continue
                authorization = self._require_mapping(
                    self.authorizer(plan) if self.authorizer is not None else {},
                    "authorization adapter",
                )
                if authorization.get("approved") is not True:
                    unresolved.append(str(gap["gap_id"]) + ": approval_required_or_denied")
                    self.ledger.append(cycle_id, "promotion_blocked", {
                        "gap_id": gap["gap_id"], "authorization": authorization,
                    })
                    continue
                promotion = self._require_mapping(self.promoter(plan, result), "promotion adapter")
                if promotion.get("promoted") is not True or not promotion.get("artifact_ref"):
                    unresolved.append(str(gap["gap_id"]) + ": promotion_not_verified")
                    self.ledger.append(cycle_id, "promotion_not_verified", {
                        "gap_id": gap["gap_id"], "promotion": promotion,
                    })
                    continue
                promoted += 1
                self.ledger.append(cycle_id, "capability_promoted", {
                    "gap_id": gap["gap_id"], "promotion": promotion,
                    "authorization": authorization,
                })

            if promoted and not unresolved:
                status = "complete"
            elif verified:
                status = "verified_pending_promotion"
            elif experiments_run:
                status = "experiments_inconclusive"
            elif status != "no_gap_found":
                status = "blocked_or_budget_exhausted"
        except Exception as exc:
            status = "failed"
            unresolved.append(f"{type(exc).__name__}: {exc}")
            self.ledger.append(cycle_id, "cycle_failed", {
                "error_type": type(exc).__name__, "error": str(exc),
                "request_sha256": request_hash,
            })
            raise

        self.ledger.append(cycle_id, "cycle_finished", {
            "status": status, "gaps_found": gaps_found,
            "experiments_run": experiments_run, "experiments_verified": verified,
            "promoted": promoted, "cost_units": spent, "unresolved": unresolved,
        })
        return CapabilityCycleResult(
            cycle_id=cycle_id, status=status, gaps_found=gaps_found,
            experiments_run=experiments_run, experiments_verified=verified,
            promoted=promoted, ledger_path=str(self.ledger.path),
            unresolved=unresolved,
        )
