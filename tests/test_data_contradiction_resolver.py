"""Tests for evidence-preserving contradiction review."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_report(tmp_path: Path, records: list[dict]) -> dict:
    env = os.environ.copy()
    env["TEST_DATA"] = json.dumps(records)
    env.pop("GROQ_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "data_contradiction_resolver.py")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    path = next(tmp_path.glob("contradiction_review_*.json"))
    return json.loads(path.read_text(encoding="utf-8"))


def test_conflicting_values_preserve_all_sources_and_minority_objections(tmp_path: Path) -> None:
    records = [
        {"id": "xrp_price", "value": "1.20", "source_id": "venue-a", "source_independence_group": "a"},
        {"id": "xrp_price", "value": "1.22", "source_id": "venue-b", "source_independence_group": "b"},
    ]
    report = run_report(tmp_path, records)
    conflict = report["conflicts"][0]
    assert report["conflict_count"] == 1
    assert conflict["observations"] == records
    assert conflict["minority_objections"] == records
    assert conflict["resolution_status"] == "UNRESOLVED_PRIMARY_EVIDENCE_REQUIRED"
    assert conflict["winner"] is None
    assert report["model_eligible"] is False
    assert report["forecast_status"] == "NOT_ISSUED"


def test_identical_values_are_not_reported_as_a_conflict(tmp_path: Path) -> None:
    records = [
        {"id": "xrp_price", "value": "1.20", "source_id": "venue-a"},
        {"id": "xrp_price", "value": "1.20", "source_id": "venue-b"},
    ]
    report = run_report(tmp_path, records)
    assert report["conflicts"] == []
    assert report["conflict_count"] == 0
    assert report["source_record_count"] == 2


def test_records_without_stable_ids_are_preserved_as_unresolved(tmp_path: Path) -> None:
    records = [{"id": "xrp_price", "value": "1.20"}, {"value": "1.21"}]
    report = run_report(tmp_path, records)
    assert report["unresolved_record_count"] == 1
    assert report["unresolved_records"][0]["record"] == records[1]
    assert report["provenance_gap_count"] == 2


def test_non_array_input_is_rejected() -> None:
    env = os.environ.copy()
    env["TEST_DATA"] = json.dumps({"id": "not-an-array"})
    env.pop("GROQ_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "data_contradiction_resolver.py")],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode != 0
    assert "TEST_DATA must be a JSON array" in result.stderr
