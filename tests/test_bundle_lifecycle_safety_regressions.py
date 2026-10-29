"""Focused regression tests for PR #1225 durable bundle dispatch safety gates.

All tests are local and deterministic; no LLM provider or network is used.
"""
import hashlib
import json

import pytest

from barrot_agent.orchestration.bundle_lifecycle import BundleLifecycleStore, dispatch_bundle_tasks


class _Review:
    def to_dict(self):
        return {"valid": True, "quality_score": 100, "fingerprint": "sha256:test", "findings": []}


class _Result:
    status = "READY_FOR_EXECUTION_REVIEW"
    bundle = {"bundle_id": "regression"}
    review = _Review()
    attempts = []


def _complete(task_id):
    return {
        "status": "complete",
        "queue_advanced": True,
        "repair_cycle": {
            "cycle_id": "cycle-" + task_id,
            "status": "complete",
            "local_validation_passed": True,
            "resolution_verified": True,
            "commit": {"sha": "sha-" + task_id, "remote_verified": True},
        },
    }


GATES = ["queue_advanced", "local_validation_passed", "remote_verified", "resolution_verified"]


def _break_gate(result, gate):
    if gate == "queue_advanced":
        result["queue_advanced"] = False
    elif gate == "remote_verified":
        result["repair_cycle"]["commit"]["remote_verified"] = False
    else:
        result["repair_cycle"][gate] = False
    return result


def _store(tmp_path, fingerprint=None):
    store = BundleLifecycleStore(tmp_path)
    store.save_plan("w", _Result(), request_fingerprint=fingerprint)
    return store


TWO = {"tasks": [{"id": "a", "depends_on": []}, {"id": "b", "depends_on": ["a"]}]}


@pytest.mark.parametrize("gate", GATES)
def test_task_missing_any_gate_is_not_complete_and_blocks_dependents(tmp_path, gate):
    store = _store(tmp_path)
    calls = []

    def run(task):
        calls.append(task["id"])
        return _break_gate(_complete(task["id"]), gate)

    out = dispatch_bundle_tasks(store=store, work_id="w", bundle=TWO, execute_task=run)
    assert out["complete"] is False
    assert out["completed_task_ids"] == []
    assert calls == ["a"]
    assert "dependency blocked" in out["blocked_tasks"]["b"]


@pytest.mark.parametrize("gate", GATES)
def test_resume_does_not_reuse_record_missing_any_gate(tmp_path, gate):
    store = _store(tmp_path)
    record = {"status": "complete", **{g: True for g in GATES}}
    record[gate] = False
    store.record_task_execution("w", "a", record)
    calls = []
    out = dispatch_bundle_tasks(
        store=store, work_id="w", bundle=TWO,
        execute_task=lambda t: calls.append(t["id"]) or _complete(t["id"]),
    )
    assert calls == ["a", "b"]
    assert out["complete"] is True


def test_recovered_queue_result_with_conflicting_evidence_is_not_complete(tmp_path):
    store = _store(tmp_path)
    conflicting = _break_gate(_complete("a"), "remote_verified")  # status says complete, remote says no
    out = dispatch_bundle_tasks(
        store=store, work_id="w", bundle=TWO,
        execute_task=lambda t: pytest.fail("must not execute when recovery returned a result"),
        recover_task=lambda t: conflicting if t["id"] == "a" else None,
    )
    assert out["complete"] is False
    assert "a" not in out["completed_task_ids"]
    assert store.latest_task_states("w")["a"]["recovered_from_queue"] is True


@pytest.mark.parametrize("exc", [TimeoutError("command timed out"), RuntimeError("provider error"), OSError("disk")])
def test_execution_errors_and_timeouts_fail_closed(tmp_path, exc):
    store = _store(tmp_path)

    def run(task):
        raise exc

    out = dispatch_bundle_tasks(store=store, work_id="w", bundle=TWO, execute_task=run)
    assert out["complete"] is False
    states = store.latest_task_states("w")
    assert states["a"]["status"] == "failed"
    assert type(exc).__name__ in states["a"]["reason"]
    assert states["b"]["status"] == "blocked"


def test_malformed_lifecycle_json_fails_before_any_execution(tmp_path):
    store = _store(tmp_path)
    path = store._directory("w") / "lifecycle.json"
    path.write_text('{"work_id": "w", "task_states": {', encoding="utf-8")  # truncated write
    with pytest.raises(json.JSONDecodeError):
        dispatch_bundle_tasks(
            store=store, work_id="w", bundle=TWO,
            execute_task=lambda t: pytest.fail("must not execute on malformed state"),
        )


def test_non_object_task_states_fail_closed(tmp_path):
    store = _store(tmp_path)
    path = store._directory("w") / "lifecycle.json"
    payload = json.loads(path.read_text())
    payload["task_states"] = ["not", "an", "object"]
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        dispatch_bundle_tasks(
            store=store, work_id="w", bundle=TWO,
            execute_task=lambda t: pytest.fail("must not execute on malformed state"),
        )


def test_work_id_mismatch_in_state_file_fails_closed(tmp_path):
    store = _store(tmp_path)
    path = store._directory("w") / "lifecycle.json"
    payload = json.loads(path.read_text())
    payload["work_id"] = "someone-else"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="mismatch"):
        dispatch_bundle_tasks(store=store, work_id="w", bundle=TWO, execute_task=lambda t: _complete(t["id"]))


def test_orphan_partial_temp_file_does_not_affect_state(tmp_path):
    store = _store(tmp_path)
    store.record_task_execution("w", "a", {"status": "complete", **{g: True for g in GATES}})
    (store._directory("w") / ".bundle-crash.tmp").write_text('{"partial":', encoding="utf-8")
    calls = []
    out = dispatch_bundle_tasks(
        store=store, work_id="w", bundle=TWO,
        execute_task=lambda t: calls.append(t["id"]) or _complete(t["id"]),
    )
    assert calls == ["b"]
    assert out["complete"] is True


def test_interrupted_running_record_is_reexecuted_not_assumed_complete(tmp_path):
    store = _store(tmp_path)
    store.record_task_execution("w", "a", {"status": "running", "attempt": 1})
    calls = []
    dispatch_bundle_tasks(
        store=store, work_id="w", bundle=TWO,
        execute_task=lambda t: calls.append(t["id"]) or _complete(t["id"]),
    )
    assert calls == ["a", "b"]
    assert [r["status"] for r in store.load("w")["task_states"]["a"]][:2] == ["running", "running"]


def test_dependency_cycle_is_blocked_without_execution(tmp_path):
    store = _store(tmp_path)
    cyclic = {"tasks": [{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}]}
    out = dispatch_bundle_tasks(
        store=store, work_id="w", bundle=cyclic,
        execute_task=lambda t: pytest.fail("cyclic tasks must not execute"),
    )
    assert out["complete"] is False
    assert set(out["blocked_tasks"]) == {"a", "b"}


@pytest.mark.parametrize("bundle", [
    {"tasks": []},
    {"tasks": [{"id": "a"}, {"id": "a"}]},
    {"tasks": [{"id": "a", "depends_on": ["missing"]}]},
    {"tasks": [{"id": ""}]},
])
def test_invalid_bundle_graph_is_rejected(tmp_path, bundle):
    store = _store(tmp_path)
    with pytest.raises(ValueError):
        dispatch_bundle_tasks(store=store, work_id="w", bundle=bundle, execute_task=lambda t: _complete(t["id"]))


def _request_fingerprint(repo, branch, title, body):
    # Mirrors scripts/barrot_agent.py main(); kept in sync by test_script_fingerprint_formula_is_unchanged.
    return "sha256:" + hashlib.sha256(
        "\\0".join([repo, branch, title.strip(), body.strip()]).encode("utf-8")
    ).hexdigest()


def test_script_fingerprint_formula_is_unchanged():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / "scripts" / "barrot_agent.py").read_text(encoding="utf-8")
    assert '"\\\\0".join([REPO, BRANCH, TITLE.strip(), TASK.strip()])' in source


@pytest.mark.parametrize("field", ["repo", "branch", "title", "body"])
def test_resume_state_discarded_when_any_request_field_changes(tmp_path, field):
    base = {"repo": "Barrot-Agent/B-Agent", "branch": "barrot/task-1", "title": "Fix x", "body": "Details"}
    changed = dict(base, **{field: base[field] + "-changed"})
    store = _store(tmp_path, _request_fingerprint(**base))
    store.record_task_execution("w", "a", {"status": "complete", **{g: True for g in GATES}})
    assert _request_fingerprint(**changed) != _request_fingerprint(**base)
    store.save_plan("w", _Result(), request_fingerprint=_request_fingerprint(**changed))
    assert store.latest_task_states("w") == {}
    calls = []
    dispatch_bundle_tasks(
        store=store, work_id="w", bundle=TWO,
        execute_task=lambda t: calls.append(t["id"]) or _complete(t["id"]),
    )
    assert calls == ["a", "b"]
