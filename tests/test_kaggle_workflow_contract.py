"""Static safety contract for the Kaggle workflow and submission call site."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "kaggle-competitions.yml"
SCRIPT = ROOT / "scripts" / "kaggle_competitions_automation.py"


def test_workflow_invokes_existing_script_and_defaults_to_no_submissions():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "run: python scripts/kaggle_competitions_automation.py" in workflow
    assert "allow_submissions:" in workflow
    assert "default: false" in workflow
    assert "KAGGLE_ALLOW_SUBMISSIONS:" in workflow
    assert "KAGGLE_MAX_COMPETITIONS: '1'" in workflow


def test_submission_call_is_guarded_by_explicit_policy():
    source = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    guarded_calls = []
    for node in ast.walk(main):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Call):
            func = node.test.func
            if isinstance(func, ast.Name) and func.id == "submissions_allowed":
                guarded_calls.extend(
                    n for n in ast.walk(node) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name) and n.func.id == "_submit"
                )
    all_submit_calls = [
        n for n in ast.walk(main) if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name) and n.func.id == "_submit"
    ]
    assert len(guarded_calls) == 1
    assert len(all_submit_calls) == 1
    assert "dry-run (submission disabled)" in source
