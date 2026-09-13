"""Shared orchestration primitives for deterministic Barrot task execution."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


class TaskState(str, Enum):
    IDLE = "IDLE"
    RECEIVED = "RECEIVED"
    AUDITING = "AUDITING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    CHECKPOINTED = "CHECKPOINTED"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"
    FAILED = "FAILED"


class FailureCode(str, Enum):
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    UNSUPPORTED_TOOL = "UNSUPPORTED_TOOL"
    UNSAFE_PATH = "UNSAFE_PATH"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_OUTPUT_LIMIT = "TOOL_OUTPUT_LIMIT"
    PROVIDER_TIMEOUT = "LLM_TIMEOUT"
    PROVIDER_INVALID_JSON = "LLM_INVALID_JSON"
    PROVIDER_TOOL_CONFLICT = "LLM_TOOL_CONFLICT"
    PROVIDER_RATE_LIMITED = "LLM_RATE_LIMITED"
    PROVIDER_UNAVAILABLE = "LLM_UNAVAILABLE"
    PROVIDER_AUTH = "LLM_AUTHENTICATION_FAILED"
    PROVIDER_NETWORK = "LLM_NETWORK_ERROR"
    PROVIDER_API = "LLM_API_ERROR"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"
    UNCHANGED_INPUT = "UNCHANGED_INPUT"
    UNCHANGED_OUTPUT = "UNCHANGED_OUTPUT"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@dataclass(frozen=True)
class Fingerprint:
    value: str

    @staticmethod
    def create(*parts: Any) -> "Fingerprint":
        import hashlib

        body = "::".join(json.dumps(part, sort_keys=True, ensure_ascii=False, default=str) for part in parts)
        return Fingerprint(hashlib.sha256(body.encode("utf-8")).hexdigest())


@dataclass
class Provenance:
    sources: list[str] = field(default_factory=list)
    ancestry: list[str] = field(default_factory=list)
    source_commit: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Failure:
    code: str
    message: str
    failed_operation: str = ""
    raw_error: str = ""
    recovery_decision: str = ""
    retry_outcome: str = ""
    request_payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0

    def delay_for(self, attempt: int) -> float:
        return min(self.base_delay_seconds * (2 ** max(0, attempt - 1)), self.max_delay_seconds)


@dataclass
class Checkpoint:
    checkpoint_id: str
    task_id: str
    state: str
    summary: str
    fingerprint: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Artifact:
    artifact_id: str
    kind: str
    path: str
    fingerprint: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolRequest:
    tool_name: str
    arguments: dict[str, Any]
    timeout_seconds: int = 30

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    output: Any = None
    error: str = ""
    truncated: bool = False
    output_bytes: int = 0
    duration_ms: int = 0
    failure: Failure | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.failure is None:
            payload["failure"] = None
        return payload


@dataclass
class ValidationResult:
    passed: bool
    summary: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    failure: Failure | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.failure is None:
            payload["failure"] = None
        return payload


@dataclass
class ExecutionRecord:
    record_id: str
    operation: str
    state: str
    input_fingerprint: str = ""
    output_fingerprint: str = ""
    request: dict[str, Any] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)
    provider: str = ""
    retry_attempt: int = 1
    duration_ms: int = 0
    failure: Failure | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.failure is None:
            payload["failure"] = None
        return payload


@dataclass
class CompletionGate:
    gate_id: str
    requirements: dict[str, bool]
    satisfied: bool
    unresolved: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DurableStateStore:
    def __init__(self, root: str | Path, namespace: str):
        self.root = Path(root).resolve() / ".git" / namespace
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_dir = self.root / "states"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = self.root / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"

    @staticmethod
    def _safe_id(value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value).strip("_") or "record"

    def state_path(self, task_id: str) -> Path:
        return self.state_dir / f"{self._safe_id(task_id)}.json"

    def write_state(self, task_id: str, payload: dict[str, Any], *, fingerprint: str = "") -> Path:
        path = self.state_path(task_id)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        index = self.load_index()
        if fingerprint:
            index[fingerprint] = task_id
        self.index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_state(self, task_id: str) -> dict[str, Any] | None:
        path = self.state_path(task_id)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def load_index(self) -> dict[str, str]:
        if not self.index_path.exists():
            return {}
        try:
            payload = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return {str(k): str(v) for k, v in payload.items()} if isinstance(payload, dict) else {}

    def load_state_by_fingerprint(self, fingerprint: str) -> dict[str, Any] | None:
        task_id = self.load_index().get(fingerprint)
        return self.load_state(task_id) if task_id else None

    def write_checkpoint(self, checkpoint: Checkpoint) -> Path:
        path = self.checkpoint_dir / f"{self._safe_id(checkpoint.checkpoint_id)}.json"
        path.write_text(json.dumps(checkpoint.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path


class ControlledToolExecutor:
    def __init__(
        self,
        *,
        workspace: str | Path,
        tool_map: Mapping[str, Callable[[dict[str, Any]], Any]],
        output_limit_bytes: int = 20000,
    ):
        self.workspace = Path(workspace).resolve()
        self.tool_map = dict(tool_map)
        self.output_limit_bytes = output_limit_bytes

    def _validate_args(self, tool_name: str, args: dict[str, Any]) -> None:
        if tool_name not in self.tool_map:
            raise ValueError(FailureCode.UNSUPPORTED_TOOL.value)
        if not isinstance(args, dict):
            raise ValueError(FailureCode.INVALID_ARGUMENT.value)
        for key, value in args.items():
            if key.endswith("path") or key == "path":
                cleaned = str(value).strip()
                if not cleaned:
                    raise ValueError(FailureCode.INVALID_ARGUMENT.value)
                target = (self.workspace / cleaned).resolve() if not Path(cleaned).is_absolute() else Path(cleaned).resolve()
                if target != self.workspace and self.workspace not in target.parents:
                    raise ValueError(FailureCode.UNSAFE_PATH.value)

    def execute(self, request: ToolRequest) -> ToolResult:
        started = time.time()
        try:
            self._validate_args(request.tool_name, request.arguments)
            output = self.tool_map[request.tool_name](request.arguments)
            rendered = output if isinstance(output, str) else json.dumps(output, ensure_ascii=False, default=str)
            encoded = rendered.encode("utf-8", errors="replace")
            truncated = len(encoded) > self.output_limit_bytes
            if truncated:
                rendered = encoded[: self.output_limit_bytes].decode("utf-8", errors="replace")
            return ToolResult(
                tool_name=request.tool_name,
                success=True,
                output=rendered,
                truncated=truncated,
                output_bytes=len(encoded),
                duration_ms=int((time.time() - started) * 1000),
                failure=(
                    Failure(
                        code=FailureCode.TOOL_OUTPUT_LIMIT.value,
                        message="Tool output exceeded size limit.",
                        failed_operation=request.tool_name,
                    )
                    if truncated
                    else None
                ),
            )
        except Exception as exc:  # noqa: BLE001
            code = str(exc) if str(exc) in {item.value for item in FailureCode} else FailureCode.INVALID_ARGUMENT.value
            return ToolResult(
                tool_name=request.tool_name,
                success=False,
                error=str(exc),
                duration_ms=int((time.time() - started) * 1000),
                failure=Failure(code=code, message=str(exc), failed_operation=request.tool_name, raw_error=str(exc)),
            )


def normalize_provider_failure(error: Exception | str, *, request_payload: dict[str, Any] | None = None, failed_operation: str = "provider") -> Failure:
    raw = str(error)
    lowered = raw.lower()
    code = FailureCode.PROVIDER_API.value
    decision = "abort"
    retry_outcome = "not_retried"
    if "tool choice is none" in lowered and "model called a tool" in lowered:
        code = FailureCode.PROVIDER_TOOL_CONFLICT.value
        decision = "retry_without_unsupported_tool_execution"
    elif "429" in lowered or "rate limit" in lowered:
        code = FailureCode.PROVIDER_RATE_LIMITED.value
        decision = "retry"
    elif "invalid json" in lowered or raw.startswith("{"):
        code = FailureCode.PROVIDER_INVALID_JSON.value
        decision = "retry"
    elif "timed out" in lowered or isinstance(error, TimeoutError):
        code = FailureCode.PROVIDER_TIMEOUT.value
        decision = "retry"
    elif "authentication failed" in lowered or "401" in lowered or "403" in lowered:
        code = FailureCode.PROVIDER_AUTH.value
    elif "network error" in lowered or "urlopen error" in lowered:
        code = FailureCode.PROVIDER_NETWORK.value
        decision = "retry"
    elif "unavailable" in lowered:
        code = FailureCode.PROVIDER_UNAVAILABLE.value
        decision = "retry"
    return Failure(
        code=code,
        message=raw,
        failed_operation=failed_operation,
        raw_error=raw,
        recovery_decision=decision,
        retry_outcome=retry_outcome,
        request_payload=request_payload or {},
    )


class ProviderClient:
    def __init__(
        self,
        *,
        name: str,
        send: Callable[[dict[str, Any]], dict[str, Any]],
        retry_policy: RetryPolicy | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ):
        self.name = name
        self.send = send
        self.retry_policy = retry_policy or RetryPolicy()
        self.sleep_fn = sleep_fn or time.sleep

    def request(self, payload: dict[str, Any]) -> tuple[dict[str, Any] | None, list[ExecutionRecord], Failure | None]:
        execution_records: list[ExecutionRecord] = []
        last_output_fingerprint = ""
        for attempt in range(1, self.retry_policy.max_attempts + 1):
            started = time.time()
            request_fingerprint = Fingerprint.create(payload).value
            try:
                response = self.send(payload)
                output_fingerprint = Fingerprint.create(response).value
                failure: Failure | None = None
                if output_fingerprint == last_output_fingerprint and last_output_fingerprint:
                    failure = Failure(
                        code=FailureCode.UNCHANGED_OUTPUT.value,
                        message="Provider returned unchanged output on retry.",
                        failed_operation=self.name,
                        recovery_decision="continue_or_exhaust",
                        retry_outcome="unchanged_output",
                        request_payload=payload,
                    )
                record = ExecutionRecord(
                    record_id=Fingerprint.create(self.name, attempt, payload, response).value,
                    operation="provider_request",
                    state=TaskState.COMPLETE.value,
                    input_fingerprint=request_fingerprint,
                    output_fingerprint=output_fingerprint,
                    request=payload,
                    response=response,
                    provider=self.name,
                    retry_attempt=attempt,
                    duration_ms=int((time.time() - started) * 1000),
                    failure=failure,
                )
                execution_records.append(record)
                if failure is None:
                    return response, execution_records, None
                last_output_fingerprint = output_fingerprint
            except Exception as exc:  # noqa: BLE001
                failure = normalize_provider_failure(exc, request_payload=payload, failed_operation=self.name)
                if attempt >= self.retry_policy.max_attempts or failure.recovery_decision != "retry":
                    failure.retry_outcome = "failed"
                else:
                    failure.retry_outcome = "retrying"
                execution_records.append(
                    ExecutionRecord(
                        record_id=Fingerprint.create(self.name, attempt, payload, str(exc)).value,
                        operation="provider_request",
                        state=(TaskState.RETRY_EXHAUSTED.value if attempt >= self.retry_policy.max_attempts else TaskState.RETRYING.value),
                        input_fingerprint=request_fingerprint,
                        request=payload,
                        provider=self.name,
                        retry_attempt=attempt,
                        duration_ms=int((time.time() - started) * 1000),
                        failure=failure,
                    )
                )
                if failure.recovery_decision != "retry" or attempt >= self.retry_policy.max_attempts:
                    if attempt >= self.retry_policy.max_attempts and failure.code != FailureCode.PROVIDER_TOOL_CONFLICT.value:
                        failure.retry_outcome = FailureCode.RETRY_EXHAUSTED.value
                    return None, execution_records, failure
            if attempt < self.retry_policy.max_attempts:
                self.sleep_fn(self.retry_policy.delay_for(attempt))
        failure = Failure(
            code=FailureCode.RETRY_EXHAUSTED.value,
            message="Provider retry policy exhausted.",
            failed_operation=self.name,
            recovery_decision="abort",
            retry_outcome=FailureCode.RETRY_EXHAUSTED.value,
            request_payload=payload,
        )
        return None, execution_records, failure


def bounded_subprocess(argv: list[str], *, cwd: str | Path, timeout: int = 120) -> ValidationResult:
    started = time.time()
    try:
        result = subprocess.run(
            argv,
            cwd=Path(cwd).resolve(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        failure = Failure(
            code=FailureCode.TOOL_TIMEOUT.value,
            message=str(exc),
            failed_operation="subprocess",
            raw_error=str(exc),
        )
        return ValidationResult(passed=False, summary="timed out", failure=failure)
    record = {
        "argv": argv,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
        "duration_ms": int((time.time() - started) * 1000),
    }
    return ValidationResult(
        passed=result.returncode == 0,
        summary="passed" if result.returncode == 0 else "failed",
        checks=[record],
        failure=(
            None
            if result.returncode == 0
            else Failure(
                code=FailureCode.VALIDATION_FAILED.value,
                message=result.stderr[-500:] or result.stdout[-500:] or "subprocess failed",
                failed_operation="subprocess",
                raw_error=result.stderr[-1000:],
            )
        ),
    )
