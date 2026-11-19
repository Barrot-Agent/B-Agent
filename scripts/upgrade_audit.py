"""Offline upgrade audit: inventory, gaps, and a prioritised transmute plan.

This is the entry point that works with no credentials, no network, and no
language model. It exists because the LLM-assisted flywheel
(`scripts/barrot_self_upgrade.py`) hard-exits when `GROQ_API_KEY` is absent, so
the whole loop was unusable on a machine without that key.

What it does:

    walk        the working tree, skipping vendored and cache directories
    measure     file count, lines, tests, untested modules, egress violations
    score       each candidate module for transmute value, deterministically
    plan        ordered actions, each with the reason string that put it there

What it does not do:

    no network      no imports of urllib, requests, socket, ssl, httpx, aiohttp
    no subprocess   no shell, no git commands
    no writes       outside the single report path it is given
    no git          it never stages, commits, or pushes

The score is a ranking device, not a measurement of quality. It answers "which
file would a careful engineer open first", and it is stable: same tree, same
scores, no randomness, no clock in the score.

Usage:
    python3 scripts/upgrade_audit.py [--root .] [--limit 20] [--write]
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist",
    ".tox", ".nox", "site-packages", ".idea", ".vscode", "worktrees",
}

EGRESS_MODULES = {
    "urllib", "requests", "socket", "ssl", "httpx", "aiohttp",
    "urllib3", "http", "ftplib", "telnetlib", "smtplib",
}

GUARD_MARKER = "network_guard"

# Weights are declared so a reader can argue with them instead of guessing.
RISK_EGRESS = 40      # bypasses the single-egress rule
COVERAGE_NONE = 25    # no test file names this module
SIZE_PER_50 = 1       # 1 point per 50 lines
SIZE_CAP = 30         # size alone never dominates
CHURN_LIMIT = 20


@dataclass
class Module:
    path: str
    lines: int
    has_test: bool
    imports_egress: bool
    guarded: bool

    @property
    def score(self) -> int:
        score = 0
        if self.imports_egress and not self.guarded:
            score += RISK_EGRESS
        if not self.has_test:
            score += COVERAGE_NONE
        score += min(self.lines // 50 * SIZE_PER_50, SIZE_CAP)
        return score

    def reasons(self) -> list[str]:
        out: list[str] = []
        if self.imports_egress and not self.guarded:
            out.append("imports a network module without importing network_guard")
        if not self.has_test:
            out.append("no test file names this module")
        if self.lines >= 500:
            out.append(f"{self.lines} lines in one file")
        return out or ["no structural defect found"]


@dataclass
class Inventory:
    python_files: int = 0
    python_lines: int = 0
    test_files: int = 0
    modules: int = 0
    untested: int = 0
    unguarded_egress: int = 0
    largest: list[dict] = field(default_factory=list)


def _skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def _walk(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in sorted(root.rglob("*.py")):
        if _skip(path.relative_to(root)):
            continue
        if path.is_file():
            out.append(path)
    return out


def _line_count(path: Path) -> int:
    try:
        return sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))
    except OSError:
        return 0


def _imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, SyntaxError):
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def _mentions(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def _has_test(root: Path, module: Path) -> bool:
    """A module counts as tested if a test file names it.

    This is a name-based heuristic, not coverage. It is deliberately generous:
    a false "tested" is a missed target, a false "untested" is wasted work on a
    file that is already fine.
    """
    stem = module.stem
    if stem == "__init__":
        return True
    tests = root / "tests"
    if not tests.is_dir():
        return False
    for candidate in tests.glob("*.py"):
        if stem in candidate.stem or _mentions(candidate, stem):
            return True
    return False


def audit(root: Path = Path("."), limit: int = CHURN_LIMIT) -> dict:
    root = root.resolve()
    files = _walk(root)
    inv = Inventory()
    modules: list[Module] = []

    for path in files:
        rel = path.relative_to(root).as_posix()
        lines = _line_count(path)
        inv.python_files += 1
        inv.python_lines += lines
        if rel.startswith("tests/") or "/tests/" in rel:
            inv.test_files += 1
            continue
        if not rel.startswith("barrot_agent/"):
            continue

        imports = _imports(path)
        modules.append(
            Module(
                path=rel,
                lines=lines,
                has_test=_has_test(root, path),
                imports_egress=bool(imports & EGRESS_MODULES),
                guarded=_mentions(path, GUARD_MARKER),
            )
        )

    inv.modules = len(modules)
    inv.untested = sum(1 for m in modules if not m.has_test)
    inv.unguarded_egress = sum(1 for m in modules if m.imports_egress and not m.guarded)

    def size_key(p: Path) -> tuple[int, str]:
        return (-_line_count(p), p.as_posix())

    for path in sorted(files, key=size_key)[:10]:
        inv.largest.append(
            {"path": path.relative_to(root).as_posix(), "lines": _line_count(path)}
        )

    ranked = sorted(modules, key=lambda m: (-m.score, -m.lines, m.path))
    targets = [
        {
            "path": m.path,
            "score": m.score,
            "lines": m.lines,
            "has_test": m.has_test,
            "unguarded_egress": m.imports_egress and not m.guarded,
            "reasons": m.reasons(),
        }
        for m in ranked
        if m.score > 0
    ][:limit]

    gaps: list[dict] = []
    audit_path = root / "barrot_capability_audit.json"
    if audit_path.is_file():
        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
            gaps = [g for g in data.get("gaps", []) if isinstance(g, dict)]
        except (OSError, ValueError):
            gaps = []

    plan = _plan(inv, targets, gaps)

    return {
        "offline": True,
        "network_used": False,
        "git_written": False,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": root.as_posix(),
        "inventory": asdict(inv),
        "gaps_from_capability_audit": gaps,
        "targets": targets,
        "plan": plan,
    }


def _plan(inv: Inventory, targets: list[dict], gaps: list[dict]) -> list[dict]:
    plan: list[dict] = []

    egress = [t for t in targets if t["unguarded_egress"]]
    if egress:
        plan.append(
            {
                "order": 1,
                "action": "route unguarded network imports through network_guard",
                "count": len(egress),
                "why": "single-egress rule: a second egress path is unaudited egress",
                "targets": [t["path"] for t in egress[:10]],
                "reversible": True,
            }
        )

    big = [t for t in targets if t["lines"] >= 500]
    if big:
        plan.append(
            {
                "order": 2,
                "action": "write a characterisation test before touching the largest files",
                "count": len(big),
                "why": "a 500+ line file with no test cannot be safely refactored",
                "targets": [t["path"] for t in big[:10]],
                "reversible": True,
            }
        )

    untested = [t for t in targets if not t["has_test"]]
    if untested:
        plan.append(
            {
                "order": 3,
                "action": "add one test per untested module, highest score first",
                "count": inv.untested,
                "why": "coverage is the precondition for every later transmute",
                "targets": [t["path"] for t in untested[:10]],
                "reversible": True,
            }
        )

    if gaps:
        plan.append(
            {
                "order": 4,
                "action": "close capability gaps that have no owning module",
                "count": len(gaps),
                "why": "a gap with no module cannot be fixed by refactoring",
                "targets": [str(g.get("name", g)) for g in gaps[:10]],
                "reversible": False,
            }
        )

    if not plan:
        plan.append(
            {
                "order": 0,
                "action": "no structural target found; do not manufacture work",
                "count": 0,
                "why": "an empty plan is a valid result",
                "targets": [],
                "reversible": True,
            }
        )
    return plan


def render(report: dict) -> str:
    inv = report["inventory"]
    lines = [
        "BARROT OFFLINE UPGRADE AUDIT",
        f"root        {report['root']}",
        f"generated   {report['generated_at']}",
        f"python      {inv['python_files']} files, {inv['python_lines']} lines",
        f"tests       {inv['test_files']} files",
        f"modules     {inv['modules']} under barrot_agent, {inv['untested']} untested",
        f"egress      {inv['unguarded_egress']} unguarded network importers",
        "",
        "TARGETS",
    ]
    for t in report["targets"][:10]:
        lines.append(f"  {t['score']:>3}  {t['path']}  ({t['lines']} lines)")
        for reason in t["reasons"]:
            lines.append(f"       - {reason}")
    lines.append("")
    lines.append("PLAN")
    for step in report["plan"]:
        lines.append(f"  {step['order']}. {step['action']} [{step['count']}]")
        lines.append(f"     why: {step['why']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline upgrade audit. No network, no git writes."
    )
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--limit", type=int, default=CHURN_LIMIT, help="max targets")
    parser.add_argument("--write", action="store_true", help="write results/upgrade_audit.json")
    args = parser.parse_args(argv)

    report = audit(Path(args.root), limit=args.limit)
    print(render(report))

    if args.write:
        out_dir = Path(args.root) / "results"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "upgrade_audit.json"
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
