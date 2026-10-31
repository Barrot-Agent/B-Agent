#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path[:] = [
    str(ROOT),
    *[
        entry
        for entry in sys.path
        if Path(entry or ".").resolve() != SCRIPTS
        and str(Path(entry or ".").resolve()) != str(ROOT)
    ],
]

from barrot_agent.ingestion.mmi_contract import (  # noqa: E402
    MMI_MAX_DEPTH,
    MMIOutcome,
    MMIState,
    MMIStage,
    StageStatus,
    build_stage_map,
)


def evaluate(payload: dict) -> dict:
    stages = [
        MMIStage(
            name=str(item["name"]),
            status=StageStatus(item["status"]),
            evidence_refs=list(item.get("evidence_refs", [])),
            details=dict(item.get("details", {})),
        )
        for item in payload.get("stages", [])
    ]

    stage_map = build_stage_map(stages)
    errors: list[str] = []
    warnings: list[str] = []

    for required in (
        MMIState.RECEIVED.value,
        MMIState.PROVENANCE_CAPTURED.value,
        MMIState.DECOMPOSED.value,
        MMIState.REPRESENTATIONS_ASSESSED.value,
        MMIState.EVIDENCE_NORMALIZED.value,
        MMIState.CORROBORATION.value,
        MMIState.GAP_ANALYSIS.value,
        MMIState.RECONCILIATION.value,
        MMIState.LEARNING_EXTRACTED.value,
        MMIState.CAPABILITY_ANALYZED.value,
        MMIState.ACQUISITION_TARGETS_GENERATED.value,
        MMIState.VERIFICATION.value,
    ):
        if required not in stage_map:
            errors.append(f"required stage missing: {required}")
            continue

        status = stage_map[required].status

        if status == StageStatus.BLOCKED:
            errors.append(f"required stage blocked: {required}")
        elif status == StageStatus.UNKNOWN:
            errors.append(f"required stage unknown: {required}")
        elif status == StageStatus.PARTIAL:
            warnings.append(f"required stage partial: {required}")

    source = payload.get("source", {})
    for field in (
        "source_id",
        "source_type",
        "uri",
        "version",
        "content_hash",
        "acquired_at",
    ):
        if not source.get(field):
            errors.append(f"source provenance missing: {field}")

    for component in payload.get("components", []):
        component_depth = int(component.get("component_depth", -1))
        provenance_depth = int(component.get("provenance_depth", -1))

        if not 0 <= component_depth <= MMI_MAX_DEPTH:
            errors.append(
                f"component depth outside 0..{MMI_MAX_DEPTH}: "
                f"{component.get('component_id')}"
            )

        if not 0 <= provenance_depth <= MMI_MAX_DEPTH:
            errors.append(
                f"provenance depth outside 0..{MMI_MAX_DEPTH}: "
                f"{component.get('component_id')}"
            )

    for evidence in payload.get("evidence", []):
        if evidence.get("generated_by_barrot"):
            refs = set(evidence.get("independent_sources", []))
            if evidence.get("evidence_id") in refs:
                errors.append(
                    f"Barrot-generated evidence cannot independently corroborate itself: "
                    f"{evidence.get('evidence_id')}"
                )

    termination = payload.get("termination", {})
    if not termination.get("bounded", False):
        errors.append("recursion termination controls not established")

    scope = payload.get("scope_boundary", {})
    if not scope.get("defined", False):
        errors.append("scope boundary not defined")

    protocol_complete = not errors

    knowledge_complete = bool(payload.get("knowledge_complete", False))
    if protocol_complete and not knowledge_complete:
        warnings.append(
            "protocol complete does not imply knowledge completeness"
        )

    if any(
        stage.status == StageStatus.PARTIAL
        for stage in stages
    ):
        outcome = MMIOutcome.PARTIAL_REINGESTION.value
    else:
        outcome = payload.get(
            "outcome",
            MMIOutcome.NEW_DATASET.value,
        )

    return {
        "protocol_version": payload.get("protocol_version", "unknown"),
        "protocol_complete": protocol_complete,
        "knowledge_complete": knowledge_complete,
        "outcome": outcome,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "complete": protocol_complete,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", help="JSON MMI result file")
    args = parser.parse_args()

    payload = json.loads(
        Path(args.payload).read_text(encoding="utf-8")
    )

    result = evaluate(payload)
    print(json.dumps(result, indent=2, sort_keys=True))

    return 0 if result["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
