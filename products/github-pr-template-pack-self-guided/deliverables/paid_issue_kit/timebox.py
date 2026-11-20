"""A 120-minute timebox with ordered phase gates and an audit trail.

The tool makes one claim only: whether this run finished its six phases inside
120 minutes. It does not claim that a maintainer merges the PR, that a bounty
pays, or that the work is good.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable

PHASES: tuple[tuple[str, int, str], ...] = (
    ("triage", 15, "Read the issue. Confirm amount, acceptance criteria, and one-PR scope."),
    ("reproduce", 20, "Reproduce the failure or restate the requirement in a failing test."),
    ("patch", 40, "Smallest change that makes the test pass. No unrelated edits."),
    ("test", 25, "Run the suite. Capture command, exit code, and output."),
    ("package", 15, "Write the PR body and evidence pack. Check every claim."),
    ("submit", 5, "Open the PR, link the issue, and record the URL."),
)
TOTAL_MINUTES = sum(minutes for _, minutes, _ in PHASES)
PHASE_NAMES = tuple(name for name, _, _ in PHASES)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Timebox:
    def __init__(self, mission: str, clock: Callable[[], datetime] | None = None):
        if not mission or not mission.strip():
            raise ValueError("mission must be a non-empty string")
        self.mission = mission.strip()
        self._clock = clock or utc_now
        self.started_at: str | None = None
        self.checkpoints: list[dict[str, Any]] = []

    def start(self) -> dict[str, Any]:
        if self.started_at is not None:
            raise ValueError("timebox already started")
        self.started_at = self._clock().isoformat()
        return self.status()

    def checkpoint(self, phase: str, note: str = "") -> dict[str, Any]:
        if self.started_at is None:
            raise ValueError("start the timebox before checkpointing")
        expected = self.next_phase()
        if expected is None:
            raise ValueError("all phases are already complete")
        if phase != expected:
            raise ValueError(f"phase order violation: expected {expected!r}, got {phase!r}")
        self.checkpoints.append({"phase": phase, "at": self._clock().isoformat(), "note": note})
        return self.status()

    @property
    def completed(self) -> list[str]:
        return [item["phase"] for item in self.checkpoints]

    def next_phase(self) -> str | None:
        done = set(self.completed)
        for name in PHASE_NAMES:
            if name not in done:
                return name
        return None

    def elapsed_minutes(self, now: datetime | None = None) -> float:
        if self.started_at is None:
            return 0.0
        moment = now or self._clock()
        return max((moment - datetime.fromisoformat(self.started_at)).total_seconds() / 60.0, 0.0)

    def status(self, now: datetime | None = None) -> dict[str, Any]:
        elapsed = self.elapsed_minutes(now)
        planned_done = sum(minutes for name, minutes, _ in PHASES if name in self.completed)
        upcoming = self.next_phase()
        budgets = {name: minutes for name, minutes, _ in PHASES}
        upcoming_minutes = budgets.get(upcoming or "", 0)
        in_phase = max(elapsed - planned_done, 0.0) if upcoming else 0.0
        if self.started_at is None:
            verdict = "NOT STARTED"
        elif elapsed > TOTAL_MINUTES:
            verdict = "CLAIM BROKEN"
        elif upcoming is None:
            verdict = "CLAIM HOLDS"
        else:
            verdict = "IN PROGRESS"
        return {
            "mission": self.mission,
            "verdict": verdict,
            "claim_scope": "six phases inside 120 minutes; merge and payment are excluded",
            "started_at": self.started_at,
            "elapsed_minutes": round(elapsed, 2),
            "remaining_minutes": round(TOTAL_MINUTES - elapsed, 2),
            "total_minutes": TOTAL_MINUTES,
            "completed_phases": self.completed,
            "next_phase": upcoming,
            "next_phase_budget_minutes": upcoming_minutes,
            "minutes_into_next_phase": round(in_phase, 2),
            "next_phase_over_budget": bool(upcoming and in_phase > upcoming_minutes),
            "checkpoints": list(self.checkpoints),
        }

    def report(self, now: datetime | None = None) -> str:
        state = self.status(now)
        lines = [
            f"Mission: {state['mission']}",
            f"Verdict: {state['verdict']} ({state['elapsed_minutes']} of "
            f"{state['total_minutes']} minutes)",
            f"Claim scope: {state['claim_scope']}",
            f"Done: {', '.join(state['completed_phases']) or 'none'}",
            f"Next: {state['next_phase'] or 'none'}",
        ]
        if state["next_phase"]:
            lines.append(
                f"Budget: {state['minutes_into_next_phase']} of "
                f"{state['next_phase_budget_minutes']} minutes in this phase"
            )
            if state["next_phase_over_budget"]:
                lines.append("WARNING: current phase is over budget")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission": self.mission,
            "started_at": self.started_at,
            "checkpoints": list(self.checkpoints),
            "phases": [{"name": name, "minutes": minutes, "purpose": purpose}
                       for name, minutes, purpose in PHASES],
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], clock: Callable[[], datetime] | None = None
    ) -> "Timebox":
        box = cls(str(data.get("mission", "")), clock=clock)
        box.started_at = data.get("started_at")
        box.checkpoints = list(data.get("checkpoints", []))
        return box

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)
            handle.write("\n")

    @classmethod
    def load(cls, path: str, clock: Callable[[], datetime] | None = None) -> "Timebox":
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle), clock=clock)
