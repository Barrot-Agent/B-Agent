from __future__ import annotations

import importlib.util
import json
from types import SimpleNamespace

import pytest
from pathlib import Path

from barrot_agent.orchestration.repository_repair import RepairCycleEvidence, WorkItemEvidence


_SINGLE_TASK_BUNDLE = {
    "objective": "Repair issue",
    "tasks": [{
        "id": "task-1", "title": "Repair", "description": "Repair the issue", "depends_on": [],
        "files": [], "acceptance_criteria": ["validated"], "tests": ["pytest"], "rollback_plan": ["revert"],
    }],
}

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "barrot_agent.py"


def load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_barrot_agent_main_routes_through_work_queue_controller(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "Fix the reproduced issue.")
    monkeypatch.setenv("TASK_TITLE", "Repair issue")
    monkeypatch.setenv("ISSUE_NUMBER", "42")
    monkeypatch.setenv("BRANCH", "barrot/task-42")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    module = load_script_module("barrot_agent_script_test")

    calls: dict[str, object] = {}

    class FakeController:
        def __init__(self, **kwargs):
            calls["init"] = kwargs
    class FakeQueue:
        def __init__(self, **kwargs):
            calls["queue_init"] = kwargs
            self.work_store = SimpleNamespace(load=lambda work_id: None)

        def run(self, **kwargs):
            calls["run"] = kwargs
            work = WorkItemEvidence(work_id="work-123")
            cycle = RepairCycleEvidence(cycle_id="cycle-123")
            cycle.status = "no_repair_required"
            cycle.current_state = "NO_REPAIR_REQUIRED"
            cycle.report = "Already healthy."
            cycle.report_only = False
            repair_cycle = cycle.to_dict()
            # Deterministic reproduction evidence: the issue does not reproduce.
            repair_cycle["issue_reproduced"] = False
            repair_cycle["validation"] = {"issue_reproduction": {"issue_reproduced": False}}
            work.repair_cycle = repair_cycle
            work.status = "complete"
            work.queue_advanced = True
            return work

    class FakeBundleController:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, **kwargs):
            return SimpleNamespace(
                status="READY_FOR_EXECUTION_REVIEW",
                bundle=_SINGLE_TASK_BUNDLE,
                attempts=(),
                review=SimpleNamespace(quality_score=100, fingerprint="sha256:test", to_dict=lambda: {"valid": True}),
            )

    # Real durable lifecycle store, isolated in a temporary workspace.
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "BundleEngineeringController", FakeBundleController)
    monkeypatch.setattr(module, "RepositoryRepairController", FakeController)
    monkeypatch.setattr(module, "WorkQueueController", FakeQueue)
    monkeypatch.setattr(module, "configure_git", lambda: calls.setdefault("configured", True))
    monkeypatch.setattr(module, "checkout_branch", lambda branch: calls.setdefault("branch", branch))
    monkeypatch.setattr(module, "build_audit_context", lambda title, body: {"inventory": f"{title}:{body}"})
    monkeypatch.setattr(module, "post_issue_comment", lambda message: calls.setdefault("comment", message))
    monkeypatch.setattr(module, "create_pull_request", lambda cycle: calls.setdefault("pr", cycle))
    monkeypatch.setattr(module, "write_collaboration_record", lambda cycle: calls.setdefault("record", cycle))

    module.main()

    assert "init" in calls
    assert "run" in calls
    assert calls["run"]["branch"] == "barrot/task-42"
    assert "no pull request was created" in calls["comment"]
    assert "NO_CHANGE_REQUIRED" in calls["comment"]
    assert "pr" not in calls


def test_barrot_agent_report_only_bundle_task_is_not_reported_complete(monkeypatch, tmp_path):
    """A report-only result is not verified completion: the bundle fails closed and opens no PR."""
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "Audit only.")
    monkeypatch.setenv("TASK_TITLE", "Repair issue")
    monkeypatch.setenv("ISSUE_NUMBER", "42")
    monkeypatch.setenv("BRANCH", "barrot/task-42")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    module = load_script_module("barrot_agent_report_only_test")
    calls: dict[str, object] = {}

    class FakeController:
        def __init__(self, **kwargs):
            calls["init"] = kwargs
    class FakeQueue:
        def __init__(self, **kwargs):
            calls["queue_init"] = kwargs
            self.work_store = SimpleNamespace(load=lambda work_id: None)

        def run(self, **kwargs):
            calls["run"] = kwargs
            work = WorkItemEvidence(work_id="work-456")
            cycle = RepairCycleEvidence(cycle_id="cycle-456")
            cycle.status = "no_repair_required"
            cycle.current_state = "NO_REPAIR_REQUIRED"
            cycle.report = "Audit only."
            cycle.report_only = True
            work.repair_cycle = cycle.to_dict()
            work.status = "complete"
            work.queue_advanced = True
            return work

    class FakeBundleController:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, **kwargs):
            return SimpleNamespace(
                status="READY_FOR_EXECUTION_REVIEW",
                bundle=_SINGLE_TASK_BUNDLE,
                attempts=(),
                review=SimpleNamespace(quality_score=100, fingerprint="sha256:test", to_dict=lambda: {"valid": True}),
            )

    # Real durable lifecycle store, isolated in a temporary workspace.
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "BundleEngineeringController", FakeBundleController)
    monkeypatch.setattr(module, "RepositoryRepairController", FakeController)
    monkeypatch.setattr(module, "WorkQueueController", FakeQueue)
    monkeypatch.setattr(module, "configure_git", lambda: None)
    monkeypatch.setattr(module, "checkout_branch", lambda branch: None)
    monkeypatch.setattr(module, "build_audit_context", lambda title, body: {"inventory": f"{title}:{body}"})
    monkeypatch.setattr(module, "post_issue_comment", lambda message: calls.setdefault("comment", message))
    monkeypatch.setattr(module, "write_collaboration_record", lambda cycle: calls.setdefault("record", cycle))
    monkeypatch.setattr(module, "create_pull_request", lambda cycle: calls.setdefault("pr", cycle))

    with pytest.raises(SystemExit):
        module.main()

    assert "run" in calls
    assert "pr" not in calls
    assert "unfinished tasks were not reported complete" in calls["comment"]


def test_groq_payload_omits_tool_choice_when_tools_not_supplied(monkeypatch):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    module = load_script_module("barrot_agent_payload_test")

    payload = module._groq_payload([{"role": "user", "content": "hello"}], tools=None)

    assert "tool_choice" not in payload
    assert "tools" not in payload


def test_script_brain_executes_repo_browser_tools_with_auto_tool_choice(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    module = load_script_module("barrot_agent_tool_test")

    workspace = tmp_path / "repo"
    (workspace / "pkg").mkdir(parents=True)
    (workspace / "pkg" / "sample.py").write_text("FLAG = 'BROKEN'\n", encoding="utf-8")

    payloads: list[dict[str, object]] = []

    def sender(payload: dict[str, object]) -> dict[str, object]:
        payloads.append(json.loads(json.dumps(payload)))
        index = len(payloads)
        if index == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "type": "function",
                                    "function": {
                                        "name": "repo_browser.print_tree",
                                        "arguments": json.dumps({"path": ".", "depth": 2}),
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        if index == 2:
            tool_messages = [m for m in payload["messages"] if m["role"] == "tool"]
            assert any("pkg/sample.py" in m["content"] for m in tool_messages)
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call-2",
                                    "type": "function",
                                    "function": {
                                        "name": "repo_browser.search",
                                        "arguments": json.dumps({"query": "BROKEN", "path": ".", "recursive": True}),
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        tool_messages = [m for m in payload["messages"] if m["role"] == "tool"]
        assert any("BROKEN" in m["content"] for m in tool_messages)
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({"mode": "report", "report": "done"}),
                    }
                }
            ]
        }

    brain = module.ScriptBrain(request_sender=sender, repo_root=workspace)
    result = brain.think("Inspect the repository.", system="Return JSON only.", use_tools=True)

    assert json.loads(result) == {"mode": "report", "report": "done"}
    assert len(payloads) == 3
    for payload in payloads:
        assert payload["tool_choice"] == "auto"
        assert payload["tools"]


def test_repo_browser_empty_path_defaults_to_repository_root(monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    module = load_script_module("barrot_agent_repo_browser_test")

    browser = module.RepoBrowser(Path(__file__).resolve().parents[1])
    response = browser.print_tree({"path": "", "depth": 1})

    assert response.splitlines()[0] == "."


def test_create_pull_request_accepts_cycle_objects(monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("TASK_TITLE", "Repair issue")
    module = load_script_module("barrot_agent_pr_test")

    calls: dict[str, object] = {}
    cycle = RepairCycleEvidence(cycle_id="cycle-123")
    cycle.commit.branch = "repair/from-cycle"
    cycle.commit.sha = "abc123"
    cycle.issue = {"summary": "repair issue"}

    def fake_run_gh(args):
        calls["args"] = args
        body_path = Path(args[7])
        calls["body_exists_during_call"] = body_path.is_file()
        calls["body_text"] = body_path.read_text(encoding="utf-8") if body_path.is_file() else ""

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(module, "run_gh", fake_run_gh)
    module.create_pull_request(cycle)

    assert "--draft" in calls["args"]
    head_index = calls["args"].index("--head")
    assert calls["args"][head_index + 1] == "repair/from-cycle"
    assert calls["body_exists_during_call"] is True
    assert "cycle-123" in str(calls["body_text"])
    assert "abc123" in str(calls["body_text"])
    assert Path(calls["args"][7]).exists() is False



def test_explicit_read_only_audit_bypasses_bundle_and_repair(monkeypatch):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "AUDIT AND RECOMMEND ONLY. No implementation changes are authorized by this issue.")
    monkeypatch.setenv("TASK_TITLE", "Repository-wide read-only audit")
    monkeypatch.setenv("TASK_MODE", "engineering")
    monkeypatch.setenv("ISSUE_NUMBER", "1167")
    monkeypatch.setenv("BRANCH", "barrot/task-1167")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    module = load_script_module("barrot_agent_read_only_audit_test")
    calls: dict[str, object] = {}

    class FakeBrain:
        def __init__(self, **kwargs):
            calls.setdefault("brain_inits", []).append(kwargs)

        def think(self, message, system=None, use_tools=None, max_output_tokens=None):
            calls["prompt"] = json.loads(message)
            calls["system"] = system
            calls["use_tools"] = use_tools
            calls["max_output_tokens"] = max_output_tokens
            return "## Evidence report\\n\\nCONFIRMED: repository context inspected."

    def forbidden(*args, **kwargs):
        raise AssertionError("audit-only task must not enter bundle or repair execution")

    monkeypatch.setattr(module, "ScriptBrain", FakeBrain)
    monkeypatch.setattr(module, "BundleEngineeringController", forbidden)
    monkeypatch.setattr(module, "RepositoryRepairController", forbidden)
    monkeypatch.setattr(module, "WorkQueueController", forbidden)
    monkeypatch.setattr(module, "configure_git", lambda: None)
    monkeypatch.setattr(module, "checkout_branch", lambda branch: None)
    monkeypatch.setattr(
        module,
        "build_audit_context",
        lambda title, body: {"inventory": "real inventory", "file_context": "source excerpts"},
    )
    monkeypatch.setattr(module, "build_read_only_audit_snapshot", lambda: {"branch_count": 1})
    monkeypatch.setattr(
        module,
        "post_issue_comment",
        lambda message: calls.setdefault("comment", message),
    )
    monkeypatch.setattr(module, "write_collaboration_record", forbidden)
    monkeypatch.setattr(module, "create_pull_request", forbidden)

    module.main()

    assert "## Barrot Read-Only Audit Report" in calls["comment"]
    assert "CONFIRMED: repository context inspected." in calls["comment"]
    assert calls["prompt"]["repository_context"]["inventory"] == "real inventory"
    assert calls["prompt"]["rules"]


def test_script_brain_can_disable_tools_per_call(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    module = load_script_module("barrot_agent_tool_mode_test")
    workspace = tmp_path / "repo"
    workspace.mkdir()
    payloads: list[dict[str, object]] = []

    def sender(payload: dict[str, object]) -> dict[str, object]:
        payloads.append(json.loads(json.dumps(payload)))
        return {"choices": [{"message": {"role": "assistant", "content": "{}"}}]}

    brain = module.ScriptBrain(request_sender=sender, repo_root=workspace)
    result = brain.think("Return a JSON object.", system="JSON only.", use_tools=False, max_output_tokens=1536)

    assert json.loads(result) == {}
    assert len(payloads) == 1
    assert "tools" not in payloads[0]
    assert payloads[0]["response_format"] == {"type": "json_object"}
    assert payloads[0]["reasoning_effort"] == "low"
    assert payloads[0]["max_tokens"] == 1536


def test_repo_browser_open_file_is_bounded_and_confined(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    module = load_script_module("barrot_agent_open_file_test")
    workspace = tmp_path / "repo"
    workspace.mkdir()
    target = workspace / "sample.py"
    target.write_text("\n".join(f"line-{i}" for i in range(1, 151)), encoding="utf-8")
    browser = module.RepoBrowser(workspace)

    result = json.loads(browser.open_file({"path": "sample.py", "line_start": 2, "line_end": 200}))
    assert result["success"] is True
    assert result["line_start"] == 2
    assert result["line_end"] == 61
    assert "2: line-2" in result["content"]
    assert "61: line-61" in result["content"]
    assert "62: line-62" not in result["content"]

    escaped = json.loads(browser.open_file({"path": "../outside.txt"}))
    assert escaped["success"] is False
    assert "escapes the repository root" in escaped["error"]


def test_barrot_agent_dispatch_remains_quarantined_until_integration_gates_are_verified() -> None:
    workflow = (
        Path(__file__).resolve().parents[1] / ".github" / "workflows" / "barrot-agent.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch: {}" in workflow
    assert "permissions: {}" in workflow
    assert "if: \u0024{{ false }}" in workflow
    assert "confirm:" not in workflow
    for forbidden in (
        "schedule:",
        "issues:",
        "contents: write",
        "pull-requests: write",
        "GROQ_API_KEY",
        "GH_TOKEN",
        "scripts/barrot_agent.py",
    ):
        assert forbidden not in workflow


def test_mission_mode_dispatches_primary_xrp_goal_without_provider_or_repository_mutation(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_MODE", "mission")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    module = load_script_module("barrot_agent_primary_mission_dispatch_test")
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("read-only mission mode must not configure git or check out a branch")

    monkeypatch.setattr(module, "configure_git", forbidden)
    monkeypatch.setattr(module, "checkout_branch", forbidden)

    module.main()
    result = json.loads(capsys.readouterr().out)

    assert result["status"] == "READY"
    assert result["mission_id"] == "xrp_intelligence_prediction_engine"
    assert result["priority"] == 1
    assert result["topic_id"] == "xrp_source_provenance"
    assert result["foundation"]["id"] == "barrot_v3"
    assert result["provider_calls"] is False
    assert result["repository_mutation"] is False
    assert result["external_actions_authorized"] is False


def test_mission_mode_advances_only_from_verified_learning_records(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_MODE", "mission")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    from barrot_agent.orchestration.learning_filter import LearningRecord
    from barrot_agent.orchestration.verified_learning_store import (
        VERIFIED_LEARNING_REASON,
        VerifiedLearningStore,
    )

    lesson_store = tmp_path / "data" / "evolution" / "verified_lessons.jsonl"
    lesson_store.parent.mkdir(parents=True)
    verified_store = VerifiedLearningStore(lesson_store)
    assert verified_store.append(
        LearningRecord(
            accepted=True,
            lesson=(
                "Goal: MISSION_TOPIC_ID: xrp_source_provenance\n"
                "Verified findings:\n"
                "- READ_FILE: inspected source provenance requirements.\n"
                "- RUN_TESTS: source receipt regression tests passed."
            ),
            reason=VERIFIED_LEARNING_REASON,
        )
    )

    module = load_script_module("barrot_agent_primary_mission_progress_test")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "configure_git", lambda: (_ for _ in ()).throw(AssertionError("unexpected git configuration")))
    monkeypatch.setattr(module, "checkout_branch", lambda branch: (_ for _ in ()).throw(AssertionError("unexpected checkout")))

    module.main()
    result = json.loads(capsys.readouterr().out)

    assert result["status"] == "READY"
    assert result["topic_id"] == "xrp_public_data_ingestion"
    assert result["provider_calls"] is False
    assert result["repository_mutation"] is False


def test_groq_tpm_rate_limit_retries_once_then_uses_deduplicated_fallback_model(monkeypatch):
    import io
    import urllib.error

    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("BRAIN_MODEL", "openai/gpt-oss-120b")
    monkeypatch.delenv("BRAIN_FALLBACK_MODELS", raising=False)
    module = load_script_module("barrot_agent_groq_tpm_fallback_test")

    calls: list[str] = []
    sleeps: list[float] = []

    def rate_limit_error() -> urllib.error.HTTPError:
        body = (
            '{"error":{"message":"Rate limit reached for model '
            '`openai/gpt-oss-120b` on tokens per minute: Limit 8000, '
            'Used 4116, Requested 4521. Please try again in 0.5s.",'
            '"type":"tokens","code":"rate_limit_exceeded"}}'
        ).encode("utf-8")
        return urllib.error.HTTPError(
            module.GROQ_ENDPOINT,
            429,
            "Too Many Requests",
            {},
            io.BytesIO(body),
        )

    def fake_urlopen(request, timeout=90):
        payload = json.loads(request.data.decode("utf-8"))
        calls.append(payload["model"])
        if payload["model"] == "openai/gpt-oss-120b":
            raise rate_limit_error()
        return io.BytesIO(
            json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": "fallback-ok"}}]}
            ).encode("utf-8")
        )

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(module.time, "sleep", lambda seconds: sleeps.append(seconds))

    result = module._send_groq_request(
        {
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 128,
        }
    )

    assert calls == [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
    ]
    assert sleeps == [0.5]
    assert result["choices"][0]["message"]["content"] == "fallback-ok"
    assert module._groq_fallback_models("openai/gpt-oss-120b") == ["openai/gpt-oss-20b"]




def test_groq_tpm_http_413_falls_back_to_deduplicated_model(monkeypatch):
    import io
    import urllib.error

    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("BRAIN_MODEL", "openai/gpt-oss-120b")
    monkeypatch.delenv("BRAIN_FALLBACK_MODELS", raising=False)
    module = load_script_module("barrot_agent_groq_tpm_413_fallback_test")

    calls: list[str] = []

    def fake_urlopen(request, timeout=90):
        payload = json.loads(request.data.decode("utf-8"))
        calls.append(payload["model"])
        if payload["model"] == "openai/gpt-oss-120b":
            body = (
                '{"error":{"message":"Rate limit reached for model '
                'openai/gpt-oss-120b. Tokens per minute (TPM): '
                'Limit 8000, Requested 11534, Used 0."}}'
            ).encode("utf-8")
            raise urllib.error.HTTPError(
                module.GROQ_ENDPOINT,
                413,
                "Content Too Large",
                {},
                io.BytesIO(body),
            )
        return io.BytesIO(
            json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": "fallback-ok"}}]}
            ).encode("utf-8")
        )

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)

    result = module._send_groq_request(
        {
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 128,
        }
    )

    assert calls == ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    assert result["choices"][0]["message"]["content"] == "fallback-ok"
    assert module._is_groq_rate_limit_error(
        RuntimeError(
            "Groq HTTP 413: Rate limit reached. Tokens per minute (TPM): "
            "Limit 8000, Requested 11534, Used 0."
        )
    )

def test_deterministic_rate_limit_report_is_explicitly_blocked_and_read_only(monkeypatch):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    module = load_script_module("barrot_agent_deterministic_rate_limit_report_test")

    error = RuntimeError(
        "Groq HTTP 413: Rate limit reached for openai/gpt-oss-120b; "
        "Tokens per minute (TPM): Limit 8000, Requested 11534, Used 0."
    )
    assert module._is_groq_rate_limit_error(error)

    report = module._build_deterministic_rate_limit_report(
        task_title="Repository-wide integration audit",
        issue_number="1652",
        error=error,
        audit_context={
            "inventory": "tracked repository inventory",
            "github_context": "PR #1640 and PR #1643",
            "file_context": "read-only file excerpts",
            "directory_context": "top-level tree",
        },
        snapshot={"head": "abc123", "working_tree": "clean", "actions": {"runs": []}},
    )

    assert "**Status:** `BLOCKED_PROVIDER_RATE_LIMIT`" in report
    assert "Repository-wide integration audit" in report
    assert "#1652" in report
    assert "PR #1640 and PR #1643" in report
    assert "No repository source file was changed" in report
    assert "Repository repair is **not complete**" in report


def test_bundle_provider_rate_limit_posts_deterministic_snapshot_without_starting_repair(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("TASK_BODY", "Implement the requested repository improvement.")
    monkeypatch.setenv("TASK_TITLE", "Continue Barrot integration")
    monkeypatch.setenv("TASK_MODE", "engineering")
    monkeypatch.setenv("ISSUE_NUMBER", "1652")
    monkeypatch.setenv("BRANCH", "barrot/task-1652")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    module = load_script_module("barrot_agent_bundle_rate_limit_fallback_test")
    calls: dict[str, object] = {}

    class FakeBundleController:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, **kwargs):
            raise RuntimeError(
                "Groq HTTP 429: rate_limit_exceeded; tokens per minute limit exhausted."
            )

    def forbidden(*args, **kwargs):
        raise AssertionError("rate-limit fallback must not start repository repair or PR creation")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "BundleEngineeringController", FakeBundleController)
    monkeypatch.setattr(module, "configure_git", lambda: None)
    monkeypatch.setattr(module, "checkout_branch", lambda branch: None)
    monkeypatch.setattr(
        module,
        "build_audit_context",
        lambda title, body: {
            "inventory": "tracked files",
            "github_context": "PR #1640",
            "file_context": "read-only excerpts",
            "directory_context": "repository tree",
        },
    )
    monkeypatch.setattr(
        module,
        "build_read_only_audit_snapshot",
        lambda: {"head": "abc123", "working_tree": "clean"},
    )
    monkeypatch.setattr(
        module,
        "post_issue_comment",
        lambda message: calls.setdefault("comment", message),
    )
    monkeypatch.setattr(module, "RepositoryRepairController", forbidden)
    monkeypatch.setattr(module, "WorkQueueController", forbidden)
    monkeypatch.setattr(module, "create_pull_request", forbidden)

    with pytest.raises(SystemExit):
        module.main()

    report = calls["comment"]
    assert "**Status:** `BLOCKED_PROVIDER_RATE_LIMIT`" in report
    assert "PR #1640" in report
    assert "No repository source file was changed" in report
    assert "Repository repair is **not complete**" in report
