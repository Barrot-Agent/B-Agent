"""Deterministic repository repair controller for Barrot."""

from __future__ import annotations

import ast
import json
import os
import shlex
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class RepairState(str, Enum):
    IDLE = "IDLE"
    AUDITING = "AUDITING"
    ANALYZING = "ANALYZING"
    REPAIR_PLANNING = "REPAIR_PLANNING"
    PATCHING = "PATCHING"
    LOCAL_VALIDATION = "LOCAL_VALIDATION"
    COMMITTING = "COMMITTING"
    REMOTE_VERIFICATION = "REMOTE_VERIFICATION"
    POST_REPAIR_VALIDATION = "POST_REPAIR_VALIDATION"
    SYNCING = "SYNCING"
    COMPLETE = "COMPLETE"
    PATCH_FAILED = "PATCH_FAILED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class CommandEvidence:
    command: str
    success: bool
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class ValidationEvidence:
    commands: list[CommandEvidence] = field(default_factory=list)
    compile_check: CommandEvidence | None = None
    workspace_check_passed: bool | None = None
    workspace_check_report: str = ""
    issue_reproduced: bool = False
    passed: bool = False


@dataclass
class CommitEvidence:
    created: bool = False
    sha: str = ""
    message: str = ""
    remote_verified: bool = False


@dataclass
class RemoteSyncEvidence:
    remote: str
    applicable: bool
    attempted: bool = False
    pushed: bool = False
    verified: bool = False
    branch: str = ""
    sha: str = ""
    reason: str = ""


@dataclass
class FailureEvidence:
    state: str
    message: str
    rollback_attempted: bool = False
    rollback_succeeded: bool = False


@dataclass
class RepairCycleEvidence:
    cycle_id: str
    status: str = "failed"
    current_state: str = RepairState.IDLE.value
    state_history: list[str] = field(default_factory=lambda: [RepairState.IDLE.value])
    audit_completed: bool = False
    issue_identified: bool = False
    repair_plan_created: bool = False
    changeset_created: bool = False
    changes_applied: bool = False
    local_validation_passed: bool = False
    post_repair_validation_passed: bool = False
    resolution_verified: bool = False
    report_only: bool = False
    report: str = ""
    issue: dict[str, Any] = field(default_factory=dict)
    repair_plan: dict[str, Any] = field(default_factory=dict)
    changes: list[dict[str, Any]] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    commit: CommitEvidence = field(default_factory=CommitEvidence)
    sync: list[RemoteSyncEvidence] = field(default_factory=list)
    failure: FailureEvidence | None = None

    def transition(self, state: RepairState) -> None:
        self.current_state = state.value
        self.state_history.append(state.value)

    def can_complete(self) -> bool:
        applicable = [item for item in self.sync if item.applicable]
        sync_ok = all(item.verified for item in applicable)
        return all(
            [
                self.audit_completed,
                self.issue_identified,
                self.repair_plan_created,
                self.changeset_created,
                self.changes_applied,
                self.local_validation_passed,
                self.commit.created,
                self.commit.remote_verified,
                self.post_repair_validation_passed,
                self.resolution_verified,
                sync_ok,
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RepairDirective:
    mode: str
    issue: dict[str, Any]
    repair_plan: dict[str, Any]
    changeset: dict[str, Any]
    report: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


class RepairError(RuntimeError):
    """Raised when the repair controller cannot advance safely."""


class AuditEngine:
    """Wrap the repository-grounded audit context for the repair controller."""

    def build_prompt(
        self,
        *,
        task_title: str,
        task_body: str,
        audit_context: dict[str, str],
        previous_failure: str = "",
    ) -> str:
        prompt = (
            f"TASK:\n{task_title}\n{task_body}\n\n"
            f"CURRENT REPO FILES:\n{audit_context.get('inventory', '')}"
            f"{audit_context.get('file_context', '')}"
            f"{audit_context.get('directory_context', '')}"
            f"{audit_context.get('github_context', '')}"
            f"{audit_context.get('note', '')}"
        )
        if previous_failure:
            prompt += f"\n\nPREVIOUS FAILURE:\n{previous_failure}\n"
        prompt += (
            "\n\nReturn JSON only using the deterministic repair schema."
        )
        return prompt


class RepairPlanner:
    """Ask the configured Barrot brain for either an audit report or a repair plan."""

    SYSTEM = """You are Barrot acting as a deterministic repository repair planner.

Return JSON only. No prose. No markdown fences.

Schema:
{
  "mode": "report" | "repair",
  "report": "required when mode=report",
  "issue": {
    "summary": "one concrete repository issue",
    "evidence": ["repository-grounded facts only"],
    "validation_commands": ["repo-local command proving the issue"],
    "files": ["relative/path.py"]
  },
  "repair_plan": {
    "summary": "minimal repair plan",
    "reason": "why this repair resolves the issue",
    "resolution_checks": ["specific proof after repair"]
  },
  "changeset": {
    "commands": ["mkdir -p docs"],
    "transmutations": [
      {
        "path": "relative/path.py",
        "content": "full file content",
        "justification": "optional override justification"
      }
    ],
    "expected_files": ["relative/path.py"],
    "commit_message": "short commit message"
  }
}

Rules:
- Use mode=report when the task is audit-only or cannot be repaired deterministically.
- For mode=repair, identify exactly one concrete issue.
- validation_commands must be repository-local and must fail before repair and pass after repair.
- List every file expected to change in changeset.expected_files.
- Use transmutations for file content changes.
- Do not include git add, git commit, git push, git checkout, git reset, sed -i, or rm -rf.
- Keep changes minimal and repository-grounded.
- Never claim the repair succeeded.
"""

    def __init__(self, brain: Any):
        self.brain = brain

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            raise RepairError("Planner returned no JSON object.")
        return json.loads(text[start : end + 1])

    def generate(self, prompt: str) -> RepairDirective:
        raw = self.brain.think(prompt, system=self.SYSTEM)
        payload = self._extract_json(raw)

        if payload.get("report") and not payload.get("mode"):
            return RepairDirective(
                mode="report",
                issue={},
                repair_plan={},
                changeset={},
                report=str(payload.get("report", "")).strip(),
                raw=payload,
            )

        mode = str(payload.get("mode", "")).strip().lower()
        if mode not in {"report", "repair"}:
            raise RepairError("Planner mode must be 'report' or 'repair'.")

        return RepairDirective(
            mode=mode,
            issue=payload.get("issue") or {},
            repair_plan=payload.get("repair_plan") or {},
            changeset=payload.get("changeset") or {},
            report=str(payload.get("report", "")).strip(),
            raw=payload,
        )


class PatchExecutor:
    """Apply guarded repository mutations and verify affected paths."""

    ALLOWED_COMMANDS = {"git", "mkdir", "mv", "cp", "touch"}
    PROTECTED_WRITE = (
        "core/",
        "hf_space/",
        "web/",
        "scripts/emit_signal.py",
        ".github/workflows/",
    )
    BLOCKED_SUBSTRINGS = (
        "git push",
        "git add",
        "git commit",
        "git checkout",
        "git reset",
        "git rebase",
        "rm -rf",
        ".git/",
        "sed -i",
    )

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

    def _run(self, command: str) -> CommandEvidence:
        result = subprocess.run(
            command,
            shell=True,
            cwd=self.workspace,
            capture_output=True,
            text=True,
        )
        return CommandEvidence(
            command=command,
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout[-4000:],
            stderr=result.stderr[-4000:],
        )

    def _resolve_file(self, relative_path: str) -> Path:
        target = (self.workspace / relative_path).resolve()
        if self.workspace not in target.parents and target != self.workspace:
            raise RepairError(f"Path escapes workspace: {relative_path}")
        return target

    def _validate_command(self, command: str) -> None:
        stripped = command.strip()
        if not stripped:
            raise RepairError("Empty command is not allowed.")
        lowered = stripped.lower()
        if any(token in lowered for token in self.BLOCKED_SUBSTRINGS):
            raise RepairError(f"Blocked command: {command}")
        try:
            parts = shlex.split(stripped)
        except ValueError as exc:
            raise RepairError(f"Invalid command syntax: {exc}") from exc
        if not parts:
            raise RepairError("Command produced no tokens.")
        if parts[0] not in self.ALLOWED_COMMANDS:
            raise RepairError(f"Disallowed command verb: {parts[0]}")
        if parts[0] == "git":
            if len(parts) < 2 or parts[1] not in {"mv", "rm"}:
                raise RepairError(f"Only git mv and git rm are allowed: {command}")

    def _verify_content(self, path: str, content: str) -> None:
        ext = Path(path).suffix.lower()
        if ext == ".py":
            ast.parse(content)
            return
        if ext == ".json":
            json.loads(content)
            return
        if ext == ".jsonl":
            for line in content.splitlines():
                line = line.strip()
                if line:
                    json.loads(line)
            return
        if ext in {".md", ".txt", ".yml", ".yaml"}:
            return
        raise RepairError(f"Rewrite not allowed for extension: {ext}")

    def _preservation_check(self, old_content: str, new_content: str, min_retain: float = 0.5) -> None:
        old_tokens = {word for word in old_content.split() if len(word) > 3}
        if not old_tokens:
            return
        new_tokens = {word for word in new_content.split() if len(word) > 3}
        retained = len(old_tokens & new_tokens) / len(old_tokens)
        size_ratio = len(new_content) / max(len(old_content), 1)
        if retained < min_retain:
            raise RepairError(f"Rewrite rejected: only {retained:.0%} content retained.")
        if size_ratio < 0.3:
            raise RepairError(f"Rewrite rejected: file shrank to {size_ratio:.0%}.")

    def _command_paths(self, command: str) -> list[str]:
        parts = shlex.split(command)
        paths: list[str] = []
        if not parts:
            return paths
        verb = parts[0]
        if verb == "mkdir":
            return paths
        if verb == "touch":
            return [part for part in parts[1:] if not part.startswith("-")]
        if verb in {"mv", "cp"} and len(parts) >= 3:
            return [parts[-2], parts[-1]]
        if verb == "git" and len(parts) >= 3:
            op = parts[1]
            if op == "mv" and len(parts) >= 4:
                return [parts[2], parts[3]]
            if op == "rm":
                return [part for part in parts[2:] if not part.startswith("-")]
        return paths

    def collect_snapshot_paths(self, changeset: dict[str, Any]) -> list[str]:
        paths: list[str] = []
        for path in changeset.get("expected_files", []) or []:
            if isinstance(path, str) and path and path not in paths:
                paths.append(path)
        for item in changeset.get("transmutations", []) or []:
            path = item.get("path")
            if isinstance(path, str) and path and path not in paths:
                paths.append(path)
        for command in changeset.get("commands", []) or []:
            if isinstance(command, str):
                for path in self._command_paths(command):
                    if path and path not in paths:
                        paths.append(path)
        return paths

    def snapshot(self, paths: list[str]) -> dict[str, str | None]:
        snapshots: dict[str, str | None] = {}
        for path in paths:
            target = self._resolve_file(path)
            snapshots[path] = target.read_text(encoding="utf-8") if target.exists() else None
        return snapshots

    def rollback(self, snapshots: dict[str, str | None]) -> bool:
        try:
            for path, original in snapshots.items():
                target = self._resolve_file(path)
                if original is None:
                    if target.exists():
                        target.unlink()
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(original, encoding="utf-8")
            return True
        except Exception:
            return False

    def apply(self, changeset: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
        commands = changeset.get("commands", []) or []
        transmutations = changeset.get("transmutations", []) or []
        expected_files = changeset.get("expected_files", []) or []
        if not isinstance(commands, list) or not isinstance(transmutations, list):
            raise RepairError("Changeset commands/transmutations must be lists.")
        if not isinstance(expected_files, list) or not expected_files:
            raise RepairError("Changeset must declare non-empty expected_files.")

        evidence: list[dict[str, Any]] = []

        for command in commands:
            if not isinstance(command, str):
                raise RepairError("Changeset command must be a string.")
            self._validate_command(command)
            result = self._run(command)
            evidence.append(
                {
                    "type": "command",
                    "command": result.command,
                    "success": result.success,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
            if not result.success:
                raise RepairError(f"Command failed: {command}\n{result.stderr}")

        for item in transmutations:
            path = item.get("path", "")
            content = item.get("content")
            justification = str(item.get("justification", "")).strip()
            if not isinstance(path, str) or not path:
                raise RepairError("Transmutation path is required.")
            if not isinstance(content, str):
                raise RepairError(f"Transmutation content must be a string: {path}")
            if any(path.startswith(prefix) for prefix in self.PROTECTED_WRITE):
                raise RepairError(f"Protected path cannot be rewritten: {path}")
            target = self._resolve_file(path)
            self._verify_content(path, content)
            if target.exists():
                old_content = target.read_text(encoding="utf-8")
                try:
                    self._preservation_check(old_content, content)
                except RepairError:
                    if len(justification) < 40:
                        raise
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            evidence.append(
                {
                    "type": "transmutation",
                    "path": path,
                    "success": True,
                }
            )

        changed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            check=False,
        )
        changed_files = []
        for line in changed.stdout.splitlines():
            if not line.strip():
                continue
            changed_files.append(line[3:].strip())
        if not changed_files:
            raise RepairError("Changeset produced no repository changes.")
        unexpected = sorted(set(changed_files) - set(expected_files))
        if unexpected:
            raise RepairError(
                "Unexpected repository mutations detected: " + ", ".join(unexpected)
            )
        return evidence, changed_files


class Validator:
    """Run issue-specific and repository-wide validation."""

    def __init__(
        self,
        workspace: str | Path,
        *,
        workspace_verifier: Callable[[str], tuple[bool, str]] | None = None,
    ):
        self.workspace = Path(workspace).resolve()
        self.workspace_verifier = workspace_verifier

    def _run(self, command: str) -> CommandEvidence:
        result = subprocess.run(
            command,
            shell=True,
            cwd=self.workspace,
            capture_output=True,
            text=True,
        )
        return CommandEvidence(
            command=command,
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout[-4000:],
            stderr=result.stderr[-4000:],
        )

    def reproduce_issue(self, commands: list[str]) -> ValidationEvidence:
        evidence = ValidationEvidence()
        for command in commands:
            result = self._run(command)
            evidence.commands.append(result)
        evidence.issue_reproduced = any(not result.success for result in evidence.commands)
        evidence.passed = evidence.issue_reproduced
        return evidence

    def validate_repair(self, commands: list[str]) -> ValidationEvidence:
        evidence = ValidationEvidence()
        for command in commands:
            result = self._run(command)
            evidence.commands.append(result)
        compile_result = self._run("python -m compileall -q barrot_agent scripts")
        evidence.compile_check = compile_result
        if self.workspace_verifier is not None:
            ok, report = self.workspace_verifier(str(self.workspace))
            evidence.workspace_check_passed = ok
            evidence.workspace_check_report = report
        evidence.passed = (
            all(result.success for result in evidence.commands)
            and compile_result.success
            and (evidence.workspace_check_passed is not False)
        )
        return evidence


class GitGateway:
    """Create commits and publish them through explicit git operations."""

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            check=False,
        )

    def configured_remotes(self) -> list[str]:
        result = self._run("remote")
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def commit(self, message: str) -> CommitEvidence:
        sanitized = " ".join(str(message).split()).strip()[:120] or "Barrot autonomous repair"
        add = self._run("add", "-A")
        if add.returncode != 0:
            raise RepairError(add.stderr.strip() or "git add failed")

        status = self._run("status", "--porcelain")
        if status.returncode != 0:
            raise RepairError(status.stderr.strip() or "git status failed")
        if not status.stdout.strip():
            raise RepairError("No repository changes available to commit.")

        commit = self._run("commit", "-m", sanitized)
        if commit.returncode != 0:
            raise RepairError(commit.stderr.strip() or "git commit failed")

        sha = self._run("rev-parse", "HEAD")
        if sha.returncode != 0:
            raise RepairError(sha.stderr.strip() or "Unable to read commit SHA.")

        return CommitEvidence(
            created=True,
            sha=sha.stdout.strip(),
            message=sanitized,
        )

    def push(self, remote: str, branch: str) -> CommandEvidence:
        result = self._run("push", remote, f"HEAD:{branch}")
        return CommandEvidence(
            command=f"git push {remote} HEAD:{branch}",
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout[-4000:],
            stderr=result.stderr[-4000:],
        )

    def remote_head(self, remote: str, branch: str) -> str:
        result = self._run("ls-remote", remote, f"refs/heads/{branch}")
        if result.returncode != 0:
            raise RepairError(result.stderr.strip() or f"git ls-remote {remote} failed")
        line = result.stdout.strip().splitlines()
        if not line:
            return ""
        return line[0].split()[0].strip()


class RemoteVerifier:
    """Verify that pushed commits are visible on configured remotes."""

    def __init__(self, git_gateway: GitGateway):
        self.git_gateway = git_gateway

    def push_and_verify(self, remote: str, branch: str, sha: str) -> RemoteSyncEvidence:
        evidence = RemoteSyncEvidence(
            remote=remote,
            applicable=True,
            attempted=True,
            branch=branch,
            sha=sha,
        )
        pushed = self.git_gateway.push(remote, branch)
        evidence.pushed = pushed.success
        if not pushed.success:
            evidence.reason = pushed.stderr or pushed.stdout or "push failed"
            return evidence
        remote_sha = self.git_gateway.remote_head(remote, branch)
        evidence.verified = bool(remote_sha and remote_sha == sha)
        evidence.reason = (
            f"remote head {remote_sha}" if remote_sha else "remote branch not visible after push"
        )
        return evidence


class RepairController:
    """Enforce a deterministic audit -> repair -> verification lifecycle."""

    def __init__(
        self,
        *,
        brain: Any,
        workspace: str | Path,
        workspace_verifier: Callable[[str], tuple[bool, str]] | None = None,
        max_attempts: int = 1,
    ):
        self.workspace = Path(workspace).resolve()
        self.audit_engine = AuditEngine()
        self.repair_planner = RepairPlanner(brain)
        self.patch_executor = PatchExecutor(self.workspace)
        self.validator = Validator(
            self.workspace,
            workspace_verifier=workspace_verifier,
        )
        self.git_gateway = GitGateway(self.workspace)
        self.remote_verifier = RemoteVerifier(self.git_gateway)
        self.max_attempts = max_attempts

    @staticmethod
    def _new_cycle_id() -> str:
        return uuid.uuid4().hex[:12]

    @staticmethod
    def _as_dict(value: ValidationEvidence) -> dict[str, Any]:
        return asdict(value)

    def _fail(
        self,
        cycle: RepairCycleEvidence,
        *,
        state: RepairState,
        message: str,
        rollback_attempted: bool = False,
        rollback_succeeded: bool = False,
        rolled_back: bool = False,
    ) -> RepairCycleEvidence:
        cycle.transition(state)
        cycle.failure = FailureEvidence(
            state=state.value,
            message=message,
            rollback_attempted=rollback_attempted,
            rollback_succeeded=rollback_succeeded,
        )
        cycle.status = "rolled_back" if rolled_back else "failed"
        return cycle

    def run(
        self,
        *,
        task_title: str,
        task_body: str,
        issue_number: str,
        repo: str,
        branch: str,
        audit_context: dict[str, str],
    ) -> RepairCycleEvidence:
        cycle = RepairCycleEvidence(cycle_id=self._new_cycle_id())
        cycle.transition(RepairState.AUDITING)

        prompt = self.audit_engine.build_prompt(
            task_title=task_title,
            task_body=task_body,
            audit_context=audit_context,
        )
        cycle.audit_completed = True

        cycle.transition(RepairState.ANALYZING)
        directive = self.repair_planner.generate(prompt)
        if directive.mode == "report":
            cycle.report_only = True
            cycle.report = directive.report
            cycle.status = "report_only"
            return cycle

        issue_summary = str(directive.issue.get("summary", "")).strip()
        validation_commands = directive.issue.get("validation_commands") or []
        if not issue_summary or not isinstance(validation_commands, list) or not validation_commands:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message="Planner did not identify a concrete issue with validation commands.",
            )

        cycle.issue = {
            "number": issue_number,
            "repository": repo,
            "branch": branch,
            **directive.issue,
        }
        cycle.issue_identified = True

        cycle.transition(RepairState.REPAIR_PLANNING)
        if not directive.repair_plan:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message="Planner did not provide a repair plan.",
            )
        cycle.repair_plan = directive.repair_plan
        cycle.repair_plan_created = True

        changeset = directive.changeset or {}
        commands = changeset.get("commands") or []
        transmutations = changeset.get("transmutations") or []
        expected_files = changeset.get("expected_files") or []
        if not (commands or transmutations) or not expected_files:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message="Planner did not provide a deterministic changeset.",
            )
        cycle.changeset_created = True

        pre_validation = self.validator.reproduce_issue(validation_commands)
        cycle.validation["pre_repair"] = self._as_dict(pre_validation)
        if not pre_validation.issue_reproduced:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message="Original issue could not be reproduced locally.",
            )

        snapshot_paths = self.patch_executor.collect_snapshot_paths(changeset)
        snapshots = self.patch_executor.snapshot(snapshot_paths)

        cycle.transition(RepairState.PATCHING)
        try:
            changes, changed_files = self.patch_executor.apply(changeset)
            cycle.changes = changes
            cycle.changes_applied = bool(changed_files)
        except Exception as exc:
            rollback_ok = self.patch_executor.rollback(snapshots)
            return self._fail(
                cycle,
                state=RepairState.PATCH_FAILED if not rollback_ok else RepairState.ROLLED_BACK,
                message=str(exc),
                rollback_attempted=True,
                rollback_succeeded=rollback_ok,
                rolled_back=rollback_ok,
            )

        cycle.transition(RepairState.LOCAL_VALIDATION)
        local_validation = self.validator.validate_repair(validation_commands)
        cycle.validation["local"] = self._as_dict(local_validation)
        if not local_validation.passed:
            rollback_ok = self.patch_executor.rollback(snapshots)
            return self._fail(
                cycle,
                state=RepairState.ROLLED_BACK if rollback_ok else RepairState.FAILED,
                message="Local validation failed after applying the changeset.",
                rollback_attempted=True,
                rollback_succeeded=rollback_ok,
                rolled_back=rollback_ok,
            )
        cycle.local_validation_passed = True

        cycle.transition(RepairState.COMMITTING)
        try:
            cycle.commit = self.git_gateway.commit(
                str(changeset.get("commit_message", "")).strip()
            )
        except Exception as exc:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message=str(exc),
            )

        remotes = self.git_gateway.configured_remotes()
        if "origin" not in remotes:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message="Required remote 'origin' is not configured.",
            )

        cycle.transition(RepairState.REMOTE_VERIFICATION)
        origin_result = self.remote_verifier.push_and_verify(
            "origin",
            branch,
            cycle.commit.sha,
        )
        cycle.sync.append(origin_result)
        cycle.commit.remote_verified = origin_result.verified
        if not origin_result.verified:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message=f"Origin remote verification failed: {origin_result.reason}",
            )

        cycle.transition(RepairState.POST_REPAIR_VALIDATION)
        post_validation = self.validator.validate_repair(validation_commands)
        cycle.validation["post_repair"] = self._as_dict(post_validation)
        cycle.post_repair_validation_passed = post_validation.passed
        cycle.resolution_verified = pre_validation.issue_reproduced and post_validation.passed
        if not cycle.post_repair_validation_passed or not cycle.resolution_verified:
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message="Post-repair validation did not confirm resolution.",
            )

        cycle.transition(RepairState.SYNCING)
        for remote in ("gitlab",):
            if remote not in remotes:
                cycle.sync.append(
                    RemoteSyncEvidence(
                        remote=remote,
                        applicable=False,
                        branch=branch,
                        sha=cycle.commit.sha,
                        reason="Remote not configured.",
                    )
                )
                continue
            cycle.sync.append(
                self.remote_verifier.push_and_verify(
                    remote,
                    branch,
                    cycle.commit.sha,
                )
            )

        if not cycle.can_complete():
            return self._fail(
                cycle,
                state=RepairState.FAILED,
                message="Completion contract not satisfied.",
            )

        cycle.transition(RepairState.COMPLETE)
        cycle.status = "complete"
        return cycle
