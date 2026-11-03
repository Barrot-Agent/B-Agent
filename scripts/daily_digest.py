#!/usr/bin/env python3
import json
import time
from datetime import datetime
from pathlib import Path

def _read_json(path):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _count_recent_content(hours=24):
    d = Path("content")
    if not d.exists():
        return 0
    cutoff = time.time() - hours * 3600
    return sum(1 for f in d.glob("*.md") if f.stat().st_mtime >= cutoff)

def _count_recent_kb(hours=24):
    p = Path("ping-pongings/knowledge-base/log.jsonl")
    if not p.exists():
        return 0
    cutoff = time.time() - hours * 3600
    count = 0
    for line in p.read_text(encoding="utf-8").splitlines()[-500:]:
        try:
            e = json.loads(line)
            dt = datetime.fromisoformat(e.get("ingested_at", "").replace("Z", "+00:00"))
            if dt.timestamp() >= cutoff:
                count += 1
        except Exception:
            continue
    return count

def main():
    signal = _read_json("web/latest_signal.json")
    lines = ["## Barrot Daily Digest", ""]

    if signal.get("signal_kind") == "sentiment_feature_only" and float(signal.get("confidence", 0) or 0) > 0:
        lines.append(f"**Latest XRP sentiment feature (not a price forecast):** label {signal.get('sentiment_label', 'unclassified')}, score {signal.get('score')}/100, source `{signal.get('source')}`")
        lines.append("**Confidence semantics:** uncalibrated model-reported sentiment confidence; not a probability of price direction.")
    else:
        lines.append("**Latest XRP sentiment feature:** unavailable or unclassified")

    lines.append("**Directional forecast status:** NOT_ISSUED — this pipeline does not publish a validated fixed-horizon price forecast.")
    lines.append(f"**New knowledge base entries (24h):** {_count_recent_kb()}")
    lines.append(f"**New content drafts (24h):** {_count_recent_content()}")
    body = "\\n".join(lines)
    Path("digest_body.md").write_text(body, encoding="utf-8")
    print(body)

if __name__ == "__main__":
    main()
