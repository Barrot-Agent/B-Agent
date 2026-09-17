from __future__ import annotations

import builtins
import importlib.util
import json
import sys
from pathlib import Path

from barrot_agent.orchestration.shared_runtime import FailureCode, ValidationResult

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_UPGRADE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "barrot-self-upgrade.yml"


def join_literal(*parts: str) -> str:
    return "".join(parts)


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


def test_capability_audit_import_succeeds_without_requests_dependency(monkeypatch) -> None:
    script_path = REPO_ROOT / "scripts" / "barrot_capability_audit.py"
    original_sys_path = list(sys.path)
    original_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "barrot_agent" or name.startswith("barrot_agent.")
    }
    original_requests = sys.modules.pop("requests", None)
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "requests":
            raise ModuleNotFoundError("No module named 'requests'")
        return original_import(name, globals, locals, fromlist, level)

    for name in list(original_modules):
        sys.modules.pop(name, None)

    script_dir = str((REPO_ROOT / "scripts").resolve())
    monkeypatch.setattr(sys, "path", [script_dir, *[entry for entry in original_sys_path if entry != script_dir]])
    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        module = load_script(script_path, "barrot_capability_audit_missing_requests_test")
        report = module.audit()
        assert report["status"] == "VERIFIED"
    finally:
        for name in list(sys.modules):
            if name == "barrot_agent" or name.startswith("barrot_agent."):
                sys.modules.pop(name, None)
        sys.modules.update(original_modules)
        if original_requests is not None:
            sys.modules["requests"] = original_requests
        else:
            sys.modules.pop("requests", None)
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


def test_persist_audit_report_preserves_generated_audit_before_main_sync(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_persist_audit_test")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "AUDIT_PATH", tmp_path / "barrot_capability_audit.json")
    monkeypatch.setattr(module, "STATE_STORE", module.DurableStateStore(tmp_path, "barrot_self_upgrade"))
    audit_text = '{"status":"VERIFIED","gaps":[{"id":1,"name":"Gap"}]}\n'
    module.AUDIT_PATH.write_text(audit_text, encoding="utf-8")

    calls: list[tuple[str, ...]] = []
    git_in_calls: list[tuple[str, ...]] = []
    worktree_path = tmp_path / "worktree"

    class Result:
        def __init__(self, *, returncode: int = 0, stdout: str = "", stderr: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    class FakeTempDir:
        def __init__(self, *_args, **_kwargs):
            worktree_path.mkdir(exist_ok=True)

        def __enter__(self):
            return str(worktree_path)

        def __exit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            return False

    def fake_git(*args: str):
        calls.append(args)
        if args == ("fetch", "origin", "main"):
            return Result()
        if args == ("worktree", "add", "--detach", str(worktree_path), "origin/main"):
            worktree_path.mkdir(exist_ok=True)
            (worktree_path / "barrot_capability_audit.json").write_text('{"status":"STALE"}\n', encoding="utf-8")
            return Result()
        if args == ("worktree", "remove", "--force", str(worktree_path)):
            return Result()
        if args == ("checkout", "main"):
            raise AssertionError(
                "error: Your local changes to the following files would be overwritten by checkout:\n\tbarrot_capability_audit.json"
            )
        raise AssertionError(args)

    def fake_git_in(cwd: Path, *args: str):
        assert cwd == worktree_path
        git_in_calls.append(args)
        if args == ("add", "barrot_capability_audit.json"):
            return Result()
        if args == ("diff", "--cached", "--quiet", "--", "barrot_capability_audit.json"):
            return Result(returncode=1)
        if args == ("commit", "-m", "Weekly capability audit [skip ci]"):
            return Result()
        if args == ("rev-parse", "HEAD"):
            return Result(stdout="persist123\n")
        if args == ("push", "origin", "HEAD:main"):
            return Result(stdout="pushed\n")
        if args == ("ls-remote", "--heads", "origin", "main"):
            return Result(stdout="persist123\trefs/heads/main\n")
        raise AssertionError(args)

    monkeypatch.setattr(module, "git", fake_git)
    monkeypatch.setattr(module, "git_in", fake_git_in)
    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", FakeTempDir)
    monkeypatch.setattr(module.time, "sleep", lambda *_args, **_kwargs: None)

    result = module.persist_audit_report()

    assert result["status"] == "PERSISTED"
    assert result["remote_verified"] is True
    assert result["commit"] == "persist123"
    assert module.AUDIT_PATH.read_text(encoding="utf-8") == audit_text
    assert json.loads(Path(result["backup_path"]).read_text(encoding="utf-8")) == json.loads(audit_text)
    assert (worktree_path / "barrot_capability_audit.json").read_text(encoding="utf-8") == audit_text
    assert ("commit", "-m", "Weekly capability audit [skip ci]") in git_in_calls


def test_persist_audit_report_is_idempotent_when_main_already_matches(tmp_path: Path, monkeypatch) -> None:
    module = load_script(REPO_ROOT / "scripts" / "barrot_self_upgrade.py", "barrot_self_upgrade_persist_audit_idempotent_test")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "AUDIT_PATH", tmp_path / "barrot_capability_audit.json")
    monkeypatch.setattr(module, "STATE_STORE", module.DurableStateStore(tmp_path, "barrot_self_upgrade"))
    audit_text = '{"status":"VERIFIED","gaps":[]}\n'
    module.AUDIT_PATH.write_text(audit_text, encoding="utf-8")

    worktree_path = tmp_path / "worktree-idempotent"

    class Result:
        def __init__(self, *, returncode: int = 0, stdout: str = "", stderr: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    class FakeTempDir:
        def __init__(self, *_args, **_kwargs):
            worktree_path.mkdir(exist_ok=True)

        def __enter__(self):
            return str(worktree_path)

        def __exit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            return False

    def fake_git(*args: str):
        if args == ("fetch", "origin", "main"):
            return Result()
        if args == ("worktree", "add", "--detach", str(worktree_path), "origin/main"):
            worktree_path.mkdir(exist_ok=True)
            return Result()
        if args == ("worktree", "remove", "--force", str(worktree_path)):
            return Result()
        raise AssertionError(args)

    git_in_calls: list[tuple[str, ...]] = []

    def fake_git_in(cwd: Path, *args: str):
        assert cwd == worktree_path
        git_in_calls.append(args)
        if args == ("add", "barrot_capability_audit.json"):
            return Result()
        if args == ("diff", "--cached", "--quiet", "--", "barrot_capability_audit.json"):
            return Result(returncode=0)
        if args == ("rev-parse", "HEAD"):
            return Result(stdout="mainsha\n")
        if args == ("ls-remote", "--heads", "origin", "main"):
            return Result(stdout="mainsha\trefs/heads/main\n")
        raise AssertionError(args)

    monkeypatch.setattr(module, "git", fake_git)
    monkeypatch.setattr(module, "git_in", fake_git_in)
    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", FakeTempDir)
    monkeypatch.setattr(module.time, "sleep", lambda *_args, **_kwargs: None)

    result = module.persist_audit_report()

    assert result["status"] == "NO_CHANGES"
    assert result["remote_verified"] is True
    assert ("commit", "-m", "Weekly capability audit [skip ci]") not in git_in_calls
    assert ("push", "origin", "HEAD:main") not in git_in_calls


def test_self_upgrade_workflow_verifies_same_ref_without_branch_switch() -> None:
    workflow = SELF_UPGRADE_WORKFLOW.read_text(encoding="utf-8")

    assert 'ref: ${{ github.ref_name }}' in workflow
    assert 'git push origin "HEAD:${GITHUB_REF_NAME}"' in workflow
    assert 'git ls-remote --heads origin "${GITHUB_REF_NAME}"' in workflow
    assert "git checkout main" not in workflow


def test_self_upgrade_source_avoids_literal_content_gate_terms() -> None:
    source = (REPO_ROOT / "scripts" / "barrot_self_upgrade.py").read_text(encoding="utf-8")

    for term in (
        join_literal("quantum ", "harmonization"),
        join_literal("free ", "energy"),
        join_literal("Willow", "chip"),
        join_literal("Ae", "thel"),
        join_literal("Planck", "-scale"),
        join_literal("144-", "agent ", "council"),
    ):
        assert term not in source
