#!/usr/bin/env python3
"""
Barrot self-scheduling: reads the knowledge base, detects stale sources,
and opens a gated barrot-task issue describing the gap. Never touches
code or files directly -- only creates an issue for the existing
barrot-agent.yml pipeline to pick up.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone

LOG = "ping-pongings/knowledge-base/log.jsonl"

THRESHOLDS = {
    "rss": 6,
    "academic": 168,
    "ping_pong_cycles": 48,
    "video_audio": 168,
}

def load_entries():
    entries = []
    try:
        with open(LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"ERROR: {LOG} not found", file=sys.stderr)
        sys.exit(1)
    return entries

def latest_timestamp_per_source(entries):
    latest = {}
    for e in entries:
        source = e.get("source")
        ts = e.get("timestamp") or e.get("date") or e.get("ingested_at")
        if not source or not ts:
            continue
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except ValueError:
            continue
        if source not in latest or dt > latest[source]:
            latest[source] = dt
    return latest

def hours_since(dt):
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).total_seconds() / 3600

def existing_open_gap_issues():
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--label", "barrot-task", "--state", "open",
             "--search", "[self-scheduled]", "--json", "title"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"WARN: could not check existing issues: {e}", file=sys.stderr)
    return []

def open_gap_issue(source, hours_stale, threshold):
    title = f"[self-scheduled] {source} feed stale ({hours_stale:.0f}h, threshold {threshold}h)"
    body = (
        f"Barrot self-scheduling detected a gap.\n\n"
        f"**Source:** {source}\n"
        f"**Hours since last entry:** {hours_stale:.1f}\n"
        f"**Threshold:** {threshold}h\n\n"
        f"Task: investigate why the {source} ingestion pipeline hasn't produced "
        f"a new knowledge-base entry within the threshold, and fix or re-trigger it. "
        f"This issue was opened automatically -- verify the underlying workflow "
        f"(schedule, API limits, credentials) before making changes."
    )
    create_result = subprocess.run(
        ["gh", "issue", "create", "--title", title, "--body", body],
        capture_output=True, text=True
    )
    if create_result.returncode != 0:
        print(f"FAILED to open issue for {source}: {create_result.stderr}", file=sys.stderr)
        return

    issue_url = create_result.stdout.strip()
    print(f"Opened issue: {title}")
    print(issue_url)

    label_result = subprocess.run(
        ["gh", "issue", "edit", issue_url, "--add-label", "barrot-task"],
        capture_output=True, text=True
    )
    if label_result.returncode != 0:
        print(f"FAILED to label issue {issue_url}: {label_result.stderr}", file=sys.stderr)

def main():
    entries = load_entries()
    if not entries:
        print("No entries in knowledge base -- nothing to check.")
        return

    latest = latest_timestamp_per_source(entries)
    existing = existing_open_gap_issues()
    existing_titles = {i["title"] for i in existing}

    gaps_found = 0
    for source, threshold in THRESHOLDS.items():
        if source not in latest:
            continue
        stale_hours = hours_since(latest[source])
        if stale_hours > threshold:
            if any(source in t for t in existing_titles):
                print(f"Gap already tracked for {source}, skipping duplicate issue.")
                continue
            open_gap_issue(source, stale_hours, threshold)
            gaps_found += 1

    if gaps_found == 0:
        print("No gaps detected -- all tracked sources within threshold.")

if __name__ == "__main__":
    main()
