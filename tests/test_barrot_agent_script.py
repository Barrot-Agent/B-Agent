from __future__ import annotations

import importlib.util
import json
from types import SimpleNamespace
from pathlib import Path

from barrot_agent.orchestration.repository_repair import RepairCycleEvidence, WorkItemEvidence


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "barrot_agent.py"


def load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_barrot_agent_main_routes_through_work_queue_controller(monkeypatch):
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

        def run(self, **kwargs):
            calls["run"] = kwargs
            work = WorkItemEvidence(work_id="work-123")
            cycle = RepairCycleEvidence(cycle_id="cycle-123")
            cycle.status = "no_repair_required"
            cycle.current_state = "NO_REPAIR_REQUIRED"
            cycle.report = "Already healthy."
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
                review=SimpleNamespace(quality_score=100, fingerprint="sha256:test"),
            )

    class FakeLifecycleStore:
        def __init__(self, *args, **kwargs):
            pass

        def save_plan(self, *args, **kwargs):
            return "test-plan"

        def record_execution(self, *args, **kwargs):
            return None

    monkeypatch.setattr(module, "BundleEngineeringController", FakeBundleController)
    monkeypatch.setattr(module, "BundleLifecycleStore", FakeLifecycleStore)
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
    assert calls["comment"] == "Already healthy."
    assert "record" in calls
    assert "pr" not in calls


def test_barrot_agent_report_only_does_not_post_issue_comment(monkeypatch):
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
                review=SimpleNamespace(quality_score=100, fingerprint="sha256:test"),
            )

    class FakeLifecycleStore:
        def __init__(self, *args, **kwargs):
            pass

        def save_plan(self, *args, **kwargs):
            return "test-plan"

        def record_execution(self, *args, **kwargs):
            return None

    monkeypatch.setattr(module, "BundleEngineeringController", FakeBundleController)
    monkeypatch.setattr(module, "BundleLifecycleStore", FakeLifecycleStore)
    monkeypatch.setattr(module, "RepositoryRepairController", FakeController)
    monkeypatch.setattr(module, "WorkQueueController", FakeQueue)
    monkeypatch.setattr(module, "configure_git", lambda: None)
    monkeypatch.setattr(module, "checkout_branch", lambda branch: None)
    monkeypatch.setattr(module, "build_audit_context", lambda title, body: {"inventory": f"{title}:{body}"})
    monkeypatch.setattr(module, "post_issue_comment", lambda message: calls.setdefault("comment", message))
    monkeypatch.setattr(module, "write_collaboration_record", lambda cycle: calls.setdefault("record", cycle))

    module.main()

    assert "record" in calls
    assert "comment" not in calls


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

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(module, "run_gh", fake_run_gh)
    module.create_pull_request(cycle)

    assert calls["args"][8] == "--head"
    assert calls["args"][9] == "repair/from-cycle"



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

        def think(self, message, system=None):
            calls["prompt"] = json.loads(message)
            calls["system"] = system
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
    result = brain.think("Return a JSON object.", system="JSON only.", use_tools=False)

    assert json.loads(result) == {}
    assert len(payloads) == 1
    assert "tools" not in payloads[0]
    assert payloads[0]["response_format"] == {"type": "json_object"}
    assert payloads[0]["reasoning_effort"] == "low"
