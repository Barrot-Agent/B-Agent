from __future__ import annotations

import json

import pytest

from barrot_agent.mmi.contracts import MMIExecutionState, ParsabilityState
from barrot_agent.mmi.ledger import LedgerIntegrityError, MMIExecutionLedger
from barrot_agent.mmi.lifecycle import MMIEvaluationInput, evaluate_mmi_state


def test_ledger_appends_sequence_and_verifies_hash_chain(tmp_path) -> None:
    ledger = MMIExecutionLedger(tmp_path / "mmi.jsonl")
    first = ledger.append(
        execution_id="run-1", event_type="declared", payload={"scope": ["body"]},
        evaluator_version="mmi-eval/1", actor="operator",
    )
    second = ledger.append(
        execution_id="run-1", event_type="acquired", payload={"sha256": "a" * 64},
        evaluator_version="mmi-eval/1", actor="barrot",
        parent_execution_id="run-0",
    )
    verified = ledger.verify()
    assert [row["sequence"] for row in verified] == [1, 2]
    assert second["previous_hash"] == first["record_hash"]


def test_ledger_fails_closed_on_tampering_and_malformed_history(tmp_path) -> None:
    path = tmp_path / "mmi.jsonl"
    ledger = MMIExecutionLedger(path)
    ledger.append(
        execution_id="run-1", event_type="declared", payload={"scope": ["body"]},
        evaluator_version="1", actor="operator",
    )
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]["payload"]["scope"] = ["all"]
    path.write_text(json.dumps(rows[0]) + "\n")
    with pytest.raises(LedgerIntegrityError):
        ledger.verify()
    path.write_text("{broken\n")
    with pytest.raises(LedgerIntegrityError):
        ledger.verify()


def test_state_machine_separates_protocol_from_knowledge_completeness() -> None:
    result = evaluate_mmi_state(MMIEvaluationInput(
        authorized=True, acquired=True,
        parse_states=(ParsabilityState.COMPLETE,),
        protocol_requirements_met=True,
        unresolved_gaps=("independent sources",),
    ))
    assert result.state is MMIExecutionState.CORROBORATED
    assert result.protocol_complete is True
    assert result.knowledge_complete is False


def test_state_machine_never_calls_partial_parse_complete() -> None:
    result = evaluate_mmi_state(MMIEvaluationInput(
        authorized=True, acquired=True,
        parse_states=(ParsabilityState.PARTIAL,),
        protocol_requirements_met=True,
    ))
    assert result.state is MMIExecutionState.PARTIAL
    assert result.protocol_complete is False


def test_state_machine_blocks_unauthorized_and_preserves_conflicts() -> None:
    blocked = evaluate_mmi_state(MMIEvaluationInput(
        authorized=False, acquired=False, parse_states=(),
        protocol_requirements_met=False,
    ))
    assert blocked.state is MMIExecutionState.BLOCKED

    disputed = evaluate_mmi_state(MMIEvaluationInput(
        authorized=True, acquired=True,
        parse_states=(ParsabilityState.COMPLETE,),
        protocol_requirements_met=True, has_conflicts=True,
    ))
    assert disputed.state is MMIExecutionState.DISPUTED
    assert disputed.protocol_complete and not disputed.knowledge_complete
