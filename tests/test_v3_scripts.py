from __future__ import annotations

import importlib.util
from pathlib import Path

from barrot_agent.orchestration.shared_runtime import FailureCode, ValidationResult

REPO_ROOT = Path("/home/runner/work/B-Agent/B-Agent")


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_capability_audit_writes_verified_report(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_capability_audit.py", "barrot_capability_audit_test")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "SCRIPTS_DIR", tmp_path / "scripts")
    monkeypatch.setattr(module, "WORKFLOWS_DIR", tmp_path / ".github" / "workflows")
    monkeypatch.setattr(module, "OUTPUT_PATH", tmp_path / "barrot_capability_audit.json")
    monkeypatch.setattr(module, "STATE_STORE", module.DurableStateStore(tmp_path, "barrot_capability_audit"))
    module.SCRIPTS_DIR.mkdir(parents=True)
    module.WORKFLOWS_DIR.mkdir(parents=True)
    (module.SCRIPTS_DIR / "alpha.py").write_text("print('x')\n", encoding="utf-8")

    report = module.audit()

    assert report["status"] == "VERIFIED"
    assert (tmp_path / "barrot_capability_audit.json").exists()
    assert (tmp_path / ".git" / "barrot_capability_audit" / "states" / "latest.json").exists()


def test_self_upgrade_normalizes_tool_conflict(monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_conflict_test")
    monkeypatch.setattr(module, "GROQ_KEY", "test")
    monkeypatch.setattr(module, "MODEL_CANDIDATES", ["model-a"])
    monkeypatch.setattr(module, "_send_groq_request", lambda payload: (_ for _ in ()).throw(RuntimeError("Tool choice is none, but model called a tool")))

    _, records, failure = module.call_groq("hello")

    assert records
    assert failure is not None
    assert failure.code == FailureCode.PROVIDER_TOOL_CONFLICT.value


def test_self_upgrade_no_gaps_returns_no_repair_required(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_nogap_test")
    monkeypatch.setattr(module, "AUDIT_PATH", tmp_path / "barrot_capability_audit.json")
    monkeypatch.setattr(module, "STATE_STORE", module.DurableStateStore(tmp_path, "barrot_self_upgrade"))
    module.AUDIT_PATH.write_text('{"gaps": []}', encoding="utf-8")

    code = module.self_upgrade()

    assert code == 0
    states = list((tmp_path / ".git" / "barrot_self_upgrade" / "states").glob("*.json"))
    assert states


def test_self_upgrade_blocks_when_remote_verification_fails(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_blocked_test")
    monkeypatch.setattr(module, "AUDIT_PATH", tmp_path / "barrot_capability_audit.json")
    monkeypatch.setattr(module, "STATE_STORE", module.DurableStateStore(tmp_path, "barrot_self_upgrade"))
    module.AUDIT_PATH.write_text('{"gaps": [{"id": 1, "name": "Gap"}]}', encoding="utf-8")
    monkeypatch.setattr(module, "generate_capability", lambda gap_id, gap_name: ("#!/usr/bin/env python3\nprint(1)\n", [], None))
    monkeypatch.setattr(module, "verify_syntax", lambda code: ValidationResult(passed=True, summary="ok"))
    monkeypatch.setattr(
        module,
        "open_capability_pr",
        lambda gap_name, code: {"branch": "b", "target": "t", "commit": "abc", "remote_verified": False, "pr_output": "url"},
    )

    code = module.self_upgrade()

    assert code == 1
