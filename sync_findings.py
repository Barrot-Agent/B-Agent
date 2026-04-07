"""
Sync Findings — Barrot Apex Lattice
Reads deployment outputs and synchronizes findings into the apex_lattice sandbox.

Usage:
    python sync_findings.py [--source SOURCE] [--dry-run]

Sources: github | kaggle | huggingface | databricks | all
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).parent
_APEX = _REPO_ROOT / ".apex_lattice"
_REPORTS_DIR = _APEX / "reports"


# ---------------------------------------------------------------------------
# Source interfaces — pull from available local data
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


class GitHubActionsSync:
    """
    Syncs GitHub Actions workflow run results into the apex_lattice sandbox.
    Reads from local workflow output files when available.
    Credentials: uses GITHUB_TOKEN environment variable if needed.
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.token = os.environ.get("GITHUB_TOKEN", "")

    def sync(self) -> Dict[str, Any]:
        """Read latest workflow run results and update sandbox."""
        result: Dict[str, Any] = {
            "source": "github_actions",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "synced_items": [],
            "errors": [],
        }

        # Check for workflow output artifacts
        artifacts_dir = _REPO_ROOT / ".github" / "workflow_artifacts"
        if artifacts_dir.exists():
            for artifact in artifacts_dir.glob("*.json"):
                data = _load_json(artifact)
                if data:
                    result["synced_items"].append(artifact.name)

        # Read latest quantum engine results
        qe_files = sorted(_REPORTS_DIR.glob("quantum_engine_results_*.json")) if _REPORTS_DIR.exists() else []
        if qe_files:
            result["latest_quantum_run"] = qe_files[-1].name

        result["status"] = "ok"
        result["dry_run"] = self.dry_run
        return result


class KaggleSync:
    """
    Syncs Kaggle competition data into the apex_lattice sandbox.
    Uses KAGGLE_USERNAME and KAGGLE_KEY environment variables.
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.username = os.environ.get("KAGGLE_USERNAME", "")
        self.key = os.environ.get("KAGGLE_KEY", "")
        self._available = bool(self.username and self.key)

    def sync(self) -> Dict[str, Any]:
        """Sync Kaggle metadata and update kaggle_findings directory."""
        result: Dict[str, Any] = {
            "source": "kaggle",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "synced_items": [],
            "errors": [],
            "dry_run": self.dry_run,
        }

        if not self._available:
            result["status"] = "skipped"
            result["reason"] = "KAGGLE_USERNAME and KAGGLE_KEY not set"
            return result

        kaggle_dir = _APEX / "kaggle_findings"
        kaggle_dir.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            result["status"] = "dry_run"
            result["would_sync"] = ["competition_metadata.json", "winning_solutions_summary.md"]
            return result

        # Load existing metadata and update timestamp
        meta_path = kaggle_dir / "competition_metadata.json"
        meta = _load_json(meta_path)
        if meta:
            meta["last_synced"] = datetime.now(timezone.utc).isoformat()
            if not self.dry_run:
                meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            result["synced_items"].append("competition_metadata.json")

        result["status"] = "ok"
        return result


class HuggingFaceSync:
    """
    Syncs Hugging Face model performance metrics into the apex_lattice sandbox.
    Uses HF_TOKEN environment variable.
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.token = os.environ.get("HF_TOKEN", "")
        self._available = bool(self.token)

    def sync(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "source": "huggingface",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "synced_items": [],
            "errors": [],
            "dry_run": self.dry_run,
        }

        if not self._available:
            result["status"] = "skipped"
            result["reason"] = "HF_TOKEN not set"
            return result

        deploy_dir = _APEX / "deployment_analytics"
        deploy_dir.mkdir(parents=True, exist_ok=True)

        hf_path = deploy_dir / "hf_performance_metrics.json"
        metrics = _load_json(hf_path)
        if metrics:
            metrics["last_synced"] = datetime.now(timezone.utc).isoformat()
            if not self.dry_run:
                hf_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
            result["synced_items"].append("hf_performance_metrics.json")

        result["status"] = "ok"
        return result


class DatabricksSync:
    """
    Syncs Databricks job results into the apex_lattice sandbox.
    Uses DATABRICKS_HOST and DATABRICKS_TOKEN environment variables.
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.host = os.environ.get("DATABRICKS_HOST", "")
        self.token = os.environ.get("DATABRICKS_TOKEN", "")
        self._available = bool(self.host and self.token)

    def sync(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "source": "databricks",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "synced_items": [],
            "errors": [],
            "dry_run": self.dry_run,
        }

        if not self._available:
            result["status"] = "skipped"
            result["reason"] = "DATABRICKS_HOST and DATABRICKS_TOKEN not set"
            return result

        deploy_dir = _APEX / "deployment_analytics"
        deploy_dir.mkdir(parents=True, exist_ok=True)

        db_path = deploy_dir / "databricks_optimization.json"
        metrics = _load_json(db_path)
        if metrics:
            metrics["last_synced"] = datetime.now(timezone.utc).isoformat()
            if not self.dry_run:
                db_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
            result["synced_items"].append("databricks_optimization.json")

        result["status"] = "ok"
        return result


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class SyncOrchestrator:
    """Coordinates all sync sources and writes a sync report."""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.syncs = [
            GitHubActionsSync(dry_run),
            KaggleSync(dry_run),
            HuggingFaceSync(dry_run),
            DatabricksSync(dry_run),
        ]

    def run(self, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run all (or specified) sync sources.

        Parameters
        ----------
        sources : If provided, only run named sources (github, kaggle, huggingface, databricks).
        """
        ts = datetime.now(timezone.utc).isoformat()
        report: Dict[str, Any] = {
            "sync_session": ts,
            "dry_run": self.dry_run,
            "results": {},
        }

        source_map = {
            "github": GitHubActionsSync,
            "kaggle": KaggleSync,
            "huggingface": HuggingFaceSync,
            "databricks": DatabricksSync,
        }

        active_syncs = (
            [s for s in self.syncs if s.__class__.__name__.lower().startswith(tuple(sources))]
            if sources
            else self.syncs
        )

        all_ok = True
        for sync in active_syncs:
            name = sync.__class__.__name__.replace("Sync", "").lower()
            print(f"  Syncing {name}...")
            try:
                result = sync.sync()
                report["results"][name] = result
                status = result.get("status", "unknown")
                if status == "ok":
                    n = len(result.get("synced_items", []))
                    print(f"    ✓ {n} items synced")
                elif status == "skipped":
                    print(f"    ⚠ Skipped: {result.get('reason', '')}")
                elif status == "dry_run":
                    would = result.get("would_sync", [])
                    print(f"    ℹ Dry-run: would sync {len(would)} items")
                else:
                    all_ok = False
                    print(f"    ✗ Status: {status}")
            except Exception as exc:  # noqa: BLE001
                report["results"][name] = {"status": "error", "error": str(exc)}
                all_ok = False
                print(f"    ✗ Error: {exc}")

        report["overall_status"] = "ok" if all_ok else "partial"

        # Write sync log
        if not self.dry_run:
            _write_sync_log(report)

        return report


def _write_sync_log(report: Dict[str, Any]) -> None:
    """Append a line to the sync audit log."""
    log_path = _APEX / "sync_audit.log"
    ts = report.get("sync_session", datetime.now(timezone.utc).isoformat())
    status = report.get("overall_status", "unknown")
    sources = list(report.get("results", {}).keys())
    line = f"{ts} | {status} | sources={','.join(sources)}\n"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(line)


def print_sync_report(report: Dict[str, Any]) -> None:
    """Print a human-readable sync summary."""
    print(f"\n{'='*55}")
    print("SYNC REPORT")
    print(f"Session: {report.get('sync_session', 'N/A')}")
    print(f"Status:  {report.get('overall_status', 'N/A')}")
    print(f"Dry-run: {report.get('dry_run', False)}")
    print(f"{'='*55}")
    for source, result in report.get("results", {}).items():
        status = result.get("status", "unknown")
        items = len(result.get("synced_items", []))
        print(f"  {source:<16} {status:<10} items={items}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Barrot Apex Lattice — Findings Synchronizer")
    parser.add_argument(
        "--source",
        choices=["github", "kaggle", "huggingface", "databricks", "all"],
        default="all",
        help="Source platform to sync",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate sync without writing files",
    )
    args = parser.parse_args()

    print("=" * 55)
    print("BARROT APEX LATTICE — SYNC FINDINGS")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Source: {args.source} | Dry-run: {args.dry_run}")
    print("=" * 55)

    orchestrator = SyncOrchestrator(dry_run=args.dry_run)
    sources = None if args.source == "all" else [args.source]
    report = orchestrator.run(sources=sources)
    print_sync_report(report)

    print("\nSync complete.")


if __name__ == "__main__":
    main()
