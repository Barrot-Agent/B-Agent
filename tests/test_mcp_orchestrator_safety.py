from __future__ import annotations

import sys
from types import SimpleNamespace

from barrot_agent.mcp_approval import ActionType, ApprovalDecision
from barrot_agent.orchestration.mcp_orchestrator import MCPOrchestrator, OrchestratorConfig, OrchestratorStep


class DenyGate:
    def __init__(self) -> None:
        self.requests = []

    def request_approval(self, request):
        self.requests.append(request)
        return ApprovalDecision(
            request_id=request.request_id,
            approved=False,
            decided_by="test",
            reason="denied by test gate",
        )


class Episode:
    title = "Safety test episode"
    scenes = ["scene"]
    characters = ["character"]
    description = "test"
    runtime_minutes = 1

    def full_script(self):
        return "test script"


def install_episode_fixture(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "stupid_sindy_series_generator",
        SimpleNamespace(get_episode=lambda _episode_number: Episode()),
    )


def test_external_mcp_operations_default_off_and_fail_closed():
    config = OrchestratorConfig()
    assert config.download_models is False
    assert config.use_databricks is False
    assert config.commit_to_github is False
    assert config.trigger_cicd is False
    assert config.approval_mode == "always_deny"
    assert config.interactive_approval is False


def test_huggingface_download_requires_approval(monkeypatch):
    install_episode_fixture(monkeypatch)
    orchestrator = MCPOrchestrator(OrchestratorConfig(download_models=True))
    gate = DenyGate()
    orchestrator._approval_gate = gate
    orchestrator._get_hf = lambda: (_ for _ in ()).throw(AssertionError("HF client must not initialize"))
    orchestrator._local_render = lambda _episode_number: None

    events = list(orchestrator.run_episode(1))

    assert [request.action_type for request in gate.requests] == [ActionType.INSTALL]
    assert any(event.step == OrchestratorStep.HF_MODELS and "blocked" in event.message.lower() for event in events)


def test_databricks_submission_requires_approval(monkeypatch):
    install_episode_fixture(monkeypatch)
    config = OrchestratorConfig(use_databricks=True, databricks_host="https://workspace.example", databricks_token="test-token")
    orchestrator = MCPOrchestrator(config)
    gate = DenyGate()
    orchestrator._approval_gate = gate
    orchestrator._get_db = lambda: (_ for _ in ()).throw(AssertionError("Databricks client must not initialize"))
    orchestrator._local_render = lambda _episode_number: None

    events = list(orchestrator.run_episode(1))

    assert [request.action_type for request in gate.requests] == [ActionType.WORKFLOW_EXECUTION]
    assert any(event.step == OrchestratorStep.DATABRICKS_SUBMIT and "blocked" in event.message.lower() for event in events)


def test_github_commit_and_cicd_each_require_separate_approval(monkeypatch, tmp_path):
    install_episode_fixture(monkeypatch)
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"test-video")
    config = OrchestratorConfig(commit_to_github=True, trigger_cicd=True, github_token="test-token")
    orchestrator = MCPOrchestrator(config)
    gate = DenyGate()
    orchestrator._approval_gate = gate
    orchestrator._get_gh = lambda: (_ for _ in ()).throw(AssertionError("GitHub client must not initialize"))
    orchestrator._local_render = lambda _episode_number: str(video)

    events = list(orchestrator.run_episode(1))

    assert [request.action_type for request in gate.requests] == [ActionType.REPO_WRITE, ActionType.WORKFLOW_EXECUTION]
    blocked = [
        event for event in events
        if event.step in {OrchestratorStep.GITHUB_COMMIT, OrchestratorStep.CICD_TRIGGER}
        and "blocked" in event.message.lower()
    ]
    assert len(blocked) == 2
