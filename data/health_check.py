"""
data/health_check.py — Data layer health check and topology introspection.

Step 5 (Self-Determined): Barrot Initiative
============================================
After completing Steps 1–4 (JSON consolidation, schema standardization,
doc consolidation, and central registry), the next highest-value action
is a cross-cutting health-check and topology reporter that:

  1. Validates every registered data asset is present and parseable.
  2. Reports schema conformance for each domain (spot-checks key fields).
  3. Reports cross-domain statistics (counts, timestamps, sizes).
  4. Produces a machine-readable topology JSON that any module can import
     to discover the current state of the data layer without touching files.

This script is executable stand-alone:
    python data/health_check.py

Or importable:
    from data.health_check import run_health_check, get_topology
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Allow import from repo root even when run directly
_REPO_ROOT = Path(__file__).parent.parent.resolve()
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from data.registry import list_assets, _load, _DATA_DIR  # noqa: E402


# ---------------------------------------------------------------------------
# Schema spot-check helpers
# ---------------------------------------------------------------------------

def _check_merge_conflict(data: Dict[str, Any]) -> List[str]:
    """Return list of issues found in merge_conflict data."""
    issues: List[str] = []
    for key in ("patterns", "scenarios", "tools", "best_practices",
                "resolution_techniques", "learning_outcomes", "knowledge_summary"):
        if key not in data:
            issues.append(f"Missing top-level key: '{key}'")
    patterns = data.get("patterns", [])
    if patterns and not isinstance(patterns, list):
        issues.append("'patterns' should be a list")
    elif patterns:
        first = patterns[0]
        for field in ("pattern_id", "name", "conflict_type"):
            if field not in first:
                issues.append(f"Pattern missing field: '{field}'")
    return issues


def _check_millennium_problems(data: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    for key in ("problems", "overview", "taxonomy", "search_summaries"):
        if key not in data:
            issues.append(f"Missing top-level key: '{key}'")
    problems = data.get("problems", [])
    if len(problems) != 7:
        issues.append(f"Expected 7 problems, found {len(problems)}")
    if problems:
        first = problems[0]
        for field in ("number", "name", "problem_statement", "official_status"):
            if field not in first:
                issues.append(f"Problem missing field: '{field}'")
    return issues


def _check_mmi_monetization(data: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    for key in ("mmi_recommendations", "monetization_protocols", "council_weights"):
        if key not in data:
            issues.append(f"Missing top-level key: '{key}'")
    return issues


def _check_character_capabilities(data: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    for key in ("character_database", "discovered_capabilities"):
        if key not in data:
            issues.append(f"Missing top-level key: '{key}'")
    return issues


_SCHEMA_CHECKS = {
    "merge_conflict": _check_merge_conflict,
    "millennium_problems": _check_millennium_problems,
    "mmi_monetization": _check_mmi_monetization,
    "character_capabilities": _check_character_capabilities,
}


# ---------------------------------------------------------------------------
# Topology builder
# ---------------------------------------------------------------------------

def get_topology() -> Dict[str, Any]:
    """Return a full topology dict describing the current data layer state."""
    topology: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_dir": str(_DATA_DIR),
        "assets": {},
    }

    assets_info = list_assets()
    for name, info in assets_info.items():
        entry: Dict[str, Any] = {
            "path": info["path"],
            "exists": info["exists"],
            "size_bytes": info["size_bytes"],
            "cached": info["cached"],
            "schema_issues": [],
            "record_count": None,
            "error": None,
        }
        if info["exists"]:
            try:
                data = _load(name)
                # Record count heuristic
                if isinstance(data, list):
                    entry["record_count"] = len(data)
                elif isinstance(data, dict):
                    # Count top-level list values
                    for v in data.values():
                        if isinstance(v, list):
                            entry["record_count"] = len(v)
                            break
                # Schema check
                checker = _SCHEMA_CHECKS.get(name)
                if checker:
                    entry["schema_issues"] = checker(data)
            except Exception as exc:
                entry["error"] = str(exc)

        topology["assets"][name] = entry

    # Summary
    total = len(assets_info)
    present = sum(1 for a in topology["assets"].values() if a["exists"])
    issues_total = sum(len(a["schema_issues"]) for a in topology["assets"].values())
    topology["summary"] = {
        "total_assets": total,
        "present": present,
        "missing": total - present,
        "schema_issues_total": issues_total,
        "healthy": (present == total and issues_total == 0),
    }
    return topology


# ---------------------------------------------------------------------------
# Pretty-print report
# ---------------------------------------------------------------------------

def run_health_check(verbose: bool = True) -> bool:
    """Run the full health check; return True if everything is healthy."""
    topology = get_topology()
    summary = topology["summary"]

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Barrot Data Layer — Health Check")
        print(f"  {topology['generated_at']}")
        print(f"{'='*60}")
        print(f"  Data directory: {topology['data_dir']}")
        print()

        for name, asset in topology["assets"].items():
            status_icon = "✓" if asset["exists"] else "✗"
            size_str = (
                f"{asset['size_bytes']:,} bytes" if asset["size_bytes"] else "N/A"
            )
            count_str = (
                f"  records={asset['record_count']}"
                if asset["record_count"] is not None
                else ""
            )
            print(f"  [{status_icon}] {name:<30} {size_str:<20}{count_str}")
            if asset["schema_issues"]:
                for issue in asset["schema_issues"]:
                    print(f"         ⚠  {issue}")
            if asset["error"]:
                print(f"         ✗  Error: {asset['error']}")

        print()
        print(f"  Summary: {summary['present']}/{summary['total_assets']} assets present  "
              f"|  {summary['schema_issues_total']} schema issues")
        healthy_label = "✓ HEALTHY" if summary["healthy"] else "✗ NEEDS ATTENTION"
        print(f"  Status : {healthy_label}")
        print(f"{'='*60}\n")

    return summary["healthy"]


def save_topology(output_path: Optional[str] = None) -> str:
    """Persist the topology to a JSON file; return the file path."""
    if output_path is None:
        output_path = str(_DATA_DIR / "data_topology.json")
    topology = get_topology()
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(topology, fh, indent=2)
    return output_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    healthy = run_health_check(verbose=True)
    topology_path = save_topology()
    print(f"Topology written to: {topology_path}\n")
    sys.exit(0 if healthy else 1)
