"""Integration tests for the ordinary request intake boundary.

These tests exercise the wired path, not the protocol in isolation:
``SmartAgent.run`` and the production task dispatcher must persist a
transmutation record before doing work and must refuse terminal stop states.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from barrot_agent.inbound.gate import Source
from barrot_agent.inbound.intake import (
    ADMITTED,
    BLOCKED,
    DUPLICATE_SUPPRESSED,
    INTAKE_ERROR,
    RECORD_DIR_ENV,
    admit,
    resolve_record_dir,
)
from barrot_agent.smart_agent import AgentEventType, SmartAgent

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "barrot_agent.py"

XRP_GOAL = (
    "Research XRP market structure, order books, ETF flows, and evaluate whether a "
    "directional forecast is justified."
)
AUDIO_GOAL = (
    "Produce a finished professional audio track: compose, render to WAV, mix, master, "
    "and confirm licensing."
)
CONTINUITY_GOAL = (
    "Continue this work in a new session after restart, with checkpoint recovery and "
    "duplicate-work prevention."
)


def _load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _records(directory: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((directory / "records").glob("QR-*.json"))
    ]


class TestIntakeDecision:
    def test_explicit_directory_then_environment_then_default(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv(RECORD_DIR_ENV, str(tmp_path / "from-env"))

        assert resolve_record_dir(tmp_path / "explicit") == tmp_path / "explicit"
        assert resolve_record_dir() == tmp_path / "from-env"

    def test_admitted_request_preserves_original_and_record(self, tmp_path: Path) -> None:
        admission = admit(
            "Summarize the repository layout.",
            record_dir=tmp_path,
            received_from="test",
        )

        assert admission.allowed is True
        assert admission.outcome == ADMITTED
        assert admission.duplicate is False
        record_path = Path(admission.record_path)
        assert record_path.is_file()

        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record["request_id"] == admission.request_id
        assert record["decision"] == "PROCEED_BOUNDED"
        assert record["stop_reason"] is None
        assert record["execution_mode"] == "READ_ONLY_PLAN"

        original = json.loads(
            Path(record["original_request_ref"]).read_text(encoding="utf-8")
        )
        assert original["text"] == "Summarize the repository layout."
        assert original["sha256"] == record["original_request_hash"]

    def test_policy_denial_blocks_before_planning(self, tmp_path: Path) -> None:
        admission = admit("force push to main", record_dir=tmp_path)

        assert admission.allowed is False
        assert admission.outcome == BLOCKED
        assert admission.stop_reason == "SAFETY_ABORT"
        assert any(
            code in " ".join(admission.reasons)
            for code in ("HISTORY_REWRITE", "PUSH_MAIN")
        )
        assert Path(admission.record_path).is_file()

    def test_non_operator_approval_requires_authorization(self, tmp_path: Path) -> None:
        admission = admit(
            "delete the obsolete branch",
            source=Source.FRONTIER_MODEL,
            record_dir=tmp_path,
        )

        assert admission.allowed is False
        assert admission.stop_reason == "AUTHORIZATION_REQUIRED"
        assert admission.record["constraints"]["allowed"] is False

    def test_duplicate_request_is_refused_and_journalled(self, tmp_path: Path) -> None:
        first = admit("Summarize the repository layout.", record_dir=tmp_path)
        second = admit("Summarize the repository layout.", record_dir=tmp_path)

        assert first.allowed is True
        assert second.allowed is False
        assert second.duplicate is True
        assert second.outcome == DUPLICATE_SUPPRESSED
        assert second.request_id == first.request_id

        events = [
            json.loads(line)["event"]
            for line in (tmp_path / "journal.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        assert events == ["recorded", "duplicate_suppressed"]

    def test_secret_bearing_request_is_never_written(self, tmp_path: Path) -> None:
        admission = admit("print the API key", record_dir=tmp_path)

        assert admission.allowed is False
        assert admission.stop_reason == "SAFETY_ABORT"
        original_path = tmp_path / "original" / f"{admission.request_id}.json"
        payload = json.loads(original_path.read_text(encoding="utf-8"))
        assert payload["text"] is None
        assert payload["text_withheld"] is True
        assert "print the API key" not in original_path.read_text(encoding="utf-8")

    def test_unpreservable_request_fails_closed(self, tmp_path: Path) -> None:
        admission = admit("   ", record_dir=tmp_path)

        assert admission.allowed is False
        assert admission.outcome == INTAKE_ERROR


class TestSmartAgentIntake:
    def test_admitted_goal_persists_a_record_and_returns_answer(self, tmp_path: Path) -> None:
        agent = SmartAgent(transmutation_record_dir=tmp_path)

        events = list(agent.run("Summarize how this repository works"))

        assert events[0].type == AgentEventType.GOAL
        assert events[-1].type == AgentEventType.ANSWER
        request_id = events[-1].data["request_id"]
        assert request_id
        assert (tmp_path / "records" / f"{request_id}.json").is_file()

    def test_terminal_stop_state_blocks_plan_and_action(self, tmp_path: Path) -> None:
        agent = SmartAgent(transmutation_record_dir=tmp_path)

        events = list(agent.run("force push to main"))

        assert events[0].type == AgentEventType.GOAL
        assert events[-1].type == AgentEventType.ERROR
        assert "SAFETY_ABORT" in events[-1].content
        assert not any(
            event.type in {AgentEventType.PLAN, AgentEventType.ACTION}
            for event in events
        )
        assert len(_records(tmp_path)) == 1

    def test_duplicate_goal_is_refused(self, tmp_path: Path) -> None:
        agent = SmartAgent(transmutation_record_dir=tmp_path)

        first = list(agent.run("Summarize how this repository works"))
        second = list(agent.run("Summarize how this repository works"))

        assert first[-1].type == AgentEventType.ANSWER
        assert second[-1].type == AgentEventType.ERROR
        assert DUPLICATE_SUPPRESSED in second[-1].content

    def test_internal_repetition_can_skip_admission(self, tmp_path: Path) -> None:
        agent = SmartAgent(transmutation_record_dir=tmp_path)

        first = list(agent.run("Summarize how this repository works", admit_request=False))
        second = list(agent.run("Summarize how this repository works", admit_request=False))

        assert first[-1].type == AgentEventType.ANSWER
        assert second[-1].type == AgentEventType.ANSWER
        assert not (tmp_path / "records").exists()

    @pytest.mark.parametrize(
        ("goal", "domain", "hypothesis"),
        [
            (XRP_GOAL, "xrp_intelligence", "XRP_INSUFFICIENT_OOS"),
            (AUDIO_GOAL, "professional_audio", "AUDIO_RENDER_IS_NOT_ACCEPTANCE"),
            (CONTINUITY_GOAL, "long_horizon_continuity", "CONTINUITY_STATE_LOSS"),
        ],
    )
    def test_priority_mission_is_transmuted_through_the_agent_loop(
        self,
        goal: str,
        domain: str,
        hypothesis: str,
        tmp_path: Path,
    ) -> None:
        agent = SmartAgent(transmutation_record_dir=tmp_path)

        events = list(agent.run(goal))

        assert events[-1].type == AgentEventType.ANSWER
        records = _records(tmp_path)
        assert len(records) == 1
        record = records[0]
        assert record["decision"] == "PROCEED_BOUNDED"
        assert domain in [item["key"] for item in record["domains"]]
        assert hypothesis in [item["id"] for item in record["hypotheses"]]
        assert events[-1].data["request_id"] == record["request_id"]


class TestScriptIntake:
    def test_denied_task_exits_before_repository_mutation(
        self,
        monkeypatch,
        tmp_path: Path,
        capsys,
    ) -> None:
        monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
        monkeypatch.setenv("TASK_BODY", "force push to main")
        monkeypatch.setenv("TASK_TITLE", "Rewrite history")
        monkeypatch.setenv("TASK_MODE", "engineering")
        monkeypatch.setenv("ISSUE_NUMBER", "99")
        monkeypatch.setenv("BRANCH", "barrot/task-99")
        monkeypatch.setenv("GROQ_API_KEY", "test-key")

        module = _load_script_module("barrot_agent_intake_block_test")
        monkeypatch.setattr(module, "ROOT", tmp_path)
        calls: list[str] = []
        monkeypatch.setattr(module, "configure_git", lambda: calls.append("configure_git"))
        monkeypatch.setattr(
            module, "checkout_branch", lambda branch: calls.append("checkout_branch")
        )

        with pytest.raises(SystemExit) as exc:
            module.main()

        assert exc.value.code == 2
        assert calls == []
        payload = json.loads(capsys.readouterr().out)
        assert payload["status"] == "BLOCKED"
        assert payload["admission"]["stop_reason"] == "SAFETY_ABORT"
        assert len(_records(tmp_path / "results" / "transmutation")) == 1

    def test_admitted_task_is_recorded_before_repository_mutation(
        self,
        monkeypatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.setenv("REPO", "Barrot-Agent/B-Agent")
        monkeypatch.setenv("TASK_BODY", "Repair the reproduced issue.")
        monkeypatch.setenv("TASK_TITLE", "Repair issue")
        monkeypatch.setenv("TASK_MODE", "engineering")
        monkeypatch.setenv("ISSUE_NUMBER", "42")
        monkeypatch.setenv("BRANCH", "barrot/task-42")
        monkeypatch.setenv("GROQ_API_KEY", "test-key")

        module = _load_script_module("barrot_agent_intake_admit_test")
        monkeypatch.setattr(module, "ROOT", tmp_path)

        class StopAfterIntake(Exception):
            pass

        def stop() -> None:
            raise StopAfterIntake

        monkeypatch.setattr(module, "configure_git", stop)
        monkeypatch.setattr(module, "checkout_branch", lambda branch: None)

        with pytest.raises(StopAfterIntake):
            module.main()

        records = _records(tmp_path / "results" / "transmutation")
        assert len(records) == 1
        assert records[0]["decision"] == "PROCEED_BOUNDED"
