"""
sync_manager.py
===============
Orchestrates all three deployment systems (Hugging Face, Databricks, Kaggle)
with structured logging, per-step error recovery, and an audit trail written
to sync_audit.log in the repository root.

Usage:
    python sync_manager.py [--hf] [--databricks] [--kaggle] [--all]

When no flags are passed, --all is assumed.
"""

import argparse
import importlib
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG = Path(__file__).parent / "sync_audit.log"

# ---------------------------------------------------------------------------
# Logging: console + rotating audit file
# ---------------------------------------------------------------------------
log = logging.getLogger("sync_manager")
log.setLevel(logging.DEBUG)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s – %(message)s")

_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(_fmt)
log.addHandler(_console)

_file_handler = logging.FileHandler(AUDIT_LOG, encoding="utf-8")
_file_handler.setFormatter(_fmt)
log.addHandler(_file_handler)


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------


class AuditTrail:
    """Append-only JSONL audit log."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def record(self, step: str, status: str, detail: str = "") -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "step": step,
            "status": status,
            "detail": detail,
        }
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")


AUDIT = AuditTrail(AUDIT_LOG)


# ---------------------------------------------------------------------------
# Deployment runners
# ---------------------------------------------------------------------------


def _run_module(module_name: str, label: str) -> bool:
    """
    Import *module_name* and call its ``main()`` function.
    Returns True on success, False on failure (exception caught).
    """
    AUDIT.record(label, "started")
    try:
        mod = importlib.import_module(module_name)
        mod.main()
        AUDIT.record(label, "success")
        return True
    except SystemExit as exc:
        msg = f"SystemExit({exc.code})"
        log.error("%s exited early: %s", label, msg)
        AUDIT.record(label, "failed", msg)
        return False
    except Exception:
        tb = traceback.format_exc()
        log.error("%s raised an exception:\n%s", label, tb)
        AUDIT.record(label, "failed", tb.splitlines()[-1])
        return False


def run_huggingface() -> bool:
    log.info("━━━ Starting Hugging Face deployment ━━━")
    return _run_module("deploy_huggingface", "huggingface")


def run_databricks() -> bool:
    log.info("━━━ Starting Databricks deployment ━━━")
    return _run_module("deploy_databricks", "databricks")


def run_kaggle() -> bool:
    log.info("━━━ Starting Kaggle automation ━━━")
    return _run_module("kaggle_competitions_automation", "kaggle")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _check_credential(name: str) -> bool:
    present = bool(os.environ.get(name, "").strip())
    if not present:
        log.warning("Credential not set: %s", name)
    return present


def validate_credentials(run_hf: bool, run_db: bool, run_kg: bool) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    if run_hf:
        checks["HF_TOKEN"] = _check_credential("HF_TOKEN")
    if run_db:
        checks["DATABRICKS_HOST"] = _check_credential("DATABRICKS_HOST")
        checks["DATABRICKS_TOKEN"] = _check_credential("DATABRICKS_TOKEN")
    if run_kg:
        checks["KAGGLE_USERNAME"] = _check_credential("KAGGLE_USERNAME")
        checks["KAGGLE_KEY"] = _check_credential("KAGGLE_KEY")
    return checks


# ---------------------------------------------------------------------------
# Argument parsing & main
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="B-Agent multi-platform sync manager")
    parser.add_argument("--hf", action="store_true", help="Deploy to Hugging Face")
    parser.add_argument("--databricks", action="store_true", help="Deploy to Databricks")
    parser.add_argument("--kaggle", action="store_true", help="Run Kaggle automation")
    parser.add_argument(
        "--all", dest="all_", action="store_true", help="Run all deployers (default)"
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    run_all = args.all_ or not any([args.hf, args.databricks, args.kaggle])
    run_hf = run_all or args.hf
    run_db = run_all or args.databricks
    run_kg = run_all or args.kaggle

    log.info("════════ B-Agent Sync Manager ════════")
    log.info("Targets: HF=%s  Databricks=%s  Kaggle=%s", run_hf, run_db, run_kg)

    creds = validate_credentials(run_hf, run_db, run_kg)
    AUDIT.record("credential_check", "ok", str(creds))

    results: dict[str, bool] = {}

    if run_hf:
        results["huggingface"] = run_huggingface()

    if run_db:
        results["databricks"] = run_databricks()

    if run_kg:
        results["kaggle"] = run_kaggle()

    # ── Summary ──
    log.info("\n════════ Sync Summary ════════")
    all_ok = True
    for step, ok in results.items():
        icon = "✅" if ok else "❌"
        log.info("  %s  %s", icon, step)
        if not ok:
            all_ok = False

    AUDIT.record("sync_manager", "complete" if all_ok else "partial_failure", str(results))

    if not all_ok:
        log.error("One or more deployment steps failed.  Check logs above.")
        sys.exit(1)

    log.info("✅ All deployments completed successfully.")


if __name__ == "__main__":
    main()
