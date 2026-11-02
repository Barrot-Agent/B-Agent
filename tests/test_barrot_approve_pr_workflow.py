from pathlib import Path


WORKFLOW = Path(".github/workflows/barrot-approve-pr.yml")


def test_barrot_approval_workflow_exists():
    assert WORKFLOW.is_file()


def test_barrot_approval_workflow_is_fail_closed_without_write_permissions():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "permissions: {}" in text
    assert "if: ${{ false }}" in text
    assert "pull-requests: write" not in text
    assert "contents: write" not in text
    assert "APPROVAL_NOT_PERFORMED" in text


def test_barrot_approval_workflow_cannot_apply_labels_comments_or_merge():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "labels[]=approved" not in text
    assert "gh api" not in text
    assert "gh pr" not in text
    assert "gh pr merge" not in text
    assert "merge_performed=true" not in text


def test_barrot_approval_workflow_explains_protected_human_review_requirement():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "distinct human reviewer" in text
    assert "protected-environment approval" in text
    assert "required reviewers" in text
