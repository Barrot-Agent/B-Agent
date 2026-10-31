from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "scripts/barrot_agent.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/barrot-agent.yml").read_text(encoding="utf-8")


def test_barrot_agent_default_branch_is_non_protected_task_branch():
    assert 'BRANCH = os.environ.get("BRANCH", "barrot/task-0")' in SCRIPT


def test_barrot_agent_checkout_rejects_main_and_arbitrary_branches():
    assert "def is_safe_task_branch(branch: str) -> bool:" in SCRIPT
    assert 're.fullmatch(r"barrot/task-[0-9]+", branch)' in SCRIPT
    assert 'branch.startswith(("repair/", "research/"))' in SCRIPT
    assert "Invalid Barrot task branch" in SCRIPT


def test_barrot_agent_pr_head_must_be_numeric_task_branch():
    assert "if not is_safe_task_branch(head_branch):" in SCRIPT
    assert "protected or unsafe branch" in SCRIPT
    assert 'BRANCH: barrot/task-${{' in WORKFLOW


def test_barrot_agent_script_never_merges_or_force_pushes():
    assert "gh pr merge" not in SCRIPT
    assert "git push --force" not in SCRIPT
    assert "git push -f" not in SCRIPT
