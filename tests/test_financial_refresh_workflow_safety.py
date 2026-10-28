from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "financial-data-refresh.yml"


def test_financial_refresh_workflow_is_read_only_and_artifact_based() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "if: always()" in workflow
    assert "if-no-files-found: warn" in workflow
    assert "retention-days: 30" in workflow
    assert "run: python3 scripts/financial_data_refresh.py" in workflow
    assert "cron: '0 8 1 * *'" in workflow

    expected_outputs = (
        "ping-pongings/knowledge-base/financial_data.json",
        "web/financial_data.json",
    )
    for output in expected_outputs:
        assert output in workflow

    # Generated data must not mutate the protected source branch.
    assert not re.search(r"(?m)^\s*git\s+(?:commit|push)\b", workflow)
    assert "contents: write" not in workflow
