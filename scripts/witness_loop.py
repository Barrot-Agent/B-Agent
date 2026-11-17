"""V3 — WITNESS LEDGER, hardened.

Same public API as V2, three changes that matter when the ledger grows:

1. `verify_ledger` is single-pass and streaming: one read, one json parse per
   line, one hash per line, O(1) memory. V2 built the full list first and then
   re-serialised every record twice.
2. Appends go through os.open(O_APPEND) + os.write + os.fsync, so two processes
   recording at once cannot interleave a half line, and a crash cannot leave a
   record that the chain claims exists.
3. `iter_ledger` lets `assert_supported` stop at the first match instead of
   loading the whole ledger.

Every refusal V2 makes, V3 makes identically.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator

GENESIS = "0" * 64


class EvidenceRequired(RuntimeError):
    """Raised when a claim is recorded without a valid, executed witness."""


SUPPORTED = "SUPPORTED"
REFUTED = "REFUTED"
CONTRADICTED = "CONTRADICTED"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(body: dict) -> str:
    return json.dumps(body, sort_keys=True, separators=(",", ":"))


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
    """Execute the same task twice: once with the rule, once without it."""
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
    if not isinstance(witness, Witness):
        raise EvidenceRequired("a claim cannot be recorded without a witness")
    if witness.rule_id != claim.rule_id:
        raise EvidenceRequired(
            f"witness is for rule {witness.rule_id!r}, claim is {claim.rule_id!r}"
        )
    if witness.task_sha256 != sha256_text(claim.task):
        raise EvidenceRequired("witness was executed against a different task")


def _append_durable(path: Path, line: str) -> None:
    """One atomic, fsynced append. O_APPEND makes concurrent writes non-overlapping."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)


def record(
    claim: Claim,
    witness: Witness | None,
    ledger_path: str | os.PathLike[str],
) -> dict:
    """Append one (claim, witness, state) record to the hash-chained ledger."""
    claim.validate()
    _check(claim, witness)
    assert witness is not None

    path = Path(ledger_path)
    previous = GENESIS
    if path.exists() and path.stat().st_size:
        tail = _tail_record(path)
        previous = tail["record_sha256"]

    body = {
        "claim": asdict(claim),
        "witness": asdict(witness),
        "state": classify(claim, witness),
        "prev_sha256": previous,
    }
    body["record_sha256"] = sha256_text(_canonical(body))
    _append_durable(path, json.dumps(body, sort_keys=True) + "\n")
    return body


def _tail_record(path: Path) -> dict:
    """Last non-empty line only — never parse the whole file to append one record."""
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        chunk = min(size, 65536)
        handle.seek(size - chunk)
        block = handle.read().splitlines()
    for raw in reversed(block):
        if raw.strip():
            return json.loads(raw)
    return {"record_sha256": GENESIS}


def iter_ledger(ledger_path: str | os.PathLike[str]) -> Iterator[dict]:
    path = Path(ledger_path)
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def read_ledger(ledger_path: str | os.PathLike[str]) -> list[dict]:
    return list(iter_ledger(ledger_path))


def verify_ledger(ledger_path: str | os.PathLike[str]) -> bool:
    """True only if every record's hash matches and the chain is unbroken."""
    previous = GENESIS
    for record_ in iter_ledger(ledger_path):
        stored = record_.get("record_sha256")
        body = {k: v for k, v in record_.items() if k != "record_sha256"}
        if body.get("prev_sha256") != previous:
            return False
        if sha256_text(_canonical(body)) != stored:
            return False
        previous = stored
    return True


def assert_supported(ledger_path: str | os.PathLike[str], rule_id: str) -> dict:
    """Fail closed: raise unless ``rule_id`` has a SUPPORTED record."""
    for record_ in iter_ledger(ledger_path):
        if record_["claim"]["rule_id"] == rule_id and record_["state"] == SUPPORTED:
            return record_
    raise EvidenceRequired(f"no SUPPORTED witness for rule {rule_id!r}")
