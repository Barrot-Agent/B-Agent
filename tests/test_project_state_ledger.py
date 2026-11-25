from datetime import datetime, timezone
import copy

import pytest

from barrot_agent.orchestration.project_state import ProjectStateLedger, _hash

NOW = "2026-11-25T00:00:00Z"


def record(kind, key, value, *, status="active", observed=NOW, stale=None,
           supersedes=None, depends=None, priority=5, source="test"):
    if kind == "task" and value is None:
        value = {"priority": priority}
    return {
        "record_type": kind,
        "key": key,
        "value": value,
        "status": status,
        "observed_at_utc": observed,
        "confidence": 0.9,
        "provenance": {"source_type": "test", "source_ref": source},
        "stale_after_seconds": stale,
        "supersedes": supersedes or [],
        "depends_on": depends or [],
    }


def test_export_import_recovers_state_across_independent_workspaces(tmp_path):
    first_workspace = ProjectStateLedger(tmp_path / "first")
    first = first_workspace.add_record(
        record("objective", "xrp", "Build measured XRP model", source="user:mission")
    )
    bundle = first_workspace.export_bundle()

    second_workspace = ProjectStateLedger(tmp_path / "second")
    imported = second_workspace.reconcile_bundle(bundle)
    assert imported["records"][0]["record_id"] == first["record_id"]
    assert second_workspace.load()["revision"] == imported["revision"]

    second_workspace.add_record(record("decision", "forecast_gate", "withhold", source="workspace-b"))
    first_workspace.reconcile_bundle(second_workspace.export_bundle())
    assert {item["record_type"] for item in first_workspace.load()["records"]} == {"objective", "decision"}
    assert first_workspace.summary()["record_count"] == 2


def test_divergent_values_are_preserved_as_unresolved_conflict(tmp_path):
    first_workspace = ProjectStateLedger(tmp_path / "first")
    second_workspace = ProjectStateLedger(tmp_path / "second")
    base = first_workspace.add_record(record("decision", "audio_soundfont", "candidate-A", source="base"))
    second_workspace.reconcile_bundle(first_workspace.export_bundle())

    first_workspace.add_record(record("decision", "audio_soundfont", "candidate-B", source="workspace-a"))
    second_workspace.add_record(record("decision", "audio_soundfont", "candidate-C", source="workspace-b"))
    first_workspace.reconcile_bundle(second_workspace.export_bundle())

    state = first_workspace.load()
    assert len([item for item in state["records"] if item["key"] == "audio_soundfont"]) == 3
    assert len(state["conflicts"]) == 1
    assert state["conflicts"][0]["status"] == "unresolved"
    assert base["record_id"] in state["conflicts"][0]["record_ids"]


def test_explicit_supersession_resolves_conflict_without_erasing_history(tmp_path):
    ledger = ProjectStateLedger(tmp_path / "workspace")
    first = ledger.add_record(record("decision", "market_cutoff", "cutoff-A", source="a"))
    second = ledger.add_record(record("decision", "market_cutoff", "cutoff-B", source="b"))
    conflict_id = ledger.load()["conflicts"][0]["conflict_id"]

    resolution = ledger.add_record(record(
        "decision", "market_cutoff", "cutoff-verified", source="review",
        supersedes=[first["record_id"], second["record_id"]],
    ))
    state = ledger.load()
    assert state["conflicts"] == []
    historical = next(item for item in state["conflict_history"] if item["conflict_id"] == conflict_id)
    assert historical["status"] == "resolved"
    assert historical["resolution_record_id"] == resolution["record_id"]
    assert len([item for item in state["records"] if item["key"] == "market_cutoff"]) == 3


def test_stale_detection_and_dependency_aware_task_selection(tmp_path):
    ledger = ProjectStateLedger(tmp_path / "workspace")
    stale = ledger.add_record(record(
        "evidence", "old_quote", "$0.50", observed="2026-11-20T00:00:00Z", stale=60
    ))
    setup = ledger.add_record(record("task", "rights_clearance", None, status="open", priority=1))
    ledger.add_record(record("task", "render_bundle", {"priority": 2}, status="open", depends=["rights_clearance"]))
    ledger.add_record(record("task", "event_receipts", {"priority": 1}, status="open"))

    assert stale["record_id"] in ledger.stale_record_ids(now_utc=NOW)
    assert [item["key"] for item in ledger.select_ready_tasks(now_utc=NOW)] == [
        "rights_clearance", "event_receipts"
    ]

    ledger.add_record(record(
        "task", "rights_clearance", {"priority": 1}, status="complete",
        supersedes=[setup["record_id"]],
    ))
    assert [item["key"] for item in ledger.select_ready_tasks(now_utc=NOW)] == [
        "event_receipts", "render_bundle"
    ]


def test_bundle_tampering_and_stale_revision_fail_closed(tmp_path):
    ledger = ProjectStateLedger(tmp_path / "first")
    ledger.add_record(record("objective", "continuity", "recover state"))
    bundle = ledger.export_bundle()
    tampered = copy.deepcopy(bundle)
    tampered["records"][0]["value"] = "tampered"

    other = ProjectStateLedger(tmp_path / "second")
    with pytest.raises(ValueError, match="bundle digest mismatch"):
        other.reconcile_bundle(tampered)
    with pytest.raises(RuntimeError, match="revision changed"):
        ledger.add_record(record("lesson", "stale-write", "reject"), expected_revision="0" * 64)



def test_local_history_event_tampering_fails_closed(tmp_path):
    ledger = ProjectStateLedger(tmp_path / "workspace")
    ledger.add_record(record("objective", "continuity", "preserve state"))
    state = ledger.store.load(ledger.TASK_ID)
    state["history"][0]["detail"]["record_id"] = "tampered"
    ledger.store.save(ledger.TASK_ID, state)

    with pytest.raises(ValueError, match="history event hash mismatch"):
        ledger.load()


def test_bundle_history_event_tampering_fails_even_with_recomputed_outer_digest(tmp_path):
    source = ProjectStateLedger(tmp_path / "source")
    source.add_record(record("objective", "continuity", "preserve state"))
    bundle = copy.deepcopy(source.export_bundle())
    bundle["history"][0]["detail"]["record_id"] = "tampered"
    unsigned = {key: value for key, value in bundle.items() if key != "bundle_sha256"}
    bundle["bundle_sha256"] = _hash(unsigned)

    destination = ProjectStateLedger(tmp_path / "destination")
    with pytest.raises(ValueError, match="history event hash mismatch"):
        destination.reconcile_bundle(bundle)


def test_reimporting_same_bundle_is_idempotent(tmp_path):
    source = ProjectStateLedger(tmp_path / "source")
    source.add_record(record("objective", "audio", "build full production path"))
    bundle = source.export_bundle()

    destination = ProjectStateLedger(tmp_path / "destination")
    first = destination.reconcile_bundle(bundle)
    second = destination.reconcile_bundle(bundle)
    assert second["revision"] == first["revision"]
    assert len(second["records"]) == 1


def test_history_archive_receipt_survives_bundle_exchange(tmp_path):
    source = ProjectStateLedger(tmp_path / "source")
    for index in range(60):
        source.add_record(record("lesson", f"lesson-{index}", f"verified-{index}", source="run-log"))
    bundle = source.export_bundle()
    assert bundle["history_archive_receipts"]

    destination = ProjectStateLedger(tmp_path / "destination")
    destination.reconcile_bundle(bundle)
    assert destination.summary()["record_count"] == 60
    actual = {(item["digest"], item["count"]) for item in destination.export_bundle()["history_archive_receipts"]}
    expected = {(item["digest"], item["count"]) for item in bundle["history_archive_receipts"]}
    assert actual >= expected
