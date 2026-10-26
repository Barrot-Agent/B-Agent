#!/usr/bin/env python3
"""List workflows whose latest run within a UTC window failed.

Uses GitHub's paginated Actions API. API/JSON/pagination errors fail closed; they
must never be interpreted as an empty failure list.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping

UTC = timezone.utc


class ScanError(RuntimeError):
    """The run scan is incomplete or its evidence is invalid."""


def parse_timestamp(value: Any, field: str = "created_at") -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ScanError(f"{field}: missing timestamp")
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ScanError(f"{field}: invalid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ScanError(f"{field}: timezone is required")
    return parsed.astimezone(UTC)


def flatten_pages(pages: Any) -> list[dict[str, Any]]:
    if not isinstance(pages, list) or not pages:
        raise ScanError("Actions API pagination returned no page objects")
    counts = set()
    records: list[dict[str, Any]] = []
    for index, page in enumerate(pages):
        if not isinstance(page, Mapping):
            raise ScanError(f"page {index}: object required")
        count = page.get("total_count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ScanError(f"page {index}: invalid total_count")
        counts.add(count)
        runs = page.get("workflow_runs")
        if not isinstance(runs, list):
            raise ScanError(f"page {index}: workflow_runs array required")
        if not all(isinstance(run, Mapping) for run in runs):
            raise ScanError(f"page {index}: malformed workflow record")
        records.extend(dict(run) for run in runs)
    if len(counts) != 1:
        raise ScanError("pagination total_count changed during scan; retry required")
    expected = next(iter(counts))
    if expected != len(records):
        raise ScanError(f"incomplete pagination: API reports {expected} runs, received {len(records)}")
    ids = [r.get("id") for r in records]
    if any(i is None for i in ids) or len(set(ids)) != len(ids):
        raise ScanError("missing or duplicate workflow run IDs")
    return records


def select_latest_failures(
    records: Iterable[Mapping[str, Any]],
    *,
    cutoff: datetime,
    now: datetime,
    future_tolerance_seconds: float = 60.0,
) -> list[dict[str, str]]:
    cutoff = cutoff.astimezone(UTC)
    now = now.astimezone(UTC)
    latest: dict[str, tuple[datetime, int, Mapping[str, Any]]] = {}
    for record in records:
        name = record.get("name") or record.get("workflowName")
        conclusion = record.get("conclusion")
        created_raw = record.get("created_at") or record.get("createdAt")
        run_id = record.get("id")
        url = record.get("html_url") or record.get("url")
        if not isinstance(name, str) or not name.strip():
            raise ScanError("workflow record has no name")
        if not isinstance(run_id, int) or isinstance(run_id, bool):
            raise ScanError(f"{name}: workflow record has no numeric run ID")
        if not isinstance(conclusion, (str, type(None))):
            raise ScanError(f"{name}: invalid conclusion")
        if not isinstance(url, str) or not url.strip():
            raise ScanError(f"{name}: workflow record has no URL")
        created = parse_timestamp(created_raw, f"{name}.created_at")
        if created > now + timedelta(seconds=future_tolerance_seconds):
            raise ScanError(f"{name}: run timestamp is materially in the future")
        previous = latest.get(name)
        key = (created, run_id)
        if previous is None or key > (previous[0], previous[1]):
            latest[name] = (created, run_id, record)

    result = []
    for name, (created, _run_id, record) in latest.items():
        if created >= cutoff and record.get("conclusion") == "failure":
            result.append({
                "workflow_name": name,
                "url": str(record.get("html_url") or record.get("url")),
                "created_at_utc": created.isoformat().replace("+00:00", "Z"),
            })
    return sorted(result, key=lambda item: item["workflow_name"].casefold())


def fetch_recent_runs(repo: str, cutoff: datetime) -> list[dict[str, Any]]:
    cutoff_text = cutoff.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    endpoint = f"repos/{repo}/actions/runs?per_page=100&created=%3E%3D{cutoff_text}"
    try:
        completed = subprocess.run(
            ["gh", "api", "--paginate", "--slurp", endpoint],
            check=True, capture_output=True, text=True, timeout=90,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ScanError(f"GitHub Actions API request failed: {exc}") from exc
    try:
        pages = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ScanError("GitHub Actions API returned invalid JSON") from exc
    return flatten_pages(pages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repository")
    parser.add_argument("--hours", type=float, default=24.0)
    args = parser.parse_args(argv)
    if not args.repo or "/" not in args.repo or args.hours <= 0:
        parser.error("--repo must be owner/repository and --hours must be positive")
    now = datetime.now(UTC)
    cutoff = now - timedelta(hours=args.hours)
    try:
        runs = fetch_recent_runs(args.repo, cutoff)
        results = select_latest_failures(runs, cutoff=cutoff, now=now)
    except ScanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(results, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
