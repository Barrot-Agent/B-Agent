from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from barrot_agent.orchestration.repository_repair import RepairCycleEvidence


SCRIPT_PATH = Path("/home/runner/work/B-Agent/B-Agent/scripts/barrot_agent.py")


def load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_barrot_agent_main_routes_through_repository_repair_controller(monkeypatch):
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

        def run(self, **kwargs):
            calls["run"] = kwargs
            cycle = RepairCycleEvidence(cycle_id="cycle-123")
            cycle.status = "no_repair_required"
            cycle.current_state = "NO_REPAIR_REQUIRED"
            cycle.report = "Already healthy."
            return cycle

    monkeypatch.setattr(module, "RepositoryRepairController", FakeController)
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
    result = brain.think("Inspect the repository.", system="Return JSON only.")

    assert json.loads(result) == {"mode": "report", "report": "done"}
    assert len(payloads) == 3
    for payload in payloads:
        assert payload["tool_choice"] == "auto"
        assert payload["tools"]


def test_repo_browser_rejects_empty_path_arguments(monkeypatch) -> None:
    monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    module = load_script_module("barrot_agent_repo_browser_test")

    browser = module.RepoBrowser(Path("/home/runner/work/B-Agent/B-Agent"))
    response = json.loads(browser.print_tree({"path": "", "depth": 1}))

    assert response["success"] is False
    assert "non-empty" in response["error"]
