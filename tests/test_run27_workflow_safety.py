from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _text(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8").lower()


def test_automerge_workflow_is_manual_and_read_only():
    text = _text("barrot-pr-automerge.yml")
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "pull_request:" not in text
    assert "contents: read" in text
    assert "pull-requests: read" in text
    assert "contents: write" not in text
    assert "pull-requests: write" not in text
    assert "gh pr merge" not in text
    assert "actions/checkout" not in text


def test_gated_merge_workflow_is_manual_and_read_only():
    text = _text("barrot-gated-merge.yml")
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "pull_request:" not in text
    assert "contents: read" in text
    assert "pull-requests: read" in text
    assert "statuses: write" not in text
    assert "gh api" not in text
    assert "gh pr merge" not in text
    assert "actions/checkout" not in text
    assert "not an approval" in text
    assert "must not be interpreted as merge approval" in text
