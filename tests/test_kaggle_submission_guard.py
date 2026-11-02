from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_kaggle_workflow_is_manual_and_submission_is_explicitly_gated():
    workflow = (ROOT / ".github" / "workflows" / "kaggle-competitions.yml").read_text(encoding="utf-8")
    assert "schedule:" not in workflow
    assert "workflow_dispatch:" in workflow
    assert "allow_submission:" in workflow
    assert "default: false" in workflow
    assert "inputs.allow_submission == true" in workflow
    assert "KAGGLE_ALLOW_SUBMISSIONS:" in workflow
    assert "python scripts/kaggle_competitions_automation.py" in workflow
    assert "python kaggle_competitions_automation.py" not in workflow


def test_kaggle_script_checks_submission_permission_before_api_authentication():
    script = (ROOT / "scripts" / "kaggle_competitions_automation.py").read_text(encoding="utf-8")
    main = script[script.index("def main()"):]
    assert "KAGGLE_ALLOW_SUBMISSIONS" in main
    assert main.index("_submission_authorized()") < main.index("_build_api()")
    submit = script[script.index("def _submit("):script.index("# ---------------------------------------------------------------------------\n# Main")]
    assert "_submission_authorized()" in submit
