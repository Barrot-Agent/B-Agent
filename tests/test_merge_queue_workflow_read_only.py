from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "merge-queue.yml"


def test_merge_queue_workflow_has_read_only_permissions_and_trigger():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Merge Queue Audit (read-only)" in content
    assert "workflow_dispatch:" in content
    assert "contents: read" in content
    assert "pull-requests: read" in content
    assert "checks: read" in content
    assert "statuses: read" in content
    assert "secrets.GITHUB_TOKEN" in content
    assert "pulls?state=open&per_page=100" in content


def test_merge_queue_workflow_contains_no_mutation_path():
    content = WORKFLOW.read_text(encoding="utf-8").lower()
    forbidden = (
        "contents: write",
        "pull-requests: write",
        "gh pr merge",
        "gh pr comment",
        "update-branch",
        "--delete-branch",
        "secrets.gh_pat",
        "dry_run",
        "max_prs",
        "mode=all",
        "--method put",
    )
    for marker in forbidden:
        assert marker not in content, f"mutation-capable marker found: {marker}"
