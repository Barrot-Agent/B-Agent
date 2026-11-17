#!/usr/bin/env python3
"""Cross-artifact consistency checks for Barrot's published state.

Read-only. No network. Every check here exists because the repo actually
shipped a state that violated it:

  * web/paper_trading_state.json held position_size > 0 with
    position_product = null and an avg_entry_price, and nothing noticed
    (wishlist item 6)
  * web/latest_signal.json published confidence 0.0 with score 44 while
    scripts/signal_summary.py:135 requires 0 < confidence (item 1)
  * that signal was 18.6 days old and every reader treated it as current
    (item 2)
  * web/signal_accuracy.json reports 45.5% over 1697 samples with no floor
    anywhere in the trading path (item 3)

Exit code is 1 when any ERROR is found, so this can gate CI (item 30/49).
A violation is a dict: {"artifact", "code", "level", "detail"}.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_SIGNAL_AGE_S = 3600
MIN_ACCURACY_PCT = 52.0
MIN_ACCURACY_SAMPLES = 200

ERROR = "error"
WARN = "warn"


def _violation(artifact: str, code: str, detail: str, level: str = ERROR) -> dict:
    return {"artifact": artifact, "code": code, "level": level, "detail": detail}


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(float(value)):
        return None
    return float(value)


# --------------------------------------------------------------- paper state


def check_paper_state(state: dict, artifact: str = "web/paper_trading_state.json") -> list[dict]:
    out: list[dict] = []

    size = _number(state.get("position_size"))
    cash = _number(state.get("cash_usd"))
    entry = _number(state.get("avg_entry_price"))
    product = state.get("position_product")

    if size is None or size < 0:
        out.append(_violation(artifact, "position_size_invalid", f"position_size={state.get('position_size')!r}"))
    if cash is None or cash < 0:
        out.append(_violation(artifact, "cash_invalid", f"cash_usd={state.get('cash_usd')!r}"))

    has_position = bool(size) and size > 0
    if has_position:
        if not isinstance(product, str) or not product.strip():
            out.append(_violation(
                artifact, "position_without_product",
                f"position_size={size} but position_product={product!r} — the book cannot be sold",
            ))
        if entry is None or entry <= 0:
            out.append(_violation(
                artifact, "position_without_entry",
                f"position_size={size} but avg_entry_price={state.get('avg_entry_price')!r}",
            ))
    else:
        if isinstance(product, str) and product.strip():
            out.append(_violation(
                artifact, "product_without_position",
                f"position_product={product!r} but position_size={size!r}",
            ))
        if entry is not None and entry > 0:
            out.append(_violation(
                artifact, "entry_without_position",
                f"avg_entry_price={entry} with no position",
            ))

    count = state.get("trade_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        out.append(_violation(artifact, "trade_count_invalid", f"trade_count={count!r}"))

    return out


# -------------------------------------------------------------------- signal


def check_signal(
    signal: dict,
    *,
    now: float | None = None,
    max_age_s: int = DEFAULT_MAX_SIGNAL_AGE_S,
    artifact: str = "web/latest_signal.json",
) -> list[dict]:
    out: list[dict] = []
    now = time.time() if now is None else now

    if not isinstance(signal, dict) or not signal:
        return [_violation(artifact, "signal_missing", "signal file is empty or not an object")]

    score = _number(signal.get("score"))
    if score is None or not 0 <= score <= 100:
        out.append(_violation(artifact, "score_invalid", f"score={signal.get('score')!r}"))

    confidence = _number(signal.get("confidence"))
    if confidence is None:
        out.append(_violation(artifact, "confidence_invalid", f"confidence={signal.get('confidence')!r}"))
    elif not 0 < confidence <= 1:
        # scripts/signal_summary.py:135 already rejects this shape; publishing it
        # means one validator is not on the write path.
        out.append(_violation(
            artifact, "confidence_not_publishable",
            f"confidence={confidence} (must be 0 < c <= 1) with score={score}",
        ))

    generated = _number(signal.get("generated_at_unix"))
    timestamp = signal.get("timestamp")
    if generated is None:
        out.append(_violation(artifact, "generated_at_missing", f"generated_at_unix={signal.get('generated_at_unix')!r}"))
    else:
        age = now - generated
        if age < -300:
            out.append(_violation(artifact, "generated_at_in_future", f"age={age:.0f}s"))
        elif age > max_age_s:
            out.append(_violation(
                artifact, "signal_stale",
                f"age={age/86400:.1f} days > max {max_age_s}s",
            ))
    if not isinstance(timestamp, str) or not timestamp.strip():
        out.append(_violation(artifact, "timestamp_missing", f"timestamp={timestamp!r}"))

    source = signal.get("source")
    if not isinstance(source, str) or not source.strip():
        out.append(_violation(artifact, "source_missing", f"source={source!r}"))

    return out


# ------------------------------------------------------------------ accuracy


def check_accuracy(
    accuracy: dict,
    *,
    min_pct: float = MIN_ACCURACY_PCT,
    min_samples: int = MIN_ACCURACY_SAMPLES,
    artifact: str = "web/signal_accuracy.json",
) -> list[dict]:
    out: list[dict] = []
    checked = accuracy.get("checked_count")
    correct = accuracy.get("correct_count")
    pct = _number(accuracy.get("accuracy_pct"))

    for name, value in (("checked_count", checked), ("correct_count", correct)):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            out.append(_violation(artifact, f"{name}_invalid", f"{name}={value!r}"))
    if pct is None:
        out.append(_violation(artifact, "accuracy_pct_invalid", f"accuracy_pct={accuracy.get('accuracy_pct')!r}"))
        return out

    if isinstance(checked, int) and isinstance(correct, int) and checked > 0:
        if correct > checked:
            out.append(_violation(artifact, "correct_exceeds_checked", f"{correct} > {checked}"))
        else:
            recomputed = round(100 * correct / checked, 1)
            if abs(recomputed - pct) > 0.15:
                out.append(_violation(
                    artifact, "accuracy_mismatch",
                    f"stored {pct}% but counts give {recomputed}%",
                ))
    if pct < min_pct and (checked or 0) >= min_samples:
        out.append(_violation(
            artifact, "below_chance_floor",
            f"accuracy {pct}% over {checked} samples < {min_pct}% floor — trading on this is negative EV",
        ))
    return out


# --------------------------------------------------------------------- all


def verify(root: Path = REPO_ROOT, now: float | None = None) -> list[dict]:
    findings: list[dict] = []
    root = Path(root)

    paper = root / "web" / "paper_trading_state.json"
    if paper.exists():
        findings += check_paper_state(json.loads(paper.read_text()))

    signal = root / "web" / "latest_signal.json"
    if signal.exists():
        findings += check_signal(json.loads(signal.read_text()), now=now)

    accuracy = root / "web" / "signal_accuracy.json"
    if accuracy.exists():
        findings += check_accuracy(json.loads(accuracy.read_text()))

    return findings


def _print(findings: Iterable[dict]) -> None:
    findings = list(findings)
    if not findings:
        print("verify_artifacts: OK — no violations")
        return
    for f in findings:
        print(f"[{f['level'].upper():5s}] {f['artifact']}  {f['code']}\n        {f['detail']}")
    errors = sum(1 for f in findings if f["level"] == ERROR)
    print(f"\n{len(findings)} finding(s), {errors} error(s)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check published artifacts for internal contradictions.")
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--now", type=float, default=None, help="override current unix time (tests)")
    args = ap.parse_args(argv)

    findings = verify(args.root, now=args.now)
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        _print(findings)
    return 1 if any(f["level"] == ERROR for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
