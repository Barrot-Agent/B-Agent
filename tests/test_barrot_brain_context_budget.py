import json
import subprocess
from types import SimpleNamespace

import pytest
import requests

from barrot_agent.barrot_brain import BarrotBrain
from barrot_agent.context_budget import (
    MAX_ESTIMATED_INPUT_TOKENS,
    estimate_messages_tokens,
)
from barrot_agent.orchestration.repository_repair import (
    ModelFailure,
    ModelFailureCode,
    RepairPlanner,
    RepositoryRepairController,
)


class RecordingBrain:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def think(self, message, history=None, system=None):
        self.calls.append({"message": message, "system": system})
        return self.response


class ToolAwareRateLimitedBrain:
    def __init__(self):
        self.calls = []

    def think(self, message, history=None, system=None, use_tools=False, max_output_tokens=None):
        self.calls.append({"message": message, "system": system, "use_tools": use_tools})
        return "[BARROT_RATE_LIMITED] provider=Groq; TPM 8099 exceeds 8000"


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = str(self._payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}: {self.text}")


def _init_clean_task_repo(path):
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", "task"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Barrot Test"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "barrot-test@example.invalid"], cwd=path, check=True)
    (path / "README.md").write_text("clean test repository\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True, text=True)


def test_conservative_estimator_counts_system_and_user_messages():
    messages = [
        {"role": "system", "content": "abcd"},
        {"role": "user", "content": "123456"},
    ]
    assert estimate_messages_tokens(messages) == 16 + 2 + 16 + 3
    assert MAX_ESTIMATED_INPUT_TOKENS == 4800


def test_barrot_brain_blocks_oversized_context_before_any_provider_call(monkeypatch):
    brain = BarrotBrain()
    brain.auth = SimpleNamespace(ready=False)
    brain.groq_key = "test-groq-key"
    brain.fireworks_key = "test-fireworks-key"
    brain.allow_fireworks_fallback = True
    calls = []

    def fake_post(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("oversized context must be blocked before HTTP")

    monkeypatch.setattr("barrot_agent.barrot_brain.requests.post", fake_post)
    result = brain.think("x" * 20_000, system="short system")
    assert result.startswith("[BARROT_CONTEXT_BUDGET_EXCEEDED]")
    assert "no provider request was sent" in result
    assert calls == []



def test_external_inference_is_disabled_by_default_without_provider_requests(monkeypatch):
    brain = BarrotBrain()
    brain.auth = SimpleNamespace(ready=False)
    brain.groq_key = "test-groq-key"
    brain.fireworks_key = "test-fireworks-key"
    brain.allow_fireworks_fallback = True
    calls = []

    def fake_post(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("default-disabled external inference must not send HTTP")

    monkeypatch.setattr("barrot_agent.barrot_brain.requests.post", fake_post)
    result = brain.think("small request", system="short system")
    assert result.startswith("[BARROT_EXTERNAL_INFERENCE_DISABLED]")
    assert "no provider request was sent" in result
    assert brain.backend_name == "None (external inference disabled)"
    assert calls == []

def test_groq_429_fails_fast_without_retry_or_fireworks_fallback(monkeypatch):
    brain = BarrotBrain(allow_external_inference=True)
    brain.auth = SimpleNamespace(ready=False)
    brain.groq_key = "test-groq-key"
    brain.fireworks_key = "test-fireworks-key"
    brain.allow_fireworks_fallback = True
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        return FakeResponse(429, {"error": {"message": "TPM 8099 exceeds 8000"}})

    monkeypatch.setattr("barrot_agent.barrot_brain.requests.post", fake_post)
    result = brain.think("small request", system="short system")
    assert result.startswith("[BARROT_RATE_LIMITED]")
    assert "no retry" in result
    assert calls == [brain.GROQ_ENDPOINT]


def test_fireworks_fallback_is_disabled_without_explicit_opt_in(monkeypatch):
    brain = BarrotBrain(allow_external_inference=True)
    brain.auth = SimpleNamespace(ready=False)
    brain.groq_key = "test-groq-key"
    brain.fireworks_key = "test-fireworks-key"
    brain.allow_fireworks_fallback = False
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        return FakeResponse(503, {"error": {"message": "provider unavailable"}})

    monkeypatch.setattr("barrot_agent.barrot_brain.requests.post", fake_post)
    result = brain.think("small request", system="short system")
    assert result.startswith("[BARROT_PROVIDER_UNAVAILABLE]")
    assert "Fireworks fallback is disabled" in result
    assert calls == [brain.GROQ_ENDPOINT]


def test_repair_planner_blocks_oversized_context_before_calling_brain():
    brain = RecordingBrain('{"mode":"report","report":"should not be reached"}')
    planner = RepairPlanner(brain, max_attempts=3)
    with pytest.raises(ModelFailure) as raised:
        planner.generate("x" * 20_000)
    assert raised.value.code == ModelFailureCode.CONTEXT_BUDGET
    assert brain.calls == []


def test_repair_planner_maps_rate_limit_marker_without_retry():
    brain = RecordingBrain("[BARROT_RATE_LIMITED] provider=Groq; TPM 8099 exceeds 8000")
    planner = RepairPlanner(brain, max_attempts=3, backoff_seconds=0)
    with pytest.raises(ModelFailure) as raised:
        planner.generate("small request")
    assert raised.value.code == ModelFailureCode.RATE_LIMITED_TPM
    assert len(brain.calls) == 1


def test_repair_planner_preserves_full_safety_system_for_in_budget_request():
    brain = RecordingBrain('{"mode":"report","report":"read-only result"}')
    planner = RepairPlanner(brain)
    directive = planner.generate("small request")
    assert directive.mode == "report"
    assert len(brain.calls) == 1
    system = brain.calls[0]["system"]
    assert "Never claim the repair succeeded." in system
    assert 'Use only operation type "replace".' in system
    assert 'exact current text for "old".' in system


def test_repository_repair_records_read_only_snapshot_after_planner_rate_limit(tmp_path, monkeypatch):
    _init_clean_task_repo(tmp_path)
    brain = BarrotBrain(allow_external_inference=True)
    brain.auth = SimpleNamespace(ready=False)
    brain.groq_key = "test-groq-key"
    brain.fireworks_key = "test-fireworks-key"
    brain.allow_fireworks_fallback = True
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        return FakeResponse(429, {"error": {"message": "TPM 8099 exceeds 8000"}})

    monkeypatch.setattr("barrot_agent.barrot_brain.requests.post", fake_post)
    controller = RepositoryRepairController(brain=brain, workspace=tmp_path)
    cycle = controller.run(
        task_title="Small repository task",
        task_body="Inspect one configured subsystem.",
        issue_number="1657",
        repo="Barrot-Agent/B-Agent",
        branch="task",
        audit_context={"inventory": "README.md"},
    )
    assert cycle.status == "blocked"
    assert cycle.failure.code == ModelFailureCode.RATE_LIMITED_TPM.value
    report = json.loads(cycle.report)
    assert report["same_provider_retry_performed"] is False
    assert report["patch_applied"] is False
    assert report["commit_created"] is False
    assert report["remote_write_attempted"] is False
    assert calls == [brain.GROQ_ENDPOINT]
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "clean test repository\n"


def test_repository_repair_stops_after_rate_limited_read_only_audit(tmp_path):
    _init_clean_task_repo(tmp_path)
    brain = ToolAwareRateLimitedBrain()
    controller = RepositoryRepairController(brain=brain, workspace=tmp_path)
    cycle = controller.run(
        task_title="Small repository task",
        task_body="Inspect one configured subsystem.",
        issue_number="1657",
        repo="Barrot-Agent/B-Agent",
        branch="task",
        audit_context={"inventory": "README.md"},
    )
    assert cycle.status == "blocked"
    assert cycle.failure.code == ModelFailureCode.RATE_LIMITED_TPM.value
    report = json.loads(cycle.report)
    assert report["same_provider_retry_performed"] is False
    assert report["patch_applied"] is False
    assert len(brain.calls) == 1
    assert brain.calls[0]["use_tools"] is True
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "clean test repository\n"
