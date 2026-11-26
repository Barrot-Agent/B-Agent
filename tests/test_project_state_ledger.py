from datetime import datetime, timezone
import copy

import pytest

from barrot_agent.orchestration.project_state import ProjectStateLedger, _hash, generate_transfer_keypair

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


def test_rejected_partial_supersession_does_not_hide_unresolved_conflict(tmp_path):
    ledger = ProjectStateLedger(tmp_path / "workspace")
    first = ledger.add_record(record("decision", "source_identity", "candidate-A", source="a"))
    second = ledger.add_record(record("decision", "source_identity", "candidate-B", source="b"))
    original_conflict = ledger.load()["conflicts"][0]

    ledger.add_record(record(
        "decision", "source_identity", "candidate-B-rejected",
        status="rejected", supersedes=[second["record_id"]], source="review",
    ))

    state = ledger.load()
    assert state["conflicts"] == [original_conflict]
    assert state["conflicts"][0]["status"] == "unresolved"
    assert first["record_id"] in state["conflicts"][0]["record_ids"]


def test_task_dependency_disagreement_blocks_selection(tmp_path):
    ledger = ProjectStateLedger(tmp_path / "workspace")
    ledger.add_record(record(
        "task", "integrate_audio", {"priority": 1},
        status="open", depends=["rights_review_a"], source="workspace-a",
    ))
    ledger.add_record(record(
        "task", "integrate_audio", {"priority": 1},
        status="open", depends=["rights_review_b"], source="workspace-b",
    ))

    state = ledger.load()
    assert len(state["conflicts"]) == 1
    assert state["conflicts"][0]["key"] == "integrate_audio"
    assert ledger.select_ready_tasks() == []


def test_same_revision_reconciliation_merges_independent_history(tmp_path):
    source = ProjectStateLedger(tmp_path / "source")
    source.add_record(record("objective", "continuity", "recover all mission state"))
    bundle = source.export_bundle()

    left = ProjectStateLedger(tmp_path / "left")
    right = ProjectStateLedger(tmp_path / "right")
    left.reconcile_bundle(bundle)
    right.reconcile_bundle(bundle)

    left_state = left.load()
    right_state = right.load()
    left._history(left_state, "independent_observation", {"workspace": "left"})
    right._history(right_state, "independent_observation", {"workspace": "right"})
    left.store.save(left.TASK_ID, left_state)
    right.store.save(right.TASK_ID, right_state)
    assert left.load()["revision"] == right.load()["revision"]

    right_event_ids = {item["event_id"] for item in right.load()["history"]}
    left.reconcile_bundle(right.export_bundle())
    left_event_ids = {item["event_id"] for item in left.load()["history"]}
    assert right_event_ids.issubset(left_event_ids)



def test_signed_transfer_authenticates_sender_and_persists_replay_guard(tmp_path):
    keys = generate_transfer_keypair()
    sender = ProjectStateLedger(tmp_path / "sender")
    original = sender.add_record(
        record("objective", "cross_host", "Recover signed state", source="sender")
    )
    envelope = sender.export_signed_bundle(keys["private_key_b64"], issued_at_utc=NOW)
    receiver = ProjectStateLedger(tmp_path / "receiver")
    trusted = {keys["sender_id"]: keys["public_key_b64"]}

    imported = receiver.reconcile_signed_bundle(envelope, trusted_public_keys=trusted, now_utc=NOW)
    assert imported["state"]["records"][0]["record_id"] == original["record_id"]
    assert imported["transfer_receipt"]["sequence"] == 1
    assert receiver.transfer_guard.summary()["incoming_sequences"][keys["sender_id"]] == 1

    restarted_receiver = ProjectStateLedger(tmp_path / "receiver")
    with pytest.raises(ValueError, match="replay"):
        restarted_receiver.reconcile_signed_bundle(envelope, trusted_public_keys=trusted, now_utc=NOW)


def test_signed_transfer_rejects_tampering_unknown_sender_and_key_mismatch(tmp_path):
    keys = generate_transfer_keypair()
    sender = ProjectStateLedger(tmp_path / "sender")
    sender.add_record(record("decision", "approval", "required", source="sender"))
    envelope = sender.export_signed_bundle(keys["private_key_b64"], issued_at_utc=NOW)
    trusted = {keys["sender_id"]: keys["public_key_b64"]}

    tampered = copy.deepcopy(envelope)
    tampered["bundle"]["records"][0]["value"] = "modified"
    receiver = ProjectStateLedger(tmp_path / "tampered")
    with pytest.raises(ValueError, match="bundle digest mismatch"):
        receiver.reconcile_signed_bundle(tampered, trusted_public_keys=trusted, now_utc=NOW)

    # Recompute the public digests after changing a valid bundle field. This gets
    # past integrity checks and proves the original Ed25519 signature still rejects
    # a sender who can rewrite hashes but does not possess the trusted private key.
    forged = copy.deepcopy(envelope)
    forged["bundle"].setdefault("history_archive_receipts", []).append(
        {"digest": "a" * 64, "count": 1}
    )
    forged["bundle"]["bundle_sha256"] = _hash({
        key: value for key, value in forged["bundle"].items() if key != "bundle_sha256"
    })
    forged["bundle_sha256"] = forged["bundle"]["bundle_sha256"]
    forged["transfer_id"] = _hash({
        "schema": forged["schema"],
        "project_id": forged["project_id"],
        "sender_id": forged["sender_id"],
        "sequence": forged["sequence"],
        "issued_at_utc": forged["issued_at_utc"],
        "expires_at_utc": forged["expires_at_utc"],
        "bundle_sha256": forged["bundle_sha256"],
    })
    signature_receiver = ProjectStateLedger(tmp_path / "signature")
    with pytest.raises(ValueError, match="signature"):
        signature_receiver.reconcile_signed_bundle(
            forged, trusted_public_keys=trusted, now_utc=NOW
        )

    unknown = ProjectStateLedger(tmp_path / "unknown")
    with pytest.raises(ValueError, match="not trusted"):
        unknown.reconcile_signed_bundle(envelope, trusted_public_keys={}, now_utc=NOW)

    other_keys = generate_transfer_keypair()
    mismatch = ProjectStateLedger(tmp_path / "mismatch")
    with pytest.raises(ValueError, match="does not match"):
        mismatch.reconcile_signed_bundle(
            envelope,
            trusted_public_keys={keys["sender_id"]: other_keys["public_key_b64"]},
            now_utc=NOW,
        )


def test_signed_transfer_rejects_expired_future_and_replayed_sequence(tmp_path):
    keys = generate_transfer_keypair()
    sender = ProjectStateLedger(tmp_path / "sender")
    sender.add_record(record("objective", "ordered", "v1", source="sender"))
    first = sender.export_signed_bundle(
        keys["private_key_b64"], issued_at_utc=NOW, expires_in_seconds=60
    )
    sender.add_record(record("objective", "ordered", "v2", source="sender-2"))
    second = sender.export_signed_bundle(
        keys["private_key_b64"], issued_at_utc=NOW, expires_in_seconds=3600
    )
    trusted = {keys["sender_id"]: keys["public_key_b64"]}

    expired_receiver = ProjectStateLedger(tmp_path / "expired")
    with pytest.raises(ValueError, match="expired"):
        expired_receiver.reconcile_signed_bundle(
            first, trusted_public_keys=trusted, now_utc="2026-11-25T00:02:00Z"
        )

    future_receiver = ProjectStateLedger(tmp_path / "future")
    with pytest.raises(ValueError, match="future"):
        future_receiver.reconcile_signed_bundle(
            second,
            trusted_public_keys=trusted,
            now_utc="2026-11-24T23:00:00Z",
        )

    ordered_receiver = ProjectStateLedger(tmp_path / "ordered")
    ordered_receiver.reconcile_signed_bundle(second, trusted_public_keys=trusted, now_utc=NOW)
    with pytest.raises(ValueError, match="sequence"):
        ordered_receiver.reconcile_signed_bundle(first, trusted_public_keys=trusted, now_utc=NOW)


def test_signed_transfer_sender_sequence_survives_process_restart(tmp_path):
    keys = generate_transfer_keypair()
    first_sender = ProjectStateLedger(tmp_path / "sender")
    first_sender.add_record(record("objective", "sequence", "first", source="sender"))
    first = first_sender.export_signed_bundle(keys["private_key_b64"], issued_at_utc=NOW)
    second_sender = ProjectStateLedger(tmp_path / "sender")
    second = second_sender.export_signed_bundle(keys["private_key_b64"], issued_at_utc=NOW)
    assert first["sequence"] == 1
    assert second["sequence"] == 2

def test_signed_transfer_survives_independent_processes(tmp_path):
    """Verify durable signed export/import and replay rejection across process boundaries."""
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path

    keys = generate_transfer_keypair()
    repository_root = Path(__file__).resolve().parents[1]
    bundle_path = tmp_path / "signed-transfer.json"
    sender_workspace = tmp_path / "sender-process"
    receiver_workspace = tmp_path / "receiver-process"
    environment = os.environ.copy()
    environment.update({
        "WORKSPACE": str(sender_workspace),
        "BUNDLE_PATH": str(bundle_path),
        "PRIVATE_KEY_B64": keys["private_key_b64"],
        "PUBLIC_KEY_B64": keys["public_key_b64"],
        "SENDER_ID": keys["sender_id"],
        "NOW_UTC": NOW,
        "RECORD_JSON": json.dumps(record(
            "objective", "cross_process_recovery", "persisted across process restart",
            source="subprocess-sender",
        )),
    })

    sender_script = """
import json, os
from pathlib import Path
from barrot_agent.orchestration.project_state import ProjectStateLedger
ledger = ProjectStateLedger(os.environ["WORKSPACE"])
ledger.add_record(json.loads(os.environ["RECORD_JSON"]))
envelope = ledger.export_signed_bundle(
    os.environ["PRIVATE_KEY_B64"],
    issued_at_utc=os.environ["NOW_UTC"],
)
Path(os.environ["BUNDLE_PATH"]).write_text(
    json.dumps(envelope, sort_keys=True), encoding="utf-8"
)
"""
    sender = subprocess.run(
        [sys.executable, "-c", sender_script],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert sender.returncode == 0, sender.stderr
    assert bundle_path.is_file()

    environment["WORKSPACE"] = str(receiver_workspace)
    receiver_script = """
import json, os
from pathlib import Path
from barrot_agent.orchestration.project_state import ProjectStateLedger
ledger = ProjectStateLedger(os.environ["WORKSPACE"])
envelope = json.loads(Path(os.environ["BUNDLE_PATH"]).read_text(encoding="utf-8"))
result = ledger.reconcile_signed_bundle(
    envelope,
    trusted_public_keys={os.environ["SENDER_ID"]: os.environ["PUBLIC_KEY_B64"]},
    now_utc=os.environ["NOW_UTC"],
)
print(json.dumps({
    "record_count": len(result["state"]["records"]),
    "value": result["state"]["records"][0]["value"],
    "sequence": result["transfer_receipt"]["sequence"],
}))
"""
    receiver = subprocess.run(
        [sys.executable, "-c", receiver_script],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert receiver.returncode == 0, receiver.stderr
    assert json.loads(receiver.stdout.strip()) == {
        "record_count": 1,
        "value": "persisted across process restart",
        "sequence": 1,
    }

    replay_script = """
import json, os
from pathlib import Path
from barrot_agent.orchestration.project_state import ProjectStateLedger
ledger = ProjectStateLedger(os.environ["WORKSPACE"])
envelope = json.loads(Path(os.environ["BUNDLE_PATH"]).read_text(encoding="utf-8"))
try:
    ledger.reconcile_signed_bundle(
        envelope,
        trusted_public_keys={os.environ["SENDER_ID"]: os.environ["PUBLIC_KEY_B64"]},
        now_utc=os.environ["NOW_UTC"],
    )
except ValueError as exc:
    if "replay" not in str(exc).lower():
        raise
    print("replay blocked")
else:
    raise SystemExit("replayed transfer was accepted")
"""
    replay = subprocess.run(
        [sys.executable, "-c", replay_script],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert replay.returncode == 0, replay.stderr
    assert replay.stdout.strip() == "replay blocked"

