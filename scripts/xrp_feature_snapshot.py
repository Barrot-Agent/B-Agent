#!/usr/bin/env python3
"""Build a provenance-bound, point-in-time XRP news-feature snapshot.

This script performs deterministic local accounting only. It does not issue a
price forecast, call a model, or mutate the source JSONL log.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

KB_DIR = Path("ping-pongings/knowledge-base")
LOG_PATH = KB_DIR / "log.jsonl"
CONFIG_PATH = KB_DIR / "config.json"
OUT_PATH = KB_DIR / "xrp_feature_snapshot.json"
STAGE_DIR = Path("artifacts/xrp_feature_store")

SENTIMENT_WEIGHT = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}


def parse_utc(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def parse_publication_timestamp(entry):
    """Parse normalized or legacy RSS publication time; reject naive timestamps."""
    for raw in (entry.get("published_at_utc"), entry.get("published")):
        parsed = parse_utc(raw)
        if parsed is not None:
            return parsed
        if not isinstance(raw, str) or not raw.strip():
            continue
        try:
            parsed = parsedate_to_datetime(raw.strip())
        except (TypeError, ValueError, OverflowError):
            continue
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc)
    return None


def sha256_file(path):
    path = Path(path)
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path):
    entries = []
    malformed = 0
    path = Path(path)
    if not path.exists():
        return entries, malformed
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                malformed += 1
                continue
            if not isinstance(value, dict):
                malformed += 1
                continue
            entries.append(value)
    return entries, malformed


def _weighted_score(numerator, denominator):
    if denominator <= 0:
        return None
    return int(round((numerator / denominator + 1.0) * 50.0))


def build_snapshot(log_path=LOG_PATH, config_path=CONFIG_PATH, now=None,
                   restore_status=None, restore_run_id=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(timezone.utc)
    recent_start = now - timedelta(hours=24)
    prior_start = now - timedelta(hours=48)

    entries, malformed = load_jsonl(log_path)
    url_counts = Counter()
    feed_counts = Counter()
    missing_timestamp = 0
    missing_published_timestamp = 0
    missing_url = 0
    future_timestamp = 0
    future_published_timestamp = 0
    recent_entries = 0
    prior_entries = 0
    recent_published_entries = 0
    prior_published_entries = 0
    distilled_entries = 0
    undistilled_entries = 0
    missing_relevance = 0
    invalid_sentiment = 0
    recent_relevant = 0
    recent_num = recent_den = 0.0
    prior_num = prior_den = 0.0
    recent_entities = Counter()
    all_entities = Counter()
    latest_ingested = None
    earliest_ingested = None
    latest_published = None
    earliest_published = None
    recent_ingested_relevant = 0

    for entry in entries:
        url = entry.get("url")
        if isinstance(url, str) and url.strip():
            url_counts[url.strip()] += 1
        else:
            missing_url += 1

        feed = entry.get("feed") or entry.get("source") or "unknown"
        feed_counts[str(feed)] += 1

        ts = parse_utc(entry.get("ingested_at"))
        if ts is None:
            missing_timestamp += 1
        else:
            latest_ingested = ts if latest_ingested is None else max(latest_ingested, ts)
            earliest_ingested = ts if earliest_ingested is None else min(earliest_ingested, ts)
            if ts > now + timedelta(minutes=5):
                future_timestamp += 1
            elif recent_start <= ts <= now:
                recent_entries += 1
            elif prior_start <= ts < recent_start:
                prior_entries += 1

        pub_ts = parse_publication_timestamp(entry)
        if pub_ts is None:
            missing_published_timestamp += 1
        else:
            latest_published = pub_ts if latest_published is None else max(latest_published, pub_ts)
            earliest_published = pub_ts if earliest_published is None else min(earliest_published, pub_ts)
            if pub_ts > now:
                future_published_timestamp += 1
            elif recent_start <= pub_ts <= now:
                recent_published_entries += 1
            elif prior_start <= pub_ts < recent_start:
                prior_published_entries += 1

        distill = entry.get("distill")
        if not entry.get("distilled") or not isinstance(distill, dict):
            undistilled_entries += 1
            continue
        distilled_entries += 1

        sentiment = distill.get("sentiment")
        weight = SENTIMENT_WEIGHT.get(sentiment)
        if weight is None:
            invalid_sentiment += 1

        try:
            relevance = float(distill.get("xrp_relevance"))
        except (TypeError, ValueError):
            relevance = None
        if relevance is None or not math.isfinite(relevance) or relevance < 0 or relevance > 1:
            missing_relevance += 1
            relevance = None

        entities = distill.get("entities", [])
        if not isinstance(entities, list):
            entities = []
        clean_entities = {
            str(entity).strip()
            for entity in entities
            if isinstance(entity, str) and entity.strip()
        }
        all_entities.update(clean_entities)

        if ts is not None and recent_start <= ts <= now:
            if relevance is not None and relevance > 0:
                recent_ingested_relevant += 1

        if pub_ts is not None and recent_start <= pub_ts <= now:
            recent_entities.update(clean_entities)
            if relevance is not None and relevance > 0:
                recent_relevant += 1
                if weight is not None:
                    recent_num += weight * relevance
                    recent_den += relevance
        elif pub_ts is not None and prior_start <= pub_ts < recent_start:
            if relevance is not None and relevance > 0 and weight is not None:
                prior_num += weight * relevance
                prior_den += relevance

    duplicate_urls = sum(count - 1 for count in url_counts.values() if count > 1)
    recent_score = _weighted_score(recent_num, recent_den)
    prior_score = _weighted_score(prior_num, prior_den)
    shift = recent_score - prior_score if recent_score is not None and prior_score is not None else None

    if (malformed or missing_timestamp or missing_published_timestamp or missing_url
            or future_timestamp or future_published_timestamp or duplicate_urls
            or missing_relevance or invalid_sentiment):
        status = "DEGRADED"
    elif recent_published_entries == 0:
        status = "STALE"
    elif undistilled_entries:
        status = "PARTIAL"
    else:
        status = "OK"

    snapshot = {
        "schema_version": "1.0",
        "captured_at_utc": now.isoformat(),
        "data_cutoff_utc": now.isoformat(),
        "status": status,
        "restore_status": restore_status or os.getenv("XRP_STORE_RESTORE_STATUS", "UNKNOWN"),
        "restore_run_id": restore_run_id or os.getenv("XRP_STORE_RESTORE_RUN_ID") or None,
        "source_files": {
            "log_path": str(log_path),
            "log_sha256": sha256_file(log_path),
            "config_path": str(config_path),
            "config_sha256": sha256_file(config_path),
        },
        "entries_total": len(entries),
        "unique_url_count": len(url_counts),
        "duplicate_url_count": duplicate_urls,
        "malformed_jsonl_lines": malformed,
        "missing_ingested_at": missing_timestamp,
        "missing_published_at": missing_published_timestamp,
        "missing_url": missing_url,
        "future_ingested_at": future_timestamp,
        "future_published_at": future_published_timestamp,
        "earliest_ingested_at_utc": earliest_ingested.isoformat() if earliest_ingested else None,
        "latest_ingested_at_utc": latest_ingested.isoformat() if latest_ingested else None,
        "earliest_published_at_utc": earliest_published.isoformat() if earliest_published else None,
        "latest_published_at_utc": latest_published.isoformat() if latest_published else None,
        "recent_24h_entries": recent_entries,
        "prior_24h_entries": prior_entries,
        "recent_24h_published_entries": recent_published_entries,
        "prior_24h_published_entries": prior_published_entries,
        "distilled_entries": distilled_entries,
        "undistilled_entries": undistilled_entries,
        "missing_or_invalid_xrp_relevance": missing_relevance,
        "invalid_sentiment_labels": invalid_sentiment,
        "recent_24h_xrp_relevant_entries": recent_relevant,
        "recent_24h_ingested_xrp_relevant_entries": recent_ingested_relevant,
        "recent_24h_weighted_sentiment_score": recent_score,
        "prior_24h_weighted_sentiment_score": prior_score,
        "sentiment_shift_points": shift,
        "entries_by_feed": dict(sorted(feed_counts.items())),
        "recent_top_entities": [
            {"entity": entity, "mentions": count}
            for entity, count in recent_entities.most_common(20)
        ],
        "all_time_top_entities": [
            {"entity": entity, "mentions": count}
            for entity, count in all_entities.most_common(20)
        ],
        "forecast_status": "NOT_ISSUED",
        "notes": [
            "Ingested-at windows measure capture/arrival time and are retained for ingestion diagnostics.",
            "Publisher publication timestamps drive recent/prior sentiment and entity windows; legacy RFC822 published fields are parsed when normalized timestamps are absent.",
            "Entries with missing or future publication timestamps are excluded from publication-time windows and degrade the snapshot.",
            "Entity and sentiment counts are descriptive features, not causal evidence or price forecasts.",
            "This snapshot does not establish source independence; feed URLs are retained for later corroboration.",
        ],
    }
    return snapshot


def write_snapshot(snapshot, log_path=LOG_PATH, config_path=CONFIG_PATH,
                   output_path=OUT_PATH, stage_dir=STAGE_DIR):
    output_path = Path(output_path)
    stage_dir = Path(stage_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    stage_dir.mkdir(parents=True, exist_ok=True)
    for source, name in (
        (Path(log_path), "log.jsonl"),
        (Path(config_path), "config.json"),
        (output_path, "xrp_feature_snapshot.json"),
        (Path("distillation.log"), "distillation.log"),
    ):
        if source.exists() and source.is_file():
            shutil.copy2(source, stage_dir / name)


def main():
    snapshot = build_snapshot()
    write_snapshot(snapshot)
    print(json.dumps({
        "status": snapshot["status"],
        "entries_total": snapshot["entries_total"],
        "recent_24h_entries": snapshot["recent_24h_entries"],
        "recent_24h_xrp_relevant_entries": snapshot["recent_24h_xrp_relevant_entries"],
        "undistilled_entries": snapshot["undistilled_entries"],
        "malformed_jsonl_lines": snapshot["malformed_jsonl_lines"],
        "restore_status": snapshot["restore_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
