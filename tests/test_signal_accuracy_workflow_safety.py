from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_signal_accuracy_workflow_is_disabled_until_fixed_horizon_evaluator_is_verified() -> None:
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "check-signal-accuracy.yml"
    ).read_text(encoding="utf-8")

    assert "workflow_dispatch: {}" in workflow
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    for forbidden in (
        "schedule:",
        "contents: write",
        "actions/checkout",
        "scripts/check_signal_accuracy.py",
        "git add",
        "git commit",
        "git push",
        "requests",
        "GH_TOKEN",
    ):
        assert forbidden not in workflow
