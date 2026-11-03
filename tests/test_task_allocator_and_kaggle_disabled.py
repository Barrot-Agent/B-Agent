from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_unverified_multi_platform_task_allocator_is_inert() -> None:
    workflow = (WORKFLOWS / "task-allocator.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch: {}" in workflow
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    for forbidden in (
        "GROQ_API_KEY",
        "OPENAI_API_KEY",
        "CHATGPT_TOKEN",
        "GITHUB_TOKEN",
        "secrets.",
        "contents: write",
        "pull-requests: write",
        "scripts/barrot_task_allocator.py",
        "git push",
    ):
        assert forbidden not in workflow


def test_kaggle_submission_workflow_is_inert_until_protected_review() -> None:
    workflow = (WORKFLOWS / "kaggle-competitions.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch: {}" in workflow
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "schedule:" not in workflow
    for forbidden in (
        "KAGGLE_USERNAME",
        "KAGGLE_KEY",
        "secrets.",
        "kaggle_competitions_automation.py",
        "kaggle.com",
        "contents: write",
    ):
        assert forbidden not in workflow
