from __future__ import annotations

import importlib.util
import json
from argparse import Namespace
from pathlib import Path

from barrot_agent.orchestration.shared_runtime import DurableStateStore


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPO_ROOT = Path("/home/runner/work/B-Agent/B-Agent")


def test_defensive_self_test_records_current_blocker_categories(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_defensive_self_test.py", "barrot_defensive_self_test_module")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "ARTIFACT_DIR", tmp_path / ".git" / "barrot_defensive_self_test" / "artifacts")
    monkeypatch.setattr(module, "STATE_STORE", DurableStateStore(tmp_path, "barrot_defensive_self_test"))
    monkeypatch.setattr(module, "parse_args", lambda: Namespace(workspace=str(tmp_path), repo="Barrot-Agent/B-Agent", pr_number=755, ci_failure_message="ModuleNotFoundError: No module named 'requests'", timeout=30))

    audit_path = tmp_path / "barrot_capability_audit.json"
    audit_path.write_text('{"gaps": [{"id": 1, "name": "Gap"}]}', encoding="utf-8")

    def write_state(namespace: str, name: str, payload: dict[str, object]) -> None:
        state_dir = tmp_path / ".git" / namespace / "states"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def fake_run_local_command(command: list[str], *, cwd=None, timeout=0):
        del cwd, timeout
        if command[:3] == ["git", "rev-parse", "HEAD"]:
            return {"command": command, "stdout": "deadbeef\n", "stderr": "", "returncode": 0, "success": True}
        if command[:3] == ["git", "branch", "--show-current"]:
            return {"command": command, "stdout": "copilot/barrot-repo-repair-system\n", "stderr": "", "returncode": 0, "success": True}
        if command[:4] == ["python", "-m", "compileall", "-q"]:
            return {"command": command, "stdout": "", "stderr": "", "returncode": 0, "success": True}
        if command[:3] == ["python", "-m", "pytest"]:
            return {"command": command, "stdout": "ok", "stderr": "", "returncode": 0, "success": True}
        if command[:2] == ["python", "scripts/barrot_capability_audit.py"]:
            write_state("barrot_capability_audit", "latest.json", {"status": "VERIFIED", "gaps": [{"id": 1, "name": "Gap"}]})
            audit_path.write_text('{"gaps": [{"id": 1, "name": "Gap"}], "status": "VERIFIED"}', encoding="utf-8")
            return {"command": command, "stdout": "audit ok", "stderr": "", "returncode": 0, "success": True}
        if command[:2] == ["python", "scripts/barrot_self_upgrade.py"]:
            write_state(
                "barrot_self_upgrade",
                "latest.json",
                {
                    "status": "FAILED",
                    "failure": {"code": "LLM_AUTHENTICATION_FAILED", "message": "GROQ_API_KEY not set"},
                    "completion_gate": {"requirements": {"audit_loaded": True}},
                },
            )
            return {"command": command, "stdout": "Generation failed", "stderr": "", "returncode": 1, "success": False}
        raise AssertionError(command)

    def fake_github_request(path: str, *, method: str = "GET", payload=None):
        del method, payload
        if path.endswith("/actions/workflows/ci.yml/runs?branch=main&per_page=20"):
            return {
                "workflow_runs": [
                    {"id": 34415087951, "head_sha": "993321902a792be0ca2118d7134fe44a075a3b49", "conclusion": "failure", "name": "CI"}
                ]
            }, None
        if path.endswith("/actions/runs/34415087951/jobs?per_page=20"):
            return {"jobs": [{"name": "Tests", "conclusion": "failure"}]}, None
        if path.endswith("/pulls/755"):
            return {"head": {"sha": "deadbeef"}, "mergeable_state": "dirty"}, None
        if path.endswith("/commits/deadbeef/status"):
            return {
                "state": "failure",
                "statuses": [{"context": "barrot-gated-merge", "state": "failure"}],
            }, None
        raise AssertionError(path)

    monkeypatch.setattr(module, "run_local_command", fake_run_local_command)
    monkeypatch.setattr(module, "github_request", fake_github_request)

    module.main()

    latest = module.STATE_STORE.load_state("latest")
    assert latest is not None
    incidents = latest["incidents"]
    assert [item["category"] for item in incidents] == [
        "ENVIRONMENT_FAILURE",
        "STATE_FAILURE",
        "ENVIRONMENT_FAILURE",
        "POLICY_FAILURE",
    ]
    assert incidents[0]["root_cause"]["failure"] == "ModuleNotFoundError: No module named 'requests'"
    assert incidents[1]["root_cause"]["current_local_failure"]["code"] == "LLM_AUTHENTICATION_FAILED"
    assert incidents[2]["final_state"]["status"] == "NOT_EXECUTED"
    assert incidents[2]["root_cause"]["toolchain"]["lake"] is None
    assert incidents[3]["verification_result"]["status"] == "failure"
    assert audit_path.read_text(encoding="utf-8") == '{"gaps": [{"id": 1, "name": "Gap"}]}'
