from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


COLLABORATION_ROOT = ".barrot/collaboration_records"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _fingerprint(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass
class AgentReport:
    agent: str
    status: str
    observations: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    interpretation: str = ""
    proposed_action: str = ""
    risks: list[str] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    confidence: str = ""
    independent: bool = True
    created_at: str = field(default_factory=_now)


@dataclass
class EvidencePacket:
    case_id: str
    repository: str
    ref: str
    commit_sha: str
    working_tree_fingerprint: str
    relevant_files: list[str] = field(default_factory=list)
    commands: list[dict[str, Any]] = field(default_factory=list)
    tests: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)

    @property
    def fingerprint(self) -> str:
        return _fingerprint(asdict(self))


@dataclass
class DeliberationRecord:
    case_id: str
    evidence: dict[str, Any]
    barrett: dict[str, Any] | None = None
    chatgpt: dict[str, Any] | None = None
    status: str = "AWAITING_EXTERNAL_AGENT_INPUT"
    agreements: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    disputed_claims: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    proposed_resolution: str = ""
    validation_evidence: list[str] = field(default_factory=list)
    final_decision: str = ""
    provenance: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @property
    def fingerprint(self) -> str:
        return _fingerprint(asdict(self))


class DualAgentDeliberation:
    """
    Provider-neutral collaboration layer.

    Barrett and ChatGPT reports are persisted separately.
    Agreement never implies verification.
    Material disagreement produces DISPUTED.
    """

    def __init__(
        self,
        workspace: str | Path = ".",
        storage_root: str | Path | None = None,
    ) -> None:
        # storage_root is an explicit test/runtime injection point.
        # When omitted, collaboration records remain under the repository
        # workspace's .barrot/collaboration_records directory.
        self.workspace = Path(workspace).resolve()
        self.root = (
            Path(storage_root).resolve()
            if storage_root is not None
            else self.workspace / COLLABORATION_ROOT
        )
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, case_id: str) -> Path:
        safe = "".join(
            c if c.isalnum() or c in "._-" else "_"
            for c in case_id
        )
        return self.root / f"{safe}.json"

    def create_case(
        self,
        case_id: str,
        relevant_files: list[str] | None = None,
        issue: str = "",
        repo_root: str | Path | None = None,
        ref: str | None = None,
        commit: str | None = None,
    ) -> DeliberationRecord:
        evidence_workspace = (
            Path(repo_root).resolve()
            if repo_root is not None
            else self.workspace
        )

        if commit is None:
            commit = self._git("rev-parse", "HEAD", cwd=evidence_workspace)
        if ref is None:
            ref = self._git("rev-parse", "--abbrev-ref", "HEAD", cwd=evidence_workspace)

        try:
            status = self._git(
                "status",
                "--porcelain",
                cwd=evidence_workspace,
            )
        except subprocess.CalledProcessError:
            # A caller may provide a temporary evidence workspace that is
            # intentionally not a Git repository. Preserve empty status
            # rather than failing case creation.
            status = ""

        packet = EvidencePacket(
            case_id=case_id,
            repository=str(evidence_workspace),
            ref=ref,
            commit_sha=commit,
            working_tree_fingerprint=_fingerprint(status),
            relevant_files=relevant_files or [],
            provenance=["barrot_dual_agent_deliberation"],
        )

        if issue:
            packet.provenance.append(f"issue:{issue}")

        record = DeliberationRecord(
            case_id=case_id,
            evidence=asdict(packet),
            provenance=["barrot_dual_agent_deliberation"],
        )
        self.save(record)
        return record

    def add_report(
        self,
        case_id: str,
        report: AgentReport | None = None,
        *,
        agent: str | None = None,
        proposed_action: str | None = None,
        interpretation: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> DeliberationRecord:
        if report is None:
            if agent is None:
                raise TypeError("agent is required when report is omitted")
            report = AgentReport(
                agent=agent,
                status="PROPOSED",
                proposed_action=proposed_action or "",
                interpretation=interpretation or "",
                evidence_refs=evidence_refs or [],
            )

        record = self.load(case_id)

        if report.agent.upper() == "BARRETT":
            record.barrett = asdict(report)
        elif report.agent.upper() == "CHATGPT":
            record.chatgpt = asdict(report)
        else:
            raise ValueError(f"Unsupported agent: {report.agent}")

        record.updated_at = _now()
        self._evaluate(record)
        self.save(record)
        return record

    def _evaluate(self, record: DeliberationRecord) -> None:
        record.agreements = []
        record.disagreements = []

        if not record.barrett or not record.chatgpt:
            record.status = "AWAITING_EXTERNAL_AGENT_INPUT"
            return

        b = record.barrett
        c = record.chatgpt

        b_action = b.get("proposed_action", "").strip()
        c_action = c.get("proposed_action", "").strip()

        if b_action and c_action and b_action == c_action:
            record.agreements.append("proposed_action")
        else:
            record.disagreements.append("proposed_action")

        b_interp = b.get("interpretation", "").strip()
        c_interp = c.get("interpretation", "").strip()

        if b_interp and c_interp and b_interp == c_interp:
            record.agreements.append("interpretation")
        else:
            record.disagreements.append("interpretation")

        if record.disagreements:
            record.status = "DISPUTED"
            record.disputed_claims = list(record.disagreements)
            record.required_evidence = [
                "independent repository evidence resolving disputed claims"
            ]
        else:
            record.status = "AGREED_AWAITING_VALIDATION"
            record.required_evidence = [
                "deterministic validation independent of agent agreement"
            ]

    def can_execute(self, case_id: str) -> bool:
        record = self.load(case_id)

        return (
            record.status == "AGREED_AWAITING_VALIDATION"
            and bool(record.barrett)
            and bool(record.chatgpt)
        )

    def record_validation(
        self,
        case_id: str,
        evidence: list[str] | None = None,
        success: bool = False,
        *,
        evidence_refs: list[str] | None = None,
    ) -> DeliberationRecord:
        if evidence is None:
            evidence = evidence_refs or []
        elif evidence_refs is not None:
            evidence = [*evidence, *evidence_refs]

        record = self.load(case_id)
        record.validation_evidence.extend(evidence)

        if success:
            record.status = "VALIDATED"
            record.final_decision = "VALIDATED_BY_DETERMINISTIC_EVIDENCE"
        else:
            record.status = "VALIDATION_FAILED"
            record.final_decision = "VALIDATION_FAILED"

        record.updated_at = _now()
        self.save(record)
        return record

    def export_chatgpt_packet(self, case_id: str) -> Path:
        record = self.load(case_id)
        path = self.root / f"{case_id}.chatgpt_packet.json"

        payload = {
            "protocol": "barrot-dual-agent-deliberation-v1",
            "agent": "CHATGPT",
            "case_id": case_id,
            "evidence": record.evidence,
            "barrett_report": record.barrett,
            "status": record.status,
            "anti_circularity": True,
        }

        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return path

    def import_chatgpt_packet(
        self,
        case_id: str,
        packet_path: str | Path,
    ) -> DeliberationRecord:
        payload = json.loads(
            Path(packet_path).read_text(encoding="utf-8")
        )

        if payload.get("agent") != "CHATGPT":
            raise ValueError("Packet is not a CHATGPT packet")

        if payload.get("case_id") != case_id:
            raise ValueError("Packet case_id mismatch")

        report = payload.get("chatgpt_report")

        if not isinstance(report, dict):
            raise ValueError("Missing chatgpt_report")

        return self.add_report(
            case_id,
            AgentReport(
                agent="CHATGPT",
                status=report.get("status", "ANALYZED"),
                observations=report.get("observations", []),
                evidence_refs=report.get("evidence_refs", []),
                interpretation=report.get("interpretation", ""),
                proposed_action=report.get("proposed_action", ""),
                risks=report.get("risks", []),
                objections=report.get("objections", []),
                unresolved_questions=report.get(
                    "unresolved_questions", []
                ),
                confidence=report.get("confidence", ""),
                independent=True,
            ),
        )

    def save(self, record: DeliberationRecord) -> None:
        path = self._path(record.case_id)
        tmp = path.with_suffix(".tmp")

        tmp.write_text(
            json.dumps(asdict(record), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        tmp.replace(path)

    def get_case(self, case_id: str) -> DeliberationRecord:
        """Return an existing deliberation case by identifier."""
        return self.load(case_id)

    def load(self, case_id: str) -> DeliberationRecord:
        data = json.loads(
            self._path(case_id).read_text(encoding="utf-8")
        )

        return DeliberationRecord(**data)

    def _git(
        self,
        *args: str,
        cwd: str | Path | None = None,
    ) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=Path(cwd).resolve() if cwd is not None else self.workspace,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()


__all__ = [
    "AgentReport",
    "EvidencePacket",
    "DeliberationRecord",
    "DualAgentDeliberation",
]
