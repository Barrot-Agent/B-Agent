from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "xrp-ledger-validation.yml"
TEXT = WORKFLOW.read_text(encoding="utf-8")


def test_archive_validator_workflow_is_read_only_and_non_manual():
    assert "permissions:\n  contents: read" in TEXT
    assert "contents: write" not in TEXT
    assert "actions: write" not in TEXT
    assert "workflow_dispatch" not in TEXT
    assert "persist-credentials: false" in TEXT


def test_push_trigger_includes_exact_verification_branch():
    assert "verify/xrp-ledger-archive-20261101T031615Z" in TEXT
    assert "research/xrp-ledger-shard-migration-20261029T2210Z" in TEXT


def test_pull_request_trigger_covers_research_staging_bases():
    assert "research/xrp-ledger-shard-migration-20261029T2210Z" in TEXT
    assert "research/binance-xrp-hack-graph-20261101T0108Z" in TEXT
    assert "github.event.pull_request.head.repo.full_name == github.repository" in TEXT


def test_push_and_pull_request_triggers_cover_current_archive_base_branch():
    assert TEXT.count("verify/xrp-ledger-archive-20261101T070712Z") >= 2
