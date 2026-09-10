from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from barrot_agent.orchestration.repository_repair import (
    FailureEvidence,
    RemoteSyncEvidence,
    RepairCycleEvidence,
    RepairError,
    RepairState,
    RepositoryRepairController,
)


class FakeBrain:
    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = 0

    def think(self, message: str, history=None, system=None) -> str:
        del message, history, system
        index = self.calls if self.calls < len(self._responses) else len(self._responses) - 1
        response = self._responses[index]
        self.calls += 1
        if isinstance(response, Exception):
            raise response
        return response


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def init_repo(tmp_path: Path, *, origin: bool = False, gitlab: bool = False) -> tuple[Path, str]:
    workspace = tmp_path / "repo"
    workspace.mkdir()
    (workspace / "barrot_agent").mkdir()
    (workspace / "scripts").mkdir()
    (workspace / "barrot_agent" / "__init__.py").write_text("", encoding="utf-8")
    (workspace / "scripts" / "__init__.py").write_text("", encoding="utf-8")
    (workspace / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
    target = workspace / "barrot_agent" / "target.py"
    target.write_text('FLAG = "BROKEN"\n', encoding="utf-8")

    assert git(workspace, "init", "-b", "main").returncode == 0
    assert git(workspace, "config", "user.email", "test@example.com").returncode == 0
    assert git(workspace, "config", "user.name", "Test User").returncode == 0
    assert git(workspace, "add", ".").returncode == 0
    assert git(workspace, "commit", "-m", "initial").returncode == 0
    assert git(workspace, "checkout", "-b", "repair/test").returncode == 0

    if origin:
        remote = tmp_path / "origin.git"
        assert git(tmp_path, "init", "--bare", str(remote)).returncode == 0
        assert git(workspace, "remote", "add", "origin", str(remote)).returncode == 0
    if gitlab:
        remote = tmp_path / "gitlab.git"
        assert git(tmp_path, "init", "--bare", str(remote)).returncode == 0
        assert git(workspace, "remote", "add", "gitlab", str(remote)).returncode == 0

    return workspace, "barrot_agent/target.py"


def defect_command(path: str, token: str = "BROKEN", *, timeout: int = 5) -> dict[str, object]:
    code = (
        "from pathlib import Path; import sys; "
        f"text = Path({path!r}).read_text(); "
        f"sys.exit(1 if {token!r} in text else 0)"
    )
    return {"program": sys.executable, "args": ["-c", code], "timeout": timeout}


def success_command(*, timeout: int = 5) -> dict[str, object]:
    return {"program": sys.executable, "args": ["-c", "import sys; sys.exit(0)"], "timeout": timeout}


def failure_command(*, timeout: int = 5) -> dict[str, object]:
    return {"program": sys.executable, "args": ["-c", "import sys; sys.exit(1)"], "timeout": timeout}


def timeout_command(*, timeout: int = 1) -> dict[str, object]:
    return {
        "program": sys.executable,
        "args": ["-c", "import time; time.sleep(2)"],
        "timeout": timeout,
    }


def repair_payload(
    path: str,
    *,
    old: str = 'FLAG = "BROKEN"',
    new: str = 'FLAG = "FIXED"',
    reproduction_commands: list[dict[str, object]] | None = None,
    validation_commands: list[dict[str, object]] | None = None,
    resolution_commands: list[dict[str, object]] | None = None,
    expected_files: list[str] | None = None,
    mode: str = "repair",
) -> str:
    payload = {
        "mode": mode,
        "report": "",
        "issue": {
            "summary": "target file remains broken",
            "evidence": [f"{path} contains the BROKEN marker"],
            "files": [path],
            "reproduction_commands": reproduction_commands or [defect_command(path)],
            "validation_commands": validation_commands or [defect_command(path)],
            "resolution_commands": resolution_commands or [defect_command(path)],
        },
        "repair_plan": {
            "summary": "Replace the BROKEN marker with FIXED",
            "reason": "The reproduced defect is the BROKEN marker in the target file.",
        },
        "changeset": {
            "operations": [
                {
                    "type": "replace",
                    "path": path,
                    "old": old,
                    "new": new,
                    "reason": "Swap the broken marker for the fixed marker.",
                }
            ],
            "expected_files": expected_files or [path],
            "commit_message": "Fix broken target marker",
        },
    }
    return json.dumps(payload)


def make_controller(workspace: Path, brain: FakeBrain) -> RepositoryRepairController:
    return RepositoryRepairController(
        brain=brain,
        workspace=workspace,
        planner_attempts=3,
    )


def run_cycle(workspace: Path, brain: FakeBrain) -> RepairCycleEvidence:
    controller = make_controller(workspace, brain)
    return controller.run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": "barrot_agent/target.py"},
    )


def test_healthy_repository_returns_no_repair_required(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    (workspace / path).write_text('FLAG = "FIXED"\n', encoding="utf-8")
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "no_repair_required"
    assert cycle.current_state == RepairState.NO_REPAIR_REQUIRED.value
    assert cycle.commit.created is False


def test_reproducible_defect_starts_repair_lifecycle(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.issue_identified is True
    assert cycle.issue_reproduced is True
    assert RepairState.PATCHING.value in cycle.state_history


def test_invalid_llm_json_fails_safely(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = FakeBrain("{not-json")

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "failed"
    assert cycle.failure is not None
    assert cycle.failure.code == "LLM_INVALID_JSON"


def test_llm_rate_limit_uses_bounded_retries(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = FakeBrain(RuntimeError("429 rate limited"), RuntimeError("429 rate limited"), RuntimeError("429 rate limited"))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "failed"
    assert cycle.failure is not None
    assert cycle.failure.code == "LLM_RATE_LIMITED"
    assert brain.calls == 3


def test_llm_tool_conflict_is_classified_safely(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = FakeBrain(RuntimeError("Tool choice is none, but model called a tool"))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "failed"
    assert cycle.failure is not None
    assert cycle.failure.code == "LLM_TOOL_CONFLICT"


def test_invalid_patch_path_is_rejected(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    payload = repair_payload(path, expected_files=["../escape.py"])
    data = json.loads(payload)
    data["changeset"]["operations"][0]["path"] = "../escape.py"
    brain = FakeBrain(json.dumps(data))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "failed"
    assert cycle.failure is not None
    assert cycle.failure.code == "SNAPSHOT_FAILED"


def test_missing_old_text_rejects_patch(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    brain = FakeBrain(repair_payload(path, old='FLAG = "MISSING"'))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "rolled_back"
    assert cycle.failure is not None
    assert cycle.failure.rollback_succeeded is True


def test_ambiguous_replacement_rejects_patch(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    (workspace / path).write_text('FLAG = "BROKEN"\nFLAG = "BROKEN"\n', encoding="utf-8")
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "rolled_back"
    assert cycle.failure is not None
    assert cycle.failure.rollback_succeeded is True


def test_successful_patch_runs_validation(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert "local_validation" in cycle.validation
    assert cycle.local_validation_passed is True


def test_validation_failure_restores_workspace(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    brain = FakeBrain(
        repair_payload(
            path,
            validation_commands=[failure_command()],
            resolution_commands=[success_command()],
        )
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "rolled_back"
    assert (workspace / path).read_text(encoding="utf-8") == 'FLAG = "BROKEN"\n'


def test_successful_commit_records_sha(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.commit.created is True
    assert cycle.commit.exists is True
    assert len(cycle.commit.sha) == 40


def test_remote_sha_mismatch_blocks_complete(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    controller = make_controller(workspace, FakeBrain(repair_payload(path)))

    def mismatch(remote: str, branch: str, sha: str) -> RemoteSyncEvidence:
        return RemoteSyncEvidence(
            remote=remote,
            applicable=True,
            attempted=True,
            pushed=True,
            verified=False,
            branch=branch,
            sha=sha,
            reason="remote head different",
        )

    monkeypatch.setattr(controller.remote_verifier, "push_and_verify", mismatch)
    cycle = controller.run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": "barrot_agent/target.py"},
    )

    assert cycle.status == "failed"
    assert cycle.commit.created is True
    assert cycle.commit.remote_verified is False


def test_remote_verification_failure_is_recorded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, path = init_repo(tmp_path, origin=True, gitlab=True)
    controller = make_controller(workspace, FakeBrain(repair_payload(path)))
    original = controller.remote_verifier.push_and_verify

    def mixed(remote: str, branch: str, sha: str) -> RemoteSyncEvidence:
        if remote == "gitlab":
            return RemoteSyncEvidence(
                remote=remote,
                applicable=True,
                attempted=True,
                pushed=True,
                verified=False,
                branch=branch,
                sha=sha,
                reason="gitlab mismatch",
            )
        return original(remote, branch, sha)

    monkeypatch.setattr(controller.remote_verifier, "push_and_verify", mixed)
    cycle = controller.run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": "barrot_agent/target.py"},
    )

    gitlab_sync = next(item for item in cycle.sync if item.remote == "gitlab")
    assert cycle.status == "failed"
    assert gitlab_sync.applicable is True
    assert gitlab_sync.verified is False


def test_original_defect_remaining_blocks_complete(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(
        repair_payload(
            path,
            validation_commands=[success_command()],
            resolution_commands=[failure_command()],
        )
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "failed"
    assert cycle.resolution_verified is False


def test_original_defect_resolved_passes_post_repair_verification(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.post_repair_validation_passed is True
    assert cycle.resolution_verified is True


def test_duplicate_repair_attempt_is_idempotent(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    first = run_cycle(workspace, FakeBrain(repair_payload(path)))
    second = run_cycle(workspace, FakeBrain(repair_payload(path)))

    assert first.status == "complete"
    assert second.status == "no_repair_required"
    assert git(workspace, "status", "--porcelain").stdout.strip() == ""


def test_unsupported_command_is_rejected(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    payload = repair_payload(
        path,
        reproduction_commands=[{"program": "bash", "args": ["-lc", "exit 1"], "timeout": 5}],
    )
    brain = FakeBrain(payload)

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "failed"
    assert cycle.failure is not None
    assert cycle.failure.code == "REPRODUCE_ERROR"


def test_command_timeout_is_controlled_failure(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    brain = FakeBrain(
        repair_payload(
            path,
            reproduction_commands=[defect_command(path)],
            validation_commands=[timeout_command()],
            resolution_commands=[success_command()],
        )
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "rolled_back"
    evidence = cycle.validation["local_validation"]["commands"][0]
    assert evidence["timed_out"] is True


def test_cannot_transition_directly_to_complete_without_evidence() -> None:
    cycle = RepairCycleEvidence(cycle_id="cycle-1")

    with pytest.raises(RepairError):
        cycle.transition(RepairState.COMPLETE)


def test_full_successful_lifecycle_reaches_complete(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "complete"
    assert cycle.current_state == RepairState.COMPLETE.value
    assert cycle.remote_sync_verified is True


def test_full_failure_lifecycle_ends_in_terminal_failure_state(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(
        repair_payload(
            path,
            validation_commands=[success_command()],
            resolution_commands=[failure_command()],
        )
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "failed"
    assert cycle.current_state == RepairState.FAILED.value


def test_no_repair_required_mode_is_supported(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = FakeBrain(json.dumps({"mode": "no_repair_required", "report": "Repository already healthy."}))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "no_repair_required"
    assert cycle.report == "Repository already healthy."


def test_report_mode_is_supported(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = FakeBrain(json.dumps({"mode": "report", "report": "Audit only."}))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "no_repair_required"
    assert cycle.report_only is True


def test_commit_records_expected_changed_paths(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.commit.changed_paths == [path]


def test_issue_and_changeset_fingerprints_are_recorded(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.issue_fingerprint
    assert cycle.plan_fingerprint
    assert cycle.changeset_fingerprint


def test_cycle_records_are_persisted(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    cycle = run_cycle(workspace, FakeBrain(repair_payload(path)))

    latest = workspace / ".git" / "barrot_repair" / "repair_cycles" / "latest.json"
    record = workspace / ".git" / "barrot_repair" / "repair_cycles" / f"{cycle.cycle_id}.json"

    assert latest.exists()
    assert record.exists()
    assert json.loads(latest.read_text(encoding="utf-8"))["latest_cycle_id"] == cycle.cycle_id


def test_empty_project_identity_uses_last_valid_project_identity(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    first = make_controller(workspace, FakeBrain(json.dumps({"mode": "no_repair_required", "report": "healthy"})))
    cycle = first.run(
        task_title="Repair target",
        task_body="Check target",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": path},
    )
    assert cycle.status == "no_repair_required"

    second = make_controller(workspace, FakeBrain(json.dumps({"mode": "no_repair_required", "report": "healthy"})))
    resumed = second.run(
        task_title="Repair target",
        task_body="Check target",
        issue_number="123",
        repo="",
        branch="",
        audit_context={"inventory": path},
    )

    assert resumed.status == "no_repair_required"
    assert resumed.project_identity["repository"] == "Barrot-Agent/B-Agent"
    assert resumed.project_identity["branch"] == "repair/test"
    assert resumed.resumed_from_cycle_id == cycle.cycle_id


def test_repeated_identical_failed_plan_hits_retry_exhaustion(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    payload = repair_payload(
        path,
        validation_commands=[failure_command()],
        resolution_commands=[success_command()],
    )

    first = RepositoryRepairController(
        brain=FakeBrain(payload),
        workspace=workspace,
        planner_attempts=3,
        max_unchanged_attempts=1,
    ).run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": "barrot_agent/target.py"},
    )
    second = RepositoryRepairController(
        brain=FakeBrain(payload),
        workspace=workspace,
        planner_attempts=3,
        max_unchanged_attempts=1,
    ).run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": "barrot_agent/target.py"},
    )

    assert first.status == "rolled_back"
    assert second.status == "blocked"
    assert second.current_state == RepairState.BLOCKED.value
    assert second.failure is not None
    assert second.failure.code == "LLM_RETRY_EXHAUSTED"
