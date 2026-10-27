from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

from barrot_agent.ingestion.mmi_contract import (
    MMI_MAX_DEPTH,
    MMIState,
    MMIStage,
    MMISource,
    MMIComponent,
    MMIEvidence,
    MMIResult,
    StageStatus,
    EvidenceState,
    MMIOutcome,
    build_stage_map,
    assess_representation,
)
from barrot_agent.ingestion.mmi_ledger import MMILedger
from barrot_agent.sources.mmi_adapter import MMIIngestionRequest


EXECUTION_VERSION = "1.0"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(value: Any) -> str:
    return sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class MMIExecutionInput:
    request: MMIIngestionRequest
    content: bytes
    content_type: str = "application/octet-stream"
    source_version: str = "unspecified"
    retrieval_uri: str | None = None
    retrieval_timestamp: str = field(default_factory=_utc)

    @property
    def content_hash(self) -> str:
        return sha256(self.content).hexdigest()

    @property
    def source_id(self) -> str:
        return _hash(
            {
                "target_id": self.request.target_id,
                "source_uri": self.request.source_uri,
                "source_version": self.source_version,
                "content_hash": self.content_hash,
            }
        )


class MMIExecutionEngine:
    """
    Thin deterministic execution layer for the canonical MMI contract.

    This layer captures and normalizes execution evidence. It does not
    silently invent unavailable component, provenance, or corroboration data.
    """

    def __init__(
        self,
        ledger_path: str | Path = ".barrot/mmi/execution_ledger.jsonl",
    ):
        self.ledger = MMILedger(ledger_path)

    def execute(
        self,
        execution_input: MMIExecutionInput,
        *,
        components: Iterable[MMIComponent] | None = None,
        evidence: Iterable[MMIEvidence] | None = None,
        representations: Iterable[str] | None = None,
        stages: Iterable[MMIStage] | None = None,
    ) -> MMIResult:
        request = execution_input.request

        # Construct MMISource strictly from the installed contract.
        source = MMISource(
            source_id=execution_input.source_id,
            source_type=request.source_type,
            uri=request.source_uri,
            version=execution_input.source_version,
            content_hash=execution_input.content_hash,
            acquired_at=execution_input.retrieval_timestamp,
            provenance={
                "publisher": request.publisher,
                "retrieval_uri": execution_input.retrieval_uri,
                "retrieval_timestamp": execution_input.retrieval_timestamp,
                "provenance_requirements": list(
                    request.provenance_requirements
                ),
                "verification_requirements": list(
                    request.verification_requirements
                ),
            },
        )

        component_list = list(components or [])
        evidence_list = list(evidence or [])
        representation_list = list(representations or [])

        stage_map = build_stage_map(list(stages or []))

        # Capture the execution itself before evaluating completeness.
        execution_record = {
            "event": "MMI_EXECUTION_RECEIVED",
            "execution_version": EXECUTION_VERSION,
            "target_id": request.target_id,
            "need_id": request.need_id,
            "source_id": source.source_id,
            "source_uri": source.uri,
            "source_version": source.version,
            "content_hash": source.content_hash,
            "component_count": len(component_list),
            "evidence_count": len(evidence_list),
            "representation_count": len(representation_list),
            "timestamp": _utc(),
        }

        ledger_record = self.ledger.append(
            execution_record["event"],
            execution_record,
        )

        # Missing representations are explicit rather than fabricated.
        representation_assessments = [
            assess_representation(name)
            for name in representation_list
        ]

        normalized_evidence = []
        for item in evidence_list:
            normalized_evidence.append(asdict(item))

        result = MMIResult(
            source=source,
            stages=list(stage_map.values()),
            components=component_list,
            evidence=evidence_list,
            gaps=[],
            acquisition_targets=[],
            outcome=MMIOutcome.NEW_DATASET,
            scope_boundary={
                "source_uri": source.uri,
                "source_type": source.source_type,
                "content_hash": source.content_hash,
                "content_type": execution_input.content_type,
            },
            termination={
                "bounded": True,
                "max_component_depth": MMI_MAX_DEPTH,
                "max_provenance_depth": MMI_MAX_DEPTH,
                "reason": "Execution layer does not fabricate recursive components.",
            },
            knowledge_complete=False,
            protocol_complete=False,
        )

        # Persist the resulting state as a second ledger event.
        result_record = {
            "event": "MMI_EXECUTION_RESULT",
            "target_id": request.target_id,
            "source_id": source.source_id,
            "request_hash": request.content_hash(),
            "protocol_complete": result.protocol_complete,
            "knowledge_complete": result.knowledge_complete,
            "outcome": result.outcome.value,
            "stage_statuses": {
                key: value.status.value
                for key, value in stage_map.items()
            },
            "component_count": len(component_list),
            "evidence_count": len(evidence_list),
            "timestamp": _utc(),
        }

        self.ledger.append(
            result_record["event"],
            result_record,
        )

        return result


def execute_bytes(
    request: MMIIngestionRequest,
    content: bytes,
    *,
    ledger_path: str | Path = ".barrot/mmi/execution_ledger.jsonl",
    content_type: str = "application/octet-stream",
    source_version: str = "unspecified",
    retrieval_uri: str | None = None,
) -> MMIResult:
    return MMIExecutionEngine(ledger_path).execute(
        MMIExecutionInput(
            request=request,
            content=content,
            content_type=content_type,
            source_version=source_version,
            retrieval_uri=retrieval_uri,
        )
    )
