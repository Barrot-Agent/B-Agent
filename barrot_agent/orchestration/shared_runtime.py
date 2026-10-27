"""Shared orchestration primitives for deterministic Barrot task execution."""

from __future__ import annotations

import json
import re
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
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    SAFE_MODE_ACTIVE = "SAFE_MODE_ACTIVE"
    SECURITY_INCIDENT = "SECURITY_INCIDENT"
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


class Capability(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    NETWORK = "NETWORK"
    CREDENTIAL = "CREDENTIAL"
    DEPLOY = "DEPLOY"
    EXTERNAL_ACTION = "EXTERNAL_ACTION"
    ADMIN = "ADMIN"


class ThreatClassification(str, Enum):
    NORMAL = "NORMAL"
    SUSPICIOUS = "SUSPICIOUS"
    RESTRICTED = "RESTRICTED"
    COMPROMISED = "COMPROMISED"
    CONTAINED = "CONTAINED"
    RECOVERED = "RECOVERED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


class IncidentCategory(str, Enum):
    CODE_FAILURE = "CODE_FAILURE"
    ENVIRONMENT_FAILURE = "ENVIRONMENT_FAILURE"
    PERMISSION_FAILURE = "PERMISSION_FAILURE"
    POLICY_FAILURE = "POLICY_FAILURE"
    STATE_FAILURE = "STATE_FAILURE"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"


@dataclass
class AuthorizationDecision:
    allowed: bool
    capability: str
    requested_action: str
    threat_classification: str
    reason: str = ""
    incident_id: str = ""
    safe_mode_active: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IncidentRecord:
    incident_id: str
    fingerprint: str
    status: str
    summary: str
    requested_action: str
    authorization: str
    result: str
    category: str = ""
    evidence: list[str] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)
    root_cause: dict[str, Any] = field(default_factory=dict)
    containment_action: dict[str, Any] = field(default_factory=dict)
    recovery_action: dict[str, Any] = field(default_factory=dict)
    validation_result: dict[str, Any] = field(default_factory=dict)
    verification_result: dict[str, Any] = field(default_factory=dict)
    final_state: dict[str, Any] = field(default_factory=dict)
    agent: str = ""
    provider: str = ""
    model: str = ""
    session: str = ""
    task: str = ""
    tool: str = ""
    credential_scope: str = ""
    process: str = ""
    workspace: str = ""
    repository: str = ""
    timestamp: float = field(default_factory=time.time)
    safe_mode_active: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["provenance"] = self.provenance.to_dict()
        return payload


class SecurityLedger:
    """Tamper-evident incident ledger for deterministic runtime signals."""

    def __init__(self, workspace: str | Path):
        self.root = Path(workspace).resolve() / ".git" / "barrot_security"
        self.root.mkdir(parents=True, exist_ok=True)
        self.incident_dir = self.root / "incidents"
        self.incident_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.root / "ledger.jsonl"

    @staticmethod
    def _safe_id(value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value).strip("_") or "incident"

    def record(self, incident: IncidentRecord) -> Path:
        path = self.incident_dir / f"{self._safe_id(incident.incident_id)}.json"
        payload = incident.to_dict()
        rendered = json.dumps(payload, sort_keys=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "incident_id": incident.incident_id,
                        "fingerprint": incident.fingerprint,
                        "status": incident.status,
                        "category": incident.category,
                        "summary": incident.summary,
                        "requested_action": incident.requested_action,
                        "authorization": incident.authorization,
                        "result": incident.result,
                        "repository": incident.repository,
                        "workspace": incident.workspace,
                        "safe_mode_active": incident.safe_mode_active,
                        "timestamp": incident.timestamp,
                        "entry_fingerprint": Fingerprint.create(rendered).value,
                    },
                    sort_keys=True,
                )
            )
            handle.write("\n")
        return path


class DefensiveWatchdog:
    """Independent policy gate for containment, safe mode, and incident evidence."""

    BYPASS_PATTERNS = (
        r"ignore previous instructions",
        r"pretend\b",
        r"role-?play",
        r"simulate\b",
        r"act as unrestricted",
        r"emergency override",
        r"grant yourself",
        r"disable (?:the )?(?:watchdog|safe mode|logging|audit)",
        r"fake administrator",
    )
    SECRET_PATTERNS = (
        r"api[_-]?key",
        r"access[_-]?token",
        r"secret[_-]?key",
        r"password",
        r"authorization:\s*bearer",
    )
    PROCESS_PATTERNS = (r"subprocess\.", r"os\.system", r"pty\.spawn", r"multiprocessing\.", r"nohup ")
    NETWORK_PATTERNS = (r"requests\.", r"urllib\.", r"socket\.", r"curl ", r"wget ", r"nc ")
    PROTECTED_PATH_PREFIXES = (
        ".git/",
        ".barrot/",
        "barrot_agent/orchestration/shared_runtime.py",
        "barrot_agent/orchestration/repository_repair.py",
        "scripts/barrot_agent.py",
        "scripts/barrot_self_upgrade.py",
    )

    def __init__(
        self,
        workspace: str | Path,
        *,
        repository: str = "",
        session: str = "",
        task: str = "",
        allowed_capabilities: Iterable[Capability | str] | None = None,
    ):
        self.workspace = Path(workspace).resolve()
        self.repository = repository
        self.session = session
        self.task = task
        self.allowed_capabilities = {
            (item.value if isinstance(item, Capability) else str(item))
            for item in (
                allowed_capabilities
                or {
                    Capability.READ,
                    Capability.WRITE,
                    Capability.EXECUTE,
                    Capability.NETWORK,
                    Capability.EXTERNAL_ACTION,
                }
            )
        }
        self.ledger = SecurityLedger(self.workspace)
        self.state_path = self.ledger.root / "watchdog_state.json"
        self.safe_mode_active = False
        self.denied_requests = 0
        self.isolated_providers: set[str] = set()
        self._load_state()

    def _load_state(self) -> None:
        if not self.state_path.exists():
            return
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        self.safe_mode_active = bool(payload.get("safe_mode_active", False))
        self.denied_requests = int(payload.get("denied_requests", 0) or 0)
        self.isolated_providers = {str(item) for item in payload.get("isolated_providers", []) if str(item)}

    def _persist_state(self) -> None:
        self.state_path.write_text(
            json.dumps(
                {
                    "safe_mode_active": self.safe_mode_active,
                    "denied_requests": self.denied_requests,
                    "isolated_providers": sorted(self.isolated_providers),
                    "repository": self.repository,
                    "session": self.session,
                    "task": self.task,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _matches(patterns: Iterable[str], text: str) -> bool:
        lowered = text.lower()
        return any(re.search(pattern, lowered) for pattern in patterns)

    def _record_incident(
        self,
        *,
        status: ThreatClassification,
        summary: str,
        requested_action: str,
        authorization: str,
        result: str,
        evidence: Iterable[str] | None = None,
        provider: str = "",
        tool: str = "",
        process: str = "",
        credential_scope: str = "",
        category: IncidentCategory | str = "",
        root_cause: Mapping[str, Any] | None = None,
        containment_action: Mapping[str, Any] | None = None,
        recovery_action: Mapping[str, Any] | None = None,
        validation_result: Mapping[str, Any] | None = None,
        verification_result: Mapping[str, Any] | None = None,
        final_state: Mapping[str, Any] | None = None,
        provenance: Provenance | None = None,
    ) -> IncidentRecord:
        payload = {
            "status": status.value,
            "category": category.value if isinstance(category, IncidentCategory) else str(category),
            "summary": summary,
            "requested_action": requested_action,
            "authorization": authorization,
            "result": result,
            "provider": provider,
            "tool": tool,
            "process": process,
            "credential_scope": credential_scope,
            "workspace": str(self.workspace),
            "repository": self.repository,
            "session": self.session,
            "task": self.task,
        }
        incident = IncidentRecord(
            incident_id=Fingerprint.create(time.time(), payload).value[:16],
            fingerprint=Fingerprint.create(payload, sorted(evidence or [])).value,
            status=status.value,
            category=payload["category"],
            summary=summary,
            requested_action=requested_action,
            authorization=authorization,
            result=result,
            evidence=list(evidence or []),
            provenance=provenance or Provenance(),
            root_cause=dict(root_cause or {}),
            containment_action=dict(containment_action or {}),
            recovery_action=dict(recovery_action or {}),
            validation_result=dict(validation_result or {}),
            verification_result=dict(verification_result or {}),
            final_state=dict(final_state or {}),
            workspace=str(self.workspace),
            repository=self.repository,
            session=self.session,
            task=self.task,
            provider=provider,
            tool=tool,
            process=process,
            credential_scope=credential_scope,
            safe_mode_active=self.safe_mode_active,
        )
        self.ledger.record(incident)
        return incident

    def record_runtime_incident(
        self,
        *,
        category: IncidentCategory | str,
        status: ThreatClassification,
        summary: str,
        requested_action: str,
        authorization: str,
        result: str,
        evidence: Iterable[str] | None = None,
        root_cause: Mapping[str, Any] | None = None,
        containment_action: Mapping[str, Any] | None = None,
        recovery_action: Mapping[str, Any] | None = None,
        validation_result: Mapping[str, Any] | None = None,
        verification_result: Mapping[str, Any] | None = None,
        final_state: Mapping[str, Any] | None = None,
        provider: str = "",
        tool: str = "",
        process: str = "",
        credential_scope: str = "",
        provenance: Provenance | None = None,
    ) -> IncidentRecord:
        incident = self._record_incident(
            status=status,
            category=category,
            summary=summary,
            requested_action=requested_action,
            authorization=authorization,
            result=result,
            evidence=evidence,
            root_cause=root_cause,
            containment_action=containment_action,
            recovery_action=recovery_action,
            validation_result=validation_result,
            verification_result=verification_result,
            final_state=final_state,
            provider=provider,
            tool=tool,
            process=process,
            credential_scope=credential_scope,
            provenance=provenance,
        )
        self._persist_state()
        return incident

    def set_context(self, *, repository: str = "", session: str = "", task: str = "") -> None:
        if repository:
            self.repository = repository
        if session:
            self.session = session
        if task:
            self.task = task
        self._persist_state()

    def snapshot(self) -> dict[str, Any]:
        return {
            "safe_mode_active": self.safe_mode_active,
            "denied_requests": self.denied_requests,
            "isolated_providers": sorted(self.isolated_providers),
            "repository": self.repository,
            "session": self.session,
            "task": self.task,
        }

    def enter_safe_mode(self, reason: str, *, requested_action: str = "", authorization: str = "") -> IncidentRecord:
        self.safe_mode_active = True
        incident = self._record_incident(
            status=ThreatClassification.CONTAINED,
            summary="BARROT_SAFE_MODE activated",
            requested_action=requested_action or "enter_safe_mode",
            authorization=authorization or "watchdog containment",
            result=reason,
            evidence=[reason],
        )
        self._persist_state()
        return incident

    def authorize(
        self,
        capability: Capability | str,
        requested_action: str,
        *,
        authorization: str = "",
        tool: str = "",
        provider: str = "",
        process: str = "",
        credential_scope: str = "",
    ) -> AuthorizationDecision:
        capability_name = capability.value if isinstance(capability, Capability) else str(capability)
        action_text = " ".join(part for part in [requested_action, authorization, tool, provider, process] if part)
        if self.safe_mode_active and capability_name != Capability.READ.value:
            incident = self._record_incident(
                status=ThreatClassification.CONTAINED,
                summary="Safe Mode blocked external or mutating action",
                requested_action=requested_action,
                authorization=authorization or "safe_mode",
                result="blocked",
                evidence=[f"capability={capability_name}"],
                tool=tool,
                provider=provider,
                process=process,
                credential_scope=credential_scope,
            )
            self.denied_requests += 1
            self._persist_state()
            return AuthorizationDecision(
                allowed=False,
                capability=capability_name,
                requested_action=requested_action,
                threat_classification=ThreatClassification.CONTAINED.value,
                reason="BARROT_SAFE_MODE is active.",
                incident_id=incident.incident_id,
                safe_mode_active=True,
            )
        if capability_name not in self.allowed_capabilities:
            incident = self._record_incident(
                status=ThreatClassification.RESTRICTED,
                summary="Capability escalation denied",
                requested_action=requested_action,
                authorization=authorization or "policy",
                result="blocked",
                evidence=[f"capability={capability_name} not allowed"],
                tool=tool,
                provider=provider,
                process=process,
                credential_scope=credential_scope,
            )
            self.denied_requests += 1
            if self.denied_requests >= 3:
                self.enter_safe_mode("Repeated denied requests exceeded threshold.", requested_action=requested_action, authorization=authorization or "policy")
            self._persist_state()
            return AuthorizationDecision(
                allowed=False,
                capability=capability_name,
                requested_action=requested_action,
                threat_classification=ThreatClassification.RESTRICTED.value,
                reason="Requested capability is not authorized.",
                incident_id=incident.incident_id,
                safe_mode_active=self.safe_mode_active,
            )
        if self._matches(self.BYPASS_PATTERNS, action_text):
            incident = self._record_incident(
                status=ThreatClassification.SUSPICIOUS,
                summary="Instruction-bypass attempt detected",
                requested_action=requested_action,
                authorization=authorization or "policy",
                result="blocked",
                evidence=[action_text[:500]],
                tool=tool,
                provider=provider,
                process=process,
                credential_scope=credential_scope,
            )
            self.denied_requests += 1
            if self.denied_requests >= 3:
                self.enter_safe_mode("Repeated instruction-bypass attempts detected.", requested_action=requested_action, authorization=authorization or "policy")
            self._persist_state()
            return AuthorizationDecision(
                allowed=False,
                capability=capability_name,
                requested_action=requested_action,
                threat_classification=ThreatClassification.SUSPICIOUS.value,
                reason="Instruction-bypass language is not trusted.",
                incident_id=incident.incident_id,
                safe_mode_active=self.safe_mode_active,
            )
        if capability_name == Capability.CREDENTIAL.value or self._matches(self.SECRET_PATTERNS, action_text):
            incident = self._record_incident(
                status=ThreatClassification.HUMAN_REVIEW_REQUIRED,
                summary="Credential access request denied",
                requested_action=requested_action,
                authorization=authorization or "credential policy",
                result="blocked",
                evidence=[action_text[:500]],
                tool=tool,
                provider=provider,
                process=process,
                credential_scope=credential_scope or "withheld",
            )
            self.denied_requests += 1
            self._persist_state()
            return AuthorizationDecision(
                allowed=False,
                capability=capability_name,
                requested_action=requested_action,
                threat_classification=ThreatClassification.HUMAN_REVIEW_REQUIRED.value,
                reason="Credential possession is separated from model authority.",
                incident_id=incident.incident_id,
                safe_mode_active=self.safe_mode_active,
            )
        return AuthorizationDecision(
            allowed=True,
            capability=capability_name,
            requested_action=requested_action,
            threat_classification=ThreatClassification.NORMAL.value,
            safe_mode_active=self.safe_mode_active,
        )

    def inspect_command(self, argv: Iterable[str]) -> AuthorizationDecision:
        command_text = " ".join(str(part) for part in argv)
        if self._matches(self.PROCESS_PATTERNS, command_text):
            return self.authorize(
                Capability.ADMIN,
                command_text,
                authorization="hidden_subprocess_policy",
                process="subprocess",
            )
        if self._matches(self.NETWORK_PATTERNS, command_text):
            return self.authorize(
                Capability.NETWORK,
                command_text,
                authorization="network_policy",
                process="network",
            )
        return self.authorize(Capability.EXECUTE, command_text, authorization="bounded_repository_validation")

    def inspect_patch(self, *, path: str, new_content: str, reason: str = "") -> AuthorizationDecision:
        if any(path.startswith(prefix) for prefix in self.PROTECTED_PATH_PREFIXES):
            incident = self._record_incident(
                status=ThreatClassification.HUMAN_REVIEW_REQUIRED,
                summary="Security boundary self-modification blocked",
                requested_action=f"patch {path}",
                authorization="security_boundary",
                result="blocked",
                evidence=[path],
            )
            self.denied_requests += 1
            self._persist_state()
            return AuthorizationDecision(
                allowed=False,
                capability=Capability.WRITE.value,
                requested_action=f"patch {path}",
                threat_classification=ThreatClassification.HUMAN_REVIEW_REQUIRED.value,
                reason="Protected security boundary cannot be modified autonomously.",
                incident_id=incident.incident_id,
                safe_mode_active=self.safe_mode_active,
            )
        if self._matches(self.SECRET_PATTERNS, new_content):
            incident = self._record_incident(
                status=ThreatClassification.SUSPICIOUS,
                summary="Potential secret material blocked in patch",
                requested_action=f"patch {path}",
                authorization="secret_policy",
                result="blocked",
                evidence=[path, reason[:200]],
            )
            self.denied_requests += 1
            self.enter_safe_mode("Potential secret material detected in generated patch.", requested_action=f"patch {path}", authorization="secret_policy")
            self._persist_state()
            return AuthorizationDecision(
                allowed=False,
                capability=Capability.WRITE.value,
                requested_action=f"patch {path}",
                threat_classification=ThreatClassification.CONTAINED.value,
                reason="Patch content appears to contain credential material.",
                incident_id=incident.incident_id,
                safe_mode_active=True,
            )
        return self.authorize(Capability.WRITE, f"patch {path}", authorization=reason or "repair_plan")

    def isolate_provider(self, provider: str, reason: str) -> IncidentRecord:
        self.isolated_providers.add(provider)
        incident = self._record_incident(
            status=ThreatClassification.CONTAINED,
            summary="Provider route isolated",
            requested_action=f"provider {provider}",
            authorization="provider_containment",
            result=reason,
            provider=provider,
            evidence=[reason],
        )
        self._persist_state()
        return incident

    def inspect_provider_failure(self, provider: str, failure: Failure) -> IncidentRecord:
        if failure.code == FailureCode.PROVIDER_AUTH.value:
            return self.isolate_provider(provider, failure.message or "provider authentication anomaly")
        status = ThreatClassification.SUSPICIOUS if failure.code in {FailureCode.PROVIDER_NETWORK.value, FailureCode.PROVIDER_TIMEOUT.value} else ThreatClassification.RESTRICTED
        incident = self._record_incident(
            status=status,
            summary="Provider anomaly detected",
            requested_action=f"provider {provider}",
            authorization="provider_monitoring",
            result=failure.message,
            provider=provider,
            evidence=[failure.code, failure.raw_error[:500]],
        )
        self._persist_state()
        return incident

    def provider_allowed(self, provider: str) -> bool:
        return provider not in self.isolated_providers and not self.safe_mode_active

    def inspect_checkpoint(self, payload_text: str) -> AuthorizationDecision:
        try:
            json.loads(payload_text)
        except json.JSONDecodeError:
            incident = self._record_incident(
                status=ThreatClassification.COMPROMISED,
                summary="Corrupted checkpoint detected",
                requested_action="checkpoint load",
                authorization="checkpoint_integrity",
                result="blocked",
                evidence=[payload_text[:200]],
            )
            self.denied_requests += 1
            self.enter_safe_mode("Checkpoint integrity verification failed.", requested_action="checkpoint load", authorization="checkpoint_integrity")
            self._persist_state()
            return AuthorizationDecision(
                allowed=False,
                capability=Capability.READ.value,
                requested_action="checkpoint load",
                threat_classification=ThreatClassification.CONTAINED.value,
                reason="Checkpoint payload is corrupted.",
                incident_id=incident.incident_id,
                safe_mode_active=True,
            )
        return AuthorizationDecision(
            allowed=True,
            capability=Capability.READ.value,
            requested_action="checkpoint load",
            threat_classification=ThreatClassification.NORMAL.value,
            safe_mode_active=self.safe_mode_active,
        )

    def record_completion_gate_block(self, reason: str) -> IncidentRecord:
        incident = self._record_incident(
            status=ThreatClassification.SUSPICIOUS,
            summary="Completion gate manipulation or evidence gap prevented completion",
            requested_action="completion_gate",
            authorization="completion_gate",
            result=reason,
            evidence=[reason],
        )
        self._persist_state()
        return incident


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
        watchdog: DefensiveWatchdog | None = None,
        tool_capabilities: Mapping[str, Capability | str] | None = None,
    ):
        self.workspace = Path(workspace).resolve()
        self.tool_map = dict(tool_map)
        self.output_limit_bytes = output_limit_bytes
        self.watchdog = watchdog
        self.tool_capabilities = dict(tool_capabilities or {})

    def _capability_for(self, tool_name: str) -> Capability | str:
        if tool_name in self.tool_capabilities:
            return self.tool_capabilities[tool_name]
        lowered = tool_name.lower()
        if any(token in lowered for token in ("delete", "write", "patch", "edit")):
            return Capability.WRITE
        if any(token in lowered for token in ("deploy", "publish")):
            return Capability.DEPLOY
        if any(token in lowered for token in ("network", "http", "fetch")):
            return Capability.NETWORK
        return Capability.READ

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
            if self.watchdog is not None:
                decision = self.watchdog.authorize(
                    self._capability_for(request.tool_name),
                    f"{request.tool_name} {sorted(request.arguments)}",
                    authorization="controlled_tool_execution",
                    tool=request.tool_name,
                )
                if not decision.allowed:
                    raise ValueError(
                        FailureCode.SAFE_MODE_ACTIVE.value
                        if decision.safe_mode_active
                        else FailureCode.AUTHORIZATION_DENIED.value
                    )
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
        watchdog: DefensiveWatchdog | None = None,
    ):
        self.name = name
        self.send = send
        self.retry_policy = retry_policy or RetryPolicy()
        self.sleep_fn = sleep_fn or time.sleep
        self.watchdog = watchdog

    def request(self, payload: dict[str, Any]) -> tuple[dict[str, Any] | None, list[ExecutionRecord], Failure | None]:
        execution_records: list[ExecutionRecord] = []
        last_output_fingerprint = ""
        if self.watchdog is not None:
            decision = self.watchdog.authorize(
                Capability.NETWORK,
                f"provider {self.name} request",
                authorization="provider_request",
                provider=self.name,
            )
            if not decision.allowed or not self.watchdog.provider_allowed(self.name):
                failure = Failure(
                    code=FailureCode.SAFE_MODE_ACTIVE.value if decision.safe_mode_active else FailureCode.AUTHORIZATION_DENIED.value,
                    message=decision.reason or f"Provider {self.name} is not available for use.",
                    failed_operation=self.name,
                    recovery_decision="abort",
                    retry_outcome="not_retried",
                    request_payload=payload,
                )
                execution_records.append(
                    ExecutionRecord(
                        record_id=Fingerprint.create(self.name, payload, failure.message).value,
                        operation="provider_request",
                        state=TaskState.BLOCKED.value,
                        input_fingerprint=Fingerprint.create(payload).value,
                        request=payload,
                        provider=self.name,
                        retry_attempt=1,
                        duration_ms=0,
                        failure=failure,
                    )
                )
                return None, execution_records, failure
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
                if self.watchdog is not None:
                    self.watchdog.inspect_provider_failure(self.name, failure)
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
