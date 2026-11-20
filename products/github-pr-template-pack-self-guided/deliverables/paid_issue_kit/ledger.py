"""Score paid-issue candidates against hard gates.

Pure functions: no network, no GitHub calls, no file writes except through the
caller. Every rejection carries a reason so a buyer can audit the decision
instead of trusting a score.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

SPAM_MARKERS = (
    "bounty-watcher",
    "bounty alert",
    "bounty plaza",
    "bounty radar",
    "[bounty] answer",
)


@dataclass(frozen=True)
class Policy:
    """Thresholds. Defaults mirror scripts/paid_issue_hunter.py in this repo,
    except effort: the product is a 120-minute timebox, so a task estimated over
    three hours is out of scope rather than a "later" item."""

    min_amount_usd: float = 50.0
    max_amount_usd: float = 50_000.0
    min_stars: int = 20
    max_idle_days: int = 120
    min_effective_hourly_usd: float = 30.0
    max_effort_hours: float = 3.0
    min_criteria_chars: int = 20


@dataclass(frozen=True)
class Candidate:
    issue_id: str
    url: str
    repo: str
    title: str
    amount_usd: float | None
    acceptance_criteria: str
    repo_stars: int
    repo_pushed_at: str
    archived: bool = False
    escrow_verified: bool = False
    platform: str = ""
    labels: tuple[str, ...] = ()
    comments: int = 0
    effort_hours: float = 4.0
    payout_fee_fraction: float = 0.0
    expenses_usd: float = 0.0

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Candidate":
        for key in ("issue_id", "url", "repo", "title", "acceptance_criteria"):
            if not isinstance(raw.get(key), str) or not raw[key].strip():
                raise ValueError(f"candidate field {key!r} must be a non-empty string")
        if not isinstance(raw.get("repo_pushed_at"), str) or not raw["repo_pushed_at"]:
            raise ValueError("candidate field 'repo_pushed_at' must be an ISO date string")

        amount = raw.get("amount_usd")
        if amount is not None:
            amount = _number(amount, "amount_usd")

        return cls(
            issue_id=raw["issue_id"].strip(),
            url=raw["url"].strip(),
            repo=raw["repo"].strip(),
            title=raw["title"].strip(),
            amount_usd=amount,
            acceptance_criteria=raw["acceptance_criteria"].strip(),
            repo_stars=_integer(raw.get("repo_stars", 0), "repo_stars"),
            repo_pushed_at=raw["repo_pushed_at"],
            archived=_boolean(raw.get("archived", False), "archived"),
            escrow_verified=_boolean(raw.get("escrow_verified", False), "escrow_verified"),
            platform=str(raw.get("platform", "") or ""),
            labels=tuple(str(label) for label in raw.get("labels", ())),
            comments=_integer(raw.get("comments", 0), "comments"),
            effort_hours=_number(raw.get("effort_hours", 4.0), "effort_hours"),
            payout_fee_fraction=_number(
                raw.get("payout_fee_fraction", 0.0), "payout_fee_fraction"
            ),
            expenses_usd=_number(raw.get("expenses_usd", 0.0), "expenses_usd"),
        )


@dataclass
class Verdict:
    candidate: Candidate
    decision: str
    reasons: list[str] = field(default_factory=list)
    effective_payout_usd: float = 0.0
    effective_hourly_usd: float = 0.0
    confidence: float = 0.0
    score: float = 0.0

    def to_row(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "score": round(self.score, 2),
            "effective_hourly_usd": round(self.effective_hourly_usd, 2),
            "effective_payout_usd": round(self.effective_payout_usd, 2),
            "amount_usd": self.candidate.amount_usd,
            "effort_hours": self.candidate.effort_hours,
            "repo": self.candidate.repo,
            "issue_id": self.candidate.issue_id,
            "url": self.candidate.url,
            "escrow_verified": self.candidate.escrow_verified,
            "reasons": "; ".join(self.reasons),
        }


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def confidence_for(candidate: Candidate) -> float:
    """How much the stated payout can be trusted. Escrow is the only proof."""
    if candidate.escrow_verified:
        return 1.0
    if candidate.platform.strip():
        return 0.9
    if any("bounty" in label.lower() for label in candidate.labels):
        return 0.8
    return 0.7


def evaluate(
    candidate: Candidate,
    policy: Policy | None = None,
    now: datetime | None = None,
) -> Verdict:
    policy = policy or Policy()
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []

    if candidate.amount_usd is None:
        reasons.append("no stated amount")
        amount = 0.0
    else:
        amount = candidate.amount_usd
        if amount < policy.min_amount_usd:
            reasons.append(f"amount below {policy.min_amount_usd:.0f} USD")
        if amount > policy.max_amount_usd:
            reasons.append(f"amount above {policy.max_amount_usd:.0f} USD cap")

    if len(candidate.acceptance_criteria) < policy.min_criteria_chars:
        reasons.append("acceptance criteria missing or too short")
    if candidate.archived:
        reasons.append("repository archived")
    if candidate.repo_stars < policy.min_stars:
        reasons.append(f"repository has fewer than {policy.min_stars} stars")
    if not candidate.url.startswith(("https://", "http://")):
        reasons.append("issue url is not http(s)")

    lowered = candidate.title.lower()
    if any(marker in lowered for marker in SPAM_MARKERS):
        reasons.append("spam marker in title")

    try:
        idle_days = (now - parse_iso(candidate.repo_pushed_at)).total_seconds() / 86400
    except ValueError:
        reasons.append("repo_pushed_at is not a valid ISO date")
        idle_days = policy.max_idle_days + 1
    if idle_days > policy.max_idle_days:
        reasons.append(f"repository idle for more than {policy.max_idle_days} days")

    if candidate.effort_hours <= 0:
        reasons.append("effort_hours must be greater than zero")
    elif candidate.effort_hours > policy.max_effort_hours:
        reasons.append(f"effort above {policy.max_effort_hours:.0f} hour cap")

    fee = min(max(candidate.payout_fee_fraction, 0.0), 1.0)
    payout = max(amount * (1.0 - fee) - max(candidate.expenses_usd, 0.0), 0.0)
    hourly = payout / candidate.effort_hours if candidate.effort_hours > 0 else 0.0
    if hourly < policy.min_effective_hourly_usd:
        reasons.append(f"effective rate below {policy.min_effective_hourly_usd:.0f} USD/hour")

    confidence = confidence_for(candidate)
    score = hourly * confidence
    decision = "GO" if not reasons else "NO-GO"
    return Verdict(
        candidate=candidate,
        decision=decision,
        reasons=reasons,
        effective_payout_usd=payout,
        effective_hourly_usd=hourly,
        confidence=confidence,
        score=score,
    )


def audit(
    candidates: Iterable[Candidate | dict[str, Any]],
    policy: Policy | None = None,
    now: datetime | None = None,
) -> list[Verdict]:
    """Evaluate every candidate, best score first. GO rows before NO-GO rows."""
    policy = policy or Policy()
    now = now or datetime.now(timezone.utc)
    verdicts = []
    for item in candidates:
        candidate = item if isinstance(item, Candidate) else Candidate.from_dict(item)
        verdicts.append(evaluate(candidate, policy, now))
    verdicts.sort(key=lambda v: (v.decision != "GO", -v.score, v.candidate.issue_id))
    return verdicts


def summarize(verdicts: Iterable[Verdict]) -> dict[str, Any]:
    rows = list(verdicts)
    go = [row for row in rows if row.decision == "GO"]
    return {
        "total": len(rows),
        "go": len(go),
        "no_go": len(rows) - len(go),
        "best_go_hourly_usd": round(max((v.effective_hourly_usd for v in go), default=0.0), 2),
        "go_issue_ids": [row.candidate.issue_id for row in go],
    }


def to_csv(verdicts: Iterable[Verdict]) -> str:
    rows = [verdict.to_row() for verdict in verdicts]
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"candidate field {name!r} must be a number")
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"candidate field {name!r} must be a number") from exc


def _integer(value: Any, name: str) -> int:
    number = _number(value, name)
    if number != int(number):
        raise ValueError(f"candidate field {name!r} must be an integer")
    return int(number)


def _boolean(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in ("true", "false"):
        return value.lower() == "true"
    raise ValueError(f"candidate field {name!r} must be a boolean")
