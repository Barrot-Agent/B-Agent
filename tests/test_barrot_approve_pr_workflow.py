from pathlib import Path


WORKFLOW = Path(".github/workflows/barrot-approve-pr.yml")


def test_barrot_approval_workflow_exists():
    assert WORKFLOW.is_file()


def test_barrot_approval_workflow_is_pull_request_write_scoped():
    text = WORKFLOW.read_text()
    assert "pull-requests: write" in text
    assert "contents: read" in text


def test_barrot_approval_requires_explicit_pr_inputs():
    text = WORKFLOW.read_text()
    assert "pr_number:" in text
    assert "expected_head_sha:" in text
    assert "reason:" in text


def test_barrot_approval_validates_open_main_pr_and_sha():
    text = WORKFLOW.read_text()
    assert '[[ "$state" != "open" ]]' in text
    assert '[[ "$base_ref" != "main" ]]' in text
    assert '[[ "$head_sha" != "$EXPECTED_HEAD_SHA" ]]' in text


def test_barrot_approval_rejects_cross_repository_prs():
    text = WORKFLOW.read_text()
    assert '[[ "$head_repo" != "$repo" ]]' in text


def test_barrot_approval_applies_only_approved_label():
    text = WORKFLOW.read_text()
    assert 'labels[]=approved' in text
    assert "MERGE_PERFORMED=FALSE" in text


def test_barrot_approval_records_audit_evidence():
    text = WORKFLOW.read_text()
    assert "Barrot controlled approval recorded." in text
    assert "Workflow run:" in text
    assert "Reason:" in text
