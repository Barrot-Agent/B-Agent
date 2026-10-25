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

def _format_latest_signal(signal):
    status = str(signal.get("signal_status") or "").lower()
    source = str(signal.get("source") or "")
    if status == "news_only":
        return (f"**Latest XRP record:** news-only score {signal.get('score')}/100; "
                f"no model-backed directional forecast. Source: `{source}`")
    if status == "unavailable" or (not status and "sentiment unavailable" in source.lower()):
        return f"**Latest XRP record:** model signal unavailable; no directional forecast issued. Source: `{source}`"
    if status in {"model_only", "model_and_news"}:
        confidence = signal.get("model_confidence", signal.get("confidence", "—"))
        return (f"**Latest XRP sentiment:** score {signal.get('score')}/100, model confidence {confidence}, "
                f"status {status}; not a calibrated price forecast. Source: `{source}`")
    return (f"**Latest XRP record:** legacy status unknown; score {signal.get('score')}/100 is not treated as a forecast. "
            f"Source: `{source}`")

def main():
    signal = _read_json("web/latest_signal.json")
    accuracy = _read_json("web/signal_accuracy.json")
    lines = ["## Barrot Daily Digest", ""]
    if signal:
        lines.append(_format_latest_signal(signal))
    else:
        lines.append("**Latest XRP record:** none yet")
    lines.append("")
    checked = accuracy.get("checked_count", 0)
    if checked:
        lines.append(f"**Signal accuracy:** {accuracy.get('accuracy_pct')}% correct over {checked} checked signals")
    else:
        lines.append("**Signal accuracy:** no signals have crossed the 24h check window yet")
    lines.append("")
    lines.append(f"**New knowledge base entries (24h):** {_count_recent_kb()}")
    lines.append(f"**New content drafts (24h):** {_count_recent_content()}")
    body = "\n".join(lines)
    Path("digest_body.md").write_text(body, encoding="utf-8")
    print(body)

if __name__ == "__main__":
    main()
