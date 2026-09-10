"""Deterministic repository repair controller for Barrot."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, ClassVar


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
    NO_REPAIR_REQUIRED = "NO_REPAIR_REQUIRED"
    PATCH_FAILED = "PATCH_FAILED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    BLOCKED = "BLOCKED"


class ModelFailureCode(str, Enum):
    RATE_LIMITED = "LLM_RATE_LIMITED"
    TOOL_CONFLICT = "LLM_TOOL_CONFLICT"
    INVALID_JSON = "LLM_INVALID_JSON"
    TIMEOUT = "LLM_TIMEOUT"
    AUTHENTICATION = "LLM_AUTHENTICATION_FAILED"
    NETWORK = "LLM_NETWORK_ERROR"
    API_ERROR = "LLM_API_ERROR"
    RETRY_EXHAUSTED = "LLM_RETRY_EXHAUSTED"
    UNAVAILABLE = "LLM_UNAVAILABLE"


@dataclass(frozen=True)
class StructuredCommand:
    program: str
    args: list[str] = field(default_factory=list)
    timeout: int = 120

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StructuredCommand":
        if not isinstance(data, dict):
            raise ValueError("Command must be an object.")
        program = data.get("program")
        args = data.get("args", [])
        timeout = data.get("timeout", 120)
        if not isinstance(program, str) or not program.strip():
            raise ValueError("Command program must be a non-empty string.")
        if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
            raise ValueError("Command args must be a list of strings.")
        if not isinstance(timeout, int) or timeout <= 0 or timeout > 600:
            raise ValueError("Command timeout must be an integer between 1 and 600.")
        return cls(
            program=program.strip(),
            args=[item for item in args],
            timeout=timeout,
        )

    def argv(self) -> list[str]:
        return [self.program, *self.args]

    def to_dict(self) -> dict[str, Any]:
        return {"program": self.program, "args": list(self.args), "timeout": self.timeout}

    def display(self) -> str:
        return " ".join(self.argv())


@dataclass(frozen=True)
class PatchOperation:
    type: str
    path: str
    old: str
    new: str
    reason: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PatchOperation":
        if not isinstance(data, dict):
            raise ValueError("Patch operation must be an object.")
        required = ("type", "path", "old", "new", "reason")
        if any(key not in data for key in required):
            raise ValueError("Patch operation is missing required fields.")
        values = {key: data[key] for key in required}
        if not all(isinstance(value, str) for value in values.values()):
            raise ValueError("Patch operation fields must all be strings.")
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommandEvidence:
    command: dict[str, Any]
    success: bool
    returncode: int | None
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    timed_out: bool = False


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
    exists: bool = False
    sha: str = ""
    branch: str = ""
    message: str = ""
    changed_paths: list[str] = field(default_factory=list)
    command: dict[str, Any] = field(default_factory=dict)
    timestamp: float | None = None
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
    push: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class FailureEvidence:
    state: str
    code: str = ""
    message: str = ""
    failed_operation: str = ""
    last_valid_state: str = ""
    required_external_action: str = ""
    timestamp: float = field(default_factory=time.time)
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
    issue_reproduced: bool = False
    repair_plan_created: bool = False
    changeset_created: bool = False
    changes_applied: bool = False
    local_validation_passed: bool = False
    repair_verified: bool = False
    remote_sync_verified: bool = False
    post_repair_validation_passed: bool = False
    resolution_verified: bool = False
    synchronization_recorded: bool = False
    report_only: bool = False
    report: str = ""
    attempt_number: int = 1
    resumed_from_cycle_id: str = ""
    project_identity: dict[str, Any] = field(default_factory=dict)
    issue: dict[str, Any] = field(default_factory=dict)
    repair_plan: dict[str, Any] = field(default_factory=dict)
    changeset: dict[str, Any] = field(default_factory=dict)
    changes: list[dict[str, Any]] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    commit: CommitEvidence = field(default_factory=CommitEvidence)
    sync: list[RemoteSyncEvidence] = field(default_factory=list)
    issue_fingerprint: str = ""
    plan_fingerprint: str = ""
    changeset_fingerprint: str = ""
    failure: FailureEvidence | None = None

    _ALLOWED_TRANSITIONS: ClassVar[dict[RepairState, set[RepairState]]] = {
        RepairState.IDLE: {RepairState.AUDITING, RepairState.BLOCKED},
        RepairState.AUDITING: {RepairState.ANALYZING, RepairState.FAILED, RepairState.BLOCKED},
        RepairState.ANALYZING: {
            RepairState.REPAIR_PLANNING,
            RepairState.NO_REPAIR_REQUIRED,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.REPAIR_PLANNING: {
            RepairState.PATCHING,
            RepairState.NO_REPAIR_REQUIRED,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.PATCHING: {
            RepairState.LOCAL_VALIDATION,
            RepairState.PATCH_FAILED,
            RepairState.ROLLED_BACK,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.LOCAL_VALIDATION: {
            RepairState.COMMITTING,
            RepairState.ROLLED_BACK,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.COMMITTING: {
            RepairState.REMOTE_VERIFICATION,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.REMOTE_VERIFICATION: {
            RepairState.POST_REPAIR_VALIDATION,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.POST_REPAIR_VALIDATION: {
            RepairState.SYNCING,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.SYNCING: {
            RepairState.COMPLETE,
            RepairState.FAILED,
            RepairState.BLOCKED,
        },
        RepairState.COMPLETE: set(),
        RepairState.NO_REPAIR_REQUIRED: set(),
        RepairState.PATCH_FAILED: set(),
        RepairState.FAILED: set(),
        RepairState.ROLLED_BACK: set(),
        RepairState.BLOCKED: set(),
    }

    def transition(self, state: RepairState) -> None:
        current = RepairState(self.current_state)
        allowed = self._ALLOWED_TRANSITIONS[current]
        if state not in allowed:
            raise RepairError(f"Invalid repair state transition: {current.value} -> {state.value}")
        self.current_state = state.value
        self.state_history.append(state.value)

    def can_complete(self) -> bool:
        if self.current_state != RepairState.SYNCING.value:
            return False
        origin_sync = next((item for item in self.sync if item.remote == "origin"), None)
        if origin_sync is None or not origin_sync.verified:
            return False
        applicable_sync = [item for item in self.sync if item.applicable]
        return all(
            [
                self.audit_completed,
                self.issue_identified,
                self.issue_reproduced,
                self.repair_plan_created,
                self.changeset_created,
                self.changes_applied,
                self.local_validation_passed,
                self.commit.created,
                self.commit.exists,
                self.commit.remote_verified,
                self.post_repair_validation_passed,
                self.resolution_verified,
                self.synchronization_recorded,
                all(item.verified for item in applicable_sync),
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RepairDirective:
    mode: str
    report: str = ""
    issue: dict[str, Any] = field(default_factory=dict)
    repair_plan: dict[str, Any] = field(default_factory=dict)
    changeset: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


class RepairError(RuntimeError):
    """Raised when the repair controller cannot advance safely."""


class ModelFailure(RepairError):
    """Raised when the model response or provider cannot be used safely."""

    def __init__(self, code: ModelFailureCode, message: str):
        super().__init__(message)
        self.code = code


def _fingerprint(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class DurableCycleStore:
    """Persists repair cycle records for bounded retry and safe resume."""

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        self.base_dir = self.workspace / ".git" / "barrot_repair" / "repair_cycles"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_dir / "latest.json"

    def write(self, cycle: RepairCycleEvidence) -> Path:
        payload = cycle.to_dict()
        path = self.base_dir / f"{cycle.cycle_id}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.index_path.write_text(
            json.dumps(
                {
                    "latest_cycle_id": cycle.cycle_id,
                    "record_path": str(path.relative_to(self.workspace)),
                    "project_identity": cycle.project_identity,
                    "status": cycle.status,
                    "attempt_number": cycle.attempt_number,
                    "issue_fingerprint": cycle.issue_fingerprint,
                    "plan_fingerprint": cycle.plan_fingerprint,
                    "changeset_fingerprint": cycle.changeset_fingerprint,
                    "commit_sha": cycle.commit.sha,
                    "current_state": cycle.current_state,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return path

    def load_latest(self) -> dict[str, Any] | None:
        if not self.index_path.exists():
            return None
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None


class AuditEngine:
    """Builds the grounded prompt context used by the planner."""

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
        prompt += "\n\nReturn JSON only using the deterministic repair schema."
        return prompt


class RepairPlanner:
    """Requests a bounded repair plan from the configured model."""

    SYSTEM = """You are Barrot acting as a deterministic repository repair planner.

Return JSON only. No prose. No markdown fences.

Schema:
{
  "mode": "repair" | "report" | "no_repair_required",
  "report": "required when mode=report",
  "issue": {
    "summary": "one concrete repository issue",
    "evidence": ["repository-grounded facts only"],
    "files": ["relative/path.py"],
    "reproduction_commands": [
      {"program": "python", "args": ["-m", "pytest", "-q", "tests/test_x.py", "--no-cov"]}
    ],
    "validation_commands": [
      {"program": "python", "args": ["-m", "pytest", "-q", "tests/test_x.py", "--no-cov"]}
    ],
    "resolution_commands": [
      {"program": "python", "args": ["-m", "pytest", "-q", "tests/test_x.py", "--no-cov"]}
    ]
  },
  "repair_plan": {
    "summary": "minimal plan",
    "reason": "why this fixes the issue"
  },
  "changeset": {
    "operations": [
      {
        "type": "replace",
        "path": "relative/path.py",
        "old": "exact existing text",
        "new": "replacement text",
        "reason": "why this fixes the reproduced issue"
      }
    ],
    "expected_files": ["relative/path.py"],
    "commit_message": "short commit message"
  }
}

Rules:
- Use mode=no_repair_required when the repository is already healthy for the requested issue.
- Use mode=report when the task is audit-only or cannot be repaired deterministically.
- For mode=repair, identify exactly one concrete issue.
- If repository inspection is needed, use the available repo_browser tools with non-empty relative paths such as ".".
- reproduction_commands must fail before repair when the issue exists.
- validation_commands must pass after repair.
- resolution_commands must specifically re-test the original failure condition.
- Use only operation type "replace".
- Every replace operation must use the exact current text for "old".
- Keep changes minimal and repository-grounded.
- Never claim the repair succeeded.
"""

    def __init__(
        self,
        brain: Any,
        *,
        max_attempts: int = 3,
        backoff_seconds: float = 0.1,
    ):
        self.brain = brain
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds

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
            raise ModelFailure(ModelFailureCode.INVALID_JSON, "Planner returned no JSON object.")
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ModelFailure(ModelFailureCode.INVALID_JSON, str(exc)) from exc

    @staticmethod
    def _normalize_exception(exc: Exception) -> ModelFailure:
        if isinstance(exc, ModelFailure):
            return exc
        message = str(exc)
        lowered = message.lower()
        if "429" in lowered or "rate limit" in lowered or "rate-limited" in lowered:
            return ModelFailure(ModelFailureCode.RATE_LIMITED, message)
        if "tool_choice" in lowered or "tool choice" in lowered or "tool conflict" in lowered:
            return ModelFailure(ModelFailureCode.TOOL_CONFLICT, message)
        if "retry exhaustion" in lowered:
            return ModelFailure(ModelFailureCode.RETRY_EXHAUSTED, message)
        if "authentication failed" in lowered or "unauthorized" in lowered or "forbidden" in lowered:
            return ModelFailure(ModelFailureCode.AUTHENTICATION, message)
        if "network error" in lowered or "name or service not known" in lowered or "connection refused" in lowered:
            return ModelFailure(ModelFailureCode.NETWORK, message)
        if isinstance(exc, TimeoutError) or "timeout" in lowered:
            return ModelFailure(ModelFailureCode.TIMEOUT, message)
        if "http " in lowered:
            return ModelFailure(ModelFailureCode.API_ERROR, message)
        return ModelFailure(ModelFailureCode.UNAVAILABLE, message)

    def generate(self, prompt: str) -> RepairDirective:
        last_failure: ModelFailure | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                raw = self.brain.think(prompt, system=self.SYSTEM)
                payload = self._extract_json(raw)
                mode = str(payload.get("mode", "")).strip().lower()
                if mode not in {"repair", "report", "no_repair_required"}:
                    raise ModelFailure(
                        ModelFailureCode.INVALID_JSON,
                        "Planner mode must be repair, report, or no_repair_required.",
                    )
                return RepairDirective(
                    mode=mode,
                    report=str(payload.get("report", "")).strip(),
                    issue=payload.get("issue") or {},
                    repair_plan=payload.get("repair_plan") or {},
                    changeset=payload.get("changeset") or {},
                    raw=payload,
                )
            except Exception as exc:  # noqa: BLE001
                last_failure = self._normalize_exception(exc)
                if last_failure.code in {
                    ModelFailureCode.RATE_LIMITED,
                    ModelFailureCode.TIMEOUT,
                } and attempt < self.max_attempts:
                    time.sleep(self.backoff_seconds * attempt)
                    continue
                raise last_failure
        assert last_failure is not None
        raise last_failure


class StructuredCommandExecutor:
    """Runs only explicitly allowed repository-local commands."""

    ALLOWED_PROGRAMS = {"python", "python3", "pytest"}

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

    @staticmethod
    def _is_path_traversal(argument: str) -> bool:
        return argument == ".." or argument.startswith("../") or "/../" in argument or argument.startswith("/")

    def validate(self, command: StructuredCommand) -> None:
        program = os.path.basename(command.program)
        if program not in self.ALLOWED_PROGRAMS:
            raise RepairError(f"Unsupported executable: {command.program}")
        previous = ""
        for argument in command.args:
            if "\x00" in argument:
                raise RepairError("Command arguments must not contain NUL bytes.")
            if previous not in {"-c", "-m"} and self._is_path_traversal(argument):
                raise RepairError(f"Command argument escapes workspace: {argument}")
            previous = argument

    def run(self, command: StructuredCommand) -> CommandEvidence:
        self.validate(command)
        try:
            completed = subprocess.run(
                command.argv(),
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=command.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandEvidence(
                command=command.to_dict(),
                success=False,
                returncode=None,
                stdout=(exc.stdout or "")[-4000:],
                stderr=(exc.stderr or "")[-4000:],
                error=f"Command timed out after {command.timeout}s",
                timed_out=True,
            )
        return CommandEvidence(
            command=command.to_dict(),
            success=completed.returncode == 0,
            returncode=completed.returncode,
            stdout=completed.stdout[-4000:],
            stderr=completed.stderr[-4000:],
        )


class PatchExecutor:
    """Applies exact, guarded in-repository patch operations."""

    PROTECTED_WRITE = (
        "core/",
        "hf_space/",
        "web/",
        "scripts/emit_signal.py",
        ".github/workflows/",
    )
    ALLOWED_EXTENSIONS = {".py", ".json", ".jsonl", ".yml", ".yaml", ".md", ".txt", ".toml"}

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

    def _resolve_path(self, relative_path: str) -> Path:
        if not relative_path or Path(relative_path).is_absolute():
            raise RepairError(f"Invalid patch path: {relative_path}")
        target = (self.workspace / relative_path).resolve()
        if self.workspace not in target.parents:
            raise RepairError(f"Patch path escapes workspace: {relative_path}")
        return target

    def _verify_content(self, path: str, content: str) -> None:
        suffix = Path(path).suffix.lower()
        if suffix not in self.ALLOWED_EXTENSIONS:
            raise RepairError(f"Unsupported file type for patching: {suffix}")
        if suffix == ".py":
            ast.parse(content)
        elif suffix == ".json":
            json.loads(content)
        elif suffix == ".jsonl":
            for line in content.splitlines():
                line = line.strip()
                if line:
                    json.loads(line)

    def snapshot(self, paths: list[str]) -> dict[str, str | None]:
        snapshots: dict[str, str | None] = {}
        for path in paths:
            target = self._resolve_path(path)
            snapshots[path] = target.read_text(encoding="utf-8") if target.exists() else None
        return snapshots

    def rollback(self, snapshots: dict[str, str | None]) -> bool:
        try:
            for path, original in snapshots.items():
                target = self._resolve_path(path)
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
        raw_operations = changeset.get("operations")
        raw_expected = changeset.get("expected_files")
        if not isinstance(raw_operations, list) or not raw_operations:
            raise RepairError("Changeset must contain a non-empty operations list.")
        if not isinstance(raw_expected, list) or not raw_expected:
            raise RepairError("Changeset must contain a non-empty expected_files list.")

        operations = [PatchOperation.from_dict(item) for item in raw_operations]
        expected_files = [str(item) for item in raw_expected if isinstance(item, str) and item]
        evidence: list[dict[str, Any]] = []

        for operation in operations:
            if operation.type != "replace":
                raise RepairError(f"Unsupported patch operation type: {operation.type}")
            if any(operation.path.startswith(prefix) for prefix in self.PROTECTED_WRITE):
                raise RepairError(f"Protected path cannot be modified: {operation.path}")
            target = self._resolve_path(operation.path)
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            occurrences = current.count(operation.old)
            if occurrences == 0:
                raise RepairError(f"Patch precondition failed; old text not found in {operation.path}")
            if occurrences > 1:
                raise RepairError(f"Patch precondition ambiguous in {operation.path}")
            updated = current.replace(operation.old, operation.new, 1)
            if updated == current:
                raise RepairError(f"Patch produced no change in {operation.path}")
            self._verify_content(operation.path, updated)
            target.write_text(updated, encoding="utf-8")
            evidence.append(
                {
                    "type": "replace",
                    "path": operation.path,
                    "reason": operation.reason,
                    "old_hash": hashlib.sha256(operation.old.encode("utf-8")).hexdigest(),
                    "new_hash": hashlib.sha256(operation.new.encode("utf-8")).hexdigest(),
                }
            )

        changed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            check=False,
        )
        changed_files = sorted(
            line[3:].strip()
            for line in changed.stdout.splitlines()
            if line.strip()
        )
        if not changed_files:
            raise RepairError("Changeset produced no repository mutation.")
        if sorted(expected_files) != changed_files:
            raise RepairError(
                "Changed files do not match expected_files: "
                f"expected={sorted(expected_files)} actual={changed_files}"
            )
        return evidence, changed_files


class Validator:
    """Separates reproduction, general validation, and resolution verification."""

    def __init__(
        self,
        workspace: str | Path,
        *,
        workspace_verifier: Callable[[str], tuple[bool, str]] | None = None,
    ):
        self.command_executor = StructuredCommandExecutor(workspace)
        self.workspace = Path(workspace).resolve()
        self.workspace_verifier = workspace_verifier

    @staticmethod
    def _parse_commands(raw: Any) -> list[StructuredCommand]:
        if not isinstance(raw, list) or not raw:
            raise RepairError("Validation command list must be non-empty.")
        return [StructuredCommand.from_dict(item) for item in raw]

    def reproduce_issue(self, raw_commands: Any) -> ValidationEvidence:
        commands = self._parse_commands(raw_commands)
        evidence = ValidationEvidence()
        for command in commands:
            result = self.command_executor.run(command)
            evidence.commands.append(result)
        evidence.issue_reproduced = any(not item.success for item in evidence.commands)
        evidence.passed = evidence.issue_reproduced
        return evidence

    def validate_changes(self, raw_commands: Any) -> ValidationEvidence:
        commands = self._parse_commands(raw_commands)
        evidence = ValidationEvidence()
        for command in commands:
            result = self.command_executor.run(command)
            evidence.commands.append(result)
        compile_result = self.command_executor.run(
            StructuredCommand(
                program="python",
                args=["-m", "compileall", "-q", "barrot_agent", "scripts"],
                timeout=120,
            )
        )
        evidence.compile_check = compile_result
        if self.workspace_verifier is not None:
            ok, report = self.workspace_verifier(str(self.workspace))
            evidence.workspace_check_passed = ok
            evidence.workspace_check_report = report
        evidence.passed = (
            all(item.success for item in evidence.commands)
            and compile_result.success
            and (evidence.workspace_check_passed is not False)
        )
        return evidence

    def verify_resolution(self, raw_commands: Any) -> ValidationEvidence:
        commands = self._parse_commands(raw_commands)
        evidence = ValidationEvidence()
        for command in commands:
            result = self.command_executor.run(command)
            evidence.commands.append(result)
        evidence.passed = all(item.success for item in evidence.commands)
        return evidence


class GitGateway:
    """Deterministic git operations with evidence capture."""

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
            raise RepairError(result.stderr.strip() or "git remote failed")
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def current_branch(self) -> str:
        result = self._run("branch", "--show-current")
        if result.returncode != 0:
            raise RepairError(result.stderr.strip() or "git branch --show-current failed")
        return result.stdout.strip()

    def commit(self, message: str, expected_paths: list[str]) -> CommitEvidence:
        sanitized = " ".join(str(message).split()).strip()[:120] or "Barrot autonomous repair"
        add = self._run("add", "--", *expected_paths)
        if add.returncode != 0:
            raise RepairError(add.stderr.strip() or "git add failed")

        staged = self._run("diff", "--cached", "--name-only")
        if staged.returncode != 0:
            raise RepairError(staged.stderr.strip() or "git diff --cached failed")
        changed_paths = sorted(line.strip() for line in staged.stdout.splitlines() if line.strip())
        if changed_paths != sorted(expected_paths):
            raise RepairError(
                "Staged files do not match expected paths: "
                f"expected={sorted(expected_paths)} actual={changed_paths}"
            )

        commit = self._run("commit", "-m", sanitized)
        if commit.returncode != 0:
            raise RepairError(commit.stderr.strip() or "git commit failed")

        sha_result = self._run("rev-parse", "HEAD")
        if sha_result.returncode != 0:
            raise RepairError(sha_result.stderr.strip() or "git rev-parse failed")
        sha = sha_result.stdout.strip()

        exists = self._run("cat-file", "-e", f"{sha}^{{commit}}")
        branch = self.current_branch()

        return CommitEvidence(
            created=True,
            exists=exists.returncode == 0,
            sha=sha,
            branch=branch,
            message=sanitized,
            changed_paths=changed_paths,
            command={
                "program": "git",
                "args": ["commit", "-m", sanitized],
                "stdout": commit.stdout[-4000:],
                "stderr": commit.stderr[-4000:],
                "returncode": commit.returncode,
            },
            timestamp=time.time(),
        )

    def push(self, remote: str, branch: str) -> CommandEvidence:
        result = self._run("push", remote, f"HEAD:{branch}")
        return CommandEvidence(
            command={"program": "git", "args": ["push", remote, f"HEAD:{branch}"]},
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout[-4000:],
            stderr=result.stderr[-4000:],
        )

    def remote_head(self, remote: str, branch: str) -> CommandEvidence:
        result = self._run("ls-remote", remote, f"refs/heads/{branch}")
        stdout = result.stdout[-4000:]
        sha = ""
        lines = stdout.strip().splitlines()
        if lines:
            sha = lines[0].split()[0].strip()
        return CommandEvidence(
            command={"program": "git", "args": ["ls-remote", remote, f"refs/heads/{branch}"]},
            success=result.returncode == 0 and bool(sha),
            returncode=result.returncode,
            stdout=sha,
            stderr=result.stderr[-4000:],
        )


class RemoteVerifier:
    """Pushes and independently verifies branch head SHAs."""

    def __init__(self, git_gateway: GitGateway):
        self.git_gateway = git_gateway

    def push_and_verify(self, remote: str, branch: str, sha: str) -> RemoteSyncEvidence:
        push = self.git_gateway.push(remote, branch)
        evidence = RemoteSyncEvidence(
            remote=remote,
            applicable=True,
            attempted=True,
            pushed=push.success,
            branch=branch,
            sha=sha,
            push=asdict(push),
        )
        if not push.success:
            evidence.reason = push.stderr or push.stdout or "push failed"
            return evidence

        verification = self.git_gateway.remote_head(remote, branch)
        evidence.verification = asdict(verification)
        evidence.verified = verification.success and verification.stdout.strip() == sha
        evidence.reason = (
            f"remote head {verification.stdout.strip()}"
            if verification.stdout.strip()
            else "remote branch not visible after push"
        )
        return evidence


class RepositoryRepairController:
    """Authoritative repair lifecycle for the live Barrot entrypoint."""

    def __init__(
        self,
        *,
        brain: Any,
        workspace: str | Path,
        workspace_verifier: Callable[[str], tuple[bool, str]] | None = None,
        planner_attempts: int = 3,
        max_unchanged_attempts: int = 2,
    ):
        self.workspace = Path(workspace).resolve()
        self.audit_engine = AuditEngine()
        self.repair_planner = RepairPlanner(brain, max_attempts=planner_attempts)
        self.patch_executor = PatchExecutor(self.workspace)
        self.validator = Validator(
            self.workspace,
            workspace_verifier=workspace_verifier,
        )
        self.git_gateway = GitGateway(self.workspace)
        self.remote_verifier = RemoteVerifier(self.git_gateway)
        self.cycle_store = DurableCycleStore(self.workspace)
        self.max_unchanged_attempts = max_unchanged_attempts

    @staticmethod
    def _new_cycle_id() -> str:
        return uuid.uuid4().hex[:12]

    def _persist(self, cycle: RepairCycleEvidence) -> None:
        self.cycle_store.write(cycle)

    def _failure(
        self,
        cycle: RepairCycleEvidence,
        state: RepairState,
        code: str,
        message: str,
        *,
        failed_operation: str = "",
        required_external_action: str = "",
    ) -> RepairCycleEvidence:
        last_valid_state = cycle.current_state
        cycle.transition(state)
        cycle.failure = FailureEvidence(
            state=state.value,
            code=code,
            message=message,
            failed_operation=failed_operation,
            last_valid_state=last_valid_state,
            required_external_action=required_external_action,
        )
        cycle.status = "blocked" if state == RepairState.BLOCKED else "failed"
        self._persist(cycle)
        return cycle

    def _rolled_back(
        self,
        cycle: RepairCycleEvidence,
        state: RepairState,
        message: str,
        rollback_succeeded: bool,
        *,
        failed_operation: str = "",
    ) -> RepairCycleEvidence:
        last_valid_state = cycle.current_state
        cycle.transition(state)
        cycle.failure = FailureEvidence(
            state=state.value,
            code=state.value,
            message=message,
            failed_operation=failed_operation,
            last_valid_state=last_valid_state,
            rollback_attempted=True,
            rollback_succeeded=rollback_succeeded,
        )
        cycle.status = "rolled_back" if rollback_succeeded else "failed"
        self._persist(cycle)
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
        latest = self.cycle_store.load_latest() or {}
        repo_name = str(repo).strip() or str(latest.get("project_identity", {}).get("repository", "")).strip()
        branch_name = str(branch).strip() or str(latest.get("project_identity", {}).get("branch", "")).strip()
        if not repo_name or not branch_name:
            cycle.project_identity = {
                "repository": str(repo).strip(),
                "branch": str(branch).strip(),
            }
            self._persist(cycle)
            return self._failure(
                cycle,
                RepairState.BLOCKED,
                "PROJECT_IDENTITY_MISSING",
                "Repository and branch must both be non-empty.",
                failed_operation="initialize_cycle",
                required_external_action="Provide a non-empty repository and branch for the repair cycle.",
            )
        cycle.project_identity = {
            "repository": repo_name,
            "branch": branch_name,
            "task_title": task_title,
        }
        if latest.get("project_identity", {}) == cycle.project_identity:
            cycle.attempt_number = int(latest.get("attempt_number") or 0) + 1
            cycle.resumed_from_cycle_id = str(latest.get("latest_cycle_id") or "")
        self._persist(cycle)
        cycle.transition(RepairState.AUDITING)
        self._persist(cycle)
        prompt = self.audit_engine.build_prompt(
            task_title=task_title,
            task_body=task_body,
            audit_context=audit_context,
        )
        cycle.audit_completed = True

        cycle.transition(RepairState.ANALYZING)
        self._persist(cycle)
        try:
            directive = self.repair_planner.generate(prompt)
        except ModelFailure as exc:
            return self._failure(
                cycle,
                RepairState.FAILED,
                exc.code.value,
                str(exc),
                failed_operation="repair_planner.generate",
            )

        if directive.mode == "report":
            cycle.report_only = True
            cycle.report = directive.report
            cycle.transition(RepairState.NO_REPAIR_REQUIRED)
            cycle.status = "no_repair_required"
            self._persist(cycle)
            return cycle

        if directive.mode == "no_repair_required":
            cycle.report = directive.report
            cycle.transition(RepairState.NO_REPAIR_REQUIRED)
            cycle.status = "no_repair_required"
            self._persist(cycle)
            return cycle

        issue = directive.issue
        repair_plan = directive.repair_plan
        changeset = directive.changeset

        if not issue or not isinstance(issue, dict):
            return self._failure(
                cycle,
                RepairState.FAILED,
                "ISSUE_MISSING",
                "Planner did not identify a concrete issue.",
                failed_operation="validate_issue",
            )

        reproduction_commands = issue.get("reproduction_commands")
        validation_commands = issue.get("validation_commands") or issue.get("resolution_commands") or reproduction_commands
        resolution_commands = issue.get("resolution_commands") or reproduction_commands
        summary = str(issue.get("summary", "")).strip()
        files = issue.get("files") or []
        if not summary or not isinstance(files, list) or not files:
            return self._failure(
                cycle,
                RepairState.FAILED,
                "ISSUE_INVALID",
                "Issue summary/files are required.",
                failed_operation="validate_issue",
            )

        cycle.issue = {
            "number": issue_number,
            "repository": repo_name,
            "branch": branch_name,
            **issue,
        }
        cycle.issue_fingerprint = _fingerprint(
            {
                "summary": summary,
                "files": files,
                "reproduction_commands": reproduction_commands,
            }
        )
        cycle.issue_identified = True
        self._persist(cycle)

        try:
            pre_repair = self.validator.reproduce_issue(reproduction_commands)
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                cycle,
                RepairState.FAILED,
                "REPRODUCE_ERROR",
                str(exc),
                failed_operation="reproduce_issue",
            )

        cycle.validation["issue_reproduction"] = asdict(pre_repair)
        cycle.issue_reproduced = pre_repair.issue_reproduced
        if not pre_repair.issue_reproduced:
            cycle.report = directive.report or "Issue condition no longer reproduces."
            cycle.transition(RepairState.NO_REPAIR_REQUIRED)
            cycle.status = "no_repair_required"
            self._persist(cycle)
            return cycle

        cycle.transition(RepairState.REPAIR_PLANNING)
        self._persist(cycle)
        if not repair_plan or not isinstance(repair_plan, dict):
            return self._failure(
                cycle,
                RepairState.FAILED,
                "PLAN_MISSING",
                "Planner did not provide a repair plan.",
                failed_operation="validate_repair_plan",
            )
        if not changeset or not isinstance(changeset, dict):
            return self._failure(
                cycle,
                RepairState.FAILED,
                "CHANGESET_MISSING",
                "Planner did not provide a changeset.",
                failed_operation="validate_changeset",
            )

        cycle.repair_plan = repair_plan
        cycle.plan_fingerprint = _fingerprint(repair_plan)
        cycle.repair_plan_created = True
        cycle.changeset = changeset
        cycle.changeset_fingerprint = _fingerprint(changeset)
        cycle.changeset_created = True
        if (
            latest.get("issue_fingerprint") == cycle.issue_fingerprint
            and latest.get("plan_fingerprint") == cycle.plan_fingerprint
            and latest.get("changeset_fingerprint") == cycle.changeset_fingerprint
            and cycle.attempt_number > self.max_unchanged_attempts
        ):
            return self._failure(
                cycle,
                RepairState.BLOCKED,
                ModelFailureCode.RETRY_EXHAUSTED.value,
                "Retry exhaustion: repeated identical repair plan and changeset for the same issue.",
                failed_operation="detect_unchanged_state",
                required_external_action="Revise the repair plan or provide new repository context before retrying.",
            )
        self._persist(cycle)

        snapshot_paths = sorted(
            {
                *[item for item in (changeset.get("expected_files") or []) if isinstance(item, str)],
                *[item for item in files if isinstance(item, str)],
            }
        )
        try:
            snapshots = self.patch_executor.snapshot(snapshot_paths)
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                cycle,
                RepairState.FAILED,
                "SNAPSHOT_FAILED",
                str(exc),
                failed_operation="snapshot_workspace",
            )

        cycle.transition(RepairState.PATCHING)
        self._persist(cycle)
        try:
            cycle.changes, changed_files = self.patch_executor.apply(changeset)
            cycle.changes_applied = bool(changed_files)
        except Exception as exc:  # noqa: BLE001
            rollback_ok = self.patch_executor.rollback(snapshots)
            if rollback_ok:
                return self._rolled_back(
                    cycle,
                    RepairState.ROLLED_BACK,
                    str(exc),
                    True,
                    failed_operation="apply_patch",
                )
            return self._failure(
                cycle,
                RepairState.PATCH_FAILED,
                "PATCH_FAILED",
                str(exc),
                failed_operation="apply_patch",
            )

        cycle.transition(RepairState.LOCAL_VALIDATION)
        self._persist(cycle)
        try:
            local_validation = self.validator.validate_changes(validation_commands)
        except Exception as exc:  # noqa: BLE001
            rollback_ok = self.patch_executor.rollback(snapshots)
            if rollback_ok:
                return self._rolled_back(
                    cycle,
                    RepairState.ROLLED_BACK,
                    str(exc),
                    True,
                    failed_operation="validate_changes",
                )
            return self._failure(
                cycle,
                RepairState.FAILED,
                "VALIDATION_ERROR",
                str(exc),
                failed_operation="validate_changes",
            )
        cycle.validation["local_validation"] = asdict(local_validation)
        cycle.local_validation_passed = local_validation.passed
        if not local_validation.passed:
            rollback_ok = self.patch_executor.rollback(snapshots)
            if rollback_ok:
                return self._rolled_back(
                    cycle,
                    RepairState.ROLLED_BACK,
                    "Local validation failed after patch application.",
                    True,
                    failed_operation="validate_changes",
                )
            return self._failure(
                cycle,
                RepairState.FAILED,
                "VALIDATION_FAILED",
                "Local validation failed and rollback did not complete.",
                failed_operation="validate_changes",
            )

        cycle.transition(RepairState.COMMITTING)
        self._persist(cycle)
        expected_files = [str(item) for item in changeset.get("expected_files", []) if isinstance(item, str)]
        try:
            cycle.commit = self.git_gateway.commit(
                str(changeset.get("commit_message", "")).strip(),
                expected_files,
            )
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                cycle,
                RepairState.FAILED,
                "COMMIT_FAILED",
                str(exc),
                failed_operation="git_commit",
            )
        if not cycle.commit.exists:
            return self._failure(
                cycle,
                RepairState.FAILED,
                "COMMIT_MISSING",
                "Commit SHA does not exist locally.",
                failed_operation="git_commit",
            )
        self._persist(cycle)

        cycle.transition(RepairState.REMOTE_VERIFICATION)
        self._persist(cycle)
        try:
            remotes = self.git_gateway.configured_remotes()
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                cycle,
                RepairState.BLOCKED,
                "REMOTE_LIST_FAILED",
                str(exc),
                failed_operation="list_remotes",
                required_external_action="Restore git remote configuration and rerun the repair cycle.",
            )

        if "origin" not in remotes:
            return self._failure(
                cycle,
                RepairState.BLOCKED,
                "ORIGIN_MISSING",
                "Required remote 'origin' is not configured.",
                failed_operation="verify_origin_remote",
                required_external_action="Configure the origin remote before attempting autonomous repair synchronization.",
            )

        origin_sync = self.remote_verifier.push_and_verify("origin", branch_name, cycle.commit.sha)
        cycle.sync.append(origin_sync)
        cycle.commit.remote_verified = origin_sync.verified

        cycle.transition(RepairState.POST_REPAIR_VALIDATION)
        self._persist(cycle)
        try:
            resolution = self.validator.verify_resolution(resolution_commands)
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                cycle,
                RepairState.FAILED,
                "RESOLUTION_ERROR",
                str(exc),
                failed_operation="verify_resolution",
            )
        cycle.validation["post_repair_verification"] = asdict(resolution)
        cycle.post_repair_validation_passed = resolution.passed
        cycle.resolution_verified = resolution.passed
        cycle.repair_verified = cycle.local_validation_passed and cycle.resolution_verified

        cycle.transition(RepairState.SYNCING)
        self._persist(cycle)
        for remote in remotes:
            if remote == "origin":
                continue
            if remote != "gitlab":
                cycle.sync.append(
                    RemoteSyncEvidence(
                        remote=remote,
                        applicable=False,
                        branch=branch_name,
                        sha=cycle.commit.sha,
                        reason="Remote sync not applicable.",
                    )
                )
                continue
            cycle.sync.append(self.remote_verifier.push_and_verify(remote, branch_name, cycle.commit.sha))

        if not any(item.remote == "gitlab" for item in cycle.sync):
            cycle.sync.append(
                RemoteSyncEvidence(
                    remote="gitlab",
                    applicable=False,
                    branch=branch_name,
                    sha=cycle.commit.sha,
                    reason="GitLab remote not configured.",
                )
            )

        cycle.synchronization_recorded = True
        applicable_sync = [item for item in cycle.sync if item.applicable]
        cycle.remote_sync_verified = all(item.verified for item in applicable_sync)

        if not cycle.can_complete():
            return self._failure(
                cycle,
                RepairState.FAILED,
                "COMPLETION_GATE_BLOCKED",
                "Completion gate rejected the repair evidence.",
                failed_operation="completion_gate",
            )

        cycle.transition(RepairState.COMPLETE)
        cycle.status = "complete"
        self._persist(cycle)
        return cycle


RepairController = RepositoryRepairController
