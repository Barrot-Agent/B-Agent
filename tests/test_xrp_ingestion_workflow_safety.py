"""The XRP ingestion workflow is read-only and its integration smoke path is narrowly scoped."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "xrp-public-ingestion.yml"


def test_production_schedule_is_separate_from_integration_smoke():
    payload = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert payload["on"]["schedule"] == [
        {"cron": "3 * * * *"},
        {"cron": "15 0 * * *"},
    ]
    assert payload["on"]["push"]["branches"] == ["integration/**"]
    assert payload["on"]["push"]["paths"] == [
        ".github/workflows/xrp-public-ingestion.yml",
        "barrot_agent/evolution/research_timestamp_corrections.py",
        "barrot_agent/evolution/xrp_public_ingestion.py",
        "barrot_agent/evolution/rlusd_cross_chain_research.py",
        "barrot_agent/evolution/sec_edgar.py",
    ]
    assert "workflow_dispatch" in payload["on"]
    dispatch_inputs = payload["on"]["workflow_dispatch"]["inputs"]
    assert dispatch_inputs["capture_event_sources"]["type"] == "boolean"
    assert dispatch_inputs["capture_event_sources"]["default"] == "false"
    assert dispatch_inputs["capture_event_sources"]["required"] == "false"
    capture_step = next(
        step for step in payload["jobs"]["capture"]["steps"]
        if step.get("name") == "Capture public XRP market sources and evaluate historical baselines"
    )
    assert "startsWith(github.ref, 'refs/heads/integration/')" in capture_step["env"]["INCLUDE_SEC_COMPANYFACTS"]
    capture_event_sources = capture_step["env"]["CAPTURE_EVENT_SOURCES"]
    assert "inputs.capture_event_sources" in capture_event_sources
    assert "github.event.schedule == '15 0 * * *'" in capture_event_sources
    assert "github.event_name == 'push'" in capture_event_sources
    assert "refs/heads/integration/" in capture_event_sources
    assert payload["jobs"]["capture"]["if"] == (
        "github.ref == 'refs/heads/main' || "
        "(startsWith(github.ref, 'refs/heads/integration/') && "
        "(github.event_name == 'push' || github.event_name == 'workflow_dispatch'))"
    )


def test_ingestion_checks_out_exact_commit_with_read_only_permissions():
    payload = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert payload["permissions"]["actions"] == "read"
    assert payload["permissions"]["contents"] == "read"
    checkout = next(
        step for step in payload["jobs"]["capture"]["steps"]
        if step.get("uses", "").startswith("actions/checkout@")
    )
    assert checkout["with"]["ref"] == "${{ github.sha }}"
    assert checkout["with"]["persist-credentials"] == "false"


def test_receipt_and_feature_restoration_is_same_branch_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count("branch=${GITHUB_REF_NAME}") == 2
    assert text.count('.head_branch == $branch') == 2
    assert '--arg branch "$GITHUB_REF_NAME"' in text
    assert 'head_branch == "main"' not in text


def test_completed_run_selection_filters_status_locally_paginates_and_fails_closed():
    text = WORKFLOW.read_text(encoding="utf-8")
    # GitHub's server-side status=completed collection filter omitted a successful
    # scheduled predecessor in production, creating sibling receipt-chain branches.
    assert "&status=completed" not in text
    assert text.count('.status == "completed" and .conclusion == "success"') == 2
    assert text.count("branch=${GITHUB_REF_NAME}") == 2
    assert "page=1" in text
    assert "page=$((page + 1))" in text
    assert "total_prior_runs=$((total_prior_runs + page_run_count))" in text
    assert 'if [[ "$total_prior_runs" -eq 0 ]]; then' in text
    assert "No prior ingestion runs exist" in text
    assert "refusing to bootstrap a new chain" in text

def test_ingestion_workflow_cannot_write_to_repository_or_external_services():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "contents: write" not in text
    assert "git push" not in text
    assert "gh pr merge" not in text
    assert "persist-credentials: true" not in text
    assert "actions: write" not in text


def test_backfill_replay_always_checks_latest_main_checkpoint():
    ci_workflow = ROOT / ".github" / "workflows" / "ci.yml"
    text = ci_workflow.read_text(encoding="utf-8")
    assert "Check whether this exact backfill implementation already has a committed real-artifact receipt" not in text
    assert "steps.receipt.outputs.skip" not in text
    assert "if: github.event_name == 'pull_request' && github.event.pull_request.number == 1684" in text
    assert "Discover and verify the latest successful main checkpoint" in text
    assert "git/ref/heads/main" in text



def test_raw_receipt_artifact_includes_run_summary_and_raw_only_identity_index():
    payload = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    upload = next(
        step for step in payload["jobs"]["capture"]["steps"]
        if step.get("name") == "Upload content-addressed raw-source receipts (90-day GitHub artifact; not WORM)"
    )
    paths = upload["with"]["path"].splitlines()
    assert "artifacts/xrp_ingestion/raw_only_sources.json" in paths
    assert "artifacts/xrp_ingestion/summary.json" in paths
