from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from barrot_agent.orchestration.repository_repair import (
    AuditEngine,
    FailureEvidence,
    ModelFailure,
    ModelFailureCode,
    RepairPlanner,
    GitGateway,
    PatchExecutor,
    ProjectIdentity,
    RemoteSyncEvidence,
    RepairCycleEvidence,
    RepairError,
    RepairState,
    RepositoryRepairController,
    SyncController,
    WorkQueueController,
    safe_checkout_branch,
)

from barrot_agent.orchestration.repository_repair_loop import (
    assert_clean_feature_worktree,
    run_repository_repair_loop,
)
from barrot_agent.orchestration.shared_runtime import Capability, DefensiveWatchdog


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


class ToolCapableFakeBrain:
    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = 0
        self.use_tools_calls = []
        self.max_output_tokens_calls = []

    def think(
        self,
        message: str,
        history=None,
        system=None,
        use_tools: bool = False,
        max_output_tokens=None,
    ) -> str:
        del message, history, system
        self.use_tools_calls.append(use_tools)
        self.max_output_tokens_calls.append(max_output_tokens)
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


def authorized_watchdog(workspace: Path) -> DefensiveWatchdog:
    return DefensiveWatchdog(
        workspace,
        repository="Barrot-Agent/B-Agent",
        allowed_capabilities={
            Capability.READ,
            Capability.WRITE,
            Capability.EXECUTE,
            Capability.NETWORK,
            Capability.EXTERNAL_ACTION,
        },
    )


def make_controller(workspace: Path, brain: FakeBrain) -> RepositoryRepairController:
    return RepositoryRepairController(
        brain=brain,
        workspace=workspace,
        planner_attempts=3,
        watchdog=authorized_watchdog(workspace),
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
    assert git(workspace, "add", path).returncode == 0
    assert git(workspace, "commit", "-m", "commit healthy fixture").returncode == 0
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


def test_llm_rate_limit_blocks_without_retry_and_runs_local_read_only_fallback(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    before_status = git(workspace, "status", "--porcelain=v1").stdout
    brain = FakeBrain(RuntimeError("429 rate limited"), RuntimeError("429 rate limited"))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "blocked"
    assert cycle.failure is not None
    assert cycle.failure.code == "LLM_RATE_LIMITED"
    assert brain.calls == 1
    report = json.loads(cycle.report)
    assert report["mode"] == "read_only_provider_failure_snapshot"
    assert report["provider_failure_code"] == "LLM_RATE_LIMITED"
    assert report["same_provider_retry_performed"] is False
    assert report["patch_applied"] is False
    assert report["commit_created"] is False
    assert report["remote_write_attempted"] is False
    assert report["git_snapshot"]["head"]["returncode"] == 0
    assert report["git_snapshot"]["status"]["stdout"] == before_status
    assert git(workspace, "status", "--porcelain=v1").stdout == before_status
    assert cycle.commit.created is False


def test_tpm_413_is_classified_before_generic_http_413():
    tpm = RepairPlanner._normalize_exception(
        RuntimeError(
            "Groq HTTP 413: Request too large on tokens per minute; "
            "Limit 8000, Requested 8099."
        )
    )
    context = RepairPlanner._normalize_exception(
        RuntimeError("Groq HTTP 413: Request too large; maximum context window exceeded.")
    )
    assert tpm.code == ModelFailureCode.RATE_LIMITED_TPM
    assert context.code == ModelFailureCode.CONTEXT_BUDGET


def test_read_only_audit_tpm_limit_skips_planner_and_uses_local_fallback(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    before_status = git(workspace, "status", "--porcelain=v1").stdout
    brain = ToolCapableFakeBrain(
        RuntimeError(
            "Groq HTTP 413: Request too large on tokens per minute; "
            "Limit 8000, Requested 8099."
        ),
        repair_payload("barrot_agent/target.py"),
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "blocked"
    assert cycle.failure is not None
    assert cycle.failure.code == "LLM_RATE_LIMITED_TPM"
    assert brain.calls == 1
    assert brain.use_tools_calls == [True]
    report = json.loads(cycle.report)
    assert report["failed_operation"] == "read_only_repository_audit"
    assert report["same_provider_retry_performed"] is False
    assert report["patch_applied"] is False
    assert report["git_snapshot"]["status"]["stdout"] == before_status
    assert git(workspace, "status", "--porcelain=v1").stdout == before_status
    assert cycle.commit.created is False


def test_planner_tpm_limit_blocks_and_captures_local_snapshot_after_audit(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = ToolCapableFakeBrain(
        "Read-only audit completed with repository facts.",
        RuntimeError(
            "Groq HTTP 413: Request too large on tokens per minute; "
            "Limit 8000, Requested 8099."
        ),
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "blocked"
    assert cycle.failure is not None
    assert cycle.failure.code == "LLM_RATE_LIMITED_TPM"
    assert brain.calls == 2
    assert brain.use_tools_calls == [True, False]
    report = json.loads(cycle.report)
    assert report["failed_operation"] == "repair_planner.generate"
    assert report["same_provider_retry_performed"] is False
    assert report["patch_applied"] is False
    assert cycle.commit.created is False


def test_planner_context_413_blocks_without_retry_and_captures_local_snapshot(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = ToolCapableFakeBrain(
        "Read-only audit completed with repository facts.",
        RuntimeError("Groq HTTP 413: Request too large; maximum context window exceeded."),
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "blocked"
    assert cycle.failure is not None
    assert cycle.failure.code == "LLM_CONTEXT_BUDGET_EXCEEDED"
    assert brain.calls == 2
    assert brain.use_tools_calls == [True, False]
    report = json.loads(cycle.report)
    assert report["failed_operation"] == "repair_planner.generate"
    assert report["patch_applied"] is False
    assert report["same_provider_retry_performed"] is False
    assert cycle.commit.created is False


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
    assert git(workspace, "add", path).returncode == 0
    assert git(workspace, "commit", "-m", "commit ambiguous fixture").returncode == 0
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


def test_git_gateway_requires_explicit_authorization_for_nonprotected_push(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path, origin=True)

    result = GitGateway(workspace).push("origin", "repair/test")

    assert result.success is False
    assert "explicitly configured authorization gate" in result.error
    assert git(workspace, "ls-remote", "--heads", "origin", "repair/test").stdout.strip() == ""


def test_repository_repair_controller_blocks_before_patch_without_external_action_grant(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    controller = RepositoryRepairController(
        brain=FakeBrain(repair_payload(path)),
        workspace=workspace,
    )

    cycle = controller.run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": "barrot_agent/target.py"},
    )

    assert cycle.status == "blocked"
    assert cycle.failure is not None
    assert cycle.failure.code == "EXTERNAL_SYNC_NOT_AUTHORIZED"
    assert cycle.failure.failed_operation == "authorize_remote_sync"
    assert cycle.commit.created is False
    assert cycle.changes_applied is False
    assert (workspace / path).read_text(encoding="utf-8") == 'FLAG = "BROKEN"\n'
    assert len(git(workspace, "log", "--oneline").stdout.splitlines()) == 1
    assert git(workspace, "ls-remote", "--heads", "origin", "repair/test").stdout.strip() == ""


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
        watchdog=authorized_watchdog(workspace),
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
        watchdog=authorized_watchdog(workspace),
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


def test_valid_project_identity_is_preserved_across_sync_attempts(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    observed = iter(
        [
            {
                "id": 77830382,
                "path_with_namespace": "Barrot-Agent/B-Agent",
                "namespace_id": 122592030,
                "namespace_path": "Barrot-Agent",
                "namespace_kind": "user",
                "transfer_completed": False,
            },
            {
                "id": 77830382,
                "path_with_namespace": "Barrot-Agent/B-Agent",
                "namespace_id": 122592030,
                "namespace_path": "Barrot-Agent",
                "namespace_kind": "user",
                "transfer_completed": True,
            },
        ]
    )
    sleeps: list[float] = []
    sync = SyncController(max_attempts=3, backoff_seconds=2, sleep_fn=sleeps.append)

    result = sync.run(
        work_id="night-watch-1",
        operation="transfer_project",
        project_identity={
            "id": 77830382,
            "path_with_namespace": "Barrot-Agent/B-Agent",
            "namespace_id": 122592030,
            "namespace_path": "Barrot-Agent",
            "namespace_kind": "user",
        },
        submit_operation=lambda identity: {"submitted": identity["path_with_namespace"]},
        observe_state=lambda: next(observed),
        is_complete=lambda state, _: bool(state.get("transfer_completed")),
    )

    assert result.status == RepairState.COMPLETE.value
    assert result.last_valid_project["path_with_namespace"] == "Barrot-Agent/B-Agent"
    assert result.last_valid_project["namespace_path"] == "Barrot-Agent"
    assert sleeps == [2]


def test_empty_namespace_cannot_overwrite_last_valid_project_identity(tmp_path: Path) -> None:
    init_repo(tmp_path)
    sync = SyncController(max_attempts=3, backoff_seconds=1, sleep_fn=lambda _: None)

    result = sync.run(
        work_id="night-watch-2",
        operation="transfer_project",
        project_identity={
            "id": 77830382,
            "path_with_namespace": "Barrot-Agent/B-Agent",
            "namespace_id": 122592030,
            "namespace_path": "Barrot-Agent",
            "namespace_kind": "user",
        },
        submit_operation=lambda identity: {"submitted": identity["path_with_namespace"]},
        observe_state=lambda: {"path": "Barrot-Agent/B-Agent", "namespace": ""},
        is_complete=lambda state, _: bool(state.get("transfer_completed")),
    )

    assert result.status == RepairState.BLOCKED.value
    assert result.last_valid_project["namespace_path"] == "Barrot-Agent"
    assert result.current_invalid_response["namespace"] == ""


def test_empty_path_cannot_overwrite_last_valid_project_identity(tmp_path: Path) -> None:
    init_repo(tmp_path)
    sync = SyncController(max_attempts=3, backoff_seconds=1, sleep_fn=lambda _: None)

    result = sync.run(
        work_id="night-watch-3",
        operation="transfer_project",
        project_identity={
            "id": 77830382,
            "path_with_namespace": "Barrot-Agent/B-Agent",
            "namespace_id": 122592030,
            "namespace_path": "Barrot-Agent",
            "namespace_kind": "user",
        },
        submit_operation=lambda identity: {"submitted": identity["path_with_namespace"]},
        observe_state=lambda: {"path": "", "namespace": "Barrot-Agent"},
        is_complete=lambda state, _: bool(state.get("transfer_completed")),
    )

    assert result.status == RepairState.BLOCKED.value
    assert result.last_valid_project["path_with_namespace"] == "Barrot-Agent/B-Agent"
    assert result.current_invalid_response["path"] == ""


def test_unchanged_state_is_detected_and_resubmission_is_bounded(tmp_path: Path) -> None:
    init_repo(tmp_path)
    observations = [
        {
            "id": 77830382,
            "path_with_namespace": "Barrot-Agent/B-Agent",
            "namespace_id": 122592030,
            "namespace_path": "Barrot-Agent",
            "namespace_kind": "user",
            "transfer_completed": False,
        }
    ]
    submits: list[dict[str, object]] = []
    sleeps: list[float] = []
    sync = SyncController(max_attempts=3, backoff_seconds=5, sleep_fn=sleeps.append)

    result = sync.run(
        work_id="night-watch-4",
        operation="transfer_project",
        project_identity=observations[0],
        submit_operation=lambda identity: submits.append(identity) or {"submitted": True},
        observe_state=lambda: dict(observations[0]),
        is_complete=lambda state, _: bool(state.get("transfer_completed")),
    )

    assert result.status == RepairState.BLOCKED.value
    assert len(submits) == 1
    assert submits[0]["path_with_namespace"] == "Barrot-Agent/B-Agent"
    assert [item.progress_occurred for item in result.retry_history] == [False, False, False]
    assert sleeps == [5, 10]
    assert result.retry_history[-1].failure_classification == "LLM_RETRY_EXHAUSTED"


def test_durable_state_survives_interruption_and_resume_uses_last_valid_state(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)

    class InterruptingController:
        def __init__(self, repo_workspace: Path):
            self.workspace = repo_workspace

        def run(self, **kwargs):
            raise RuntimeError("simulated local interruption")

    queue = WorkQueueController(repair_controller=InterruptingController(workspace))
    identity = {
        "id": 77830382,
        "path_with_namespace": "Barrot-Agent/B-Agent",
        "namespace_id": 122592030,
        "namespace_path": "Barrot-Agent",
        "namespace_kind": "user",
    }
    with pytest.raises(RuntimeError, match="simulated local interruption"):
        queue.run(
            work_id="resume-case",
            project_identity=identity,
            task_title="Repair target",
            task_body="Check target",
            issue_number="123",
            repo="Barrot-Agent/B-Agent",
            branch="repair/test",
            audit_context={"inventory": path},
        )
    persisted = workspace / ".git" / "barrot_repair" / "work_queue" / "resume-case.json"
    payload = json.loads(persisted.read_text(encoding="utf-8"))
    queue_again = WorkQueueController(
        repair_controller=make_controller(workspace, FakeBrain(json.dumps({"mode": "no_repair_required", "report": "healthy"})))
    )
    second = queue_again.run(
        work_id="resume-case",
        project_identity=ProjectIdentity.from_seed("Barrot-Agent/B-Agent").to_dict(),
        task_title="Repair target",
        task_body="Check target",
        issue_number="123",
        repo="",
        branch="",
        audit_context={"inventory": path},
    )

    assert persisted.exists()
    assert payload["current_state"] == "REPAIRING"
    assert payload["attempt_count"] == 1
    assert payload["project_identity"]["path_with_namespace"] == "Barrot-Agent/B-Agent"
    assert second.project_identity["path_with_namespace"] == "Barrot-Agent/B-Agent"
    assert second.attempt_count == 2


def test_queue_cannot_advance_after_failed_repair(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    queue = WorkQueueController(
        repair_controller=make_controller(workspace, FakeBrain("{not-json")),
        sync_controller=SyncController(max_attempts=1, sleep_fn=lambda _: None),
    )

    work = queue.run(
        work_id="failed-repair-work",
        project_identity=ProjectIdentity.from_seed("Barrot-Agent/B-Agent").to_dict(),
        task_title="Repair target",
        task_body="Fix target",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": path},
    )

    assert work.status == "blocked"
    assert work.queue_advanced is False
    assert work.current_state == RepairState.BLOCKED.value


def test_successful_repair_can_advance_queue(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    queue = WorkQueueController(
        repair_controller=make_controller(workspace, FakeBrain(repair_payload(path))),
        sync_controller=SyncController(max_attempts=1, sleep_fn=lambda _: None),
    )

    work = queue.run(
        work_id="successful-repair-work",
        project_identity=ProjectIdentity.from_seed("Barrot-Agent/B-Agent").to_dict(),
        task_title="Repair target",
        task_body="Fix target",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": path},
    )

    assert work.status == "complete"
    assert work.queue_advanced is True


def test_controlled_end_to_end_workflow_persists_sync_evidence(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path, origin=True)
    observations = iter(
        [
            {
                "id": 77830382,
                "path_with_namespace": "Barrot-Agent/B-Agent",
                "namespace_id": 122592030,
                "namespace_path": "Barrot-Agent",
                "namespace_kind": "user",
                "transfer_completed": False,
                "operation_state": "queued",
            },
            {
                "id": 77830382,
                "path_with_namespace": "Barrot-Agent/B-Agent",
                "namespace_id": 122592030,
                "namespace_path": "Barrot-Agent",
                "namespace_kind": "user",
                "transfer_completed": True,
                "operation_state": "complete",
            },
        ]
    )
    queue = WorkQueueController(
        repair_controller=make_controller(workspace, FakeBrain(repair_payload(path))),
        sync_controller=SyncController(max_attempts=3, backoff_seconds=1, sleep_fn=lambda _: None),
    )

    work = queue.run(
        work_id="e2e-work",
        project_identity=ProjectIdentity.from_seed("Barrot-Agent/B-Agent").to_dict(),
        task_title="Repair target",
        task_body="Fix target",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": path},
        external_sync_plan={
            "submit_operation": lambda identity: {"submitted": identity["path_with_namespace"]},
            "observe_state": lambda: next(observations),
            "is_complete": lambda state, _: bool(state.get("transfer_completed")),
        },
    )

    assert work.status == "complete"
    assert work.queue_advanced is True
    assert work.sync_operation["status"] == RepairState.COMPLETE.value
    assert work.sync_operation["last_valid_project"]["path_with_namespace"] == "Barrot-Agent/B-Agent"


def test_safe_checkout_branch_creates_task_branch_without_moving_main(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    assert git(workspace, "switch", "main").returncode == 0
    main_sha = git(workspace, "rev-parse", "HEAD").stdout.strip()

    safe_checkout_branch(workspace, "barrot/task-123")

    assert git(workspace, "branch", "--show-current").stdout.strip() == "barrot/task-123"
    assert git(workspace, "rev-parse", "main").stdout.strip() == main_sha
    assert git(workspace, "status", "--porcelain").stdout.strip() == ""


def test_safe_checkout_branch_refuses_dirty_worktree_without_switching(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    assert git(workspace, "switch", "main").returncode == 0
    note = workspace / "user-notes.txt"
    note.write_text("preserve this user work\n", encoding="utf-8")

    with pytest.raises(RepairError, match="pre-existing changes"):
        safe_checkout_branch(workspace, "barrot/task-123")

    assert git(workspace, "branch", "--show-current").stdout.strip() == "main"
    assert note.read_text(encoding="utf-8") == "preserve this user work\n"
    assert "user-notes.txt" in git(workspace, "status", "--porcelain").stdout


def test_safe_checkout_branch_preserves_existing_local_task_branch_commit(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    assert git(workspace, "switch", "-c", "barrot/task-existing").returncode == 0
    note = workspace / "task-evidence.txt"
    note.write_text("existing task commit\n", encoding="utf-8")
    assert git(workspace, "add", "task-evidence.txt").returncode == 0
    assert git(workspace, "commit", "-m", "existing task commit").returncode == 0
    task_sha = git(workspace, "rev-parse", "HEAD").stdout.strip()
    assert git(workspace, "switch", "main").returncode == 0

    safe_checkout_branch(workspace, "barrot/task-existing")

    assert git(workspace, "branch", "--show-current").stdout.strip() == "barrot/task-existing"
    assert git(workspace, "rev-parse", "HEAD").stdout.strip() == task_sha
    assert note.read_text(encoding="utf-8") == "existing task commit\n"


def test_safe_checkout_branch_tracks_existing_remote_branch_without_force(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path, origin=True)
    assert git(workspace, "switch", "-c", "barrot/task-remote").returncode == 0
    note = workspace / "remote-task.txt"
    note.write_text("remote task history\n", encoding="utf-8")
    assert git(workspace, "add", "remote-task.txt").returncode == 0
    assert git(workspace, "commit", "-m", "remote task history").returncode == 0
    assert git(workspace, "push", "-u", "origin", "barrot/task-remote").returncode == 0
    remote_sha = git(workspace, "rev-parse", "HEAD").stdout.strip()
    assert git(workspace, "switch", "main").returncode == 0
    assert git(workspace, "branch", "-D", "barrot/task-remote").returncode == 0

    safe_checkout_branch(workspace, "barrot/task-remote")

    assert git(workspace, "branch", "--show-current").stdout.strip() == "barrot/task-remote"
    assert git(workspace, "rev-parse", "HEAD").stdout.strip() == remote_sha
    assert note.read_text(encoding="utf-8") == "remote task history\n"


@pytest.mark.parametrize("branch", ["main", "refs/heads/main", "refs/heads/production"])
def test_safe_checkout_branch_rejects_protected_target(tmp_path: Path, branch: str) -> None:
    workspace, _ = init_repo(tmp_path)
    with pytest.raises(RepairError, match="protected branch"):
        safe_checkout_branch(workspace, branch)
    assert git(workspace, "branch", "--show-current").stdout.strip() == "repair/test"


def test_patch_executor_refuses_dirty_worktree_before_writing(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    note = workspace / "user-notes.txt"
    note.write_text("preserve this user work\n", encoding="utf-8")
    target = workspace / path
    original = target.read_text(encoding="utf-8")
    changeset = json.loads(repair_payload(path))["changeset"]

    with pytest.raises(RepairError, match="pre-existing changes"):
        PatchExecutor(workspace).apply(changeset)

    assert target.read_text(encoding="utf-8") == original
    assert note.read_text(encoding="utf-8") == "preserve this user work\n"


def test_patch_executor_refuses_to_overwrite_preexisting_ignored_file(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    ignored_path = "barrot_agent/ignored_target.py"
    with (workspace / ".gitignore").open("a", encoding="utf-8") as handle:
        handle.write("barrot_agent/ignored_target.py\n")
    assert git(workspace, "add", ".gitignore").returncode == 0
    assert git(workspace, "commit", "-m", "ignore target").returncode == 0

    target = workspace / ignored_path
    target.write_text('FLAG = "USER DATA"\n', encoding="utf-8")
    changeset = json.loads(
        repair_payload(ignored_path, old='FLAG = "USER DATA"', new='FLAG = "OVERWRITTEN"')
    )["changeset"]

    assert git(workspace, "status", "--porcelain", "--untracked-files=all").stdout.strip() == ""
    with pytest.raises(RepairError, match="untracked or ignored file"):
        PatchExecutor(workspace).apply(changeset)

    assert target.read_text(encoding="utf-8") == 'FLAG = "USER DATA"\n'
    assert git(workspace, "status", "--porcelain", "--untracked-files=all").stdout.strip() == ""


def test_controller_blocks_dirty_worktree_before_model_or_patch(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    note = workspace / "user-notes.txt"
    note.write_text("preserve this user work\n", encoding="utf-8")
    target = workspace / path
    original = target.read_text(encoding="utf-8")
    brain = FakeBrain(repair_payload(path))

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "blocked"
    assert cycle.failure is not None
    assert cycle.failure.code == "WORKTREE_PREFLIGHT_FAILED"
    assert brain.calls == 0
    assert target.read_text(encoding="utf-8") == original
    assert note.read_text(encoding="utf-8") == "preserve this user work\n"


def test_controller_blocks_branch_mismatch_before_model_or_patch(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    brain = FakeBrain(repair_payload(path))
    controller = make_controller(workspace, brain)

    cycle = controller.run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="barrot/task-123",
        audit_context={"inventory": path},
    )

    assert cycle.status == "blocked"
    assert cycle.failure is not None
    assert cycle.failure.code == "BRANCH_MISMATCH"
    assert brain.calls == 0
    assert git(workspace, "branch", "--show-current").stdout.strip() == "repair/test"


@pytest.mark.parametrize("branch", ["main", "refs/heads/main", "refs/heads/production"])
def test_git_gateway_refuses_protected_branch_push(tmp_path: Path, branch: str) -> None:
    workspace, _ = init_repo(tmp_path)
    result = GitGateway(workspace).push("origin", branch)
    assert result.success is False
    assert "protected branch" in result.error


def test_git_gateway_refuses_to_commit_pre_staged_user_changes(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    target = workspace / path
    target.write_text('FLAG = "USER EDIT"\n', encoding="utf-8")
    assert git(workspace, "add", path).returncode == 0
    head_before = git(workspace, "rev-parse", "HEAD").stdout.strip()
    staged_before = git(workspace, "diff", "--cached", "--binary").stdout

    with pytest.raises(RepairError, match="already contains staged changes"):
        GitGateway(workspace).commit("must not include user changes", [path])

    assert git(workspace, "rev-parse", "HEAD").stdout.strip() == head_before
    assert git(workspace, "diff", "--cached", "--binary").stdout == staged_before
    assert target.read_text(encoding="utf-8") == 'FLAG = "USER EDIT"\n'


def test_patch_executor_rollback_preserves_concurrent_user_edit(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    target = workspace / path
    original = target.read_text(encoding="utf-8")
    executor = PatchExecutor(workspace)
    snapshots = executor.snapshot([path])
    changeset = json.loads(repair_payload(path))["changeset"]

    _, changed = executor.apply(changeset)
    assert changed == [path]
    assert target.read_text(encoding="utf-8") == 'FLAG = "FIXED"\n'

    target.write_text("concurrent user edit\n", encoding="utf-8")
    assert executor.rollback(snapshots) is False
    assert target.read_text(encoding="utf-8") == "concurrent user edit\n"
    assert target.read_text(encoding="utf-8") != original


def test_patch_executor_refuses_commit_after_concurrent_target_edit(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    target = workspace / path
    executor = PatchExecutor(workspace)
    changeset = json.loads(repair_payload(path))["changeset"]

    executor.apply(changeset)
    target.write_text("concurrent user edit\n", encoding="utf-8")

    with pytest.raises(RepairError, match="changed after patch application"):
        executor.verify_applied_content()
    assert target.read_text(encoding="utf-8") == "concurrent user edit\n"


def test_patch_executor_refuses_tracked_symlink_target_without_modifying_referent(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    target = workspace / path
    original = target.read_text(encoding="utf-8")
    link_relative = "barrot_agent/link.py"
    link = workspace / link_relative
    link.symlink_to("target.py")
    assert git(workspace, "add", link_relative).returncode == 0
    assert git(workspace, "commit", "-m", "track symlink fixture").returncode == 0

    changeset = json.loads(repair_payload(link_relative))["changeset"]
    with pytest.raises(RepairError, match="symbolic link"):
        PatchExecutor(workspace).apply(changeset)

    assert link.is_symlink()
    assert target.read_text(encoding="utf-8") == original


def test_patch_executor_rechecks_preimage_after_patch_planning(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    target = workspace / path

    class ConcurrentEditor:
        def inspect_patch(self, *, path: str, new_content: str, reason: str):
            target.write_text("concurrent user edit\n", encoding="utf-8")

            class Allowed:
                allowed = True
                reason = ""

            return Allowed()

    executor = PatchExecutor(workspace, watchdog=ConcurrentEditor())
    changeset = json.loads(repair_payload(path))["changeset"]

    with pytest.raises(RepairError, match="changed after planning"):
        executor.apply(changeset)

    assert target.read_text(encoding="utf-8") == "concurrent user edit\n"
    assert executor._last_applied_content == {}


def test_patch_executor_refuses_to_create_new_git_ignored_path(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    ignored_relative = "barrot_agent/ignored_new.py"
    with (workspace / ".gitignore").open("a", encoding="utf-8") as handle:
        handle.write(ignored_relative + "\n")
    assert git(workspace, "add", ".gitignore").returncode == 0
    assert git(workspace, "commit", "-m", "ignore new target fixture").returncode == 0

    target = workspace / ignored_relative
    changeset = json.loads(
        repair_payload(ignored_relative, old="", new='FLAG = "FIXED"\n')
    )["changeset"]

    with pytest.raises(RepairError, match="new path ignored by Git"):
        PatchExecutor(workspace).apply(changeset)

    assert not target.exists()
    assert git(workspace, "status", "--porcelain", "--untracked-files=all").stdout.strip() == ""


def test_audit_engine_bounds_optional_context_and_preserves_task_and_safety_notes() -> None:
    engine = AuditEngine()
    prompt = engine.build_prompt(
        task_title="Preserve the existing repair objective",
        task_body="Do not weaken authorization, safety, or user-work preservation.",
        audit_context={
            "note": "PRESERVE AUTHORIZATION AND USER WORK.",
            "file_context": "FILE_CONTEXT_BEGIN\n" + ("F" * 9_000),
            "barrett_autonomous_audit": "AUDIT_REPORT_BEGIN\n" + ("A" * 5_000),
            "github_context": "GITHUB_CONTEXT_BEGIN\n" + ("G" * 5_000),
            "inventory": "INVENTORY_BEGIN\n" + ("I" * 5_000),
            "directory_context": "DIRECTORY_BEGIN\n" + ("D" * 5_000),
        },
        previous_failure="Previous failure details must remain visible.",
    )

    assert len(prompt) <= engine.MAX_PROMPT_CHARS
    assert "Preserve the existing repair objective" in prompt
    assert "Do not weaken authorization, safety, or user-work preservation." in prompt
    assert "PRESERVE AUTHORIZATION AND USER WORK." in prompt
    assert "Previous failure details must remain visible." in prompt
    assert "READ-ONLY REPOSITORY AUDIT" in prompt
    assert "[TRUNCATED" in prompt


def test_audit_engine_blocks_when_mandatory_task_text_exceeds_budget() -> None:
    with pytest.raises(ModelFailure) as error:
        AuditEngine().build_prompt(
            task_title="Task",
            task_body="x" * 15_000,
            audit_context={},
        )

    assert error.value.code == ModelFailureCode.CONTEXT_BUDGET


def test_repair_planner_uses_reduced_completion_budget_when_supported() -> None:
    class BudgetAwareBrain:
        max_output_tokens = None

        def think(self, message, system=None, use_tools=None, max_output_tokens=None):
            del message, system, use_tools
            self.max_output_tokens = max_output_tokens
            return json.dumps({"mode": "no_repair_required"})

    brain = BudgetAwareBrain()
    directive = RepairPlanner(brain).generate("A small bounded task.")

    assert directive.mode == "no_repair_required"
    assert brain.max_output_tokens == 768


def test_context_budget_failure_blocks_without_repeating_the_same_request(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    brain = FakeBrain(
        RuntimeError(
            "LLM_CONTEXT_BUDGET_EXCEEDED: Groq HTTP 413: Request too large; "
            "maximum context window exceeded."
        )
    )

    cycle = run_cycle(workspace, brain)

    assert cycle.status == "blocked"
    assert cycle.current_state == RepairState.BLOCKED.value
    assert cycle.failure is not None
    assert cycle.failure.code == ModelFailureCode.CONTEXT_BUDGET.value
    assert brain.calls == 1


def test_autonomous_audit_receives_real_task_and_uses_bounded_output(tmp_path: Path) -> None:
    class AuditBrain:
        message = ""
        use_tools = None
        max_output_tokens = None

        def think(self, message, system=None, use_tools=None, max_output_tokens=None):
            self.message = message
            self.use_tools = use_tools
            self.max_output_tokens = max_output_tokens
            return "A" * 4_000

    brain = AuditBrain()
    controller = RepositoryRepairController(brain=brain, workspace=tmp_path)
    report = controller._barrett_autonomous_audit(
        task_title="Exact task title",
        task_body="Exact task body",
        repo="Barrot-Agent/B-Agent",
        branch="barrot/task-example",
    )

    assert "Task title: Exact task title" in brain.message
    assert "Exact task body" in brain.message
    assert brain.use_tools is True
    assert brain.max_output_tokens == 384
    assert len(report) <= 2_500


def test_clean_nondefault_worktree_passes_local_repair_guard(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    assert assert_clean_feature_worktree(workspace, default_branch="main") == workspace.resolve()


def test_local_repair_guard_rejects_dirty_tracked_changes(tmp_path: Path) -> None:
    workspace, path = init_repo(tmp_path)
    (workspace / path).write_text('FLAG = "USER CHANGE"\\n', encoding="utf-8")
    with pytest.raises(ValueError, match="tracked or untracked changes"):
        assert_clean_feature_worktree(workspace, default_branch="main")


def test_local_repair_guard_rejects_untracked_files(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    (workspace / "user-notes.txt").write_text("preserve me\\n", encoding="utf-8")
    with pytest.raises(ValueError, match="tracked or untracked changes"):
        assert_clean_feature_worktree(workspace, default_branch="main")


def test_local_repair_guard_rejects_default_branch(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    assert git(workspace, "checkout", "main").returncode == 0
    with pytest.raises(ValueError, match="non-default feature branch"):
        assert_clean_feature_worktree(workspace, default_branch="main")


def test_local_repair_guard_rejects_non_git_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "not-a-repository"
    workspace.mkdir()
    with pytest.raises(ValueError, match="unable to verify Git worktree"):
        assert_clean_feature_worktree(workspace, default_branch="main")


def test_simple_repair_loop_cannot_modify_git_metadata(tmp_path: Path) -> None:
    workspace, _ = init_repo(tmp_path)
    broken = workspace / "broken.py"
    broken.write_text("def broken(:\\n", encoding="utf-8")
    assert git(workspace, "add", "broken.py").returncode == 0
    assert git(workspace, "commit", "-m", "add reproducible syntax defect").returncode == 0
    git_config = workspace / ".git" / "config"
    original_config = git_config.read_text(encoding="utf-8")

    class FakeLLM:
        def chat(self, messages):
            del messages
            return json.dumps({
                "diagnosis": "attempt to change Git metadata",
                "changes": [{
                    "path": ".git/config",
                    "old": original_config,
                    "new": original_config + "\\n[unsafe]\\n",
                }],
            })

    result = run_repository_repair_loop(workspace=workspace, llm=FakeLLM(), max_attempts=1)

    assert result.success is False
    assert "Protected repair path rejected" in result.message
    assert git_config.read_text(encoding="utf-8") == original_config
