from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from barrot_agent.orchestration.shared_runtime import FailureCode, ValidationResult

REPO_ROOT = Path("/home/runner/work/B-Agent/B-Agent")


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_direct_script_import_bootstraps_barrot_agent_package(monkeypatch) -> None:
    script_path = REPO_ROOT / "scripts" / "barrot_capability_audit.py"
    package_init = (REPO_ROOT / "barrot_agent" / "__init__.py").resolve()
    shared_runtime = (REPO_ROOT / "barrot_agent" / "orchestration" / "shared_runtime.py").resolve()
    original_sys_path = list(sys.path)
    original_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "barrot_agent" or name.startswith("barrot_agent.")
    }

    for name in list(original_modules):
        sys.modules.pop(name, None)

    script_dir = str((REPO_ROOT / "scripts").resolve())
    monkeypatch.setattr(sys, "path", [script_dir, *[entry for entry in original_sys_path if entry != script_dir]])

    try:
        load_script(script_path, "barrot_capability_audit_import_bootstrap_test")
        package_module = sys.modules["barrot_agent"]
        shared_runtime_module = sys.modules["barrot_agent.orchestration.shared_runtime"]
        assert Path(package_module.__file__).resolve() == package_init
        assert Path(shared_runtime_module.__file__).resolve() == shared_runtime
    finally:
        for name in list(sys.modules):
            if name == "barrot_agent" or name.startswith("barrot_agent."):
                sys.modules.pop(name, None)
        sys.modules.update(original_modules)
        sys.path[:] = original_sys_path


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


def test_self_upgrade_groq_request_uses_explicit_headers(monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_headers_test")
    monkeypatch.setattr(module, "GROQ_KEY", "test-key")

    captured: dict[str, object] = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            return False

        def read(self, *args, **kwargs):
            del args, kwargs
            return b'{"choices":[{"message":{"content":"ok"}}]}'

    def fake_urlopen(request, timeout=0):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        return Response()

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)

    response = module._send_groq_request({"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": "hello"}]})

    assert response["choices"][0]["message"]["content"] == "ok"
    assert captured["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert captured["timeout"] == 90
    headers = captured["headers"]
    assert headers["Authorization"].startswith("Bearer ")
    assert headers["Authorization"].endswith("test-key")
    assert headers["Content-type"] == "application/json"
    assert headers["Accept"] == "application/json"
    assert headers["User-agent"] == "Barrot-Agent/1.0"


def test_self_upgrade_no_gaps_returns_no_repair_required(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_nogap_test")
    monkeypatch.setattr(module, "AUDIT_PATH", tmp_path / "barrot_capability_audit.json")
    monkeypatch.setattr(module, "STATE_STORE", module.DurableStateStore(tmp_path, "barrot_self_upgrade"))
    module.AUDIT_PATH.write_text('{"gaps": []}', encoding="utf-8")

    code = module.self_upgrade()

    assert code == 0
    states = list((tmp_path / ".git" / "barrot_self_upgrade" / "states").glob("*.json"))
    assert states


def test_self_upgrade_requires_audit_before_no_repair_required(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_missing_audit_test")
    monkeypatch.setattr(module, "AUDIT_PATH", tmp_path / "barrot_capability_audit.json")
    monkeypatch.setattr(module, "STATE_STORE", module.DurableStateStore(tmp_path, "barrot_self_upgrade"))

    code = module.self_upgrade()

    assert code == 1
    states = list((tmp_path / ".git" / "barrot_self_upgrade" / "states").glob("*.json"))
    assert states
    latest = max(states, key=lambda item: item.stat().st_mtime)
    record = json.loads(latest.read_text(encoding="utf-8"))
    assert record["status"] == "FAILED"
    assert record["completion_gate"]["satisfied"] is False
    assert record["failure"]["failed_operation"] == "load_audit"


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


def test_open_capability_pr_requires_exact_remote_sha_and_restores_branch(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_open_pr_test")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "SCRIPTS_DIR", tmp_path / "scripts")
    module.SCRIPTS_DIR.mkdir(parents=True)

    calls: list[tuple[str, ...]] = []

    class Result:
        def __init__(self, *, returncode: int = 0, stdout: str = "", stderr: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_git(*args: str):
        calls.append(args)
        if args == ("branch", "--show-current"):
            return Result(stdout="feature/current\n")
        if args == ("checkout", "-b", "selfupgrade/gap-20260914153000"):
            return Result()
        if args == ("add", "scripts/gap.py"):
            return Result()
        if args == ("commit", "-m", "Self-upgrade candidate: Gap"):
            return Result()
        if args == ("push", "-u", "origin", "selfupgrade/gap-20260914153000"):
            return Result()
        if args == ("rev-parse", "HEAD"):
            return Result(stdout="abc123\n")
        if args == ("ls-remote", "--heads", "origin", "selfupgrade/gap-20260914153000"):
            return Result(stdout="def456\trefs/heads/selfupgrade/gap-20260914153000\n")
        if args == ("checkout", "feature/current"):
            return Result()
        raise AssertionError(args)

    class DateTimeStub:
        @staticmethod
        def now(tz=None):
            del tz

            class Stamp:
                def strftime(self, fmt: str) -> str:
                    assert fmt == "%Y%m%d%H%M%S"
                    return "20260914153000"

            return Stamp()

    def fake_run(command, cwd, capture_output, text, check):
        del cwd, capture_output, text, check
        assert command[:3] == ["gh", "pr", "create"]
        return Result(stdout="https://example.invalid/pr/1\n")

    monkeypatch.setattr(module, "git", fake_git)
    monkeypatch.setattr(module, "datetime", DateTimeStub)
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    result = module.open_capability_pr("Gap", "#!/usr/bin/env python3\nprint(1)\n")

    assert result["remote_verified"] is False
    assert result["restored_branch"] == "feature/current"
    assert ("checkout", "feature/current") in calls
