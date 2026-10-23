from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATHS = (
    ROOT / ".github/workflows/barrot-pr-automerge.yml",
    ROOT / ".github/workflows/barrot-gated-merge.yml",
)

def test_merge_workflows_are_manual_and_read_only():
    for path in WORKFLOW_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "workflow_dispatch:" in content, path
        assert "schedule:" not in content, path
        assert "pull_request:" not in content, path
        assert "contents: write" not in content, path
        assert "pull-requests: write" not in content, path
        assert "statuses: write" not in content, path
        assert "gh pr merge" not in content, path
        assert "gh pr review" not in content, path
        assert "gh pr comment" not in content, path
        assert "repos/$REPO/statuses/" not in content, path

def test_disabled_workflows_do_not_claim_to_enforce_a_merge_gate():
    for path in WORKFLOW_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "disabled" in content.lower(), path
        assert "approved" not in content.lower(), path
