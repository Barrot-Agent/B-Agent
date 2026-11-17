"""Witness loop (V2) — the winning transmutation of Barrot's 10-stage loop.

The 10-stage loop (BARROT-12AM-MASTER.md) is prose. Its anti-cheat step asks the
model "if I delete that rule, does the task still work?" and trusts the answer.
That is introspection, not evidence.

This module replaces it with three stages:

    CLAIM -> WITNESS -> LOG

A claim is "rule R transfers to domain D for task T". A witness is an *executed*
ablation: run the task with the rule, run it again without the rule, record
whether the outcome changed. No witness, no record. The ledger is append-only
and hash-chained, so a deleted or edited record is detectable.

States are evidence states, not verdicts:
    SUPPORTED     rule present -> success, rule absent -> failure
    REFUTED       outcome did not change when the rule was removed
    CONTRADICTED  the rule's removal *helped* (rule hurts the target)
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

GENESIS = "0" * 64


class EvidenceRequired(RuntimeError):
    """Raised when a claim is recorded without a valid, executed witness."""


SUPPORTED = "SUPPORTED"
REFUTED = "REFUTED"
CONTRADICTED = "CONTRADICTED"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Claim:
    rule_id: str
    source_domain: str
    target_domain: str
    task: str
    expected: str = "success"

    def validate(self) -> None:
        for field_name in ("rule_id", "source_domain", "target_domain", "task"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"claim.{field_name} must be a non-empty string")


@dataclass(frozen=True)
class Witness:
    rule_id: str
    task_sha256: str
    with_rule: bool
    without_rule: bool
    flipped: bool
    measured_tokens: int
    executed_at: str


def ablate(
    claim: Claim,
    run: Callable[[bool], bool],
    *,
    measured_tokens: int = 0,
) -> Witness:
    """Execute the same task twice: once with the rule, once without it.

    ``run`` receives ``has_rule`` and returns whether the task succeeded. It must
    be deterministic; if it is not, the witness is not evidence.
    """
    claim.validate()
    with_rule = bool(run(True))
    without_rule = bool(run(False))
    return Witness(
        rule_id=claim.rule_id,
        task_sha256=sha256_text(claim.task),
        with_rule=with_rule,
        without_rule=without_rule,
        flipped=with_rule != without_rule,
        measured_tokens=int(measured_tokens),
        executed_at=datetime.now(timezone.utc).isoformat(),
    )


def classify(claim: Claim, witness: Witness) -> str:
    if not witness.flipped:
        return REFUTED
    return SUPPORTED if witness.with_rule else CONTRADICTED


def _check(claim: Claim, witness: Witness) -> None:
    """Reject a witness that does not belong to this claim."""
    if not isinstance(witness, Witness):
        raise EvidenceRequired("a claim cannot be recorded without a witness")
    if witness.rule_id != claim.rule_id:
        raise EvidenceRequired(
            f"witness is for rule {witness.rule_id!r}, claim is {claim.rule_id!r}"
        )
    if witness.task_sha256 != sha256_text(claim.task):
        raise EvidenceRequired("witness was executed against a different task")


def record(
    claim: Claim,
    witness: Witness | None,
    ledger_path: str | os.PathLike[str],
) -> dict:
    """Append one (claim, witness, state) record to the hash-chained ledger."""
    claim.validate()
    _check(claim, witness)
    assert witness is not None  # narrowed by _check for type checkers

    path = Path(ledger_path)
    previous = GENESIS
    if path.exists() and path.stat().st_size:
        last = _last_record(path)
        previous = last["record_sha256"]

    state = classify(claim, witness)
    body = {
        "claim": asdict(claim),
        "witness": asdict(witness),
        "state": state,
        "prev_sha256": previous,
    }
    body["record_sha256"] = sha256_text(
        json.dumps(body, sort_keys=True, separators=(",", ":"))
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(body, sort_keys=True) + "\n")
    return body


def _last_record(path: Path) -> dict:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return {"record_sha256": GENESIS}
    return json.loads(lines[-1])


def read_ledger(ledger_path: str | os.PathLike[str]) -> list[dict]:
    path = Path(ledger_path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_ledger(ledger_path: str | os.PathLike[str]) -> bool:
    """True only if every record's hash matches and the chain is unbroken."""
    previous = GENESIS
    for record_ in read_ledger(ledger_path):
        body = {k: v for k, v in record_.items() if k != "record_sha256"}
        expected = sha256_text(json.dumps(body, sort_keys=True, separators=(",", ":")))
        if body.get("prev_sha256") != previous:
            return False
        if expected != record_.get("record_sha256"):
            return False
        previous = expected
    return True


def assert_supported(ledger_path: str | os.PathLike[str], rule_id: str) -> dict:
    """Fail closed: raise unless ``rule_id`` has a SUPPORTED record."""
    for record_ in read_ledger(ledger_path):
        if record_["claim"]["rule_id"] == rule_id and record_["state"] == SUPPORTED:
            return record_
    raise EvidenceRequired(f"no SUPPORTED witness for rule {rule_id!r}")
