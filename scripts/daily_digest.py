#!/usr/bin/env python3
"""Create a descriptive operations digest without publishing unvalidated signals."""
import json
import time
from datetime import datetime
from pathlib import Path


def _count_recent_content(hours=24):
    directory = Path("content")
    if not directory.exists():
        return 0
    cutoff = time.time() - hours * 3600
    return sum(1 for file in directory.glob("*.md") if file.stat().st_mtime >= cutoff)


def _count_recent_kb(hours=24):
    path = Path("ping-pongings/knowledge-base/log.jsonl")
    if not path.exists():
        return 0
    cutoff = time.time() - hours * 3600
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines()[-500:]:
        try:
            entry = json.loads(line)
            dt = datetime.fromisoformat(entry.get("ingested_at", "").replace("Z", "+00:00"))
            if dt.timestamp() >= cutoff:
                count += 1
        except (TypeError, ValueError, AttributeError):
            continue
    return count


def main():
    lines = [
        "## Barrot Daily Digest",
        "",
        "**XRP forecast status:** NOT_ISSUED",
        "Directional forecasts remain disabled until point-in-time data, leakage-safe "
        "out-of-sample evaluation, baseline comparison, calibration, and drift checks pass.",
        "",
        "**Legacy signal metric:** NOT_EVALUATED",
        "The historical variable-horizon percentage is excluded from predictive-performance claims.",
        "",
        f"**New knowledge base entries (24h):** {_count_recent_kb()}",
        f"**New content drafts (24h):** {_count_recent_content()}",
    ]
    body = "\n".join(lines)
    Path("digest_body.md").write_text(body, encoding="utf-8")
    print(body)


if __name__ == "__main__":
    main()
