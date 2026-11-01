import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = "data/repository_audits/20261101T161513Z-main-knowledge-signal-and-approval-workflow-gaps.json"


def load():
    return json.loads((ROOT / AUDIT).read_text(encoding="utf-8"))


def test_current_main_knowledge_signal_cycle_is_recorded_as_manual_writer():
    audit = load()
    item = next(x for x in audit["uncovered_workflows"] if x["path"].endswith("knowledge-signal-cycle.yml"))
    assert item["permissions"] == "contents: write"
    assert "GROQ_API_KEY" in item["secrets"]
    assert "git push main" in item["operations"]
    assert item["protected_environment"] == "NONE"


def test_current_main_approval_label_workflow_has_no_protected_human_review():
    audit = load()
    item = next(x for x in audit["uncovered_workflows"] if x["path"].endswith("barrot-approve-pr.yml"))
    assert item["permissions"] == "contents: read; pull-requests: write"
    assert item["actor_allowlist"] == "NONE_IN_CURRENT_MAIN_FILE"
    assert item["protected_environment"] == "NONE"
    assert item["merge_operation"] == "NONE_IN_THIS_WORKFLOW"


def test_security_proposal_is_distinct_from_active_main():
    audit = load()
    pr = audit["proposals"]["pr1465"]
    assert pr["state"] == "OPEN_DRAFT_UNMERGED"
    assert pr["latest_head"] == "57805749b156477e1c0b6d8bdf3040e5f5c5998a"
    assert pr["latest_head_ci"] == "PENDING_AT_CAPTURE"
    assert audit["controls"]["main_modified"] is False
    assert audit["controls"]["merge_performed"] is False


def test_research_and_security_evidence_are_exact_head_scoped():
    audit = load()
    research = audit["proposals"]["pr1464"]
    assert research["exact_head_ci"]["tests_passed"] == 401
    assert research["exact_head_ci"]["subtests_passed"] == 8
    assert research["exact_head_gate"]["conclusion"] == "SUCCESS_MERGING_DISABLED"
    assert audit["proposals"]["pr1465"]["prior_verified_ci"]["tests_passed"] == 378
