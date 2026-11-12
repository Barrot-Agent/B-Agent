from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from barrot_agent.evolution.xrp_public_ingestion import (
    XRPIngestionError,
    _capture_event_timeline_registry,
)

CUTOFF = "2026-11-12T05:00:00Z"


def _event(event_id: str, *, stance: str = "supports", captured_at: str = "2026-11-12T04:00:00Z"):
    return {
        "event_id": event_id,
        "event_type": "corporate",
        "event_name": f"Event {event_id}",
        "hypothesis_id": "evernorth-capital",
        "domain": "institutional-capital",
        "hypothesis": "Evernorth registered resale capacity may create equity supply.",
        "counter_hypothesis": "Registered shares are not completed sales or XRP sales.",
        "claim": f"Evidence {event_id}.",
        "source_id": f"source-{event_id}",
        "source_name": f"Publisher {event_id}",
        "source_url": f"https://publisher-{event_id}.example/research",
        "independence_group": f"publisher-{event_id}",
        "source_status": "verified",
        "stance": stance,
        "event_status": "occurred",
        "event_time_utc": "2026-11-11T20:00:00Z",
        "source_published_at_utc": "2026-11-11T20:01:00Z",
        "available_at_utc": captured_at,
        "captured_at_utc": captured_at,
        "raw_source_sha256": None,
        "assumptions": ["The publisher timestamp is accurate."],
        "falsification_conditions": ["A subsequent primary filing reverses the claim."],
        "related_entities": ["Evernorth"],
        "tags": ["XRP"],
    }


def _write_registry(path: Path, events):
    path.write_text(
        json.dumps(
            {
                "artifact_type": "barrot.xrp.event_registry",
                "schema_version": "1.0.0",
                "registry_version": "test",
                "captured_at_utc": "2026-11-12T04:00:00Z",
                "events": events,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_registry_builds_cutoff_safe_scenarios_and_preserves_minority_objection(tmp_path):
    path = tmp_path / "events.json"
    _write_registry(path, [_event("support"), _event("contrary", stance="contradicts")])
    result = _capture_event_timeline_registry(path, CUTOFF)
    scenario = result["timeline"]["scenario_set"]["scenarios"][0]
    assert result["registry_status"] == "LOADED"
    assert result["registry_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert result["event_count"] == 2
    assert result["scenario_count"] == 1
    assert scenario["disagreement_present"] is True
    assert scenario["minority_objection_count"] == 1
    assert result["receipt_complete"] is False
    assert result["model_eligible"] is False
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["directional_forecast"] is False
    assert result["timeline"]["event_timeline"][0]["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"


def test_registry_excludes_evidence_captured_after_cutoff(tmp_path):
    path = tmp_path / "events.json"
    _write_registry(path, [_event("late", captured_at="2026-11-12T05:00:01Z")])
    result = _capture_event_timeline_registry(path, CUTOFF)
    assert result["event_count"] == 0
    assert result["timeline"]["excluded_events"][0]["reason"] == "not_captured_by_data_cutoff"
    assert result["model_eligible"] is False


def test_missing_registry_emits_explicit_empty_not_forecast(tmp_path):
    result = _capture_event_timeline_registry(tmp_path / "missing.json", CUTOFF)
    assert result["registry_status"] == "MISSING"
    assert result["event_count"] == 0
    assert result["scenario_count"] == 0
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["model_eligible"] is False


def test_invalid_registry_schema_fails_closed(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"artifact_type": "wrong", "schema_version": "1.0.0", "events": []}), encoding="utf-8")
    with pytest.raises(XRPIngestionError, match="artifact_type is invalid"):
        _capture_event_timeline_registry(path, CUTOFF)


def test_xrp_ingestion_workflow_publishes_the_event_timeline_artifact():
    workflow = Path(".github/workflows/xrp-public-ingestion.yml").read_text(encoding="utf-8")
    assert "xrp-public-events-\${{ github.run_id }}" in workflow
    assert "artifacts/xrp_ingestion/event_timeline.json" in workflow
