from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATHS = (
    ROOT / ".github/workflows/barrot-pr-automerge.yml",
    ROOT / ".github/workflows/barrot-gated-merge.yml",
)

def test_merge_workflows_are_manual_read_only_noops():
    for path in WORKFLOW_PATHS:
        content = path.read_text(encoding="utf-8")
        assert re.search(r"(?m)^on:\s*\n\s+workflow_dispatch:\s*$", content), path
        for forbidden in (
            "schedule:",
            "pull_request:",
            "push:",
            "workflow_run:",
            "contents: write",
            "pull-requests: write",
            "statuses: write",
            "gh pr merge",
            "gh pr review",
            "gh pr comment",
            "/statuses/",
            "actions/checkout",
        ):
            assert forbidden not in content, (path, forbidden)
        assert "contents: read" in content, path
        assert "pull-requests: read" in content, path
        assert "disabled" in content.lower(), path

def test_ci_runs_on_barrot_branches_and_includes_this_regression_test():
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert '"barrot/**"' in ci, "CI must run for Barrot safety branches"
    assert "tests/test_merge_workflow_safety_run38.py" in ci
