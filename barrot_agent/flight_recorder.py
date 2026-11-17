"""Flight Recorder reader and schema.

The recorder was write-only: JSONL files existed and nothing in the repo read
them. This module is the consumer. One record per line, one mission per file.

Required fields are the minimum needed to replay or compare a run later. Extra
fields are kept as-is.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

RECORDER_DIR = Path("results") / "flight_recorder"

REQUIRED_FIELDS = ("task", "round", "role", "asked", "said", "kept", "rejected")


@dataclass
class RecorderBreak:
    path: str
    line: int
    problem: str


def validate_record(record: dict[str, Any]) -> list[str]:
    """Return the list of schema problems for one record. Empty means valid."""
    problems = [f"missing {name}" for name in REQUIRED_FIELDS if name not in record]
    if "round" in record and not isinstance(record["round"], int):
        problems.append("round must be an int")
    if "kept" in record and not isinstance(record["kept"], list):
        problems.append("kept must be a list")
    if "rejected" in record and not isinstance(record["rejected"], list):
        problems.append("rejected must be a list")
    return problems


def load_records(directory: Path | None = None) -> tuple[list[dict[str, Any]], list[RecorderBreak]]:
    """Read every JSONL record under *directory*. Returns (records, breaks)."""
    directory = directory or RECORDER_DIR
    records: list[dict[str, Any]] = []
    breaks: list[RecorderBreak] = []
    if not directory.exists():
        return records, breaks
    for path in sorted(directory.glob("*.jsonl")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                breaks.append(RecorderBreak(str(path), number, f"invalid json: {exc.msg}"))
                continue
            problems = validate_record(record)
            if problems:
                breaks.append(RecorderBreak(str(path), number, "; ".join(problems)))
                continue
            records.append(record)
    return records, breaks


def missions(records: Iterable[dict[str, Any]]) -> dict[str, int]:
    """Count rounds per task, which is what replay needs."""
    counts: dict[str, int] = {}
    for record in records:
        task = str(record.get("task", ""))
        counts[task] = counts.get(task, 0) + 1
    return counts
