from pathlib import Path


WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "coinbase-paper-trader.yml"
)


def test_paper_trader_workflow_is_manual_only_while_state_is_unreconciled():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in content
    assert "schedule:" not in content
    assert "Validate persisted paper state before any provider call" in content


def test_workflow_requires_explicit_boolean_authorization_and_has_no_schedule():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in content
    assert "allow_paper_state_mutation:" in content
    assert "default: false" in content
    assert "required: true" in content
    assert "if: ${{ inputs.allow_paper_state_mutation }}" in content
    assert "schedule:" not in content


def test_workflow_is_serialized_and_uses_only_contents_write():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "group: coinbase-paper-trader" in content
    assert "cancel-in-progress: false" in content
    assert "permissions:" in content
    assert "contents: write" in content
    assert "actions: write" not in content
    assert "timeout-minutes: 5" in content


def test_workflow_validates_state_and_requires_execute_flag():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "coinbase_paper_trader.py --validate-state" in content
    assert "coinbase_paper_trader.py --execute" in content
    assert "Persist validated paper-trading state" in content
