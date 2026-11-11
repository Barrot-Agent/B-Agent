#!/usr/bin/env python3
"""transmute.py — Barrot's automated transmutation loop.

Takes a target file, evaluates 2-3 candidate variants against it, scores them
(test pass rate > speed > brevity), keeps the winner, deletes the losers, and
appends the full result to results/transmute_log.json.

Usage:
    python scripts/transmute.py TARGET.py [--variant V1.py --variant V2.py]
        [--tests tests/test_target.py ...] [--runner auto|pytest|unittest|none]
        [--log PATH] [--keep-losers] [--cwd DIR]

Rules implemented (see .opencode/agent/barrot.md, TRANSMUTE RULES):
  1. Never settle for the first version: baseline competes against variants.
  2. Score = tests, then speed, then lines. Nothing subjective.
  3. Run before AND after: every candidate is compiled and tested.
  4. Git is the safety net: commit a checkpoint before invoking this script.
  5. Losers are deleted (unless --keep-losers archives them).
  6. No tests for the target? Scope tests with --tests or write them first.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = REPO_ROOT / "results" / "transmute_log.json"
OUTPUT_TAIL_CHARS = 2000
SCORE_TEST_WEIGHT = 1_000_000  # 1% of lost tests can never be bought back by speed.
TIE_EPS = 100.0  # score points (~100ms): sub-100ms deltas are timing noise; on a
# near-tie the VARIANT wins over baseline (rule 1: never settle for the first version).


# ---------------------------------------------------------------- primitives


def run_py_compile(path: Path, cwd: Path):
    """Syntax gate. Returns (ok, wall_ms, output_tail)."""
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=120,
    )
    wall_ms = int((time.perf_counter() - start) * 1000)
    return proc.returncode == 0, wall_ms, _tail(proc.stdout + proc.stderr)


def _tail(text: str) -> str:
    return text[-OUTPUT_TAIL_CHARS:]


def pytest_available() -> bool:
    try:
        import pytest  # noqa: F401
    except ImportError:
        return False
    return True


def run_tests(runner: str, test_paths: list[Path], cwd: Path, target_dir: Path,
              repeats: int = 1):
    """Run the test suite `repeats` times; keep the best run (max rate, min wall).

    Falls back to unittest when runner is 'auto' and pytest is not importable.
    Min-of-N suppresses subprocess startup jitter in the timing measurement.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in [str(cwd), str(target_dir), env.get("PYTHONPATH", "")] if p
    )

    if runner in ("auto", "pytest") and pytest_available():
        cmd = [
            sys.executable, "-m", "pytest", "-o", "addopts=", "-q",
            "--no-header", "-p", "no:cacheprovider", *[str(p) for p in test_paths],
        ]
        parser = _parse_pytest
    elif runner in ("auto", "pytest"):
        runner = "unittest"  # auto fallback
    if runner == "unittest":
        cmd = _unittest_cmd(test_paths)
        parser = _parse_unittest
    elif runner == "none":
        return {"ok": None, "rate": None, "passed": None, "total": None,
                "wall_ms": 0, "cmd": None, "tail": "test runner disabled"}

    runs = []
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        proc = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(cwd), env=env, timeout=1800,
        )
        wall_ms = int((time.perf_counter() - start) * 1000)
        tail = _tail(proc.stdout + proc.stderr)
        passed, total = parser(tail)
        ok = proc.returncode == 0
        rate = (passed / total) if total else (1.0 if ok else 0.0)
        runs.append({"ok": ok, "rate": rate, "passed": passed, "total": total,
                     "wall_ms": wall_ms, "cmd": " ".join(cmd), "tail": tail})
    return max(runs, key=lambda r: (r["rate"], -r["wall_ms"]))


def _unittest_cmd(test_paths: list[Path]) -> list[str]:
    files = [p for p in test_paths if p.is_file()]
    if files and len(files) == 1:
        f = files[0].resolve()
        is_pkg = (f.parent / "__init__.py").exists()
        top = f.parent.parent if is_pkg else f.parent
        return [sys.executable, "-m", "unittest", "discover",
                "-s", str(f.parent), "-p", f.name, "-t", str(top)]
    if files:
        common = Path(os.path.commonpath([str(p.resolve()) for p in files]))
    else:
        common = test_paths[0]
    is_pkg = (common / "__init__.py").exists()
    return [sys.executable, "-m", "unittest", "discover",
            "-s", str(common), "-p", "test_*.py",
            "-t", str(common.parent if is_pkg else common)]


def _parse_pytest(tail: str):
    passed = failed = 0
    m = re.search(r"(\d+) passed", tail)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", tail)
    if m:
        failed = int(m.group(1))
    total = passed + failed
    return passed, total


def _parse_unittest(tail: str):
    m = re.search(r"Ran (\d+) tests?", tail)
    total = int(m.group(1)) if m else 0
    if not total:
        return 0, 0
    if re.search(r"\bOK\b", tail):
        return total, total
    fails = len(re.findall(r"(?:FAIL|ERROR):", tail))
    return max(total - fails, 0), total if total else 0


# ------------------------------------------------------------------- scoring


def score(rate, wall_ms, lines) -> float | None:
    """Tests dominate; among equal test outcomes, faster wins; then fewer lines.

    rate=None (runner disabled) counts as neutral 1.0 so compile-only
    comparisons still rank by speed and brevity.
    """
    if rate is None:
        rate = 1.0
    return round(rate * SCORE_TEST_WEIGHT - wall_ms - lines, 2)


# ----------------------------------------------------------------- main loop


def evaluate(target: Path, cwd: Path, runner: str, test_paths: list[Path],
             repeats: int = 1) -> dict:
    """Compile + test a candidate that is currently AT the target path."""
    lines = len(target.read_bytes().splitlines())
    compile_ok, compile_ms, compile_tail = run_py_compile(target, cwd)
    if not compile_ok:
        return {"compile_ok": False, "compile_ms": compile_ms, "lines": lines,
                "tests": None, "tail": compile_tail, "score": None}
    tests = run_tests(runner, test_paths, cwd, target.parent, repeats=repeats)
    s = score(tests["rate"], tests["wall_ms"], lines)
    return {"compile_ok": True, "compile_ms": compile_ms, "lines": lines,
            "tests": tests, "tail": tests["tail"], "score": s}


def transmute(target: Path, variants: list[Path], tests: list[Path], runner: str,
              log_path: Path, keep_losers: bool, interactive: bool,
              cwd: Path | None = None, repeats: int = 1) -> dict:
    cwd = cwd or REPO_ROOT
    if not target.is_file():
        raise FileNotFoundError(f"target not found: {target}")
    if not variants and interactive and sys.stdin.isatty():
        variants = _ask_for_variants()
    if not variants:
        raise ValueError("no variants supplied (rule 1: never settle for the first version)")

    baseline_bytes = target.read_bytes()
    candidates: list[dict] = []

    # Candidate 0: baseline, evaluated in place.
    base_eval = evaluate(target, cwd, runner, tests, repeats=repeats)
    candidates.append({"name": "baseline", **_metrics(base_eval)})

    # Variants: swap in, evaluate, restore.
    for v in variants:
        if not v.is_file():
            candidates.append({"name": v.name, "error": f"missing: {v}", "score": None})
            continue
        try:
            target.write_bytes(v.read_bytes())
            ev = evaluate(target, cwd, runner, tests, repeats=repeats)
        finally:
            target.write_bytes(baseline_bytes)  # restore before any decision
        candidates.append({"name": v.name, **_metrics(ev)})

    scored = [c for c in candidates if c.get("score") is not None]
    if not scored:
        raise RuntimeError("no candidate compiled; nothing to keep (aborting, target untouched)")

    # Winner: highest score. Baseline participates; a variant must beat it
    # outright OR land within TIE_EPS (timing noise) — then the variant takes
    # it (rule 1: never settle for the first version).
    base = next(c for c in scored if c["name"] == "baseline")
    best_score = max(c["score"] for c in scored)
    variant_ties = [c for c in scored
                    if c["name"] != "baseline"
                    and c["score"] >= best_score - TIE_EPS]
    if variant_ties:
        winner = max(variant_ties, key=lambda c: c["score"])
    else:
        winner = base
    applied = winner["name"] != "baseline"
    if applied:
        winning_variant = next(v for v in variants if v.name == winner["name"])
        target.write_bytes(winning_variant.read_bytes())

    losers = [c["name"] for c in scored if c["name"] != winner["name"]
              and c["name"] != "baseline"]
    losers += [c["name"] for c in candidates if c.get("score") is None
               and "name" in c and c["name"] != "baseline"]
    if applied:
        for name in losers:
            lp = next((v for v in variants if v.name == name), None)
            if lp is None:
                continue
            if keep_losers:
                archive = log_path.parent / "transmute_losers" / _timestamp()
                archive.mkdir(parents=True, exist_ok=True)
                shutil.move(str(lp), str(archive / lp.name))
            else:
                lp.unlink(missing_ok=True)

    run = {
        "timestamp": _timestamp(),
        "target": str(target),
        "cwd": str(cwd),
        "runner": runner,
        "tests": [str(t) for t in tests],
        "candidates": candidates,
        "winner": winner["name"],
        "applied": applied,
        "losers_deleted": losers if applied else [],
    }
    _append_log(log_path, run)
    return run


def _metrics(ev: dict) -> dict:
    t = ev.get("tests") or {}
    return {
        "compile_ok": ev["compile_ok"],
        "compile_ms": ev.get("compile_ms"),
        "lines": ev["lines"],
        "test_ok": t.get("ok"),
        "test_rate": t.get("rate"),
        "test_passed": t.get("passed"),
        "test_total": t.get("total"),
        "test_wall_ms": t.get("wall_ms"),
        "score": ev.get("score"),
        "tail": (ev.get("tail") or "")[-800:],
    }


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _append_log(log_path: Path, run: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    if log_path.exists():
        try:
            runs = json.loads(log_path.read_text())
            if not isinstance(runs, list):
                runs = []
        except json.JSONDecodeError:
            runs = []
    runs.append(run)
    log_path.write_text(json.dumps(runs, indent=2))


def _ask_for_variants() -> list[Path]:
    print("Enter variant file paths, one per line. Empty line to finish.")
    out = []
    while True:
        try:
            line = input("variant> ").strip()
        except EOFError:
            break
        if not line:
            break
        p = Path(line).expanduser()
        out.append(p if p.is_absolute() else Path.cwd() / p)
    return out


# ---------------------------------------------------------------------- CLI


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Transmutation loop: variant build-off.")
    ap.add_argument("target", type=Path)
    ap.add_argument("--variant", dest="variants", type=Path, action="append", default=[])
    ap.add_argument("--tests", dest="tests", type=Path, action="append", default=[])
    ap.add_argument("--runner", choices=["auto", "pytest", "unittest", "none"], default="auto")
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG)
    ap.add_argument("--keep-losers", action="store_true")
    ap.add_argument("--repeats", type=int, default=1,
                    help="test runs per candidate; best run kept (min-of-N kills timing jitter)")
    ap.add_argument("--cwd", type=Path, default=REPO_ROOT)
    args = ap.parse_args(argv)

    if not args.variants and not sys.stdin.isatty():
        ap.error("no --variant given and stdin is not a TTY (interactive prompt impossible)")

    if Path(args.cwd).resolve() == REPO_ROOT:
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO_ROOT),
                               capture_output=True, text=True)
        if dirty.returncode == 0 and dirty.stdout.strip():
            print("[transmute] WARNING: working tree dirty — commit a checkpoint first (rule 4).")

    try:
        run = transmute(
            target=args.target.resolve(), variants=[v.resolve() for v in args.variants],
            tests=args.tests, runner=args.runner, log_path=args.log.resolve(),
            keep_losers=args.keep_losers,
            interactive=not args.variants, cwd=args.cwd.resolve(),
            repeats=args.repeats,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"[transmute] ABORT: {exc}", file=sys.stderr)
        return 1

    print(f"[transmute] target   : {run['target']}")
    for c in run["candidates"]:
        rate = c.get("test_rate")
        rate_s = f"{rate:.0%}" if rate is not None else "n/a"
        print(f"[transmute] candidate: {c['name']:<24} compile={c.get('compile_ok')} "
              f"tests={rate_s} wall={c.get('test_wall_ms')}ms lines={c.get('lines')} "
              f"score={c.get('score')}")
    verdict = "APPLIED" if run["applied"] else "KEPT BASELINE"
    print(f"[transmute] winner   : {run['winner']} -> {verdict}")
    if run["applied"]:
        print(f"[transmute] losers deleted: {run['losers_deleted']}")
    print(f"[transmute] log      : {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
