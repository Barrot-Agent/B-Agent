#!/usr/bin/env python3
"""Release gate for the Stage 1 product. Read-only, offline.

Checks the things that are cheap to check and expensive to get wrong:
required files, the capability ledger, the test suite, lint, banned marketing
phrases, secrets, version consistency, and the published fee arithmetic.

Exit 0 = every check passed. Exit 1 = at least one check failed.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT.name

REQUIRED_FILES = (
    "README.md",
    "PRODUCT_SPECIFICATION.md",
    "SALES_COPY.md",
    "PRICING.md",
    "PRODUCTION_WORKFLOW.md",
    "QUALITY_CHECKLIST.md",
    "DELIVERY_REQUIREMENTS.md",
    "LICENSE_AND_TERMS.md",
    "CAPABILITY_LEDGER.md",
    "research/SOURCES.md",
    "research/MARKET_RESEARCH.md",
    "research/EVIDENCE_LOG.md",
    "research/measure_market.py",
    "research/market_measurement.json",
    "marketing/PRODUCT_DESCRIPTION.md",
    "marketing/PROMOTIONAL_COPY.md",
    "marketing/FAQ.md",
    "evaluation/TEST_RESULTS.md",
    "evaluation/IMPROVEMENT_LOG.md",
    "deliverables/README.md",
    "deliverables/README_FIELD.md",
    "deliverables/CHANGELOG.md",
    "deliverables/run_selftest.sh",
    "deliverables/paid_issue_kit/__init__.py",
    "deliverables/paid_issue_kit/ledger.py",
    "deliverables/paid_issue_kit/pack.py",
    "deliverables/paid_issue_kit/timebox.py",
    "deliverables/paid_issue_kit/cli.py",
    "deliverables/templates/issue_intake.md",
    "deliverables/templates/decision_rules.md",
    "deliverables/templates/pr_body.md",
    "deliverables/templates/evidence_pack.md",
    "deliverables/templates/bounty_ledger.csv",
    "deliverables/templates/timebox_card.md",
    "deliverables/examples/candidates.json",
    "deliverables/examples/pr_plan.json",
    "deliverables/examples/ledger.csv",
    "deliverables/examples/PR_BODY.md",
    "deliverables/examples/EVIDENCE_PACK.md",
)

CLAIM_FILES = (
    "README.md",
    "SALES_COPY.md",
    "marketing/PRODUCT_DESCRIPTION.md",
    "marketing/PROMOTIONAL_COPY.md",
)

BANNED_MARKETING = (
    "guarantee",
    "risk-free",
    "passive income",
    "get rich",
    "easy money",
    "100%",
    "six figures",
    "always pays",
    "assured income",
)

SECRET_PATTERNS = (
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}

results: list[tuple[bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    results.append((ok, f"{name}: {detail}"))


def check_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    check("required files", not missing,
          f"{len(REQUIRED_FILES) - len(missing)}/{len(REQUIRED_FILES)} present"
          + (f"; missing {missing}" if missing else ""))


def check_capabilities() -> None:
    text = (ROOT / "CAPABILITY_LEDGER.md").read_text(encoding="utf-8")
    proposed = sum(1 for line in text.splitlines()
                   if line.startswith("| ") and "| PROPOSED |" in line)
    proven = sum(1 for line in text.splitlines()
                 if line.startswith("| ") and ("| PROVEN |" in line or "| ACTIVE |" in line))
    check("capability ledger", proposed == 10 and proven == 0,
          f"{proposed} PROPOSED, {proven} PROVEN/ACTIVE")


def check_tests() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT / "deliverables", capture_output=True, text=True, timeout=120,
    )
    output = proc.stdout + proc.stderr
    match = re.search(r"Ran (\d+) tests", output)
    count = int(match.group(1)) if match else 0
    ok = proc.returncode == 0 and count >= 74 and "\nOK" in output
    check("test suite", ok, f"Ran {count} tests, exit {proc.returncode}")


def check_lint() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "flake8", ".", "--max-line-length=100",
         "--extend-ignore=E203,W503"],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    detail = "clean" if proc.returncode == 0 else (proc.stdout.strip()[:200] or "flake8 failed")
    check("flake8", proc.returncode == 0, detail)


def check_claims() -> None:
    findings: list[str] = []
    for relative in CLAIM_FILES:
        path = ROOT / relative
        in_do_not_write = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                in_do_not_write = "do not write" in stripped.lower()
            if in_do_not_write:
                continue
            lowered = line.lower()
            for phrase in BANNED_MARKETING:
                if phrase in lowered:
                    findings.append(f"{relative}:{number} {phrase}")
    check("marketing claims", not findings,
          f"{len(CLAIM_FILES)} files, {len(findings)} banned phrases"
          + (f" {findings}" if findings else ""))


def check_secrets() -> None:
    findings: list[str] = []
    scanned = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in (".pyc", ".zip"):
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(str(path.relative_to(ROOT)))
    check("secret scan", not findings, f"{scanned} files, {len(findings)} findings")


def check_version() -> None:
    init = (ROOT / "deliverables/paid_issue_kit/__init__.py").read_text(encoding="utf-8")
    changelog = (ROOT / "deliverables/CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init)
    version = match.group(1) if match else "missing"
    ok = version == "1.0.0" and f"## {version}" in changelog
    check("version", ok, f"{version} in package, changelog match={f'## {version}' in changelog}")


def check_pricing() -> None:
    expected = {9: 7.60, 19: 16.60, 39: 34.60}
    actual = {}
    for price in expected:
        fee = round(price * 0.10 + 0.50, 2)
        actual[price] = round(price - fee, 2)
    ok = all(abs(actual[p] - expected[p]) < 0.005 for p in expected)
    check("pricing arithmetic", ok, f"net direct {actual}")


def check_stale_counts() -> None:
    stale = re.compile(r"\b73\s+(?:unit[\s-]*)?tests?\b", re.IGNORECASE)
    findings = []
    for path in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if "evaluation" in path.parts:
            continue  # history is allowed to mention old counts
        if stale.search(path.read_text(encoding="utf-8", errors="ignore")):
            findings.append(str(path.relative_to(ROOT)))
    check("test count consistency", not findings,
          "no stale '73 tests'" + (f"; found {findings}" if findings else ""))


def main() -> int:
    print(f"release gate: {PRODUCT}")
    check_files()
    check_capabilities()
    check_tests()
    check_lint()
    check_claims()
    check_secrets()
    check_version()
    check_pricing()
    check_stale_counts()

    failed = 0
    for ok, line in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {line}")
        failed += 0 if ok else 1
    print(f"RESULT: {'PASS' if failed == 0 else 'FAIL'} ({len(results)} checks, {failed} failed)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
